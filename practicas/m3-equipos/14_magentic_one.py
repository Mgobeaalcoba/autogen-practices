"""Práctica 14 — MagenticOneGroupChat: un orquestador que planifica

🎯 Objetivo: delegar la coordinación en un ORQUESTADOR que arma un plan, asigna pasos,
detecta si el equipo se estancó y replanifica.

📚 Conceptos:
- `MagenticOneGroupChat(participants, model_client)`: el `model_client` es el del orquestador.
- El orquestador mantiene dos "ledgers" (registros):
    · Task ledger: hechos conocidos, suposiciones y el plan.
    · Progress ledger: en cada paso evalúa si terminó, si hay progreso y a quién le toca.
- `max_stalls`: cuántos pasos sin progreso tolera antes de replanificar.
- Magentic-One original trae agentes especializados (WebSurfer, FileSurfer, Coder) en
  `autogen_ext.agents`. Acá usamos agentes simples para no depender de navegador ni Docker.

⚠️ Es el equipo que MÁS llamadas hace (el orquestador razona en cada paso). Con la capa
   gratuita puede tardar o chocar límites por minuto: por eso `max_turns` es bajo.

▶️ Correr:  poetry run python practicas/m3-equipos/14_magentic_one.py
"""

import asyncio

from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.teams import MagenticOneGroupChat
from autogen_agentchat.ui import Console

from comun.modelos import cliente_groq, cliente_liviano


def calcular_presupuesto(noches: int, precio_noche: float, comidas_por_dia: float) -> str:
    """Calcula el presupuesto total de un viaje: alojamiento + comidas."""
    total = noches * precio_noche + (noches + 1) * comidas_por_dia
    return f"Presupuesto total: ${total:,.0f} ({noches} noches)."


async def main() -> None:
    orquestador_llm = cliente_groq()  # el orquestador necesita el modelo más capaz
    agentes_llm = cliente_liviano()

    guia = AssistantAgent(
        "guia_turistico", agentes_llm,
        description="Conoce destinos de Argentina: qué visitar, cuándo ir y precios aproximados.",
        system_message="Sos guía turístico de Argentina. Respuestas concretas y breves (máx. 6 líneas).",
    )
    contador = AssistantAgent(
        "contador", agentes_llm,
        tools=[calcular_presupuesto],
        description="Hace cuentas de presupuesto con su herramienta.",
        system_message="Hacés cuentas SIEMPRE con la herramienta calcular_presupuesto. Respuestas breves.",
    )

    equipo = MagenticOneGroupChat(
        [guia, contador],
        model_client=orquestador_llm,
        max_turns=8,
        max_stalls=2,
    )

    await Console(
        equipo.run_stream(
            task=(
                "Armá una escapada de 3 noches a Mendoza para dos personas en otoño: "
                "3 actividades recomendadas y un presupuesto estimado total."
            )
        )
    )

    await orquestador_llm.close()
    await agentes_llm.close()


# 🧪 EJERCICIO 1: leé el primer mensaje del orquestador (el plan). ¿Qué hechos y suposiciones anotó?
# 🧪 EJERCICIO 2: sacale la herramienta al contador. ¿Detecta el orquestador que no hay progreso?
# 🧪 EJERCICIO 3 (avanzado): investigá `autogen_ext.teams.magentic_one.MagenticOne`, que trae los
#    agentes originales (web, archivos, código). Requiere Playwright y Docker.

if __name__ == "__main__":
    asyncio.run(main())
