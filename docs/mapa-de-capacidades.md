# Mapa de capacidades de AutoGen

Análisis de **todo lo que ofrece AutoGen 0.7.5** (la versión instalada en este repo) y dónde se
practica cada cosa. Sirve como índice para estudiar y como checklist para saber qué te falta.

> 📌 **Estado del proyecto (septiembre 2026):** Microsoft puso AutoGen en **modo mantenimiento**
> en octubre de 2025: recibe correcciones de bugs y seguridad, pero no funcionalidades nuevas. Su
> sucesor es **Microsoft Agent Framework** (1.0 GA en abril de 2026), que fusiona AutoGen con
> Semantic Kernel. Existe además **AG2**, un fork comunitario de la API vieja (0.2).
>
> **¿Por qué estudiar AutoGen igual?** Porque los conceptos (agentes, herramientas, equipos,
> selección de orador, handoffs, grafos, runtime de actores, humano en el loop) son los mismos en
> Agent Framework y en casi todos los frameworks de agentes. AutoGen los expone de forma clara y
> con poco código, lo que lo hace ideal para aprender. Para un proyecto productivo nuevo, evaluá
> Agent Framework.

## Arquitectura en capas

```
┌──────────────────────────────────────────────────────────────────────┐
│ AutoGen Studio (UI visual, no-code)                                   │  → no cubierto (ver abajo)
├──────────────────────────────────────────────────────────────────────┤
│ autogen-agentchat  → API de alto nivel: agentes, equipos, condiciones │  → módulos m1 a m4
├──────────────────────────────────────────────────────────────────────┤
│ autogen-core       → runtime de actores, mensajes, tópicos            │  → módulo m6
├──────────────────────────────────────────────────────────────────────┤
│ autogen-ext        → integraciones: modelos, código, MCP, memoria...  │  → módulo m5
└──────────────────────────────────────────────────────────────────────┘
```

Leyenda de estado: ✅ práctica validada contra Groq · 🟡 práctica escrita, requiere instalar algo
extra · 📖 solo mencionada (ejercicio o lectura) · ⛔ no aplicable con este stack.

## 1. Modelos (`autogen_core.models`, `autogen_ext.models`)

| Capacidad | API | Dónde | Estado |
|---|---|---|---|
| Llamar al LLM directo, sin agentes | `ChatCompletionClient.create()` | [01](../practicas/m1-fundamentos/01_cliente_modelo.py) | ✅ |
| Streaming de tokens | `create_stream()`, `model_client_stream=True` | [01](../practicas/m1-fundamentos/01_cliente_modelo.py), [02](../practicas/m1-fundamentos/02_primer_agente.py) | ✅ |
| Uso de tokens | `RequestUsage`, `total_usage()` | [01](../practicas/m1-fundamentos/01_cliente_modelo.py), [21](../practicas/m5-ecosistema/21_observabilidad.py) | ✅ |
| Proveedores compatibles con OpenAI (Groq) | `OpenAIChatCompletionClient(base_url=...)` + `model_info` | [comun/modelos.py](../comun/modelos.py) | ✅ |
| Caché de respuestas | `ChatCompletionCache` + `InMemoryStore` / `DiskCacheStore` / `RedisStore` | [19](../practicas/m5-ecosistema/19_cache_y_replay.py) | ✅ |
| Modelo falso para tests | `ReplayChatCompletionClient` | [19](../practicas/m5-ecosistema/19_cache_y_replay.py) | ✅ |
| Otros proveedores | `AnthropicChatCompletionClient`, `OllamaChatCompletionClient`, `AzureAIChatCompletionClient`, `LlamaCppChatCompletionClient`, adaptador Semantic Kernel | — | 📖 misma interfaz: cambiás el cliente y el resto del código queda igual |
| Multimodal (imágenes) | `MultiModalMessage`, `Image` | — | ⛔ hoy Groq no ofrece en la capa gratuita un modelo con visión compatible |

## 2. Agentes (`autogen_agentchat.agents`)

