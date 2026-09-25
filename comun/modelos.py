"""Cliente de modelo compartido por todas las prácticas.

Centralizamos acá la conexión con Groq para que cada práctica se concentre en UNA capacidad de
AutoGen. Si querés ver la conexión "a mano", mirá `practicas/m1-fundamentos/01_cliente_modelo.py`.
"""

import os

from autogen_ext.models.openai import OpenAIChatCompletionClient
from dotenv import load_dotenv

load_dotenv()

GROQ_BASE_URL = "https://api.groq.com/openai/v1"

# Modelo por defecto de las prácticas. `gpt-oss-120b` es el más confiable para tool calling y
# salida estructurada dentro de la capa gratuita de Groq. Se puede cambiar con GROQ_MODEL.
MODELO_POR_DEFECTO = "openai/gpt-oss-120b"
# Modelo liviano para tareas simples (elegir orador, resumir). Se cambia con GROQ_MODELO_LIVIANO.
MODELO_LIVIANO = "openai/gpt-oss-20b"


def cliente_groq(modelo: str | None = None, **kwargs) -> OpenAIChatCompletionClient:
    """Devuelve un cliente de AutoGen apuntado a Groq.

    - `modelo`: id de Groq. Si es None usa GROQ_MODEL o MODELO_POR_DEFECTO.
    - `kwargs`: parámetros extra para el modelo (temperature, max_tokens, ...).
    """
    if not os.getenv("GROQ_API_KEY"):
        raise SystemExit(
            "Falta GROQ_API_KEY. Copiá .env.example a .env y poné tu key de "
            "https://console.groq.com/keys"
        )
    kwargs.setdefault("max_tokens", 2000)  # gpt-oss razona antes de responder: dejar margen
    # La capa gratuita limita tokens por minuto. Ante un 429 el SDK espera y reintenta solo.
    kwargs.setdefault("max_retries", 6)
    return OpenAIChatCompletionClient(
        model=modelo or os.getenv("GROQ_MODEL", MODELO_POR_DEFECTO),
        base_url=GROQ_BASE_URL,
        api_key=os.environ["GROQ_API_KEY"],
        # AutoGen no conoce los modelos de Groq: le declaramos qué saben hacer.
        model_info={
            "vision": False,
            "function_calling": True,
            "json_output": True,
            "structured_output": True,
            "family": "unknown",
            # La memoria (práctica 05) inyecta un SystemMessage extra en medio del historial.
            "multiple_system_messages": True,
        },
        **kwargs,
    )


def cliente_liviano(**kwargs) -> OpenAIChatCompletionClient:
    """Cliente con el modelo chico, para tareas que no necesitan razonar mucho."""
    return cliente_groq(os.getenv("GROQ_MODELO_LIVIANO", MODELO_LIVIANO), **kwargs)
