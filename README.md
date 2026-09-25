# AutoGen en práctica

Repositorio **educativo** para aprender a construir sistemas multi-agente con
[AutoGen](https://microsoft.github.io/autogen/) usando modelos gratuitos de
[Groq](https://console.groq.com/). Todo el código y la documentación están en español.

> 📌 AutoGen está en **modo mantenimiento** desde octubre de 2025 y su sucesor es Microsoft Agent
> Framework. Los conceptos que se practican acá (agentes, herramientas, equipos, handoffs,
> grafos, runtime de actores) se transfieren directamente. Más detalle en el
> [mapa de capacidades](docs/mapa-de-capacidades.md).

## 🧭 Por dónde empezar

| Si querés... | Andá a |
|---|---|
| Ver un ejemplo completo funcionando | 🎓 [**Clase 01 — Debate multi-agente**](clase-01-debate/): investigador + crítico + moderador |
| Recorrer AutoGen de punta a punta | 🧪 [**Prácticas**](practicas/): 24 ejercicios en 6 módulos |
| Saber qué ofrece AutoGen y dónde se practica | 🗺️ [**Mapa de capacidades**](docs/mapa-de-capacidades.md) |
| Resolver un error | 🩹 [**Problemas frecuentes**](docs/problemas-frecuentes.md) |

## 🗂️ Estructura

```
autogen-practices/
├── clase-01-debate/       🎓 Ejemplo armado en clase (autocontenido, no depende de comun/)
│   ├── debate_groupchat.py    SelectorGroupChat: investigador, crítico y moderador
│   ├── transcript.md          corrida de ejemplo
│   ├── conceptos.md           teoría del group chat
│   └── ejercicios.md          prácticas sobre este ejemplo
│
├── practicas/             🧪 Recorrido por todas las capacidades
│   ├── m1-fundamentos/        01-06  agente, herramientas, salida estructurada, memoria, estado
│   ├── m2-control/            07-08  humano en el loop, terminación, cancelación
│   ├── m3-equipos/            09-14  RoundRobin, Selector, Swarm, GraphFlow, MagenticOne
│   ├── m4-composicion/        15-16  SocietyOfMind, AgentTool, TeamTool
│   ├── m5-ecosistema/         17-21  código, MCP, caché/replay, JSON, observabilidad
│   └── m6-core/               22-24  runtime de actores, RPC, pub/sub, middleware
│
├── comun/                 🔧 Código compartido por las prácticas
│   ├── modelos.py             cliente de Groq listo para usar
│   ├── compat.py              parches de compatibilidad AutoGen ↔ Groq (explicados)
│   ├── rutas.py               dónde se guardan las salidas
│   └── verificar.py           chequeo automático del repo (sin gastar cuota)
│
├── docs/                  📚 Documentación general
│   ├── mapa-de-capacidades.md
│   ├── groq.md
│   └── problemas-frecuentes.md
│
├── salidas/               (se genera al correr prácticas; ignorado por git)
├── AGENTS.md              guía para asistentes de IA que trabajen en este repo
└── pyproject.toml         dependencias (Poetry)
```

## 🚀 Puesta en marcha

**Requisitos:** Python 3.12 o 3.13, [Poetry](https://python-poetry.org/) 2.x y una API key
gratuita de Groq (<https://console.groq.com/keys>).

```bash
# 1. Instalar dependencias (y el paquete local `comun`)
poetry install

# 2. Configurar la API key
cp .env.example .env        # y editá .env con tu key

# 3. Verificar que todo está en orden (no consume cuota)
poetry run python -m comun.verificar

# 4. Correr la clase o cualquier práctica
poetry run python clase-01-debate/debate_groupchat.py
poetry run python practicas/m1-fundamentos/02_primer_agente.py
```

> ⚠️ **Red corporativa:** `pyproject.toml` usa como fuente el mirror interno
> `pypi.artifacts.furycloud.io`, que requiere **VPN**. Ver
> [problemas frecuentes](docs/problemas-frecuentes.md#instalación).

## ⚙️ Configuración

Variables en `.env` (ver [.env.example](.env.example)):

| Variable | Default | Uso |
|---|---|---|
| `GROQ_API_KEY` | (obligatoria) | Autenticación con Groq |
| `GROQ_MODEL` | `openai/gpt-oss-120b` | Modelo principal (clase 01 y prácticas) |
| `GROQ_MODELO_LIVIANO` | `openai/gpt-oss-20b` | Modelo chico de las prácticas (moderadores, tareas simples) |
| `GROQ_MODERATOR_MODEL` | `openai/gpt-oss-20b` | Moderador de la clase 01 |
| `MAX_TURNS` | `5` | Turnos del debate de la clase 01 |

## 📏 Convenciones del repo

- **Una capacidad por práctica.** Cada archivo se lee de arriba a abajo, con 🎯 objetivo,
  📚 conceptos, ▶️ cómo correrlo, pasos numerados (1️⃣ 2️⃣) y 🧪 ejercicios.
- **Lo validado se marca como validado.** Las prácticas se corrieron contra Groq con AutoGen
  0.7.5. La única que no se pudo ejecutar (la 18, MCP) lo dice explícitamente.
- **Los errores también enseñan.** Los problemas reales que aparecieron (límites por minuto,
  esquemas que Groq rechaza, bugs de AutoGen) están documentados donde ocurren, con su porqué.
- **Los LLMs alucinan.** Ningún dato que produzcan los agentes está verificado; la clase 01 lo
  muestra a propósito.
