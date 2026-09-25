# Módulo 6 — Core: cómo funciona AutoGen por dentro

`autogen-agentchat` (todo lo de los módulos 1 a 5) está construido sobre `autogen-core`: un
**modelo de actores**. Cada agente es un objeto con estado propio que solo se comunica mandando
y recibiendo mensajes, y un **runtime** se encarga de entregarlos.

Estas prácticas no necesitan LLM (salvo la 24): son rápidas y gratis.

## Prácticas

| # | Archivo | Capacidad | Idea clave |
|---|---|---|---|
| 22 | [22_mensajes_directos.py](22_mensajes_directos.py) | `RoutedAgent`, `send_message`, `AgentId` | El tipo del mensaje decide el handler. Cada clave es una instancia. |
| 23 | [23_publicar_suscribir.py](23_publicar_suscribir.py) | `publish_message`, `@type_subscription`, intervención | Tópicos para desacoplar; middleware para auditar o bloquear. |
| 24 | [24_agente_core_con_llm.py](24_agente_core_con_llm.py) | `RoutedAgent` + `ChatCompletionClient` | Un "AssistantAgent" mínimo hecho a mano. |

## Conceptos del modelo de actores

| Concepto | En AutoGen | Analogía |
|---|---|---|
| Actor | `RoutedAgent` | Un empleado con su propio escritorio (estado) |
| Mensaje | dataclass o Pydantic | Un formulario con un tipo definido |
| Handler | `@message_handler` | "Si llega este formulario, hago esto" |
| Tipo de agente | `register(runtime, "tipo", fabrica)` | Un puesto de trabajo |
| Instancia | `AgentId("tipo", "clave")` | Una persona concreta en ese puesto |
| RPC | `send_message` | Llamar a alguien y esperar la respuesta |
| Pub/sub | `publish_message` + `TopicId` | Mandar un mail a una lista de distribución |
| Runtime | `SingleThreadedAgentRuntime` | El sistema de correo interno |
| Intervención | `DefaultInterventionHandler` | Un auditor que revisa cada envío |

## ¿Cómo se relaciona con los equipos?

Un `RoundRobinGroupChat` es, por dentro:

- un runtime;
- un agente "manager" (el `RoundRobinGroupChatManager`);
- un contenedor-actor por cada participante;
- un tópico compartido por el equipo, donde se publica cada mensaje.

El manager decide el próximo orador y le manda un pedido. El participante responde publicando en
el tópico, y así todos lo reciben en su historial. Lo mismo que hiciste en la práctica 23.

## Más allá de un proceso

`SingleThreadedAgentRuntime` corre todo en un proceso. Con `GrpcWorkerAgentRuntime`
(`autogen-ext[grpc]`) los agentes pueden vivir en procesos o máquinas distintas, e incluso en
otros lenguajes (.NET), sin cambiar el código de los agentes: solo cambia el runtime.

## Detalles aprendidos al armar las prácticas

- El parámetro del handler **tiene que llamarse `message`**: AutoGen lo busca por nombre.
- Bug de `autogen-core` 0.7.5: si un intervention handler devuelve `DropMessage`,
  `stop_when_idle()` se queda esperando para siempre. La práctica 23 usa un `asyncio.Event` y
  `runtime.stop()`.

## Para repasar

1. ¿Qué pasa si mandás un mensaje de un tipo que el agente no sabe atender?
2. ¿Por qué `AgentId("cuenta", "ana")` y `AgentId("cuenta", "beto")` tienen saldos distintos?
3. ¿`publish_message` devuelve la respuesta de los suscriptores?
4. ¿Qué le agrega `AssistantAgent` al agente de la práctica 24?

<details><summary>Respuestas</summary>

1. **Nada visible**: `RoutedAgent` ignora el mensaje (solo lo registra en el log con nivel INFO)
   y `send_message` devuelve `None`. Es una trampa común: si un handler "no responde", revisá
   que el tipo anotado en `message: Tipo` sea exactamente el que estás enviando.
2. Porque son dos instancias distintas del mismo tipo, cada una con su estado.
3. No. Es "disparar y olvidar"; para esperar una respuesta se usa `send_message`.
4. El loop de herramientas, la memoria, los handoffs, el contexto configurable, la salida
   estructurada, el streaming y el manejo de estado.

</details>
