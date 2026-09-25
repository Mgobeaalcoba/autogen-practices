"""Práctica 06 — Guardar y recuperar estado

🎯 Objetivo: pausar una conversación, guardarla en disco y retomarla más tarde (incluso en otro
proceso), como haría una app real entre requests.

📚 Conceptos:
- `await agente.save_state()` → dict serializable con el historial del agente.
- `await agente.load_state(estado)` → restaura ese historial en otro agente con la misma config.
- Los equipos (`team.save_state()` / `team.load_state()`) funcionan igual y además guardan
  de quién era el turno.

▶️ Correr:  poetry run python practicas/m1-fundamentos/06_estado.py
   Corrélo DOS veces: la primera guarda el estado, la segunda lo retoma.
"""

import asyncio
import json

from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.ui import Console

from comun.modelos import cliente_liviano
from comun.rutas import ruta_salida

ARCHIVO_ESTADO = ruta_salida("m1/estado_tutor.json")


def crear_tutor(cliente) -> AssistantAgent:
    # La configuración tiene que ser la misma al guardar y al cargar: el estado solo guarda
    # el historial, no el system_message ni las herramientas.
    return AssistantAgent(
        name="tutor",
        model_client=cliente,
        system_message="Sos un tutor de inglés. Respuestas de máximo 2 oraciones.",
    )


async def main() -> None:
    cliente = cliente_liviano()
    tutor = crear_tutor(cliente)

    if not ARCHIVO_ESTADO.exists():
        print("🆕 Primera ejecución: arranco una conversación nueva.")
        await Console(tutor.run_stream(task="Hola, me llamo Lucas y quiero practicar el pasado simple."))

        # 1️⃣ Guardar: el estado es un dict común → lo pasamos a JSON.
        estado = await tutor.save_state()
        ARCHIVO_ESTADO.write_text(json.dumps(estado, indent=2, ensure_ascii=False))
        print(f"\n💾 Estado guardado en {ARCHIVO_ESTADO}. Volvé a correr el script para retomarlo.")
    else:
        print(f"♻️ Encontré {ARCHIVO_ESTADO}: retomo la conversación.")
        # 2️⃣ Cargar en un agente NUEVO (podría ser otro proceso, otro día, otro servidor).
        estado = json.loads(ARCHIVO_ESTADO.read_text())
        await tutor.load_state(estado)
        await Console(tutor.run_stream(task="¿Te acordás cómo me llamo y qué quería practicar?"))

        ARCHIVO_ESTADO.unlink()  # para que la próxima corrida empiece de cero
        print("\n🧹 Borré el estado: la próxima ejecución arranca de nuevo.")

    await cliente.close()


# 🧪 EJERCICIO 1: abrí el JSON guardado. ¿Qué tipo de mensajes contiene? ¿Está el system_message?
# 🧪 EJERCICIO 2: guardá el estado de un RoundRobinGroupChat (práctica 09) a mitad de camino y
#    retomalo con `team.load_state()`.

if __name__ == "__main__":
    asyncio.run(main())
