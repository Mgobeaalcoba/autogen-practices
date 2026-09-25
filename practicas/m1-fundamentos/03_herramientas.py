"""Práctica 03 — Herramientas (tools / function calling)

🎯 Objetivo: que el agente use funciones de Python para obtener datos o hacer cálculos.

📚 Conceptos:
- Cualquier función con type hints + docstring puede ser una herramienta. AutoGen genera el
  "esquema" que ve el LLM a partir de la firma y la docstring.
- `FunctionTool`: la forma explícita (permite cambiar nombre/descripción).
- Eventos nuevos: `ToolCallRequestEvent` (el LLM pide llamar) y `ToolCallExecutionEvent`
  (resultado de ejecutar la función).
- `reflect_on_tool_use`: si es True, el agente redacta una respuesta con el resultado; si es
  False, devuelve el resultado crudo (`ToolCallSummaryMessage`).
- `max_tool_iterations`: cuántas rondas de herramientas puede encadenar antes de responder.

▶️ Correr:  poetry run python practicas/m1-fundamentos/03_herramientas.py
"""

import asyncio
from datetime import date
from typing import Annotated

from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.ui import Console
from autogen_core.tools import FunctionTool

from comun.modelos import cliente_groq

# 1️⃣ Herramientas = funciones comunes. La docstring y los type hints son lo que "lee" el LLM.
COTIZACIONES = {"USD": 1450.0, "EUR": 1680.0, "BRL": 265.0}  # datos ficticios, en pesos


def convertir_a_pesos(
    monto: Annotated[float, "Monto en la moneda de origen"],
    moneda: Annotated[str, "Código ISO de la moneda: USD, EUR o BRL"],
) -> str:
    """Convierte un monto de una moneda extranjera a pesos argentinos."""
    tasa = COTIZACIONES.get(moneda.upper())
    if tasa is None:
        return f"No tengo cotización para {moneda}. Monedas disponibles: {list(COTIZACIONES)}"
    return f"{monto} {moneda.upper()} = {monto * tasa:,.2f} ARS (cotización {tasa})"


async def dias_hasta(fecha_iso: Annotated[str, "Fecha en formato AAAA-MM-DD"]) -> str:
    """Calcula cuántos días faltan desde hoy hasta una fecha."""
    dias = (date.fromisoformat(fecha_iso) - date.today()).days
    return f"Faltan {dias} días para el {fecha_iso}."


# 2️⃣ Versión explícita con FunctionTool: útil para renombrar o mejorar la descripción.
herramienta_dias = FunctionTool(
    dias_hasta,
    name="dias_hasta_fecha",
    description="Devuelve la cantidad de días entre hoy y la fecha indicada (AAAA-MM-DD).",
)


async def main() -> None:
    cliente = cliente_groq()

    asistente = AssistantAgent(
        name="asistente_viajes",
        model_client=cliente,
        tools=[convertir_a_pesos, herramienta_dias],  # funciones y FunctionTool se mezclan
        system_message=(
            "Ayudás a planificar viajes. Usá las herramientas para cualquier cálculo: "
            "no hagas cuentas de memoria. Respondé en español rioplatense."
        ),
        reflect_on_tool_use=True,  # redactar una respuesta final con los resultados
        max_tool_iterations=3,  # permite encadenar varias rondas de herramientas
    )

    # 3️⃣ Esta tarea necesita DOS herramientas. Mirá los eventos de llamada en la consola.
    await Console(
        asistente.run_stream(
            task="Viajo el 2026-12-15 y llevo 800 USD y 300 EUR. ¿Cuántos días faltan y cuánto es en pesos?"
        )
    )

    await cliente.close()


# 🧪 EJERCICIO 1: poné `reflect_on_tool_use=False`. ¿Qué tipo de mensaje devuelve ahora el agente?
# 🧪 EJERCICIO 2: borrá la docstring de `convertir_a_pesos`. ¿Sigue usándola bien el modelo?
# 🧪 EJERCICIO 3: agregá una herramienta `clima(ciudad)` que devuelva un dato inventado y pedile
#    al agente que arme una recomendación de ropa para el viaje.

if __name__ == "__main__":
    asyncio.run(main())
