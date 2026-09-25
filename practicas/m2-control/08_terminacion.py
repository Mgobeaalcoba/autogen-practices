"""Práctica 08 — Condiciones de terminación y cancelación

🎯 Objetivo: controlar CUÁNDO se detiene un equipo de agentes (y evitar loops infinitos que
consumen cuota).

📚 Conceptos (todas en `autogen_agentchat.conditions`):
- `MaxMessageTermination(n)`: después de n mensajes.
- `TextMentionTermination("X")`: cuando algún mensaje contiene "X".
- `TokenUsageTermination(max_total_token=n)`: al superar un presupuesto de tokens.
- `TimeoutTermination(segundos)`: al pasar un tiempo.
- `ExternalTermination()`: la detenés vos desde el código (ej: botón "Stop" en una UI).
- `SourceMatchTermination`, `FunctionCallTermination`, `HandoffTermination`, ...: ver docs.
- Se combinan con `|` (cualquiera) y `&` (todas).
- `CancellationToken`: corta en seco, incluso en medio de una llamada al LLM.

▶️ Correr:  poetry run python practicas/m2-control/08_terminacion.py
"""

import asyncio
import logging

from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.base import TaskResult
from autogen_agentchat.conditions import (
    ExternalTermination,
    MaxMessageTermination,
    TextMentionTermination,
    TokenUsageTermination,
)
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_core import CancellationToken

from comun.modelos import cliente_liviano


def crear_equipo(cliente, fin) -> RoundRobinGroupChat:
    """Dos agentes que charlan sin fin a propósito: solo la condición de fin los detiene."""
    optimista = AssistantAgent(
        "optimista", cliente, system_message="Respondés con una ventaja del tema. Una oración."
    )
    pesimista = AssistantAgent(
        "pesimista", cliente, system_message="Respondés con una desventaja del tema. Una oración."
    )
    return RoundRobinGroupChat([optimista, pesimista], termination_condition=fin)


def resumen(nombre: str, resultado: TaskResult) -> None:
    print(f"  {nombre}: {len(resultado.messages)} mensajes → stop_reason = {resultado.stop_reason!r}")


async def main() -> None:
    cliente = cliente_liviano()
    tema = "Trabajar desde casa."

    print("1️⃣ Combinación con | : cortar por palabra clave O por cantidad de mensajes")
    fin = TextMentionTermination("DESASTRE") | MaxMessageTermination(4)
    resumen("texto | máximo", await crear_equipo(cliente, fin).run(task=tema))

    print("2️⃣ Presupuesto de tokens")
    fin = TokenUsageTermination(max_total_token=1500)
    resumen("tokens", await crear_equipo(cliente, fin).run(task=tema))

    print("3️⃣ Terminación externa: el código decide parar (ej. un botón en la UI)")
    externa = ExternalTermination()
    equipo = crear_equipo(cliente, externa | MaxMessageTermination(20))
    corrida = asyncio.create_task(equipo.run(task=tema))
    await asyncio.sleep(3)
    externa.set()  # termina ordenadamente cuando el agente actual termine de hablar
    resumen("externa", await corrida)

    print("4️⃣ Cancelación: corta en seco, sin esperar al agente")
    # El runtime loguea con traceback el mensaje que quedó a medio procesar. Es esperable al
    # cancelar, así que lo silenciamos para que no parezca un error.
    logging.getLogger("autogen_core").setLevel(logging.CRITICAL)
    token = CancellationToken()
    equipo = crear_equipo(cliente, MaxMessageTermination(20))
    corrida = asyncio.create_task(equipo.run(task=tema, cancellation_token=token))
    await asyncio.sleep(2)
    token.cancel()
    try:
        await corrida
    except asyncio.CancelledError:
        print("  cancelación: la corrida se abortó (CancelledError). El equipo sigue usable.")

    await cliente.close()


# 🧪 EJERCICIO 1: combiná con `&`: `TextMentionTermination("A") & TextMentionTermination("B")`.
#    ¿Cuándo termina? ¿Qué pasa si nunca aparece una de las dos?
# 🧪 EJERCICIO 2: agregá `TimeoutTermination(5)` al escenario 1 y compará los stop_reason.
# 🧪 EJERCICIO 3: ¿qué diferencia observás entre ExternalTermination y CancellationToken?

if __name__ == "__main__":
    asyncio.run(main())
