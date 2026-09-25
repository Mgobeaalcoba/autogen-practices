"""Práctica 04 — Salida estructurada

🎯 Objetivo: que el agente devuelva un OBJETO de Python validado, no texto libre.

📚 Conceptos:
- `output_content_type=MiModelo`: el agente le pide al LLM que responda siguiendo el JSON
  Schema de un modelo Pydantic.
- La respuesta llega como `StructuredMessage[MiModelo]`: `mensaje.content` es una instancia
  de tu modelo, con tipos validados (listas, números, enums...).
- Requiere un modelo con `structured_output=True` en `model_info`.

▶️ Correr:  poetry run python practicas/m1-fundamentos/04_salida_estructurada.py
"""

import asyncio
import warnings
from typing import Literal

from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import StructuredMessage
from pydantic import BaseModel, Field

from comun.modelos import cliente_groq

# AutoGen 0.7.5 emite un warning inofensivo de Pydantic al serializar la respuesta parseada.
warnings.filterwarnings("ignore", message="Pydantic serializer warnings")


# 1️⃣ El "contrato" de salida. Las descripciones de Field ayudan al LLM a completar bien.
class FichaNoticia(BaseModel):
    titulo: str = Field(description="Título breve y neutral, máximo 10 palabras")
    actores: list[str] = Field(description="Personas, países u organizaciones involucradas")
    tema: Literal["politica", "economia", "conflicto", "sociedad", "tecnologia"]
    cifras: list[str] = Field(description="Cifras mencionadas, con su unidad")
    tono: Literal["neutral", "alarmista", "optimista"]


NOTICIA = (
    "En la Asamblea General de la ONU, Volodímir Zelenski pidió mantener la presión económica "
    "sobre Rusia y acusó al Kremlin de reclutar combatientes de 47 países. El mismo día, "
    "explosiones en Kiev dejaron al menos 2 muertos y 23 heridos."
)


async def main() -> None:
    cliente = cliente_groq()

    analista = AssistantAgent(
        name="analista",
        model_client=cliente,
        system_message="Extraés información de noticias. No inventes datos que no estén en el texto.",
        output_content_type=FichaNoticia,  # 👈 la clave de esta práctica
    )

    resultado = await analista.run(task=NOTICIA)
    mensaje = resultado.messages[-1]

    # 2️⃣ Ya no es texto: es un objeto FichaNoticia con atributos tipados.
    assert isinstance(mensaje, StructuredMessage)
    ficha: FichaNoticia = mensaje.content
    print("🧩 Tipo:", type(ficha).__name__)
    print("📰 Título:", ficha.titulo)
    print("👥 Actores:", ", ".join(ficha.actores))
    print("🏷️ Tema:", ficha.tema, "| Tono:", ficha.tono)
    print("🔢 Cifras:", ficha.cifras)

    # 3️⃣ Como es Pydantic, se puede serializar directo a JSON (para guardar, APIs, etc.).
    print("\n📄 JSON:\n", ficha.model_dump_json(indent=2))

    await cliente.close()


# 🧪 EJERCICIO 1: agregá un campo `resumen: str` con máximo 25 palabras (usá Field(description=...)).
# 🧪 EJERCICIO 2: procesá una lista de 3 noticias y armá una tabla con los temas.
# 🧪 EJERCICIO 3: pasá `output_content_type_format="{titulo} ({tema})"` y mirá `mensaje.to_text()`.

if __name__ == "__main__":
    asyncio.run(main())
