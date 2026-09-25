# Problemas frecuentes

Errores reales que aparecieron al armar este proyecto, con su causa y solución.

---

## Instalación

### `403 Forbidden` desde `pypi.artifacts.furycloud.io`

```
hint: An index URL (https://pypi.artifacts.furycloud.io/simple) returned a 403 Forbidden error.
```

**Causa:** el mirror interno solo responde conectado a la **VPN**. Da 403 para cualquier paquete,
no solo para AutoGen.

**Solución:** conectate a la VPN y verificá:

```bash
curl -s -o /dev/null -w "%{http_code}\n" https://pypi.artifacts.furycloud.io/simple/requests/
# 200 → podés instalar · 403 → todavía no tenés acceso
```

### `could not resolve host` / Poetry se queda en "Resolving dependencies..."

**Causa:** la red no llega a `pypi.org` (DNS bloqueado). Poetry reintenta durante minutos antes de
fallar.

**Solución:** cortá con `Ctrl+C` y usá el mirror con VPN (ver arriba). Si estás fuera de la red
corporativa y querés usar PyPI público, sacá el bloque `[[tool.poetry.source]]` de
`pyproject.toml` y corré `poetry lock && poetry install`.

### El proyecto usaba `uv` y ahora Poetry

Si ves referencias a `uv sync` / `uv run` en algún lado, son de una versión anterior. Los
comandos equivalentes son `poetry install` / `poetry run`.

### `ModuleNotFoundError: No module named 'comun'`

**Causa:** el paquete local `comun/` se instala con `poetry install`. Si solo instalaste las
dependencias con otra herramienta, o corrés con un Python que no es el de `.venv`, no lo encuentra.

**Solución:** `poetry install` y corré siempre con `poetry run python ...` desde la raíz del repo.

### `Falta la dependencia de MCP` (práctica 18)

**Solución:** `poetry add "autogen-ext[mcp]"` (con VPN, por el mirror interno).

---

## Ejecución

### `Falta GROQ_API_KEY`

**Causa:** no hay archivo `.env` o la variable está vacía.

**Solución:** `cp .env.example .env` y poné tu key de <https://console.groq.com/keys>.

### `401 Invalid API Key`

**Causa típica:** quedó el valor de ejemplo (`gsk_tu_key_aca`) o se pegó con espacios/comillas.

**Solución:** el archivo debe tener una sola línea así, sin comillas:

