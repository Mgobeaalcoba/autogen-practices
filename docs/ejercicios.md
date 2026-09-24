# Ejercicios guiados

Prácticas de dificultad creciente para modificar el proyecto. Cada una indica **qué tocar**, **qué
deberías observar** y una **pista**. Antes de empezar, corré el proyecto una vez tal como está
para tener una línea de base.

> 💡 Trabajá sobre una copia (`cp debate_groupchat.py mi_debate.py`) para poder comparar.

---

## Ejercicio 1 — Cambiar el tema

**Dificultad:** ⭐ Básico

**Objetivo:** entender que el tema es simplemente el primer mensaje del chat.

1. Buscá una noticia de hoy.
2. Reemplazá `TOPIC` con un resumen de 3-4 líneas y una **pregunta de debate** clara.
3. Corré y compará la transcripción.

**Observá:** ¿el investigador usa el contexto que le diste o lo ignora y habla de lo que
"recuerda"?

**Pista:** una pregunta cerrada ("¿X es eficaz o no?") genera mejores debates que una abierta
("hablen de X").

---

## Ejercicio 2 — Forzar una decisión no alternada

**Dificultad:** ⭐ Básico

**Objetivo:** comprobar que el moderador realmente decide, y no sigue un orden fijo.

Agregá esta regla al principio de la lista en `SELECTOR_PROMPT`:

```
- Si el crítico concedió que un punto es sólido, el crítico sigue hablando para atacar el siguiente punto débil.
```

**Observá:** buscá en la transcripción dos `🎙️ Moderador` seguidos que elijan al **mismo** agente.

**Para pensar:** ¿qué pasa si ponés `allow_repeated_speaker=False`? (AutoGen le pide al moderador
que elija de nuevo si repite).

---

## Ejercicio 3 — Sumar un tercer participante

**Dificultad:** ⭐⭐ Intermedio

**Objetivo:** ver cómo el moderador reparte turnos entre más de dos roles.

Creá un agente `sintetizador` con:

- `description`: "Resume en qué acuerdan y en qué no el investigador y el crítico. Solo interviene
  cuando el debate se estancó o repite argumentos."
- `system_message`: que haga un resumen neutral de 80 palabras.

Agregalo a `participants` y subí `MAX_TURNS` a 7.

**Observá:** ¿cuándo lo elige el moderador? ¿Respeta la condición de "solo cuando se estancó"?

**Pista:** si lo elige demasiado seguido, el problema está en su `description`, no en su
`system_message` (repasá [conceptos.md §4](conceptos.md#por-qué-importa-el-description-de-cada-agente)).

---

## Ejercicio 4 — Terminar cuando haya consenso

**Dificultad:** ⭐⭐ Intermedio

**Objetivo:** usar condiciones de terminación en lugar de un número fijo de turnos.

1. Pedile al crítico en su `system_message` que escriba `CONSENSO` si ya no tiene objeciones
   relevantes.
2. Importá `TextMentionTermination` y `MaxMessageTermination` de `autogen_agentchat.conditions`.
3. Pasale al equipo:

   ```python
   termination_condition=TextMentionTermination("CONSENSO") | MaxMessageTermination(12)
   ```

**Observá:** el `stop_reason` final. ¿Se llegó a un consenso o cortó por límite?

**Para pensar:** ¿por qué conviene **siempre** combinarla con un límite máximo?

---

## Ejercicio 5 — Darle una herramienta al investigador

**Dificultad:** ⭐⭐⭐ Avanzado

**Objetivo:** reducir las alucinaciones dándole al investigador datos reales.

Los agentes de AutoGen pueden usar **herramientas** (funciones Python). Idea:

```python
async def buscar_dato(consulta: str) -> str:
    """Busca información actual sobre la consulta y devuelve un resumen con la fuente."""
    ...  # llamá a una API de búsqueda, Wikipedia, datos del Banco Mundial, etc.

investigador = AssistantAgent(
    ...,
    tools=[buscar_dato],
    reflect_on_tool_use=True,  # que redacte una respuesta usando el resultado
)
```

Sugerencias de fuentes gratuitas: la API de Wikipedia o la
[API del Banco Mundial](https://datahelpdesk.worldbank.org/knowledgebase/articles/889392) (sin key).

**Observá:** compará las cifras con la corrida sin herramientas. ¿El crítico cambia de actitud
cuando ve fuentes verificables?

**Pista:** en el stream aparecen nuevos eventos (`ToolCallRequestEvent`,
`ToolCallExecutionEvent`). Agregalos a la transcripción para ver qué buscó el agente.

---

## Ejercicio 6 — Reemplazar el LLM del moderador por reglas

**Dificultad:** ⭐⭐⭐ Avanzado

**Objetivo:** entender el trade-off entre selección por LLM y selección por código.

`SelectorGroupChat` acepta `selector_func`: una función que recibe el historial y devuelve el
nombre del próximo orador (o `None` para que decida el LLM).

```python
def elegir(messages):
    ultimo = messages[-1]
    if ultimo.source == "user":
        return "investigador"
    return None  # en cualquier otro caso, que decida el LLM
```

**Observá:** ¿cuántas llamadas a Groq te ahorrás? ¿Qué se pierde?

**Para pensar:** ¿en qué casos preferirías reglas fijas y en cuáles un LLM?

---

## Autoevaluación

Deberías poder responder sin mirar el código:

1. ¿Qué campo de un agente lee el moderador para decidir, y cuál no?
2. ¿Qué diferencia hay entre `SelectorGroupChat` y `RoundRobinGroupChat`?
3. ¿Por qué el proyecto necesita `model_info` para usar Groq?
4. ¿Por qué el crítico no detectó que el dato del PIB era falso?
5. ¿Qué evento te permite ver las decisiones del moderador y qué parámetro lo habilita?

<details>
<summary>Respuestas</summary>

1. Lee `description`; no lee `system_message`.
2. El primero elige con un LLM según el contexto; el segundo sigue un orden fijo.
3. Porque AutoGen solo conoce las capacidades de los modelos de OpenAI; para otros hay que
   declararlas.
4. Porque usa el mismo modelo, con el mismo conocimiento (y errores), y no tiene acceso a fuentes
   externas para verificar.
5. `SelectSpeakerEvent`, habilitado con `emit_team_events=True`.

</details>
