"""Parches de compatibilidad entre AutoGen y Groq.

Cada parche explica QUÉ falla y POR QUÉ. Si una versión futura de AutoGen o de Groq lo resuelve,
se puede borrar y volver a usar la clase original.
"""

from typing import Any

from autogen_agentchat.base import Handoff
from autogen_core.tools import BaseTool, FunctionTool


class HandoffGroq(Handoff):
    """Igual que `Handoff`, pero con la herramienta de transferencia en modo no estricto.

    ❌ Problema (autogen 0.7.5 + Groq): `Handoff` crea una herramienta SIN parámetros y con
       `strict=True`. Groq rechaza ese esquema con:
       "invalid JSON schema ... 'required' present but 'properties' is missing" (error 400).
    ✅ Solución: crear la misma herramienta con `strict=False`. El comportamiento es idéntico.
    """

    @property
    def handoff_tool(self) -> BaseTool[Any, Any]:
        def _handoff_tool() -> str:
            return self.message

        return FunctionTool(_handoff_tool, name=self.name, description=self.description, strict=False)
