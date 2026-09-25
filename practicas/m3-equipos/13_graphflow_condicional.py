"""Práctica 13 — GraphFlow condicional: ciclos, ramas y filtrado de mensajes

🎯 Objetivo: un flujo que decide su camino según lo que dicen los agentes, con un ciclo de
revisión y un agente que solo ve parte del historial.

📚 Conceptos:
- Aristas condicionales: `add_edge(a, b, condition="TEXTO")` sigue esa arista solo si el
  último mensaje de `a` contiene "TEXTO". También acepta una función `mensaje -> bool`.
- Ciclos: una arista puede volver a un nodo anterior (revisor → redactor). Necesita una
  salida condicional y un punto de entrada (`set_entry_point`).
- `MessageFilterAgent`: envuelve a un agente y le filtra el historial. Útil para ahorrar
  tokens o para que un agente no se "contamine" con las discusiones previas.

  redactor ──► revisor ──(REVISAR)──► redactor   (ciclo)
                  │
                  └──(APROBADO)──► publicador     (solo ve el último mensaje del redactor)

▶️ Correr:  poetry run python practicas/m3-equipos/13_graphflow_condicional.py
"""

import asyncio

from autogen_agentchat.agents import AssistantAgent, MessageFilterAgent, MessageFilterConfig, PerSourceFilter
from autogen_agentchat.conditions import MaxMessageTermination
from autogen_agentchat.teams import DiGraphBuilder, GraphFlow
from autogen_agentchat.ui import Console

from comun.modelos import cliente_liviano


async def main() -> None:
    cliente = cliente_liviano()

    redactor = AssistantAgent(
        "redactor", cliente,
        system_message="Escribís tweets de máximo 200 caracteres. Si te piden cambios, reescribís el tweet completo.",
    )
    revisor = AssistantAgent(
        "revisor", cliente,
        system_message=(
            "Revisás tweets: tiene que tener un dato concreto y un llamado a la acción. "
            "Si cumple, respondé solo APROBADO. Si no, respondé REVISAR y el cambio en una línea."
        ),
    )
    publicador_base = AssistantAgent(
        "publicador", cliente,
        system_message="Recibís un tweet aprobado y le agregás 2 hashtags relevantes. Devolvés solo el tweet final.",
    )

    # 1️⃣ El publicador solo ve el ÚLTIMO mensaje del redactor (no la discusión con el revisor).
    publicador = MessageFilterAgent(
        name="publicador",
        wrapped_agent=publicador_base,
        filter=MessageFilterConfig(per_source=[PerSourceFilter(source="redactor", position="last", count=1)]),
    )

    # 2️⃣ Grafo con ciclo y ramas condicionales.
    grafo = DiGraphBuilder()
    grafo.add_node(redactor).add_node(revisor).add_node(publicador)
    grafo.add_edge(redactor, revisor)
    grafo.add_edge(revisor, redactor, condition="REVISAR")  # ciclo de corrección
    grafo.add_edge(revisor, publicador, condition="APROBADO")  # salida del ciclo
    grafo.set_entry_point(redactor)  # con ciclos, AutoGen necesita saber por dónde empezar

    flujo = GraphFlow(
        participants=grafo.get_participants(),
        graph=grafo.build(),
        termination_condition=MaxMessageTermination(10),  # red de seguridad si nunca aprueba
    )

    await Console(flujo.run_stream(task="Tweet anunciando un taller gratuito de agentes de IA con AutoGen."))

    await cliente.close()


# 🧪 EJERCICIO 1: reemplazá `condition="APROBADO"` por una función:
#    `condition=lambda msg: "APROBADO" in msg.to_model_text()`. ¿Qué ventaja tiene?
# 🧪 EJERCICIO 2: sacá el MessageFilterAgent (usá `publicador_base` directo) y compará los tokens.
# 🧪 EJERCICIO 3: agregá una tercera rama: si el revisor responde RECHAZADO, ir a un agente
#    `archivador` que explique por qué se descartó.

if __name__ == "__main__":
    asyncio.run(main())
