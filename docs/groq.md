# Groq como backend de AutoGen

## ¿Por qué Groq?

- Tiene **capa gratuita** (solo pide una cuenta, sin tarjeta).
- Es **muy rápido** (hardware propio para inferencia).
- Expone una API **compatible con OpenAI**, así que AutoGen se conecta con el cliente de OpenAI
  que ya trae, sin librerías extra.

## Cómo se conecta

```python
OpenAIChatCompletionClient(
    model="openai/gpt-oss-120b",
    base_url="https://api.groq.com/openai/v1",   # 👈 en vez de api.openai.com
    api_key=os.environ["GROQ_API_KEY"],
    model_info={...},                            # 👈 obligatorio para modelos no-OpenAI
    temperature=0.7,
    max_tokens=2000,
)
```

La única diferencia con usar OpenAI es `base_url` y `model_info`.

### ¿Qué es `model_info`?

AutoGen tiene una tabla con las capacidades de los modelos de OpenAI. Para cualquier otro modelo
**no sabe qué puede hacer**, así que se lo tenés que declarar:

| Clave | Valor acá | Significado |
|---|---|---|
| `vision` | `False` | ¿Acepta imágenes? |
| `function_calling` | `True` | ¿Puede usar herramientas (*tools*)? Necesario para el [ejercicio 5](../clase-01-debate/ejercicios.md#ejercicio-5--darle-una-herramienta-al-investigador). |
| `json_output` | `True` | ¿Soporta modo JSON? |
| `structured_output` | `False` (clase 01) / `True` (`comun/`) | ¿Soporta salida con esquema estricto? Groq lo soporta con `gpt-oss`; lo usa la práctica 04. |
| `family` | `"unknown"` | Familia del modelo; AutoGen la usa para ajustes específicos. |

| `multiple_system_messages` | `True` (`comun/`) | ¿Acepta varios mensajes de sistema? Necesario para la memoria (práctica 05). |

Si omitís `model_info`, AutoGen tira error al crear el cliente.

> 💡 La clase 01 arma su propio cliente (es autocontenida). Las prácticas usan el cliente
> compartido de [`comun/modelos.py`](../comun/modelos.py), que declara todas las capacidades y
> agrega reintentos ante límites de uso.

## Modelos

Los modelos disponibles **cambian con el tiempo**: Groq retira unos y agrega otros. Por ejemplo,
`llama-3.3-70b-versatile` ya no está disponible y devuelve:

```
404 - The model `llama-3.3-70b-versatile` does not exist or you do not have access to it.
```

Para ver los modelos que tu key puede usar hoy:

```bash
set -a && . ./.env && set +a
curl -s https://api.groq.com/openai/v1/models -H "Authorization: Bearer $GROQ_API_KEY" \
  | poetry run python -c "import sys,json; [print(m['id']) for m in json.load(sys.stdin)['data']]"
```

Después cambialos sin tocar código:

```bash
GROQ_MODEL=qwen/qwen3.8-27b poetry run python clase-01-debate/debate_groupchat.py
```

### Por qué dos modelos distintos

- **Agentes → `gpt-oss-120b`**: tienen que argumentar, así que conviene el modelo más capaz.
- **Moderador → `gpt-oss-20b`**: solo devuelve un nombre. Un modelo chico alcanza, es más rápido y
  consume menos cuota gratuita.

### Modelos que "razonan" y `max_tokens`

Los modelos `gpt-oss` **piensan antes de responder** y ese razonamiento también consume tokens.
Con un `max_tokens` bajo (por ejemplo 450) el modelo puede quedarse sin espacio antes de escribir la
respuesta. Por eso el proyecto usa `max_tokens=2000`. La **longitud** de la respuesta se controla
desde el `system_message` ("120-180 palabras"), no desde `max_tokens`.

## Límites de la capa gratuita

Groq limita las **solicitudes por minuto** y los **tokens por minuto/día** por modelo. Los valores
exactos cambian; consultalos en <https://console.groq.com/settings/limits>. Como referencia, al
armar las prácticas `gpt-oss-20b` tenía un límite de **8000 tokens por minuto**.

Cada turno de la clase 01 hace **2 llamadas** (una del moderador + una del agente), así que una
corrida de 5 turnos son ≈ 10 llamadas. Si ves `429 Too Many Requests`, esperá un minuto.
El cliente de `comun/` usa `max_retries=6`: ante un 429, el SDK espera lo que indica Groq y
reintenta solo.

## Incompatibilidades conocidas con AutoGen

| Síntoma | Causa | Parche |
|---|---|---|
| 400 `'required' present but 'properties' is missing` | Herramientas `strict=True` sin parámetros (handoffs) | `HandoffGroq` en [`comun/compat.py`](../comun/compat.py) |
| Sin modelos con visión en la capa gratuita | — | Las prácticas no cubren `MultiModalMessage` |

## Seguridad de la API key

- Guardala solo en `.env` (está en `.gitignore`).
- No la pegues en chats, issues ni capturas de pantalla.
- Si se filtra, revocala en <https://console.groq.com/keys> y creá otra.
