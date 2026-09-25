"""Práctica 01 — El cliente de modelo (la capa más baja)

🎯 Objetivo: hablar con el LLM SIN agentes, para entender qué hace AutoGen por debajo.

📚 Conceptos:
- `ChatCompletionClient`: la interfaz común a todos los proveedores (OpenAI, Groq, Ollama, ...).
- Mensajes tipados: `SystemMessage`, `UserMessage`, `AssistantMessage`.
- `CreateResult`: la respuesta, con `content`, `usage` (tokens) y `finish_reason`.
- `create_stream`: la misma llamada, pero recibiendo el texto a medida que se genera.

▶️ Correr:  poetry run python practicas/m1-fundamentos/01_cliente_modelo.py
"""

import asyncio
import os

from autogen_core.models import AssistantMessage, CreateResult, SystemMessage, UserMessage
from autogen_ext.models.openai import OpenAIChatCompletionClient
from dotenv import load_dotenv

load_dotenv()


async def main() -> None:
    # 1️⃣ Crear el cliente "a mano". En el resto de las prácticas esto lo hace
    #    `comun.modelos.cliente_groq()`, pero acá lo mostramos completo.
    cliente = OpenAIChatCompletionClient(
        model="openai/gpt-oss-20b",
        base_url="https://api.groq.com/openai/v1",  # Groq habla el mismo "idioma" que OpenAI
        api_key=os.environ["GROQ_API_KEY"],
        model_info={  # obligatorio para modelos que AutoGen no conoce
            "vision": False,
            "function_calling": True,
            "json_output": True,
            "structured_output": True,
            "family": "unknown",
        },
    )

    # 2️⃣ Una llamada simple: lista de mensajes → una respuesta.
    mensajes = [
        SystemMessage(content="Respondés en español rioplatense, en una sola oración."),
        UserMessage(content="¿Qué es un agente de IA?", source="alumno"),
    ]
    resultado = await cliente.create(mensajes)

    print("💬 Respuesta:", resultado.content)
    print("🧾 Tokens:", resultado.usage)  # prompt_tokens / completion_tokens
    print("🏁 Motivo de fin:", resultado.finish_reason)  # "stop", "length", "function_calls"...

    # 3️⃣ El modelo NO tiene memoria: para seguir la charla hay que reenviar todo el historial.
    #    Esto es exactamente lo que un agente hace por vos.
    mensajes += [
        AssistantMessage(content=str(resultado.content), source="modelo"),
        UserMessage(content="Dame un ejemplo concreto de lo que dijiste.", source="alumno"),
    ]

    # 4️⃣ Streaming: los fragmentos llegan como `str`; el último elemento es el `CreateResult`.
    print("\n🌊 Streaming: ", end="")
    async for fragmento in cliente.create_stream(mensajes):
        if isinstance(fragmento, str):
            print(fragmento, end="", flush=True)
        elif isinstance(fragmento, CreateResult):
            print(f"\n🧾 Tokens de la segunda llamada: {fragmento.usage}")

    # 5️⃣ Uso acumulado de este cliente (útil para controlar la cuota gratuita).
    print("📊 Total acumulado:", cliente.total_usage())

    await cliente.close()


# 🧪 EJERCICIO: quitá el paso 3 (no reenvíes la respuesta anterior) y preguntá "¿qué dijiste recién?".
#    ¿Qué contesta el modelo? ¿Por qué?

if __name__ == "__main__":
    asyncio.run(main())
