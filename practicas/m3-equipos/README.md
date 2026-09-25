# Módulo 3 — Equipos: varios agentes trabajando juntos

El corazón de AutoGen. Todos los equipos comparten la idea de un **historial común**. Lo que
cambia es **quién decide quién habla** en cada momento.

> 💡 Prerrequisito: la [clase 01](../../clase-01-debate/), que explica en detalle
> `SelectorGroupChat` y el Group Chat Manager.

## Prácticas

| # | Archivo | Equipo | Idea clave |
|---|---|---|---|
| 09 | [09_round_robin.py](09_round_robin.py) | `RoundRobinGroupChat` | Turnos fijos. Simple y predecible. |
| 10 | [10_selector.py](10_selector.py) | `SelectorGroupChat` + `selector_func` | LLM moderador + reglas de código donde el flujo es determinista. |
| 11 | [11_swarm.py](11_swarm.py) | `Swarm` | Sin moderador: cada agente pasa la posta con handoffs. |
| 12 | [12_graphflow_paralelo.py](12_graphflow_paralelo.py) | `GraphFlow` | El flujo se dibuja como grafo; hay ramas en paralelo. |
| 13 | [13_graphflow_condicional.py](13_graphflow_condicional.py) | `GraphFlow` + `MessageFilterAgent` | Aristas condicionales, ciclos y agentes que ven solo parte del historial. |
| 14 | [14_magentic_one.py](14_magentic_one.py) | `MagenticOneGroupChat` | Un orquestador planifica, delega y replanifica. |

## ¿Qué equipo elijo?

| Equipo | ¿Quién decide? | Predecible | Costo en llamadas | Ideal para |
|---|---|---|---|---|
| RoundRobin | Orden fijo | ⭐⭐⭐ | Bajo | Pipelines simples (escribir → revisar) |
| Selector | LLM moderador | ⭐ | Medio (+1 llamada por turno) | Debates, roles que se necesitan según el contexto |
| Selector + `selector_func` | Código, y el LLM cuando hay duda | ⭐⭐ | Bajo-medio | Planificador + ejecutores |
| Swarm | El agente que habla (handoff) | ⭐⭐ | Bajo | Mesa de ayuda, derivaciones entre áreas |
| GraphFlow | El grafo que definiste | ⭐⭐⭐ | Bajo | Procesos de negocio con pasos conocidos, paralelismo |
| MagenticOne | Orquestador con plan | ⭐ | Alto | Tareas abiertas de varios pasos |

**Regla práctica:** empezá por lo más predecible que resuelva el problema. Pasá a un equipo
más "inteligente" solo cuando el flujo no se pueda escribir de antemano.

## Detalles con Groq (aprendidos al armar las prácticas)

- **Handoffs**: `Handoff` crea herramientas `strict=True` sin parámetros y Groq las rechaza
  con un 400. Usamos `HandoffGroq` de [`comun/compat.py`](../../comun/compat.py).
- **Swarm y texto**: si un agente responde con texto sin transferir, en un Swarm vuelve a hablar
  él mismo y puede repetirse. Ayuda darle `max_tool_iterations` > 1 y que el resultado de la
  herramienta le recuerde el siguiente paso.
- **Selector con modelo chico**: el moderador liviano a veces no respeta una asignación
  explícita. Lo que es determinista, resolvelo con `selector_func`.
- **Límites por minuto**: RoundRobin con código largo o MagenticOne pueden llegar al límite de TPM;
  el cliente compartido reintenta solo.

## Para repasar

1. ¿Por qué en la práctica 10 el planificador vuelve a hablar después de cada ejecutor?
2. En GraphFlow, ¿qué diferencia hay entre `activation="all"` y `"any"` en un nodo de fan-in?
3. ¿Por qué un grafo con ciclos necesita `set_entry_point`?
4. ¿Para qué sirve envolver al publicador con `MessageFilterAgent` en la práctica 13?

<details><summary>Respuestas</summary>

1. Porque `selector_func` lo fuerza: cualquier mensaje que no sea del planificador devuelve "planificador".
2. `all` espera a todos los predecesores; `any` arranca con el primero que termine.
3. Porque en un ciclo ningún nodo queda "sin entradas", y AutoGen no puede deducir por dónde empezar.
4. Para que solo lea el tweet final y no la discusión con el revisor: menos tokens y menos ruido.

</details>
