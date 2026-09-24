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

### `429 Too Many Requests`

**Causa:** superaste el límite por minuto de la capa gratuita.

**Solución:** esperá un minuto, bajá `MAX_TURNS` o usá un modelo más chico para el moderador.

### Las respuestas salen vacías o cortadas

**Causa:** con modelos que razonan (`gpt-oss`), un `max_tokens` bajo se consume en el razonamiento
interno.

**Solución:** subí `max_tokens` en `groq_client()` (el proyecto usa 2000) y controlá la longitud
desde el `system_message`.

### No aparecen las líneas `🎙️ Moderador`

**Causa:** en AutoGen 0.7 la decisión del moderador llega como `SelectSpeakerEvent`. `SelectorEvent`
solo existe con `model_client_streaming=True`.

**Solución:** verificá `emit_team_events=True` en `SelectorGroupChat` y que el loop compare contra
`"SelectSpeakerEvent"`.

---

## Resultados

### Los agentes dan datos falsos con mucha seguridad

**No es un bug del código:** es una limitación de los LLMs sin acceso a fuentes. Ver
la sección *Limitaciones* del [README](../README.md) y el
[ejercicio 5](ejercicios.md#ejercicio-5--darle-una-herramienta-al-investigador).

### El moderador siempre alterna

**No es round-robin:** es la decisión que tomó el LLM con esas reglas. Ver
[conceptos.md §4](conceptos.md#selección-dinámica--resultado-variado) y el
[ejercicio 2](ejercicios.md#ejercicio-2--forzar-una-decisión-no-alternada).
