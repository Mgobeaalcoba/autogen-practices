"""Práctica 24 — Core: un agente con LLM hecho a mano

🎯 Objetivo: construir con `autogen_core` lo que `AssistantAgent` te da hecho, para entender
qué hace por dentro: guardar historial, llamar al modelo y publicar la respuesta.

📚 Conceptos:
- Un `RoutedAgent` puede tener su propio `ChatCompletionClient` y su historial.
- Patrón pipeline con tópicos: cada agente escucha un tópico y publica en el siguiente.
- Esto es, a grandes rasgos, lo que hacen `RoundRobinGroupChat` y compañía, pero con control
  total (y más código).

   "ideas" ──► guionista ──► "guiones" ──► critico ──► "criticas" ──► impresor

▶️ Correr:  poetry run python practicas/m6-core/24_agente_core_con_llm.py
"""

import asyncio
from dataclasses import dataclass

from autogen_core import (
    MessageContext,
    RoutedAgent,
    SingleThreadedAgentRuntime,
    TopicId,
    message_handler,
    type_subscription,
)
from autogen_core.models import ChatCompletionClient, LLMMessage, SystemMessage, UserMessage

from comun.modelos import cliente_liviano


@dataclass
class Texto:
    contenido: str
    autor: str


class AgenteLLM(RoutedAgent):
    """Base mínima: un system_message, historial propio y un tópico de salida."""

    def __init__(self, descripcion: str, cliente: ChatCompletionClient, system: str, topico_salida: str) -> None:
        super().__init__(descripcion)
        self._cliente = cliente
        self._historial: list[LLMMessage] = [SystemMessage(content=system)]
        self._topico_salida = topico_salida

    # ⚠️ El parámetro TIENE que llamarse `message`: AutoGen lo busca por nombre para saber el tipo.
    @message_handler
    async def procesar(self, message: Texto, ctx: MessageContext) -> None:
        # 1️⃣ Agregar lo recibido al historial.
        self._historial.append(UserMessage(content=message.contenido, source=message.autor))
        # 2️⃣ Llamar al modelo con TODO el historial (el modelo no tiene memoria propia).
        resultado = await self._cliente.create(self._historial, cancellation_token=ctx.cancellation_token)
        respuesta = str(resultado.content)
        # 3️⃣ Publicar la respuesta en el tópico siguiente del pipeline.
        await self.publish_message(Texto(respuesta, self.id.type), TopicId(self._topico_salida, self.id.key))


@type_subscription(topic_type="ideas")
class Guionista(AgenteLLM):
    pass


@type_subscription(topic_type="guiones")
class Critico(AgenteLLM):
    pass


@type_subscription(topic_type="criticas")
class Impresor(RoutedAgent):
    def __init__(self, guiones: list[str]) -> None:
        super().__init__("Muestra el resultado final")
        self._guiones = guiones

    @message_handler
    async def imprimir(self, message: Texto, ctx: MessageContext) -> None:
        print(f"\n🎬 Guion:\n{self._guiones[-1]}\n\n🧐 Crítica:\n{message.contenido}")


@type_subscription(topic_type="guiones")
class Archivista(RoutedAgent):
    """Escucha los guiones para que el Impresor pueda mostrarlos junto con la crítica."""

    def __init__(self, guiones: list[str]) -> None:
        super().__init__("Guarda los guiones")
        self._guiones = guiones

    @message_handler
    async def guardar(self, message: Texto, ctx: MessageContext) -> None:
        self._guiones.append(message.contenido)


async def main() -> None:
    cliente = cliente_liviano()
    guiones: list[str] = []
    runtime = SingleThreadedAgentRuntime()

    await Guionista.register(runtime, "guionista", lambda: Guionista(
        "Guionista", cliente, "Escribís un guion de 4 líneas para un video corto a partir de una idea.", "guiones"))
    await Critico.register(runtime, "critico", lambda: Critico(
        "Crítico", cliente, "Criticás guiones en 2 viñetas: un acierto y una mejora.", "criticas"))
    await Archivista.register(runtime, "archivista", lambda: Archivista(guiones))
    await Impresor.register(runtime, "impresor", lambda: Impresor(guiones))

    runtime.start()
    await runtime.publish_message(
        Texto("Un video que explique qué es un agente de IA usando una analogía con un mozo.", "usuario"),
        TopicId("ideas", source="default"),
    )
    await runtime.stop_when_idle()
    await cliente.close()


# 🧪 EJERCICIO 1: agregá herramientas a AgenteLLM: pasá `tools=[...]` a `create()` y, si el
#    resultado es una lista de FunctionCall, ejecutalas y volvé a llamar al modelo.
#    (Esto es lo que `AssistantAgent` hace por vos en su "tool loop".)
# 🧪 EJERCICIO 2: hacé que el crítico publique de nuevo en "ideas" si la crítica es muy mala,
#    armando un ciclo. ¿Cómo evitás que sea infinito?

if __name__ == "__main__":
    asyncio.run(main())
