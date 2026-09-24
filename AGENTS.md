# AGENTS.md

Guía para asistentes de IA (Claude Code, Codex, Copilot, etc.) que trabajen en este repositorio.

## Propósito del proyecto

Proyecto **educativo** que muestra un group chat de AutoGen con selección dinámica de orador:
un `investigador` y un `critico` debaten sobre una noticia real, y el Group Chat Manager de
`SelectorGroupChat` decide con un LLM quién habla en cada turno. Backend: Groq (capa gratuita).

**Todo cambio debe preservar el valor didáctico:** código corto, legible de arriba a abajo y
explicado. Priorizá la claridad sobre la abstracción.

## Stack

- Python 3.12 (rango permitido `>=3.12,<3.14`)
- Poetry 2.x (`package-mode = false`, venv en `.venv/`)
- `autogen-agentchat` / `autogen-ext[openai]` 0.7.x — **API nueva (0.4+)**, no AutoGen 0.2 ni AG2
- Groq vía `OpenAIChatCompletionClient` con `base_url="https://api.groq.com/openai/v1"`

## Comandos

```bash
poetry install                              # instalar dependencias (requiere VPN: mirror interno)
poetry run python debate_groupchat.py       # correr el debate (usa GROQ_API_KEY de .env)
poetry run python -m py_compile debate_groupchat.py   # chequeo rápido de sintaxis
```

No hay tests automatizados. Para validar un cambio, **corré el debate** y revisá que
`transcript.md` tenga el tema, las líneas `🎙️ Moderador` antes de cada turno y el `Fin:` final.
Si no tenés `GROQ_API_KEY`, al menos importá el módulo con una key falsa para validar la
construcción de objetos:

```bash
GROQ_API_KEY=dummy poetry run python -c "import debate_groupchat"
```

## Estructura

| Archivo | Contenido |
|---|---|
| `debate_groupchat.py` | Todo el programa. Mantenerlo en un solo archivo. |
| `transcript.md` | Salida de ejemplo, se sobrescribe en cada corrida. Se versiona como referencia. |
| `docs/conceptos.md` | Teoría (group chat, selección, eventos). |
| `docs/groq.md` | Conexión con Groq, `model_info`, modelos, límites. |
| `docs/ejercicios.md` | Prácticas para estudiantes. |
| `docs/problemas-frecuentes.md` | Troubleshooting. |

## Convenciones

- **Idioma:** código, comentarios, prompts y docs en **español rioplatense** (voseo: "elegí",
  "corré"). Identificadores de agentes sin tildes (`critico`, `investigador`) porque AutoGen los
  usa como nombres de tópico.
- **Comentarios:** explicar el *por qué* de cada parámetro no obvio (el lector está aprendiendo).
- **Configuración:** por variables de entorno con default razonable (`os.getenv("X", default)`);
  documentar cualquier variable nueva en la tabla de configuración del `README.md` y en
  `.env.example`.
- **Docs sincronizadas:** si cambiás nombres de agentes, modelos, eventos o comandos, actualizá
  `README.md` y el doc de `docs/` que corresponda en el mismo cambio.

## Trampas conocidas (verificadas con autogen 0.7.5)

- La decisión del moderador se emite como **`SelectSpeakerEvent`** (`content: list[str]`) cuando
  `emit_team_events=True`. `SelectorEvent` solo se emite con `model_client_streaming=True`.
- `SelectorGroupChat` reemplaza `{roles}`, `{participants}` y `{history}` en `selector_prompt`. El
  moderador ve el `description` de cada agente, **no** su `system_message`.
- Modelos no-OpenAI requieren `model_info` explícito en `OpenAIChatCompletionClient`.
- Groq retira modelos: `llama-3.3-70b-versatile` ya devuelve 404. Antes de cambiar el default,
  listá los modelos con `GET /openai/v1/models`.
- Los modelos `gpt-oss` razonan antes de responder: `max_tokens` bajo (<1000) puede dejar la
  respuesta vacía.
- La red corporativa bloquea `pypi.org`; el mirror `pypi.artifacts.furycloud.io` (fuente primaria en
  `pyproject.toml`) requiere VPN y da 403 sin ella.

## Qué NO hacer

- No leer, imprimir ni commitear el contenido de `.env`.
- No migrar a AutoGen 0.2 / AG2 (`GroupChatManager` clásico) ni a otro framework sin pedirlo.
- No reemplazar `SelectorGroupChat` por `RoundRobinGroupChat`: la selección dinámica es el objetivo
  del proyecto.
- No dividir `debate_groupchat.py` en módulos ni agregar capas de abstracción (clases base,
  factories) que dificulten leerlo de corrido.
- No presentar los datos de los agentes como verificados: los modelos alucinan y el proyecto lo
  documenta a propósito.
