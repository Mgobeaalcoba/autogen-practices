"""Práctica 22 — Core: agentes, runtime y mensajes directos (RPC)

🎯 Objetivo: bajar un nivel. Todo lo que usamos hasta ahora (AssistantAgent, equipos) está
construido sobre `autogen_core`: un sistema de ACTORES que se mandan mensajes. Acá no hay LLM.

📚 Conceptos:
- Mensajes: clases comunes (dataclasses o Pydantic). El TIPO del mensaje decide qué handler lo
  atiende.
- `RoutedAgent` + `@message_handler`: cada método decorado atiende un tipo de mensaje.
- `SingleThreadedAgentRuntime`: el "sistema operativo" que entrega los mensajes.
- Registro: `await MiAgente.register(runtime, "tipo", fabrica)`. El runtime crea instancias
  bajo demanda.
- `AgentId(tipo, clave)`: identifica UNA instancia. Misma clase + distinta clave = instancias
  distintas con estado propio (ej. una por usuario o por sesión).
- `runtime.send_message(msg, agent_id)`: mensaje directo que ESPERA una respuesta (RPC).

▶️ Correr:  poetry run python practicas/m6-core/22_mensajes_directos.py   (no usa Groq)
"""

import asyncio
from dataclasses import dataclass

from autogen_core import AgentId, MessageContext, RoutedAgent, SingleThreadedAgentRuntime, message_handler


# 1️⃣ Los mensajes son simples dataclasses.
@dataclass
class Deposito:
    monto: float


@dataclass
class ConsultaSaldo:
    pass


@dataclass
class Saldo:
    valor: float


# 2️⃣ Un agente = una clase con handlers por tipo de mensaje.
class Cuenta(RoutedAgent):
    def __init__(self) -> None:
        super().__init__("Cuenta bancaria simple")
        self.saldo = 0.0  # estado PROPIO de cada instancia

    # ⚠️ El parámetro TIENE que llamarse `message`: AutoGen lo busca por nombre para saber el tipo.
    @message_handler
    async def depositar(self, message: Deposito, ctx: MessageContext) -> Saldo:
        self.saldo += message.monto
        print(f"   [{self.id.key}] depósito de {message.monto} → saldo {self.saldo}")
        return Saldo(self.saldo)

    @message_handler
    async def consultar(self, message: ConsultaSaldo, ctx: MessageContext) -> Saldo:
        return Saldo(self.saldo)


async def main() -> None:
    runtime = SingleThreadedAgentRuntime()

    # 3️⃣ Registrar el TIPO de agente. Todavía no existe ninguna instancia.
    await Cuenta.register(runtime, "cuenta", lambda: Cuenta())
    runtime.start()  # empieza a procesar mensajes en segundo plano

    # 4️⃣ Mensajes directos. Distinta clave = distinta instancia (con su propio saldo).
    ana = AgentId("cuenta", "ana")
    beto = AgentId("cuenta", "beto")

    print("💸 Depósitos:")
    await runtime.send_message(Deposito(1000), ana)
    await runtime.send_message(Deposito(250), beto)
    await runtime.send_message(Deposito(500), ana)

    print("\n🔎 Consultas (RPC: el que envía espera la respuesta):")
    for cuenta in (ana, beto):
        saldo: Saldo = await runtime.send_message(ConsultaSaldo(), cuenta)
        print(f"   {cuenta.key}: {saldo.valor}")

    await runtime.stop()


# 🧪 EJERCICIO 1: agregá un mensaje `Extraccion(monto)` que falle (lance ValueError) si no hay
#    saldo. ¿Qué recibe quien llamó a send_message?
# 🧪 EJERCICIO 2: agregá un mensaje `Transferencia(destino: str, monto: float)`: el agente le
#    manda un Deposito a otra cuenta con `await self.send_message(..., AgentId("cuenta", destino))`.

if __name__ == "__main__":
    asyncio.run(main())
