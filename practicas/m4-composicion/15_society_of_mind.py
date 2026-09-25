"""Práctica 15 — SocietyOfMindAgent: un equipo que se ve como UN agente

🎯 Objetivo: encapsular un equipo interno (con su propia discusión) detrás de un único agente,
y usarlo dentro de otro equipo.

📚 Conceptos:
- `SocietyOfMindAgent(name, team=equipo_interno, model_client=...)`: cuando le toca hablar,
  corre el equipo interno completo y después RESUME el resultado en un solo mensaje.
- En la consola vas a ver los mensajes internos (el stream los muestra para depurar), pero al
  HISTORIAL del equipo externo solo entra el resumen: el traductor nunca lee la discusión.
- Permite anidar equipos: "equipos de equipos".

   Equipo externo (RoundRobin):  [ comite_redaccion ] ──► traductor
                                          │
                     Equipo interno:  escritor ⇄ editor

▶️ Correr:  poetry run python practicas/m4-composicion/15_society_of_mind.py
"""

import asyncio

from autogen_agentchat.agents import AssistantAgent, SocietyOfMindAgent
from autogen_agentchat.conditions import MaxMessageTermination, TextMentionTermination
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.ui import Console

from comun.modelos import cliente_liviano


async def main() -> None:
    cliente = cliente_liviano()

    # 1️⃣ Equipo INTERNO: escritor y editor iteran hasta aprobar.
    escritor = AssistantAgent(
        "escritor", cliente,
        system_message="Escribís microrrelatos de máximo 60 palabras. Si el editor pide cambios, reescribís.",
    )
    editor = AssistantAgent(
        "editor", cliente,
        system_message="Editás microrrelatos. Si está bien, respondé APROBADO. Si no, pedí UN cambio concreto.",
    )
    equipo_interno = RoundRobinGroupChat(
        [escritor, editor],
        termination_condition=TextMentionTermination("APROBADO") | MaxMessageTermination(5),
    )

    # 2️⃣ Envolverlo: hacia afuera es un solo agente llamado "comite_redaccion".
    comite = SocietyOfMindAgent(
        "comite_redaccion",
        team=equipo_interno,
        model_client=cliente,  # se usa para resumir la discusión interna en una respuesta
        response_prompt="Devolvé SOLO la versión final aprobada del microrrelato, sin comentarios.",
    )

    # 3️⃣ Equipo EXTERNO: el comité produce el texto, el traductor lo pasa al inglés.
    traductor = AssistantAgent(
        "traductor", cliente,
        system_message="Traducís al inglés el último microrrelato recibido. Devolvés solo la traducción.",
    )
    equipo_externo = RoundRobinGroupChat([comite, traductor], max_turns=2)

    await Console(equipo_externo.run_stream(task="Microrrelato sobre un colectivo que nunca llega."))

    await cliente.close()


# 🧪 EJERCICIO 1: guardá `resultado = await equipo_externo.run(...)` y recorré `resultado.messages`.
#    ¿Qué mensajes del equipo interno quedaron en el historial externo y cuáles no?
# 🧪 EJERCICIO 2: cambiá `response_prompt` para que devuelva el relato + "Versiones descartadas: N".

if __name__ == "__main__":
    asyncio.run(main())
