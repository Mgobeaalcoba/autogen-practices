# Módulo 5 — Ecosistema: llevar agentes a proyectos reales

Lo que hace falta para salir del "demo": ejecutar código de forma controlada, conectarse a
herramientas externas, no gastar de más, testear sin LLM, versionar configuraciones y ver qué
pasa por dentro.

## Prácticas

| # | Archivo | Capacidad | Idea clave |
|---|---|---|---|
| 17 | [17_ejecucion_codigo.py](17_ejecucion_codigo.py) | `CodeExecutorAgent`, `approval_func` | El agente escribe código y lo ejecuta con tu aprobación. |
| 18 | [18_mcp.py](18_mcp.py) + [servidor](servidor_mcp_biblioteca.py) | `McpWorkbench` | Herramientas estándar que viven en otro proceso. |
| 19 | [19_cache_y_replay.py](19_cache_y_replay.py) | `ChatCompletionCache`, `ReplayChatCompletionClient` | Ahorrar llamadas y testear sin LLM. |
| 20 | [20_componentes_declarativos.py](20_componentes_declarativos.py) | `dump_component` / `load_component` | Un equipo entero como JSON. |
| 21 | [21_observabilidad.py](21_observabilidad.py) | `EVENT_LOGGER_NAME`, `LLMCallEvent` | Contar tokens y registrar cada llamada. |

## Preparación extra

| Práctica | Qué instalar | Comando |
|---|---|---|
| 18 (MCP) | Cliente y servidor MCP | `poetry add "autogen-ext[mcp]"` (requiere VPN por el mirror interno) |
| 17 · ejercicio 3 | Ejecutor Docker | `poetry add "autogen-ext[docker]"` + Docker Desktop |
| 19 · ejercicio 1 | Caché en disco | `poetry add diskcache` |

> ⚠️ La práctica 18 se escribió contra la API de `autogen-ext` 0.7.5, pero **no se pudo
> ejecutar al armar el repo** porque no se pudo instalar el extra `mcp`. Si encontrás un error,
> contrastalo con la [documentación de McpWorkbench](https://microsoft.github.io/autogen/stable/reference/python/autogen_ext.tools.mcp.html).

## Seguridad al ejecutar código

| Ejecutor | Aislamiento | Cuándo usarlo |
|---|---|---|
| `LocalCommandLineCodeExecutor` | ❌ Ninguno: corre con tus permisos | Aprender, con aprobación humana |
| `DockerCommandLineCodeExecutor` | ✅ Contenedor | Cualquier uso real |
| `JupyterCodeExecutor` | ❌ Kernel local | Análisis de datos con estado entre celdas |

Reglas mínimas: carpeta de trabajo propia (`work_dir`), `timeout`, aprobación para acciones
destructivas y nunca exponer secretos en el entorno del ejecutor.

## Observabilidad: más allá de los logs

- **Logs de eventos** (práctica 21): simples, locales, suficientes para depurar y contar tokens.
- **OpenTelemetry**: AutoGen emite spans al crear agentes, invocarlos y ejecutar herramientas
  (`trace_create_agent_span`, `trace_invoke_agent_span`, `trace_tool_span`). Se pasa un
  `tracer_provider` al runtime (`SingleThreadedAgentRuntime(tracer_provider=...)`) y se visualiza
  en Jaeger, Zipkin o Azure Monitor. Requiere instalar `opentelemetry-sdk` y un exportador.

## Para repasar

1. ¿Por qué la práctica 17 pide aprobación antes de ejecutar?
2. ¿En qué se diferencia `tools=[...]` de `workbench=McpWorkbench(...)`?
3. ¿Qué pasa con la API key al exportar un equipo a JSON? ¿Y al cargarlo?
4. ¿Por qué `ReplayChatCompletionClient` es útil para tests automáticos?

<details><summary>Respuestas</summary>

1. El código lo genera un LLM y el ejecutor local corre con tus permisos: podría borrar archivos o filtrar datos.
2. Con `tools` las funciones están en tu proceso; con el workbench las provee un servidor externo con un protocolo estándar.
3. Se enmascara (`**********`). Al cargar hay que inyectar la key real desde el entorno.
4. Porque es determinista, gratis y no depende de la red.

</details>
