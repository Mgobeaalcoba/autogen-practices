"""Práctica 07 — Humano en el loop

🎯 Objetivo: sumar a una persona real a la conversación para que dé feedback o apruebe.

📚 Conceptos:
- `UserProxyAgent`: un "agente" que, cuando le toca, le pide input a un humano (por defecto con
  `input()`). Se agrega a un equipo como cualquier otro participante.
- Evento nuevo: `UserInputRequestedEvent`, avisa que el sistema está esperando al humano.
- Patrón alternativo (sin UserProxyAgent): correr el equipo, mostrar el resultado, y volver a
  llamar `team.run(task=feedback)`: el equipo retoma desde donde quedó.

▶️ Correr:  poetry run python practicas/m2-control/07_humano_en_el_loop.py
   Escribí feedback cuando te lo pida. Escribí APROBADO para terminar.
"""

import asyncio

from autogen_agentchat.agents import AssistantAgent, UserProxyAgent
from autogen_agentchat.conditions import MaxMessageTermination, TextMentionTermination
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.ui import Console

from comun.modelos import cliente_liviano


async def main() -> None:
    cliente = cliente_liviano()

    redactor = AssistantAgent(
        name="redactor",
        model_client=cliente,
        system_message=(
            "Escribís slogans publicitarios cortos (máximo 12 palabras). "
            "Cuando recibís feedback, proponés una nueva versión que lo tenga en cuenta."
        ),
    )

    # 1️⃣ El humano como participante. `input_func` se puede reemplazar (web, Slack, etc.).
    humano = UserProxyAgent(name="humano", input_func=input)

    # 2️⃣ Termina cuando el humano escribe APROBADO (o como red de seguridad, a los 10 mensajes).
    fin = TextMentionTermination("APROBADO", sources=["humano"]) | MaxMessageTermination(10)

    # 3️⃣ RoundRobin: redactor propone → humano opina → redactor corrige → ...
    equipo = RoundRobinGroupChat([redactor, humano], termination_condition=fin)

    await Console(equipo.run_stream(task="Slogan para una app que enseña a programar con agentes de IA."))

    await cliente.close()


# 🧪 EJERCICIO 1: reemplazá `input_func` por una función que siempre devuelva "APROBADO" y usala
#    para testear el flujo sin intervención manual.
# 🧪 EJERCICIO 2: sacá al humano del equipo y usá el patrón alternativo: `await equipo.run(...)`,
#    mostrás el slogan, pedís feedback con `input()` y llamás de nuevo a `equipo.run(task=feedback)`.

if __name__ == "__main__":
    asyncio.run(main())