| Capacidad | API | Dónde | Estado |
|---|---|---|---|
| Agente con LLM | `AssistantAgent` | [02](../practicas/m1-fundamentos/02_primer_agente.py) | ✅ |
| `run()` / `run_stream()` / `Console` | `TaskResult`, `autogen_agentchat.ui.Console` | [02](../practicas/m1-fundamentos/02_primer_agente.py) | ✅ |
| Herramientas (function calling) | `tools=[...]`, `FunctionTool`, `reflect_on_tool_use`, `max_tool_iterations` | [03](../practicas/m1-fundamentos/03_herramientas.py) | ✅ |
| Salida estructurada | `output_content_type=ModeloPydantic` → `StructuredMessage` | [04](../practicas/m1-fundamentos/04_salida_estructurada.py) | ✅ |
| Contexto acotado | `BufferedChatCompletionContext`, `HeadAndTail...`, `TokenLimited...` | [05](../practicas/m1-fundamentos/05_contexto_y_memoria.py) | ✅ |
| Memoria (RAG) | `memory=[ListMemory()]`, `MemoryQueryEvent` | [05](../practicas/m1-fundamentos/05_contexto_y_memoria.py) | ✅ |
| Memoria vectorial | `ChromaDBVectorMemory`, `RedisMemory`, `Mem0Memory` | [05 · ej. 3](../practicas/m1-fundamentos/05_contexto_y_memoria.py) | 📖 |
| Guardar / cargar estado | `save_state()` / `load_state()` | [06](../practicas/m1-fundamentos/06_estado.py) | ✅ |
| Humano como participante | `UserProxyAgent(input_func=...)` | [07](../practicas/m2-control/07_humano_en_el_loop.py) | ✅ |
| Ejecución de código | `CodeExecutorAgent` + `approval_func` | [17](../practicas/m5-ecosistema/17_ejecucion_codigo.py) | ✅ |
| Equipo encapsulado como agente | `SocietyOfMindAgent` | [15](../practicas/m4-composicion/15_society_of_mind.py) | ✅ |
| Filtrar el historial que ve un agente | `MessageFilterAgent`, `PerSourceFilter` | [13](../practicas/m3-equipos/13_graphflow_condicional.py) | ✅ |
| Agentes especializados | `MultimodalWebSurfer`, `FileSurfer`, `VideoSurfer`, `OpenAIAssistantAgent` | [14 · ej. 3](../practicas/m3-equipos/14_magentic_one.py) | 📖 requieren Playwright, Docker u OpenAI |

## 3. Equipos (`autogen_agentchat.teams`)

| Equipo | Quién decide el próximo orador | Dónde | Estado |
|---|---|---|---|
| `RoundRobinGroupChat` | Orden fijo | [09](../practicas/m3-equipos/09_round_robin.py) | ✅ |
| `SelectorGroupChat` | Un LLM moderador (+ `selector_func` / `candidate_func`) | [clase 01](../clase-01-debate/), [10](../practicas/m3-equipos/10_selector.py) | ✅ |
| `Swarm` | El agente que habla, vía handoff | [11](../practicas/m3-equipos/11_swarm.py) | ✅ |
| `GraphFlow` | Un grafo dirigido: secuencia, paralelo, condiciones, ciclos | [12](../practicas/m3-equipos/12_graphflow_paralelo.py), [13](../practicas/m3-equipos/13_graphflow_condicional.py) | ✅ |
| `MagenticOneGroupChat` | Un orquestador que planifica y lleva ledgers | [14](../practicas/m3-equipos/14_magentic_one.py) | ✅ |
| Equipo reanudable | volver a llamar `run()` | [09](../practicas/m3-equipos/09_round_robin.py) | ✅ |
| Estado de equipos | `team.save_state()` | [06 · ej. 2](../practicas/m1-fundamentos/06_estado.py) | 📖 |

## 4. Control de ejecución (`autogen_agentchat.conditions`)

| Capacidad | API | Dónde | Estado |
|---|---|---|---|
| Por cantidad / texto / tokens | `MaxMessageTermination`, `TextMentionTermination`, `TokenUsageTermination` | [08](../practicas/m2-control/08_terminacion.py) | ✅ |
| Desde el código | `ExternalTermination` | [08](../practicas/m2-control/08_terminacion.py) | ✅ |
| Cancelación inmediata | `CancellationToken` | [08](../practicas/m2-control/08_terminacion.py) | ✅ |
| Por handoff al usuario | `HandoffTermination` | [11](../practicas/m3-equipos/11_swarm.py) | ✅ |
| Combinar condiciones | `\|` y `&` | [08](../practicas/m2-control/08_terminacion.py) | ✅ |
| Otras | `TimeoutTermination`, `SourceMatchTermination`, `FunctionCallTermination`, `TextMessageTermination`, `StopMessageTermination`, `FunctionalTermination` | [08 · ejercicios](../practicas/m2-control/08_terminacion.py) | 📖 |

