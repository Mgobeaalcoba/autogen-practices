# Módulo 4 — Composición: sistemas hechos de piezas

Los sistemas reales mezclan patrones: un equipo que revisa dentro de otro equipo que traduce, un
coordinador que consulta especialistas... AutoGen permite **encajar agentes y equipos como
piezas**.

## Prácticas

| # | Archivo | Capacidad | Idea clave |
|---|---|---|---|
| 15 | [15_society_of_mind.py](15_society_of_mind.py) | `SocietyOfMindAgent` | Un equipo entero se presenta como un solo agente que resume. |
| 16 | [16_agentes_como_herramientas.py](16_agentes_como_herramientas.py) | `AgentTool`, `TeamTool` | Un coordinador llama a agentes y equipos como si fueran funciones. |

## Tres formas de combinar

```
 A) Group chat            B) SocietyOfMind              C) Agente como herramienta
 ───────────────          ─────────────────             ──────────────────────────
 todos ven todo           equipo interno oculto;        el coordinador pregunta;
                          afuera solo llega el resumen  cada experto ve SOLO la pregunta

  a ⇄ b ⇄ c               [ a ⇄ b ] ──► c                coord ──tool──► experto
                                                               ◄─result──
```

| | Group chat | SocietyOfMind | AgentTool / TeamTool |
|---|---|---|---|
| ¿Quién controla? | El equipo (manager) | El equipo externo | El coordinador (LLM) |
| ¿Qué ve cada agente? | Todo el historial | El interno, su discusión; el externo, el resumen | Solo la pregunta puntual |
| Costo | Crece con el historial | Discusión interna + 1 resumen | Una sub-corrida por consulta |
| Ideal para | Colaboración abierta | Encapsular un proceso de calidad | Consultar especialistas bajo demanda |

## Para repasar

1. En la práctica 15, ¿el traductor puede leer lo que discutieron el escritor y el editor?
2. ¿Por qué `AgentTool` requiere `parallel_tool_calls=False`?
3. ¿Qué devuelve un `TeamTool` con `return_value_as_last_message=True`?

<details><summary>Respuestas</summary>

1. No. La consola lo muestra, pero al historial del equipo externo solo entra el resumen del comité.
2. Porque un mismo agente no puede atender dos pedidos simultáneos sin mezclar su historial.
3. Solo el último mensaje del equipo, en lugar de toda la conversación interna.

</details>
