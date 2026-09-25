"""Group chat de AutoGen: Investigador + Crítico, moderados por un Group Chat Manager
que elige dinámicamente (vía LLM) quién habla en cada turno. Backend: Groq (capa gratuita).

Uso:
    export GROQ_API_KEY=gsk_...   # o ponerla en .env
    poetry run python debate_groupchat.py
"""

import asyncio
import os
from datetime import date
from pathlib import Path

from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.base import TaskResult
from autogen_agentchat.teams import SelectorGroupChat
from autogen_ext.models.openai import OpenAIChatCompletionClient
from dotenv import load_dotenv

load_dotenv()

GROQ_BASE_URL = "https://api.groq.com/openai/v1"
AGENT_MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")
MODERATOR_MODEL = os.getenv("GROQ_MODERATOR_MODEL", "openai/gpt-oss-20b")
MAX_TURNS = int(os.getenv("MAX_TURNS", "5"))

# Tema real del día (24/09/2026). Los modelos de Groq no conocen noticias de hoy,
# así que les pasamos el contexto de la noticia en el propio mensaje inicial.
TOPIC = (
    "Hoy, 24 de septiembre de 2026, en la Asamblea General de la ONU, Volodímir Zelenski pidió "
    "mantener la presión económica sobre Rusia: sostuvo que los ingresos de Moscú deben seguir "
    "siendo un objetivo y que el comercio continuado con Rusia prolonga la guerra. También acusó "
    "a Rusia de reclutar combatientes de 47 países. El mismo día hubo explosiones en Kiev con al "
    "menos 2 muertos y 23 heridos.\n\n"
    "Pregunta del debate: ¿las sanciones y la presión económica sobre Rusia son una herramienta "
    "eficaz para acortar la guerra, o su efecto es limitado?"
)


def groq_client(model: str) -> OpenAIChatCompletionClient:
    return OpenAIChatCompletionClient(
        model=model,
        base_url=GROQ_BASE_URL,
        api_key=os.environ["GROQ_API_KEY"],
        model_info={
            "vision": False,
            "function_calling": True,
            "json_output": True,
            "structured_output": False,
            "family": "unknown",
        },
        temperature=0.7,
        max_tokens=2000,  # gpt-oss razona antes de responder; dejar margen
    )


SELECTOR_PROMPT = """Sos el moderador (Group Chat Manager) de un debate. Participantes:
{roles}

Historial de la conversación:
{history}

Decidí quién debe hablar a continuación según el estado del debate, NO por turnos fijos:
- Si el investigador hizo una afirmación, dato o argumento que todavía no fue cuestionado, elegí al critico.
- Si el critico planteó objeciones o pidió evidencia concreta que aún no fue respondida, elegí al investigador.
- Si el critico ya cuestionó algo pero su objeción quedó incompleta o hay un punto débil nuevo, podés volver a elegir al critico.
- Si el investigador quedó a mitad de un argumento o necesita aportar un dato nuevo, podés volver a elegir al investigador.

Respondé ÚNICAMENTE con el nombre de uno de {participants}, sin nada más."""


async def main() -> None:
    if not os.getenv("GROQ_API_KEY"):
        raise SystemExit("Falta GROQ_API_KEY (creala gratis en https://console.groq.com/keys).")

    agent_client = groq_client(AGENT_MODEL)
    moderator_client = groq_client(MODERATOR_MODEL)

    investigador = AssistantAgent(
        name="investigador",
        description="Investigador: aporta datos, cifras y argumentos a favor de una postura sobre el tema.",
        model_client=agent_client,
        system_message=(
            "Sos un investigador riguroso. Proponé datos, cifras, antecedentes históricos y argumentos "
            "sobre el tema. Si el crítico te cuestiona, respondé con evidencia o reconocé límites. "
            "Aclará cuando un dato es aproximado o puede estar desactualizado (tu conocimiento tiene "
            "fecha de corte). No inventes URLs, títulos de informes ni anexos: si no estás seguro de "
            "una fuente, decilo. Cuidá las unidades (millones vs. miles de millones). "
            "Respuestas de 120-180 palabras, en español."
        ),
    )
    critico = AssistantAgent(
        name="critico",
        description="Crítico: cuestiona los datos y argumentos del investigador, busca sesgos, huecos y contraejemplos.",
        model_client=agent_client,
        system_message=(
            "Sos un crítico escéptico y honesto. Cuestioná lo que dice el investigador: pedí fuentes, "
            "señalá sesgos, correlaciones que no son causalidad, contraejemplos y efectos no deseados. "
            "No estés en desacuerdo por deporte: si un punto es sólido, concedelo y atacá el más débil. "
            "Respuestas de 120-180 palabras, en español."
        ),
    )

    team = SelectorGroupChat(
        participants=[investigador, critico],
        model_client=moderator_client,  # el LLM del Group Chat Manager
        selector_prompt=SELECTOR_PROMPT,
        allow_repeated_speaker=True,  # el moderador puede dar la palabra dos veces seguidas al mismo
        max_turns=MAX_TURNS,
        emit_team_events=True,  # emite SelectSpeakerEvent con la decisión del moderador
    )

    lines = [f"# Debate AutoGen + Groq — {date.today().isoformat()}", "",
             f"Modelo agentes: `{AGENT_MODEL}` · Modelo moderador: `{MODERATOR_MODEL}`", ""]

    def emit(text: str) -> None:
        print(text, flush=True)
        lines.append(text)

    turn = 0
    async for item in team.run_stream(task=TOPIC):
        if isinstance(item, TaskResult):
            emit(f"\n---\n*Fin: {item.stop_reason}*")
            continue
        kind = type(item).__name__
        if kind == "SelectSpeakerEvent":
            emit(f"\n> 🎙️ **Moderador** da la palabra a → `{', '.join(item.content)}`")
        elif kind == "TextMessage":
            if item.source == "user":
                emit(f"\n## Tema\n\n{item.content}")
            else:
                turn += 1
                emit(f"\n## Turno {turn} — {item.source}\n\n{item.content}")

    out = Path(__file__).with_name("transcript.md")
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"\nTranscripción guardada en {out}")

    await agent_client.close()
    await moderator_client.close()


if __name__ == "__main__":
    asyncio.run(main())