```
GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

Si lo editaste con TextEdit, asegurate de que se guardó como **texto plano** y que el archivo se
sigue llamando `.env` (no `.env.txt`).

### `404 model_not_found`

```
The model `llama-3.3-70b-versatile` does not exist or you do not have access to it.
```

**Causa:** Groq retiró ese modelo.

**Solución:** listá los modelos disponibles y elegí otro con `GROQ_MODEL` (ver
[groq.md](groq.md#modelos)).

### `429 Too Many Requests` / `rate_limit_exceeded ... tokens per minute (TPM)`

```
Rate limit reached for model `openai/gpt-oss-20b` ... on tokens per minute (TPM): Limit 8000
```

**Causa:** la capa gratuita limita tokens **por minuto y por modelo**. Los equipos que repiten
historiales largos (RoundRobin con código, MagenticOne) lo alcanzan rápido.

**Solución:** el cliente de `comun/modelos.py` ya reintenta hasta 6 veces esperando lo que indica
Groq (`max_retries`). Si igual falla: esperá un minuto entre prácticas, bajá los turnos, pedí
respuestas más cortas en los `system_message` o repartí agentes entre los dos modelos (cada uno
tiene su propio límite).

### Las respuestas salen vacías o cortadas

**Causa:** con modelos que razonan (`gpt-oss`), un `max_tokens` bajo se consume en el razonamiento
interno.

**Solución:** subí `max_tokens` en `groq_client()` (el proyecto usa 2000) y controlá la longitud
desde el `system_message`.

### `Multiple and Not continuous system messages are not supported`

**Causa:** la memoria (`memory=[ListMemory()]`) inyecta un `SystemMessage` extra en medio del
historial, y AutoGen lo bloquea salvo que el modelo declare que lo soporta.

**Solución:** agregar `"multiple_system_messages": True` en `model_info` (ya está en
`comun/modelos.py`).

### `invalid JSON schema for tool transfer_to_...: 'required' present but 'properties' is missing`

**Causa:** en AutoGen 0.7.5, `Handoff` crea herramientas sin parámetros con `strict=True`, y Groq
rechaza ese esquema (error 400). Pasa en `Swarm` o con cualquier agente que use `handoffs=`.

**Solución:** usar `HandoffGroq` de `comun/compat.py` en lugar de `Handoff` (o de pasar el
nombre como string). Es idéntico, pero con `strict=False`.

### Un agente del Swarm repite el mismo mensaje varias veces

**Causa:** en `Swarm` no hay moderador: si un agente responde con texto sin transferir, le vuelve
a tocar a él.

**Solución:** darle `max_tool_iterations` > 1 (así puede encadenar herramienta → transferencia),
decirle en el `system_message` que siempre transfiera al terminar, y hacer que el resultado de
sus herramientas le recuerde el siguiente paso. Ver práctica 11.

### `AssertionError: message parameter not found in function signature`

**Causa:** en `autogen_core`, el parámetro de un `@message_handler` tiene que llamarse
exactamente `message`.

**Solución:** `async def manejar(self, message: MiTipo, ctx: MessageContext)`.

### Un handler de `RoutedAgent` "no responde" (devuelve `None`)

**Causa:** el tipo del mensaje enviado no coincide con el tipo anotado en ningún handler.
`RoutedAgent` ignora los mensajes que no sabe atender, sin error.

**Solución:** revisá la anotación `message: Tipo` del handler.

### `stop_when_idle()` no termina nunca

**Causa:** bug de `autogen-core` 0.7.5. Si un intervention handler devuelve `DropMessage`, el
runtime no marca ese mensaje como procesado y la espera no termina.

**Solución:** avisar con un `asyncio.Event` cuando el trabajo esté listo y llamar a
`runtime.stop()`. Ver práctica 23.

### `an error occurred during closing of asynchronous generator ... PoolByteStream`

**Causa:** interacción entre el streaming de AutoGen (lee cada fragmento en una tarea de asyncio
distinta) y `httpcore2` al cerrar la conexión. Aparece de forma intermitente al usar
`create_stream()` directo.

**Solución:** ninguna necesaria: la respuesta llega completa y correcta. Es solo ruido en la
salida de errores.

### Al cargar un equipo desde JSON da `401 Invalid API Key`

**Causa:** `dump_component()` enmascara la key como `**********` al serializar (a propósito,
para poder compartir el archivo). Al cargarlo, el cliente usa ese texto como key.

**Solución:** reemplazar la key enmascarada por la real antes de `load_component()`. Ver la
función `inyectar_api_key` en la práctica 20.

### El traceback `Error processing publish message` al cancelar

**Causa:** con `CancellationToken.cancel()`, el runtime loguea el mensaje que quedó a medio
procesar. Es esperable.

**Solución:** ignorarlo o subir el nivel del logger `autogen_core` (práctica 08).

### No aparecen las líneas `🎙️ Moderador`

**Causa:** en AutoGen 0.7 la decisión del moderador llega como `SelectSpeakerEvent`. `SelectorEvent`
solo existe con `model_client_streaming=True`.

**Solución:** verificá `emit_team_events=True` en `SelectorGroupChat` y que el loop compare contra
`"SelectSpeakerEvent"`.

---

## Resultados

### Los agentes dan datos falsos con mucha seguridad

**No es un bug del código:** es una limitación de los LLMs sin acceso a fuentes. Ver
la sección *Limitaciones* del [README de la clase 01](../clase-01-debate/README.md) y el
[ejercicio 5](../clase-01-debate/ejercicios.md#ejercicio-5--darle-una-herramienta-al-investigador).

### El moderador siempre alterna

**No es round-robin:** es la decisión que tomó el LLM con esas reglas. Ver
[conceptos.md §4](../clase-01-debate/conceptos.md#selección-dinámica--resultado-variado) y el
[ejercicio 2](../clase-01-debate/ejercicios.md#ejercicio-2--forzar-una-decisión-no-alternada).
