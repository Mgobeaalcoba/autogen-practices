"""Práctica 16 — Agentes y equipos como herramientas (AgentTool / TeamTool)

🎯 Objetivo: que un agente "coordinador" llame a otros agentes como si fueran funciones.

📚 Conceptos:
- `AgentTool(agente)`: convierte un agente en una herramienta. El coordinador decide cuándo
  consultarlo, con qué pregunta, y recibe su respuesta como resultado de la herramienta.
- `TeamTool(equipo, name, description)`: lo mismo, pero con un equipo entero.
- Diferencia con un group chat: acá NO hay conversación compartida. El coordinador tiene el
  control y cada experto solo ve la pregunta puntual que le hacen.
- ⚠️ Con AgentTool hay que desactivar llamadas en paralelo (`parallel_tool_calls=False`):
  un mismo agente no puede atender dos pedidos a la vez.

▶️ Correr:  poetry run python practicas/m4-composicion/16_agentes_como_herramientas.py
"""

import asyncio

from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.conditions import MaxMessageTermination, TextMentionTermination
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.tools import AgentTool, TeamTool
from autogen_agentchat.ui import Console

from comun.modelos import cliente_groq, cliente_liviano


async def main() -> None:
    expertos_llm = cliente_liviano()
    coordinador_llm = cliente_groq(parallel_tool_calls=False)  # una herramienta por vez

    # 1️⃣ Un experto individual. Su `description` es la descripción de la herramienta.
    nutricionista = AssistantAgent(
        "nutricionista", expertos_llm,
        description="Experta en nutrición: responde preguntas sobre alimentación saludable.",
        system_message="Sos nutricionista. Respondés en máximo 3 oraciones.",
    )

    # 2️⃣ Un equipo como herramienta: entrenador propone, kinesiólogo valida.
    entrenador = AssistantAgent(
        "entrenador", expertos_llm,
        system_message="Proponés rutinas de ejercicio simples (máx. 5 líneas).",
    )
    kinesiologo = AssistantAgent(
        "kinesiologo", expertos_llm,
        system_message="Revisás rutinas por riesgo de lesión. Si es segura, escribí SEGURA y la rutina final.",
    )
    equipo_entrenamiento = RoundRobinGroupChat(
        [entrenador, kinesiologo],
        termination_condition=TextMentionTermination("SEGURA") | MaxMessageTermination(4),
    )

    coordinador = AssistantAgent(
        "coordinador",
        coordinador_llm,
        tools=[
            AgentTool(nutricionista, return_value_as_last_message=True),
            TeamTool(
                equipo_entrenamiento,
                name="equipo_entrenamiento",
                description="Diseña una rutina de ejercicio segura (entrenador + kinesiólogo).",
                return_value_as_last_message=True,  # devolver solo la respuesta final del equipo
            ),
        ],
        system_message=(
            "Sos un coach de bienestar. Consultá a las herramientas que necesites y armá un plan "
            "final breve combinando sus respuestas. No inventes lo que ellas no dijeron."
        ),
        reflect_on_tool_use=True,
        max_tool_iterations=3,
    )

    await Console(coordinador.run_stream(task="Tengo 40 años, trabajo sentado y quiero empezar a cuidarme. ¿Por dónde arranco?"))

    await expertos_llm.close()
    await coordinador_llm.close()


# 🧪 EJERCICIO 1: agregá un `psicologo` como AgentTool y pedí un plan que incluya manejo del estrés.
# 🧪 EJERCICIO 2: cambiá `return_value_as_last_message` a False en el TeamTool. ¿Qué recibe ahora
#    el coordinador? ¿Cuántos tokens más consume?
# 🧪 EJERCICIO 3: compará este diseño con un SelectorGroupChat de los mismos agentes. ¿Cuándo
#    conviene cada uno?

if __name__ == "__main__":
    asyncio.run(main())
