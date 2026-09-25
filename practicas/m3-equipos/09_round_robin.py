"""Práctica 09 — RoundRobinGroupChat: turnos fijos

🎯 Objetivo: el equipo más simple. Los agentes hablan en orden, siempre el mismo.

📚 Conceptos:
- `RoundRobinGroupChat([a, b, c])`: a → b → c → a → ... hasta que se cumpla la condición de fin.
- Todos comparten el mismo historial (cada uno ve lo que dijeron los demás).
- Patrón clásico "productor → revisor": uno propone, otro revisa y aprueba.
- Un equipo es REANUDABLE: volver a llamar `run()` sigue desde donde quedó.

▶️ Correr:  poetry run python practicas/m3-equipos/09_round_robin.py
"""

import asyncio

from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.conditions import MaxMessageTermination, TextMentionTermination
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.ui import Console

from comun.modelos import cliente_liviano


async def main() -> None:
    cliente = cliente_liviano()

    programador = AssistantAgent(
        name="programador",
        model_client=cliente,
        system_message=(
            "Escribís funciones de Python cortas (máximo 25 líneas), con type hints y docstring. "
            "Respondé solo con el código, sin explicaciones. "
            "Si el revisor pide cambios, entregás la versión corregida completa."
        ),
    )
    revisor = AssistantAgent(
        name="revisor",
        model_client=cliente,
        system_message=(
            "Revisás código Python: bugs, casos borde y legibilidad. Si hay algo para mejorar, "
            "listalo en máximo 3 viñetas cortas. Si el código está bien, respondé solo con la palabra APROBADO."
        ),
    )

    fin = TextMentionTermination("APROBADO") | MaxMessageTermination(6)
    equipo = RoundRobinGroupChat([programador, revisor], termination_condition=fin)

    await Console(equipo.run_stream(task="Función que valide un CUIT argentino (11 dígitos con dígito verificador)."))

    # 🔁 El equipo es reanudable: una tarea nueva continúa con el mismo historial.
    print("\n=== Reanudando el mismo equipo con una tarea nueva ===")
    await Console(equipo.run_stream(task="Agregale tests con pytest a la versión aprobada."))

    await cliente.close()


# 🧪 EJERCICIO 1: sumá un tercer agente `documentador` que escriba un README de 5 líneas.
#    ¿En qué posición de la lista conviene ponerlo?
# 🧪 EJERCICIO 2: llamá a `await equipo.reset()` antes de la segunda tarea. ¿Qué cambia?

if __name__ == "__main__":
    asyncio.run(main())
