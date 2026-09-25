"""Práctica 05 — Contexto del modelo y memoria

🎯 Objetivo: distinguir QUÉ historial ve el LLM (contexto) de QUÉ conocimiento extra le
inyectamos (memoria).

📚 Conceptos:
- `model_context`: decide qué parte del historial se manda al LLM en cada llamada.
    · `UnboundedChatCompletionContext` (default): todo.
    · `BufferedChatCompletionContext(buffer_size=n)`: solo los últimos n mensajes.
    · `HeadAndTailChatCompletionContext`, `TokenLimitedChatCompletionContext`: otras estrategias.
- `memory`: almacenes que se consultan ANTES de cada respuesta y agregan información al
  contexto (patrón RAG). `ListMemory` es el más simple: agrega todo lo guardado.
- Evento nuevo: `MemoryQueryEvent`, muestra qué memoria se usó.

▶️ Correr:  poetry run python practicas/m1-fundamentos/05_contexto_y_memoria.py
"""

import asyncio

from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.ui import Console
from autogen_core.memory import ListMemory, MemoryContent, MemoryMimeType
from autogen_core.model_context import BufferedChatCompletionContext

from comun.modelos import cliente_liviano


async def parte_a_contexto(cliente) -> None:
    print("\n=== A) Contexto con buffer de 2 mensajes ===")
    olvidadizo = AssistantAgent(
        name="olvidadizo",
        model_client=cliente,
        system_message="Respondés en una sola oración corta.",
        # Solo ve los últimos 2 mensajes: el dato del primer turno "se cae" de la ventana.
        model_context=BufferedChatCompletionContext(buffer_size=2),
    )
    await olvidadizo.run(task="Mi nombre es Mariana y mi color favorito es el verde.")
    await olvidadizo.run(task="¿Cuánto es 2 + 2?")
    await Console(olvidadizo.run_stream(task="¿Cómo me llamo?"))
    # Probablemente no lo sepa (o lo invente): el mensaje con el nombre ya no está en su contexto.


async def parte_b_memoria(cliente) -> None:
    print("\n=== B) Memoria de preferencias del usuario ===")
    preferencias = ListMemory()
    await preferencias.add(
        MemoryContent(content="El usuario es vegetariano.", mime_type=MemoryMimeType.TEXT)
    )
    await preferencias.add(
        MemoryContent(content="El usuario vive en Mendoza.", mime_type=MemoryMimeType.TEXT)
    )

    cocinero = AssistantAgent(
        name="cocinero",
        model_client=cliente,
        system_message="Sugerís recetas breves (3 líneas).",
        memory=[preferencias],  # se consulta antes de cada respuesta
    )
    # La tarea no menciona las preferencias: vienen de la memoria (ver MemoryQueryEvent).
    await Console(cocinero.run_stream(task="¿Qué cocino hoy para la cena?"))


async def main() -> None:
    cliente = cliente_liviano()
    await parte_a_contexto(cliente)
    await parte_b_memoria(cliente)
    await cliente.close()


# 🧪 EJERCICIO 1: cambiá `buffer_size` a 6 y verificá que ahora sí recuerde el nombre.
# 🧪 EJERCICIO 2: agregá a la memoria "Es alérgico al maní" y pedí un postre.
# 🧪 EJERCICIO 3 (avanzado): `ListMemory` agrega TODO. Investigá `autogen_ext.memory.chromadb`
#    para recuperar solo lo relevante por similitud semántica (requiere instalar chromadb).

if __name__ == "__main__":
    asyncio.run(main())
