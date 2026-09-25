# AGENTS.md

Guía para asistentes de IA (Claude Code, Codex, Copilot, etc.) que trabajen en este repositorio.

## Propósito del proyecto

Repositorio **educativo** para aprender AutoGen con modelos gratuitos de Groq. Tiene dos partes
con reglas distintas:

1. **`clase-01-debate/`**: el ejemplo armado en clase (group chat con selección dinámica de
   orador). Es **autocontenido** y se mantiene separado y fácil de identificar.
2. **`practicas/`**: un recorrido por las capacidades de AutoGen, en 24 prácticas y 6 módulos.

**Todo cambio debe preservar el valor didáctico:** código corto, legible de arriba a abajo y
explicado. Priorizá la claridad sobre la abstracción.

## Stack

- Python 3.12 (rango permitido `>=3.12,<3.14`)
- Poetry 2.x. Instala las dependencias y el paquete local `comun/` en modo editable (venv en `.venv/`).
- `autogen-agentchat` / `autogen-core` / `autogen-ext[openai]` 0.7.5: **API nueva (0.4+)**, no
  AutoGen 0.2 ni AG2.
- Groq vía `OpenAIChatCompletionClient` con `base_url="https://api.groq.com/openai/v1"`.
- AutoGen está en modo mantenimiento (sucesor: Microsoft Agent Framework). No migrar sin pedido
  explícito.

## Estructura

| Ruta | Contenido | Reglas |
|---|---|---|
| `clase-01-debate/` | `debate_groupchat.py`, `transcript.md`, `conceptos.md`, `ejercicios.md`, `README.md` | Un solo archivo de código. **No importa de `comun/`** (debe poder leerse aislado). |
| `practicas/mN-tema/NN_nombre.py` | Una práctica ejecutable por capacidad | Ver "Convenciones de prácticas". |
| `practicas/mN-tema/README.md` | Teoría del módulo, tabla de prácticas, comparaciones, preguntas de repaso | Actualizar si cambia una práctica. |
| `practicas/README.md` | Ruta de aprendizaje e índice | Actualizar si se agrega o quita una práctica. |
| `comun/modelos.py` | `cliente_groq()` / `cliente_liviano()` | Único lugar donde se configura Groq para las prácticas. |
| `comun/compat.py` | Parches AutoGen ↔ Groq | Cada parche documenta el síntoma, la causa y la solución. |
| `comun/rutas.py` | `ruta_salida()` → `salidas/` | Toda salida generada va a `salidas/` (gitignored). |
| `comun/verificar.py` | Compila todo y corre las prácticas sin LLM | Sumar ahí toda práctica nueva que no use Groq. |
| `docs/` | `mapa-de-capacidades.md`, `groq.md`, `problemas-frecuentes.md` | Generales para todo el repo. |

## Comandos

```bash
poetry install                                   # dependencias + paquete comun (requiere VPN: mirror interno)
poetry run python -m comun.verificar             # compila todo y corre prácticas sin LLM (no gasta cuota)
poetry run python clase-01-debate/debate_groupchat.py
poetry run python practicas/m1-fundamentos/01_cliente_modelo.py
```

## Cómo validar un cambio

1. `poetry run python -m comun.verificar` tiene que dar "Todo OK".
2. **Corré la práctica que tocaste** contra Groq y leé la salida: que el flujo sea el que el
   docstring promete (por ejemplo, que el Swarm derive y no se repita, o que el grafo recorra el
   ciclo). Que no tire error no alcanza.
3. Para la clase 01: `transcript.md` debe tener el tema, las líneas `🎙️ Moderador` antes de cada
   turno y el `Fin:` final.
4. Espaciá las corridas: la capa gratuita tiene un límite de tokens por minuto (ver Trampas).
5. Si no pudiste ejecutar algo (falta una dependencia o red), **decilo en el docstring o en el
   README del módulo**, como en la práctica 18.

## Convenciones

### Generales

- **Idioma:** código, comentarios, prompts y docs en **español rioplatense** (voseo: "elegí",
  "corré"). Los nombres de agentes van sin tildes ni espacios (`critico`, `guia_turistico`).
- **Comentarios:** explicar el *por qué* de cada parámetro no obvio: el lector está aprendiendo.
- **Configuración:** variables de entorno con default (`os.getenv("X", default)`). Toda variable
  nueva se documenta en la tabla del `README.md` raíz y en `.env.example`.
