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
| `function_calling` | `True` | ¿Puede usar herramientas (*tools*)? Necesario para el [ejercicio 5](ejercicios.md#ejercicio-5--darle-una-herramienta-al-investigador). |
| `json_output` | `True` | ¿Soporta modo JSON? |
| `structured_output` | `False` | ¿Soporta salida con esquema estricto? |
| `family` | `"unknown"` | Familia del modelo; AutoGen la usa para ajustes específicos. |

Si omitís `model_info`, AutoGen tira error al crear el cliente.

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
GROQ_MODEL=qwen/qwen3.8-27b poetry run python debate_groupchat.py
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
exactos cambian; consultalos en <https://console.groq.com/settings/limits>.

Cada turno de este proyecto hace **2 llamadas** (una del moderador + una del agente), así que una
corrida de 5 turnos son ≈ 10 llamadas. Si ves `429 Too Many Requests`, esperá un minuto.

## Seguridad de la API key

- Guardala solo en `.env` (está en `.gitignore`).
- No la pegues en chats, issues ni capturas de pantalla.
- Si se filtra, revocala en <https://console.groq.com/keys> y creá otra.
