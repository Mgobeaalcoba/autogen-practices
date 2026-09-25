"""Práctica 02 — Tu primer agente

🎯 Objetivo: crear un `AssistantAgent` y entender las tres formas de ejecutarlo.

📚 Conceptos:
- `AssistantAgent`: LLM + rol (`system_message`) + historial propio.
- `run()` → devuelve un `TaskResult` cuando termina.
- `run_stream()` → devuelve los mensajes/eventos a medida que ocurren.
- `Console`: muestra un stream en la terminal con formato (y estadísticas).
- `model_client_stream=True`: el agente emite los tokens a medida que se generan.

▶️ Correr:  poetry run python practicas/m1-fundamentos/02_primer_agente.py
"""

import asyncio

from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.ui import Console
from autogen_core import CancellationToken

from comun.modelos import cliente_liviano


async def main() -> None:
    cliente = cliente_liviano()

    # 1️⃣ Definir el agente. `name` identifica al agente (sin espacios ni tildes).
    #    Si no pasás `system_message`, AutoGen usa uno en inglés que pide terminar con
    #    "TERMINATE". Por eso siempre conviene definirlo.
    profe = AssistantAgent(
        name="profe",
        model_client=cliente,
        system_message="Sos un profe de programación. Respondés breve, en español rioplatense.",
        model_client_stream=True,  # emite ModelClientStreamingChunkEvent (tokens en vivo)
    )

    # 2️⃣ run(): esperar el resultado completo.
    resultado = await profe.run(task="Explicá qué es una función en Python en dos oraciones.")
    print("📦 Tipo de resultado:", type(resultado).__name__)
    print("📨 Mensajes en el resultado:", [type(m).__name__ for m in resultado.messages])
    print("💬 Última respuesta:", resultado.messages[-1].to_text())

    # 3️⃣ El agente RECUERDA: guarda su propio historial entre llamadas.
    print("\n--- Segunda tarea (el agente recuerda la anterior) ---")
    # 4️⃣ run_stream() + Console: ver cada evento, con estadísticas al final.
    await Console(
        profe.run_stream(task="Ahora dame un ejemplo de lo que explicaste."),
        output_stats=True,
    )

    # 5️⃣ reset(): borra el historial del agente.
    await profe.on_reset(CancellationToken())
    print("\n--- Después de reset (ya no recuerda) ---")
    await Console(profe.run_stream(task="¿De qué estábamos hablando?"))

    await cliente.close()


# 🧪 EJERCICIO 1: cambiá el `system_message` para que el profe responda solo con analogías futboleras.
# 🧪 EJERCICIO 2: sacá `model_client_stream=True` y compará cómo se ve la salida de Console.

if __name__ == "__main__":
    asyncio.run(main())
