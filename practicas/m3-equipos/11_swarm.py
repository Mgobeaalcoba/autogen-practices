"""Práctica 11 — Swarm: los agentes se pasan la posta (handoffs)

🎯 Objetivo: que cada agente decida a quién derivar, como en una mesa de ayuda.

📚 Conceptos:
- `handoffs=[Handoff(target="otro_agente")]`: AutoGen le da al agente una herramienta
  `transfer_to_otro_agente`. (Con OpenAI alcanza con pasar el nombre como string; con Groq
  usamos `HandoffGroq`, ver `comun/compat.py`.)
  Al llamarla, se emite un `HandoffMessage` y habla el destinatario.
- `Swarm`: no hay moderador. Habla quien recibió el último handoff.
- Si un agente responde con texto SIN transferir, sigue hablando él (no hay moderador).
- `Handoff(target="user")` + `HandoffTermination(target="user")`: el agente devuelve el
  control al humano; el equipo se pausa hasta que respondamos con otro `HandoffMessage`.

▶️ Correr:  poetry run python practicas/m3-equipos/11_swarm.py
   Cuando un agente te pregunte algo, respondé en la terminal. Escribí "salir" para terminar.
"""

import asyncio

from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.conditions import HandoffTermination, MaxMessageTermination
from autogen_agentchat.messages import HandoffMessage
from autogen_agentchat.teams import Swarm
from autogen_agentchat.ui import Console

from comun.compat import HandoffGroq as Handoff  # parche para Groq, ver comun/compat.py
from comun.modelos import cliente_groq


def estado_pedido(numero: str) -> str:
    """Consulta el estado de un pedido por su número."""
    # El resultado de una herramienta también "instruye" al modelo: le recordamos el próximo paso.
    return (
        f"El pedido {numero} fue despachado ayer; llega en 2 días hábiles. "
        "Siguiente paso: informale esto al cliente y llamá a transfer_to_user."
    )


def iniciar_devolucion(numero: str, motivo: str) -> str:
    """Inicia la devolución de un pedido."""
    return (
        f"Devolución del pedido {numero} iniciada (motivo: {motivo}). Código: DEV-4821. "
        "Siguiente paso: informale el código al cliente y llamá a transfer_to_user."
    )


async def main() -> None:
    cliente = cliente_groq()
    # La `description` de cada handoff es lo que el LLM lee para decidir a quién derivar.
    volver_al_cliente = Handoff(target="user", description="Preguntarle al cliente un dato que falta.")
    a_envios = Handoff(target="envios", description="Derivar consultas sobre dónde está un pedido.")
    a_devoluciones = Handoff(target="devoluciones", description="Derivar pedidos de devolución o reclamos.")
    a_recepcion = Handoff(target="recepcion", description="Devolver a recepción si el tema no es tuyo.")

    recepcion = AssistantAgent(
        "recepcion",
        cliente,
        handoffs=[a_envios, a_devoluciones, volver_al_cliente],
        system_message=(
            "Sos la recepción de una tienda online. NO respondas con texto: tu única acción es "
            "llamar a una herramienta de transferencia. Envíos → transfer_to_envios. "
            "Devoluciones o reclamos → transfer_to_devoluciones. Si no se entiende qué necesita, "
            "transfer_to_user."
        ),
    )
    envios = AssistantAgent(
        "envios",
        cliente,
        tools=[estado_pedido],
        handoffs=[a_recepcion, volver_al_cliente],
        # Permite encadenar "usar herramienta → transferir" en el mismo turno. Con el default (1),
        # el agente se detiene tras la herramienta y, como en Swarm habla quien tiene la posta,
        # vuelve a hablar él mismo repitiendo la respuesta.
        max_tool_iterations=3,
        system_message=(
            "Resolvés consultas de envíos con la herramienta estado_pedido. Si no tenés el número "
            "de pedido, escribí la pregunta y llamá a transfer_to_user. Cuando respondas, llamá "
            "a transfer_to_user para que el cliente siga. Si el tema no es un envío, transfer_to_recepcion."
        ),
    )
    devoluciones = AssistantAgent(
        "devoluciones",
        cliente,
        tools=[iniciar_devolucion],
        handoffs=[a_recepcion, volver_al_cliente],
        max_tool_iterations=3,
        system_message=(
            "Gestionás devoluciones con la herramienta iniciar_devolucion. Necesitás número de "
            "pedido y motivo: si falta algo, escribí la pregunta y llamá a transfer_to_user. "
            "Cuando la devolución esté iniciada, informá el código y llamá a transfer_to_user."
        ),
    )

    # El equipo se pausa cada vez que un agente le pasa la posta al usuario.
    fin = HandoffTermination(target="user") | MaxMessageTermination(20)
    equipo = Swarm([recepcion, envios, devoluciones], termination_condition=fin)

    resultado = await Console(equipo.run_stream(task="Hola, quiero devolver algo que compré."))

    # 🔁 Loop humano: respondemos al agente que nos pidió el dato, con un HandoffMessage.
    while resultado.messages and isinstance(resultado.messages[-1], HandoffMessage):
        ultimo = resultado.messages[-1]
        respuesta = input(f"\n👤 Respondele a {ultimo.source} (o 'salir'): ")
        if respuesta.strip().lower() == "salir":
            break
        mensaje = HandoffMessage(source="user", target=ultimo.source, content=respuesta)
        resultado = await Console(equipo.run_stream(task=mensaje))

    await cliente.close()


# 🧪 EJERCICIO 1: agregá un agente `facturacion` con una herramienta `reenviar_factura(email)`.
# 🧪 EJERCICIO 2: pensá: ¿qué ventaja tiene Swarm frente a SelectorGroupChat para este caso? ¿Y qué
#    riesgo aparece si un agente deriva mal?

if __name__ == "__main__":
    asyncio.run(main())
