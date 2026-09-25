"""Práctica 21 — Observabilidad: logs, tokens y costos

🎯 Objetivo: ver qué pasa por dentro (cada llamada al LLM, cuántos tokens usó) para depurar y
controlar el consumo.

📚 Conceptos:
- AutoGen usa el módulo estándar `logging` con dos loggers:
    · `EVENT_LOGGER_NAME` ("autogen_core.events"): eventos estructurados. Por ejemplo,
      `LLMCallEvent` con los mensajes enviados, la respuesta y los tokens.
    · `TRACE_LOGGER_NAME` ("autogen_core.trace"): detalle interno para depurar el framework.
- Podés agregar tu propio `logging.Handler` para contar, guardar en archivo o enviar a otro lado.
- Para trazas distribuidas, AutoGen soporta OpenTelemetry (ver README del módulo).

▶️ Correr:  poetry run python practicas/m5-ecosistema/21_observabilidad.py
"""

import asyncio
import json
import logging

from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.conditions import MaxMessageTermination
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_core import EVENT_LOGGER_NAME

from comun.modelos import cliente_liviano
from comun.rutas import ruta_salida


# 1️⃣ Un handler propio: cuenta las llamadas al LLM y suma tokens.
class ContadorDeTokens(logging.Handler):
    def __init__(self) -> None:
        super().__init__()
        self.llamadas = 0
        self.prompt = 0
        self.completion = 0

    def emit(self, record: logging.LogRecord) -> None:
        evento = record.msg
        if type(evento).__name__ == "LLMCallEvent":
            self.llamadas += 1
            self.prompt += evento.prompt_tokens
            self.completion += evento.completion_tokens


async def main() -> None:
    logger = logging.getLogger(EVENT_LOGGER_NAME)
    logger.setLevel(logging.INFO)

    contador = ContadorDeTokens()
    logger.addHandler(contador)

    # 2️⃣ Además, guardamos cada evento completo en un archivo (una línea JSON por evento).
    archivo_log = ruta_salida("m5/eventos.jsonl")
    a_archivo = logging.FileHandler(archivo_log, mode="w", encoding="utf-8")
    a_archivo.setFormatter(logging.Formatter("%(message)s"))  # los eventos se imprimen como JSON
    logger.addHandler(a_archivo)

    cliente = cliente_liviano()
    equipo = RoundRobinGroupChat(
        [
            AssistantAgent("pregunton", cliente, system_message="Hacés UNA pregunta corta sobre astronomía."),
            AssistantAgent("astronomo", cliente, system_message="Respondés en una oración."),
        ],
        termination_condition=MaxMessageTermination(5),
    )
    await equipo.run(task="Arranquen.")

    # 3️⃣ Resumen de consumo.
    print("📊 Resumen de la corrida")
    print(f"   Llamadas al LLM:     {contador.llamadas}")
    print(f"   Tokens de prompt:    {contador.prompt}")
    print(f"   Tokens de respuesta: {contador.completion}")
    print(f"   Total:               {contador.prompt + contador.completion}")

    # 4️⃣ El archivo tiene eventos de mensajes internos ("Message") y llamadas al LLM ("LLMCall").
    eventos = [json.loads(linea) for linea in archivo_log.read_text().splitlines()]
    tipos = {t: sum(e.get("type") == t for e in eventos) for t in {e.get("type") for e in eventos}}
    print(f"\n🔎 Eventos guardados en {archivo_log}: {tipos}")
    llamada = next(e for e in eventos if e.get("type") == "LLMCall")
    print(f"   Una llamada al LLM tiene: {list(llamada)}")
    print(f"   Agente: {llamada['agent_id']} | mensajes enviados: {len(llamada['messages'])}")

    await cliente.close()


# 🧪 EJERCICIO 1: abrí eventos.jsonl. Buscá un evento "LLMCall" y su campo `messages`:
#    ¿qué system_message recibió cada agente?
# 🧪 EJERCICIO 2: calculá el costo estimado si pagaras (ej. USD 0,10 por millón de tokens de prompt
#    y USD 0,50 por millón de respuesta).
# 🧪 EJERCICIO 3: activá también `TRACE_LOGGER_NAME` en nivel DEBUG y mirá qué detalle agrega.

if __name__ == "__main__":
    asyncio.run(main())
