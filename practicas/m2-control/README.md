# Módulo 2 — Control: humanos y terminación

Cuando varios agentes conversan, aparecen dos preguntas: **¿cuándo interviene una persona?** y
**¿cuándo se detiene la conversación?** Sin respuestas claras, los agentes pueden charlar para
siempre (y consumir toda tu cuota).

## Prácticas

| # | Archivo | Capacidad | Idea clave |
|---|---|---|---|
| 07 | [07_humano_en_el_loop.py](07_humano_en_el_loop.py) | `UserProxyAgent` | Una persona es un participante más del equipo. |
| 08 | [08_terminacion.py](08_terminacion.py) | Condiciones, `ExternalTermination`, `CancellationToken` | Siempre tiene que haber una condición de fin, y una red de seguridad. |

## Formas de sumar a un humano

| Patrón | Cómo | Cuándo conviene |
|---|---|---|
| **Humano como participante** | `UserProxyAgent` dentro del equipo | Feedback en cada vuelta (práctica 07). |
| **Humano entre corridas** | `team.run()` → feedback → `team.run(task=feedback)` | Aplicaciones web: cada request es una corrida. |
| **Humano por handoff** | `Handoff(target="user")` + `HandoffTermination` | El agente decide cuándo necesita al humano (práctica 11). |
| **Humano como aprobador** | `approval_func` en `CodeExecutorAgent` | Aprobar acciones riesgosas (práctica 17). |

## Parar ordenadamente o cortar en seco

| | `ExternalTermination.set()` | `CancellationToken.cancel()` |
|---|---|---|
| Cuándo corta | Cuando termina el turno del agente actual | Inmediatamente, aunque haya una llamada al LLM en curso |
| Resultado | `TaskResult` con `stop_reason` | `CancelledError` |
| Estado del equipo | Consistente, se puede reanudar | Puede quedar a mitad de un turno |
| Uso típico | Botón "Detener" en una UI | Timeout duro, el usuario cerró la pestaña |

## Para repasar

1. ¿Qué pasa si un equipo no tiene ninguna condición de terminación ni `max_turns`?
2. ¿Qué hace `TextMentionTermination("APROBADO", sources=["humano"])` que no haga sin `sources`?
3. `A | B` contra `A & B`: ¿cuál es más seguro como red de seguridad?

<details><summary>Respuestas</summary>

1. Corre hasta que algo externo lo detenga: consume tokens sin fin.
2. Solo cuenta si "APROBADO" lo escribe el humano, no si lo menciona un agente.
3. `A | B`: alcanza con que se cumpla una. Con `&` tienen que cumplirse las dos, y si una nunca
   se cumple, nunca termina.

</details>
