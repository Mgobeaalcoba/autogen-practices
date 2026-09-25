"""Práctica 20 — Componentes declarativos: equipos como JSON

🎯 Objetivo: exportar un equipo completo (agentes, modelos, condiciones) a un archivo JSON y
volver a construirlo desde ese archivo, sin código.

📚 Conceptos:
- Casi todo en AutoGen es un "componente": agentes, equipos, clientes de modelo, condiciones,
  herramientas, memoria. Todos tienen:
    · `obj.dump_component()` → `ComponentModel` (provider + config).
    · `Clase.load_component(modelo)` → reconstruye el objeto.
- Es la base de AutoGen Studio (la UI visual): los equipos que armás ahí son estos JSON.
- 🔐 Al serializar a JSON, las API keys se ENMASCARAN ("**********"). Es a propósito: el
  archivo se puede compartir. Al cargar, hay que volver a inyectar la key desde el entorno.

▶️ Correr:  poetry run python practicas/m5-ecosistema/20_componentes_declarativos.py
"""

import asyncio
import json
import os
from typing import Any

from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.conditions import MaxMessageTermination, TextMentionTermination
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.ui import Console
from autogen_core import ComponentModel

from comun.modelos import cliente_liviano
from comun.rutas import ruta_salida

ARCHIVO = ruta_salida("m5/equipo_chistes.json")


def inyectar_api_key(config: Any) -> None:
    """Recorre el JSON y reemplaza las keys enmascaradas por la real (del entorno)."""
    if isinstance(config, dict):
        if config.get("api_key") == "**********":
            config["api_key"] = os.environ["GROQ_API_KEY"]
        for valor in config.values():
            inyectar_api_key(valor)
    elif isinstance(config, list):
        for valor in config:
            inyectar_api_key(valor)


async def main() -> None:
    # 1️⃣ Armar un equipo "normal" en código.
    cliente = cliente_liviano()
    humorista = AssistantAgent("humorista", cliente, system_message="Contás un chiste corto de programadores.")
    critico = AssistantAgent(
        "critico_de_humor", cliente,
        system_message="Puntuás el chiste del 1 al 10 en una línea y terminás con LISTO.",
    )
    equipo = RoundRobinGroupChat(
        [humorista, critico],
        termination_condition=TextMentionTermination("LISTO") | MaxMessageTermination(4),
    )

    # 2️⃣ Exportarlo a JSON.
    ARCHIVO.write_text(equipo.dump_component().model_dump_json(indent=2))
    print(f"💾 Equipo exportado a {ARCHIVO}")
    print("🔐 ¿La key real quedó en el archivo?", os.environ["GROQ_API_KEY"] in ARCHIVO.read_text())

    # 3️⃣ Cargarlo desde el JSON (podría ser otro programa, o un archivo editado a mano).
    config = json.loads(ARCHIVO.read_text())
    print(f"🧩 Provider: {config['provider']} | participantes: "
          f"{[p['config']['name'] for p in config['config']['participants']]}")
    inyectar_api_key(config)
    equipo_cargado = RoundRobinGroupChat.load_component(ComponentModel(**config))

    await Console(equipo_cargado.run_stream(task="Contá un chiste."))
    await cliente.close()


# 🧪 EJERCICIO 1: abrí el JSON, cambiá el `system_message` del humorista a mano (sin tocar
#    Python) y cargalo de nuevo. Comentá los pasos 1 y 2 para no sobrescribirlo.
# 🧪 EJERCICIO 2: exportá solo la condición de terminación. ¿Cómo se ve un `OrTerminationCondition`?
# 🧪 EJERCICIO 3: instalá AutoGen Studio (`pip install autogenstudio` en un entorno aparte),
#    corré `autogenstudio ui` e importá este JSON desde la interfaz.

if __name__ == "__main__":
    asyncio.run(main())
