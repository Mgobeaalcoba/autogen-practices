"""Práctica 18 — Herramientas externas vía MCP (Model Context Protocol)

🎯 Objetivo: conectar un agente a herramientas que viven en OTRO proceso, a través de un
protocolo estándar, en vez de definirlas como funciones de Python locales.

📚 Conceptos:
- MCP: protocolo abierto para exponer herramientas y datos a los LLMs. Hay cientos de
  servidores listos (archivos, GitHub, bases de datos, navegador...).
- `McpWorkbench`: conecta a un servidor MCP y le ofrece sus herramientas al agente.
  Se pasa como `workbench=` (en vez de `tools=`).
- Transportes: `StdioServerParams` (subproceso local), `SseServerParams` y
  `StreamableHttpServerParams` (servidores remotos).

📦 Requiere una dependencia extra (no viene con la instalación base):
       poetry add "autogen-ext[mcp]"

▶️ Correr:  poetry run python practicas/m5-ecosistema/18_mcp.py
"""

import asyncio
import sys
from pathlib import Path

from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.ui import Console

from comun.modelos import cliente_groq

try:
    from autogen_ext.tools.mcp import McpWorkbench, StdioServerParams
except ImportError:
    sys.exit('Falta la dependencia de MCP. Instalala con:  poetry add "autogen-ext[mcp]"')

SERVIDOR = Path(__file__).with_name("servidor_mcp_biblioteca.py")


async def main() -> None:
    cliente = cliente_groq()

    # 1️⃣ Cómo lanzar el servidor: el mismo Python del proyecto ejecutando el archivo del servidor.
    parametros = StdioServerParams(
        command=sys.executable,
        args=[str(SERVIDOR)],
        read_timeout_seconds=30,
    )

    # 2️⃣ `async with` arranca el servidor y lo apaga al salir.
    async with McpWorkbench(server_params=parametros) as workbench:
        herramientas = await workbench.list_tools()
        print("🧰 Herramientas que expone el servidor MCP:")
        for herramienta in herramientas:
            print(f"   • {herramienta['name']}: {herramienta.get('description', '')}")

        bibliotecario = AssistantAgent(
            "bibliotecario",
            cliente,
            workbench=workbench,  # 👈 en vez de tools=[...]
            system_message="Sos bibliotecario. Usá tus herramientas para responder sobre el catálogo.",
            reflect_on_tool_use=True,
            max_tool_iterations=3,
        )
        await Console(bibliotecario.run_stream(task="¿Está disponible Ficciones? Si no, recomendame otro libro disponible del catálogo."))

    await cliente.close()


# 🧪 EJERCICIO 1: agregá al servidor una herramienta `prestar_libro(titulo)` que cambie la
#    disponibilidad. ¿Tuviste que tocar este archivo para que el agente la use?
# 🧪 EJERCICIO 2: conectá un servidor MCP público, por ejemplo el de fetch:
#    StdioServerParams(command="uvx", args=["mcp-server-fetch"]) y pedile que resuma una página.
# 🧪 EJERCICIO 3: usá `tool_overrides` de McpWorkbench para renombrar una herramienta al español.

if __name__ == "__main__":
    asyncio.run(main())
