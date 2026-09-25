"""Práctica 10 — SelectorGroupChat avanzado: selector_func y candidate_func

🎯 Objetivo: combinar la elección por LLM con reglas de código.

   ℹ️ La versión básica (el moderador eligiendo con un prompt) está en la clase 01:
      `clase-01-debate/`. Hacé esa primero.

📚 Conceptos:
- `selector_func(mensajes) -> str | None`: si devuelve un nombre, habla ese agente SIN
  consultar al LLM. Si devuelve None, decide el LLM. Ahorra llamadas y hace el flujo predecible.
- `candidate_func(mensajes) -> list[str]`: limita ENTRE QUIÉNES puede elegir el LLM.
- Patrón "planificador": un agente reparte subtareas y los demás las ejecutan; después de
  cada ejecutor, vuelve el planificador.

▶️ Correr:  poetry run python practicas/m3-equipos/10_selector.py
"""

import asyncio
from typing import Sequence

from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.conditions import MaxMessageTermination, TextMentionTermination
from autogen_agentchat.messages import BaseAgentEvent, BaseChatMessage
from autogen_agentchat.teams import SelectorGroupChat
from autogen_agentchat.ui import Console

from comun.modelos import cliente_groq, cliente_liviano

Historial = Sequence[BaseAgentEvent | BaseChatMessage]


EJECUTORES = ["historiador", "economista"]


# 1️⃣ Reglas de código. Devolver un nombre = decidir sin gastar una llamada al LLM.
def selector(mensajes: Historial) -> str | None:
    ultimo = mensajes[-1]
    # Regla A: después de cualquier ejecutor (o de la tarea inicial), vuelve el planificador.
    if ultimo.source != "planificador":
        return "planificador"
    # Regla B: si el planificador asignó explícitamente ("historiador: ..."), respetarlo.
    texto = ultimo.to_text().strip().lower()
    for nombre in EJECUTORES:
        if texto.startswith(f"{nombre}:"):
            return nombre
    # Si no hay una asignación clara, que decida el LLM moderador.
    return None


# 2️⃣ Filtro de candidatos: el LLM nunca puede elegir al planificador (eso lo resuelve la regla).
def candidatos(mensajes: Historial) -> list[str]:
    return EJECUTORES


async def main() -> None:
    cliente = cliente_groq()

    planificador = AssistantAgent(
        "planificador",
        cliente,
        description="Divide la tarea en subtareas y las asigna.",
        system_message=(
            "Coordinás a: historiador (contexto histórico) y economista (datos económicos). "
            "NUNCA respondas vos las subtareas. En cada turno escribí SOLO una línea con el "
            "formato 'nombre: subtarea' y esperá su respuesta. "
            "Cuando ya respondieron los dos, escribí una conclusión de 3 líneas y terminá con FIN."
        ),
    )
    historiador = AssistantAgent(
        "historiador",
        cliente,
        description="Aporta contexto histórico.",
        system_message="Respondés solo la subtarea histórica que te asignan, en 3 oraciones.",
    )
    economista = AssistantAgent(
        "economista",
        cliente,
        description="Aporta análisis económico.",
        system_message="Respondés solo la subtarea económica que te asignan, en 3 oraciones.",
    )

    equipo = SelectorGroupChat(
        [planificador, historiador, economista],
        model_client=cliente_liviano(),  # el LLM que elige (cuando la regla devuelve None)
        selector_func=selector,
        candidate_func=candidatos,
        termination_condition=TextMentionTermination("FIN") | MaxMessageTermination(8),
    )

    await Console(equipo.run_stream(task="¿Por qué la convertibilidad 1 a 1 terminó en la crisis de 2001?"))

    await cliente.close()


# 🧪 EJERCICIO 1: agregá un `verificador` y cambiá `selector` para que siempre hable antes del FIN.
# 🧪 EJERCICIO 2: hacé que `candidatos` devuelva solo a quienes todavía NO hablaron.
# 🧪 EJERCICIO 3: comentá la Regla B y corré varias veces. ¿El LLM respeta siempre la asignación?
#    (Spoiler: el modelo chico a veces elige mal; por eso conviene codificar lo que es determinista.)

if __name__ == "__main__":
    asyncio.run(main())