## 5. Composición

| Capacidad | API | Dónde | Estado |
|---|---|---|---|
| Agente como herramienta | `AgentTool` | [16](../practicas/m4-composicion/16_agentes_como_herramientas.py) | ✅ |
| Equipo como herramienta | `TeamTool` | [16](../practicas/m4-composicion/16_agentes_como_herramientas.py) | ✅ |
| Equipos anidados | `SocietyOfMindAgent` dentro de otro equipo | [15](../practicas/m4-composicion/15_society_of_mind.py) | ✅ |

## 6. Ecosistema (`autogen_ext`)

| Capacidad | API | Dónde | Estado |
|---|---|---|---|
| Ejecutor local | `LocalCommandLineCodeExecutor` | [17](../practicas/m5-ecosistema/17_ejecucion_codigo.py) | ✅ |
| Ejecutor aislado | `DockerCommandLineCodeExecutor`, `JupyterCodeExecutor`, Azure | [17 · ej. 3](../practicas/m5-ecosistema/17_ejecucion_codigo.py) | 📖 requiere Docker |
| Herramientas MCP | `McpWorkbench` + `StdioServerParams` / `SseServerParams` / `StreamableHttpServerParams` | [18](../practicas/m5-ecosistema/18_mcp.py) | 🟡 `poetry add "autogen-ext[mcp]"` |
| Otras herramientas | `HttpTool`, `LangChainToolAdapter`, GraphRAG, Semantic Kernel | — | 📖 |
| Componentes declarativos (JSON) | `dump_component()` / `load_component()` | [20](../practicas/m5-ecosistema/20_componentes_declarativos.py) | ✅ |
| Logging de eventos | `EVENT_LOGGER_NAME`, `LLMCallEvent` | [21](../practicas/m5-ecosistema/21_observabilidad.py) | ✅ |
| Trazas distribuidas | OpenTelemetry (`tracer_provider` en el runtime) | [21 · README](../practicas/m5-ecosistema/README.md) | 📖 |
| Memoria centrada en tareas | `autogen_ext.experimental.task_centric_memory` | — | 📖 experimental |

## 7. Core (`autogen_core`)

| Capacidad | API | Dónde | Estado |
|---|---|---|---|
| Agentes como actores | `RoutedAgent`, `@message_handler` | [22](../practicas/m6-core/22_mensajes_directos.py) | ✅ |
| Mensajes directos (RPC) | `send_message(msg, AgentId(tipo, clave))` | [22](../practicas/m6-core/22_mensajes_directos.py) | ✅ |
| Instancias por clave | `AgentId.key` | [22](../practicas/m6-core/22_mensajes_directos.py) | ✅ |
| Pub/sub | `publish_message`, `TopicId`, `@type_subscription` | [23](../practicas/m6-core/23_publicar_suscribir.py) | ✅ |
| Middleware | `DefaultInterventionHandler`, `DropMessage` | [23](../practicas/m6-core/23_publicar_suscribir.py) | ✅ |
| Agente con LLM hecho a mano | `RoutedAgent` + `ChatCompletionClient` | [24](../practicas/m6-core/24_agente_core_con_llm.py) | ✅ |
| Runtime distribuido | `GrpcWorkerAgentRuntime` (`autogen-ext[grpc]`) | — | 📖 varios procesos o máquinas |
| Agentes de clausura | `ClosureAgent` | — | 📖 |

## 8. Fuera de este repo

| Herramienta | Qué es | Por qué no está |
|---|---|---|
| **AutoGen Studio** | UI web para armar equipos sin código | Es otro paquete (`autogenstudio`) con su propio servidor. La práctica [20](../practicas/m5-ecosistema/20_componentes_declarativos.py) genera JSON compatibles para importar ahí. |
| **AutoGen Bench** | Benchmarks de agentes | Orientado a investigación. |
| **Magentic-One completo** | Equipo generalista con navegador, archivos y código | Requiere Playwright y Docker. |
