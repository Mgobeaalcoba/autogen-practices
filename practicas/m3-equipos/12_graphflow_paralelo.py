"""Práctica 12 — GraphFlow: flujos como grafo (secuencia + paralelo)

🎯 Objetivo: definir EXPLÍCITAMENTE quién habla después de quién, incluyendo ramas en paralelo.

📚 Conceptos:
- `DiGraphBuilder`: construís un grafo dirigido. Nodos = agentes. Aristas = "después de A, B".
- Fan-out: una arista de A hacia B y otra hacia C → B y C corren EN PARALELO.
- Fan-in (join): D recibe aristas de B y C → por defecto espera a que terminen AMBOS
  (`activation="all"`); con `activation="any"` arranca con el primero.
- `GraphFlow(participants, graph=...)`: el equipo que ejecuta el grafo.

        ┌──► analista_legal ──┐
  idea ─┤                     ├──► decisor
        └──► analista_costos ─┘

▶️ Correr:  poetry run python practicas/m3-equipos/12_graphflow_paralelo.py
"""

import asyncio

from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.teams import DiGraphBuilder, GraphFlow
from autogen_agentchat.ui import Console

from comun.modelos import cliente_groq, cliente_liviano


async def main() -> None:
    liviano = cliente_liviano()
    potente = cliente_groq()

    emprendedor = AssistantAgent(
        "emprendedor", liviano,
        system_message="Describís una idea de negocio en 3 oraciones concretas (qué, para quién, cómo cobra).",
    )
    analista_legal = AssistantAgent(
        "analista_legal", liviano,
        system_message="Listás 3 riesgos legales/regulatorios de la idea en Argentina. Solo viñetas.",
    )
    analista_costos = AssistantAgent(
        "analista_costos", liviano,
        system_message="Listás los 3 costos principales de arranque de la idea. Solo viñetas.",
    )
    decisor = AssistantAgent(
        "decisor", potente,
        system_message=(
            "Leés la idea y los dos análisis. Decidís AVANZAR o DESCARTAR y justificás en 3 líneas."
        ),
    )

    # 1️⃣ Construir el grafo.
    grafo = DiGraphBuilder()
    grafo.add_node(emprendedor).add_node(analista_legal).add_node(analista_costos).add_node(decisor)
    grafo.add_edge(emprendedor, analista_legal)  # fan-out: estas dos ramas
    grafo.add_edge(emprendedor, analista_costos)  # corren en paralelo
    grafo.add_edge(analista_legal, decisor)  # fan-in: el decisor espera
    grafo.add_edge(analista_costos, decisor)  # a los dos analistas

    # 2️⃣ Crear el equipo a partir del grafo.
    flujo = GraphFlow(participants=grafo.get_participants(), graph=grafo.build())

    await Console(flujo.run_stream(task="Idea: alquiler de bicicletas eléctricas por hora en Córdoba capital."))

    await liviano.close()
    await potente.close()


# 🧪 EJERCICIO 1: agregá un `analista_marketing` en paralelo con los otros dos.
# 🧪 EJERCICIO 2: cambiá el nodo decisor a `grafo.add_node(decisor, activation="any")`.
#    ¿Cuántas veces habla ahora el decisor? ¿Con qué información?

if __name__ == "__main__":
    asyncio.run(main())