- **Docs sincronizadas:** si cambiás nombres de agentes, modelos, eventos, comandos o
  numeración, actualizá en el mismo cambio los README afectados y `docs/mapa-de-capacidades.md`.

### Convenciones de prácticas

- Nombre `NN_nombre.py`, con numeración global (01 a 24) y agrupadas por módulo.
- Docstring con 🎯 Objetivo, 📚 Conceptos (con los nombres exactos de la API) y ▶️ Correr.
- Pasos numerados en el código con 1️⃣ 2️⃣ 3️⃣.
- Terminar con 2 o 3 comentarios `# 🧪 EJERCICIO N:` para modificar o experimentar.
- Una capacidad principal por práctica. Si hacen falta dos, separarlas en partes (`parte_a_...`).
- Siempre definir `system_message` (el default de AutoGen está en inglés y pide "TERMINATE").
- Siempre una red de seguridad de terminación (`MaxMessageTermination` o `max_turns`).
- Cerrar los clientes al final (`await cliente.close()`).
- Usar `cliente_liviano()` para roles simples y `cliente_groq()` donde haga falta razonar o usar
  herramientas bien. Cada modelo tiene su propio límite de uso.

## Trampas conocidas (verificadas con autogen 0.7.5 + Groq)

- **Decisión del moderador:** se emite como `SelectSpeakerEvent` (`content: list[str]`) con
  `emit_team_events=True`. `SelectorEvent` solo aparece con `model_client_streaming=True`.
- **Selector:** reemplaza `{roles}`, `{participants}` y `{history}`. El moderador ve el
  `description` de cada agente, **no** su `system_message`.
- **`model_info`:** es obligatorio para modelos no-OpenAI. `comun/` declara
  `structured_output` y `multiple_system_messages` (la memoria lo necesita).
- **Handoffs:** `Handoff` crea herramientas `strict=True` sin parámetros y Groq devuelve un 400.
  Usar `comun.compat.HandoffGroq`.
- **Swarm:** si un agente responde con texto sin transferir, vuelve a hablar él. Usar
  `max_tool_iterations` > 1 y que el resultado de la herramienta indique el siguiente paso.
- **Límites de Groq:** `gpt-oss-20b` ≈ 8000 tokens por minuto. `comun` usa `max_retries=6`.
- **Modelos retirados:** `llama-3.3-70b-versatile` ya devuelve 404. Antes de cambiar un default,
  listá los modelos con `GET /openai/v1/models`.
- **`gpt-oss` razona antes de responder:** con `max_tokens` bajo (<1000) la respuesta puede salir vacía.
- **Core:** el parámetro de un `@message_handler` tiene que llamarse `message`. Un mensaje sin
  handler se ignora en silencio (devuelve `None`).
- **Core:** `DropMessage` en un intervention handler hace que `stop_when_idle()` no termine
  nunca (bug). Usar un `asyncio.Event` + `runtime.stop()`.
- **Componentes:** `dump_component()` enmascara la API key (`**********`). Al cargar, hay que
  reinyectarla.
- **Streaming:** `create_stream()` directo puede imprimir de forma intermitente un warning de
  `httpcore2` al cerrar el generador. Es inofensivo.
- **Red:** la red corporativa bloquea `pypi.org`. El mirror `pypi.artifacts.furycloud.io` es la
  fuente primaria en `pyproject.toml`; requiere VPN y sin ella da 403.

## Qué NO hacer

- No leer, imprimir ni commitear el contenido de `.env`.
- No migrar a AutoGen 0.2 / AG2 / Microsoft Agent Framework ni a otro framework sin pedido explícito.
- No reemplazar el `SelectorGroupChat` de la clase 01 por otro tipo de equipo: la selección
  dinámica es el objetivo de esa clase.
- No hacer que la clase 01 dependa de `comun/`, ni partir `debate_groupchat.py` en módulos.
- No agregar capas de abstracción (clases base, factories, registries) en las prácticas. Si algo
  se repite, que sea por claridad; lo compartido va a `comun/` solo si es infraestructura.
- No presentar datos de los agentes como verificados: los modelos alucinan y el repo lo
  documenta a propósito.
- No agregar dependencias a `pyproject.toml` para una sola práctica: indicá el `poetry add` en
  la práctica y en el README del módulo.
