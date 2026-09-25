"""Práctica 19 — Caché de respuestas y modelos "de mentira" para tests

🎯 Objetivo: ahorrar llamadas (y cuota) cacheando respuestas, y probar agentes SIN llamar a
ningún LLM.

📚 Conceptos:
- `ChatCompletionCache(cliente, store)`: envuelve un cliente. Si la misma lista de mensajes ya
  se pidió, devuelve la respuesta guardada (`resultado.cached == True`) sin llamar a la API.
  Stores: `InMemoryStore` (dura lo que el proceso), `DiskCacheStore`, `RedisStore`.
- `ReplayChatCompletionClient(["resp 1", "resp 2", ...])`: un cliente falso que devuelve
  respuestas predefinidas en orden. Ideal para tests automáticos: rápido, gratis y determinista.

▶️ Correr:  poetry run python practicas/m5-ecosistema/19_cache_y_replay.py
   (la parte B funciona incluso sin GROQ_API_KEY)
"""

import asyncio
import os
import time

from autogen_agentchat.agents import AssistantAgent
from autogen_core import InMemoryStore
from autogen_core.models import UserMessage
from autogen_ext.models.cache import ChatCompletionCache
from autogen_ext.models.replay import ReplayChatCompletionClient
from dotenv import load_dotenv

load_dotenv()  # para saber si hay GROQ_API_KEY antes de decidir qué partes correr


async def parte_a_cache() -> None:
    from comun.modelos import cliente_liviano  # import local: la parte B no necesita Groq

    print("=== A) Caché de respuestas ===")
    cliente_real = cliente_liviano()
    cliente = ChatCompletionCache(cliente_real, store=InMemoryStore())

    pregunta = [UserMessage(content="Nombrá 3 ríos de Argentina, separados por coma.", source="alumno")]
    for intento in (1, 2):
        inicio = time.perf_counter()
        resultado = await cliente.create(pregunta)
        segundos = time.perf_counter() - inicio
        print(f"  Intento {intento}: cached={resultado.cached} | {segundos:.2f}s | {resultado.content}")

    await cliente_real.close()


async def parte_b_replay() -> None:
    print("\n=== B) Cliente de replay (sin LLM real) ===")
    # Respuestas guionadas: el "modelo" siempre devuelve estas, en este orden.
    falso = ReplayChatCompletionClient(["¡Hola! Soy un modelo de mentira.", "Sigo sin pensar nada."])

    agente = AssistantAgent("agente_de_prueba", falso, system_message="Da igual, no lo leo.")
    r1 = await agente.run(task="Hola")
    r2 = await agente.run(task="¿Pensás?")

    # Así se ve un test: comparar contra lo esperado, sin depender de la API ni de la red.
    assert r1.messages[-1].to_text() == "¡Hola! Soy un modelo de mentira."
    assert r2.messages[-1].to_text() == "Sigo sin pensar nada."
    print("  ✅ Las respuestas del agente coinciden con el guion. Tokens usados de Groq: 0")


async def main() -> None:
    if os.getenv("GROQ_API_KEY"):
        await parte_a_cache()
    else:
        print("(Salteo la parte A: no hay GROQ_API_KEY)")
    await parte_b_replay()


# 🧪 EJERCICIO 1: cambiá `InMemoryStore` por `DiskCacheStore` (requiere `poetry add diskcache`)
#    y corré el script dos veces. ¿La segunda corrida usa la caché de la primera?
# 🧪 EJERCICIO 2: escribí un test con pytest para el equipo de la práctica 09 usando
#    ReplayChatCompletionClient: guioná "código", "APROBADO" y verificá el stop_reason.
# 🧪 EJERCICIO 3: ¿qué pasa con la caché si cambiás una sola letra de la pregunta? ¿Por qué?

if __name__ == "__main__":
    asyncio.run(main())
