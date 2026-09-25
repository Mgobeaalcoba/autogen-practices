# Módulo 1 — Fundamentos: un agente

Todo arranca con **un solo agente**. En este módulo vas a entender qué hace un agente por encima
del LLM "pelado" y cómo darle herramientas, formato de salida, memoria y persistencia.

## Prácticas

| # | Archivo | Capacidad | Idea clave |
|---|---|---|---|
| 01 | [01_cliente_modelo.py](01_cliente_modelo.py) | `ChatCompletionClient` | El LLM no tiene memoria: cada llamada manda todo el historial. |
| 02 | [02_primer_agente.py](02_primer_agente.py) | `AssistantAgent`, `run`, `run_stream`, `Console` | Un agente = LLM + rol + historial propio. |
| 03 | [03_herramientas.py](03_herramientas.py) | Tools, `FunctionTool`, `reflect_on_tool_use` | El LLM no ejecuta nada: pide que ejecutes una función y lee el resultado. |
| 04 | [04_salida_estructurada.py](04_salida_estructurada.py) | `output_content_type` | Respuestas como objetos Pydantic validados, no texto libre. |
| 05 | [05_contexto_y_memoria.py](05_contexto_y_memoria.py) | `model_context`, `memory` | Contexto = qué historial se envía. Memoria = qué conocimiento extra se inyecta. |
| 06 | [06_estado.py](06_estado.py) | `save_state` / `load_state` | Una conversación se puede pausar, guardar en disco y retomar. |

## Qué hace un agente por vos

```
                 ┌─────────────── AssistantAgent ───────────────┐
 tarea ──────►   │ 1. suma el mensaje a su historial (contexto)  │
                 │ 2. consulta la memoria y la agrega            │
                 │ 3. llama al LLM con system_message+historial  │
                 │ 4. ¿pidió herramientas? → las ejecuta y vuelve│ ──► respuesta
                 │    a 3 (hasta max_tool_iterations)            │     (TextMessage o
                 │ 5. guarda la respuesta en el historial        │      StructuredMessage)
                 └───────────────────────────────────────────────┘
```

En la [práctica 24](../m6-core/24_agente_core_con_llm.py) vas a construir esto a mano.

## Para repasar

1. ¿Por qué en la práctica 01 hay que reenviar la respuesta anterior y en la 02 no?
2. ¿Qué lee el LLM para decidir cómo usar una herramienta?
3. ¿Qué diferencia hay entre `reflect_on_tool_use=True` y `False`?
4. ¿Qué tipo de mensaje devuelve un agente con `output_content_type`?
5. `BufferedChatCompletionContext(buffer_size=2)` y `ListMemory`: ¿cuál limita y cuál agrega?
6. ¿Qué NO se guarda con `save_state()`?

<details><summary>Respuestas</summary>

1. El cliente no guarda nada; el agente mantiene su propio historial.
2. El nombre de la función, su docstring y los type hints (el esquema JSON que genera AutoGen).
3. Con `True` el agente redacta una respuesta final; con `False` devuelve el resultado crudo
   (`ToolCallSummaryMessage`).
4. `StructuredMessage[TuModelo]`, cuyo `content` es una instancia del modelo.
5. El buffer limita lo que se envía; la memoria agrega información.
6. La configuración: `system_message`, herramientas y modelo. Solo se guarda el historial.

</details>

## Detalles con Groq

- Si no definís `system_message`, AutoGen usa uno en inglés que le pide al modelo terminar con
  "TERMINATE". En las prácticas siempre lo definimos.
- La memoria inyecta un segundo `SystemMessage`, por eso el cliente compartido declara
  `multiple_system_messages: True` en `model_info`.
