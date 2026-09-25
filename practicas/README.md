# Prácticas: recorrido completo por AutoGen

24 prácticas cortas y ejecutables, agrupadas en 6 módulos de dificultad creciente. Cada una se
enfoca en **una** capacidad de AutoGen.

> 🗺️ ¿Qué cubre cada práctica y qué queda afuera? → [docs/mapa-de-capacidades.md](../docs/mapa-de-capacidades.md)

## Ruta de aprendizaje

```
 m1 Fundamentos ──► m2 Control ──► m3 Equipos ──► m4 Composición ──► m5 Ecosistema
  (1 agente)       (humano,        (varios         (equipos dentro     (código, MCP,
                   terminación)    agentes)         de equipos)          caché, JSON)
                                       │
                                       └──► m6 Core (cómo funciona todo por dentro)
```

| Módulo | Prácticas | Vas a aprender |
|---|---|---|
| [m1-fundamentos](m1-fundamentos/) | 01 a 06 | Cliente de modelo, agente, herramientas, salida estructurada, memoria, estado |
| [m2-control](m2-control/) | 07 y 08 | Humano en el loop, condiciones de terminación, cancelación |
| [m3-equipos](m3-equipos/) | 09 a 14 | RoundRobin, Selector, Swarm, GraphFlow, MagenticOne |
| [m4-composicion](m4-composicion/) | 15 y 16 | SocietyOfMind, AgentTool y TeamTool |
| [m5-ecosistema](m5-ecosistema/) | 17 a 21 | Ejecución de código, MCP, caché y replay, componentes JSON, observabilidad |
| [m6-core](m6-core/) | 22 a 24 | Runtime de actores, RPC, pub/sub, middleware, agente hecho a mano |

> 💡 Antes del módulo 3, hacé la [clase 01](../clase-01-debate/): es el ejemplo completo de
> `SelectorGroupChat` que la práctica 10 da por conocido.

## Cómo está armada cada práctica

Cada archivo `NN_nombre.py` se lee de arriba a abajo y sigue siempre la misma estructura:

| Marca | Significado |
|---|---|
| 🎯 | **Objetivo**: qué vas a lograr |
| 📚 | **Conceptos**: la teoría mínima, con los nombres exactos de la API |
| ▶️ | **Cómo correrla** |
| 1️⃣ 2️⃣ 3️⃣ | Los pasos, numerados en el código |
| 🧪 | **Ejercicios** al final del archivo, para modificar y experimentar |

Cada módulo tiene además su `README.md` con la comparación entre las alternativas y las
preguntas para repasar.

## Cómo correrlas

Desde la raíz del repo:

```bash
poetry run python practicas/m1-fundamentos/01_cliente_modelo.py
```

- Todas usan el cliente compartido de [`comun/modelos.py`](../comun/modelos.py) (Groq, capa
  gratuita), salvo la 01, que arma la conexión a mano para mostrarla.
- Lo que generan (estado, JSON, código ejecutado, logs) va a `salidas/`, que está en `.gitignore`.
- Las prácticas **19, 22 y 23 no usan Groq**: funcionan sin API key.
- La **18 (MCP)** necesita instalar un extra: `poetry add "autogen-ext[mcp]"`.

## Cuidar la cuota gratuita

La capa gratuita de Groq limita los **tokens por minuto** por modelo (por ejemplo, 8000 TPM para
`gpt-oss-20b`). El cliente compartido reintenta solo cuando recibe un `429`, pero:

- Entre práctica y práctica, esperá unos segundos.
- Las prácticas más "caras" son la **14 (MagenticOne)**, la **11 (Swarm)** y la **09** con su
  segunda tarea. Si ves muchos reintentos, bajá los límites de turnos.
- Usá la **19** para aprender a cachear y a testear sin consumir cuota.

## Verificar que todo funciona

```bash
poetry run python -m comun.verificar
```

Compila todos los archivos y corre las prácticas que no necesitan LLM. No consume cuota.
