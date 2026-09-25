"""Práctica 23 — Core: publicar/suscribir (pub/sub) e intervención

🎯 Objetivo: comunicar agentes por TÓPICOS (como un bus de eventos) en vez de mensajes
directos, e interceptar mensajes con un "middleware".

📚 Conceptos:
- `publish_message(msg, TopicId(tipo, source))`: publica sin saber quién escucha ni esperar
  respuesta (fire-and-forget).
- `@type_subscription(topic_type="x")`: el agente recibe todo lo publicado en el tópico "x".
- Varios agentes pueden suscribirse al mismo tópico (fan-out) y un agente puede publicar en
  otro tópico para armar un pipeline.
- `DefaultInterventionHandler`: intercepta mensajes ANTES de entregarlos. Sirve para loguear,
  auditar, modificar o bloquear (`DropMessage`). Así funcionan, por ejemplo, las aprobaciones
  humanas de herramientas.
- Para terminar: `runtime.stop_when_idle()` (cuando no quedan mensajes) o `runtime.stop()`
  cuando se cumple una condición tuya (avisada con un `asyncio.Event`).

  pedidos ──► cocina ──(publica en "listos")──► mozo
          └─► facturacion

▶️ Correr:  poetry run python practicas/m6-core/23_publicar_suscribir.py   (no usa Groq)
"""

import asyncio
from dataclasses import dataclass
from typing import Any

from autogen_core import (
    AgentId,
    DefaultInterventionHandler,
    DropMessage,
    MessageContext,
    RoutedAgent,
    SingleThreadedAgentRuntime,
    TopicId,
    message_handler,
    type_subscription,
)


@dataclass
class Pedido:
    mesa: int
    plato: str


@dataclass
class PlatoListo:
    mesa: int
    plato: str


# 1️⃣ Dos agentes suscriptos al MISMO tópico: ambos reciben cada pedido.
@type_subscription(topic_type="pedidos")
class Cocina(RoutedAgent):
    def __init__(self) -> None:
        super().__init__("Cocina")

    # ⚠️ El parámetro TIENE que llamarse `message`: AutoGen lo busca por nombre para saber el tipo.
    @message_handler
    async def cocinar(self, message: Pedido, ctx: MessageContext) -> None:
        print(f"   👩‍🍳 cocina: preparando {message.plato} (mesa {message.mesa})")
        await asyncio.sleep(0.2)
        # 2️⃣ Pipeline: publica en OTRO tópico cuando termina.
        await self.publish_message(PlatoListo(message.mesa, message.plato), TopicId("listos", self.id.key))


@type_subscription(topic_type="pedidos")
class Facturacion(RoutedAgent):
    def __init__(self) -> None:
        super().__init__("Facturación")

    @message_handler
    async def facturar(self, message: Pedido, ctx: MessageContext) -> None:
        print(f"   🧾 facturación: sumo {message.plato} a la cuenta de la mesa {message.mesa}")


@type_subscription(topic_type="listos")
class Mozo(RoutedAgent):
    def __init__(self, platos_esperados: int, terminado: asyncio.Event) -> None:
        super().__init__("Mozo")
        self._pendientes = platos_esperados
        self._terminado = terminado  # evento compartido con main() para avisar que terminó

    @message_handler
    async def servir(self, message: PlatoListo, ctx: MessageContext) -> None:
        print(f"   🤵 mozo: llevo {message.plato} a la mesa {message.mesa}")
        self._pendientes -= 1
        if self._pendientes == 0:
            self._terminado.set()


# 3️⃣ Middleware: ve TODAS las publicaciones y puede bloquearlas.
class Auditor(DefaultInterventionHandler):
    async def on_publish(self, message: Any, *, message_context: MessageContext) -> Any | type[DropMessage]:
        if isinstance(message, Pedido) and message.plato == "plato agotado":
            print(f"   🚫 auditor: bloqueo el pedido de la mesa {message.mesa} (sin stock)")
            return DropMessage  # el mensaje no llega a ningún suscriptor
        return message

    async def on_send(self, message: Any, *, message_context: MessageContext, recipient: AgentId) -> Any:
        return message


async def main() -> None:
    runtime = SingleThreadedAgentRuntime(intervention_handlers=[Auditor()])
    await Cocina.register(runtime, "cocina", lambda: Cocina())
    await Facturacion.register(runtime, "facturacion", lambda: Facturacion())
    terminado = asyncio.Event()
    # Se van a servir 2 platos: el tercer pedido lo bloquea el auditor.
    await Mozo.register(runtime, "mozo", lambda: Mozo(platos_esperados=2, terminado=terminado))
    runtime.start()

    for pedido in (Pedido(1, "milanesa"), Pedido(2, "plato agotado"), Pedido(3, "ñoquis")):
        print(f"📣 Publico: {pedido}")
        await runtime.publish_message(pedido, TopicId("pedidos", source="salon"))

    # Lo habitual es `await runtime.stop_when_idle()`, pero:
    # ⚠️ Bug de autogen-core 0.7.5: si un intervention handler devuelve DropMessage, el runtime no
    # marca ese mensaje como terminado y stop_when_idle() espera para siempre.
    # Alternativa recomendada por AutoGen: esperar un evento propio y detener con stop().
    await terminado.wait()
    await runtime.stop()
    print("✅ Runtime detenido: se sirvieron todos los platos.")


# 🧪 EJERCICIO 1: agregá un agente `Bartender` suscripto a "pedidos" que solo reaccione a bebidas.
# 🧪 EJERCICIO 2: hacé que el Auditor cuente cuántos mensajes pasaron por cada tópico
#    (pista: `message_context.topic_id`).
# 🧪 EJERCICIO 3: ¿qué diferencia hay entre esto y un RoundRobinGroupChat? (Pista: los equipos de
#    AgentChat usan exactamente este mecanismo por dentro, con un tópico por equipo.)

if __name__ == "__main__":
    asyncio.run(main())
