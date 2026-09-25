"""Práctica 17 — Ejecución de código

🎯 Objetivo: que un agente ESCRIBA y EJECUTE código Python para resolver una tarea con datos
reales en vez de "imaginar" el resultado.

📚 Conceptos:
- `CodeExecutorAgent`: con `model_client`, genera código; con `code_executor`, lo ejecuta.
  Si hay error, lo ve y reintenta (`max_retries_on_error`).
- Ejecutores (`autogen_ext.code_executors`):
    · `LocalCommandLineCodeExecutor`: corre en TU máquina. Simple, pero riesgoso.
    · `DockerCommandLineCodeExecutor`: corre en un contenedor aislado (recomendado).
    · `JupyterCodeExecutor`: mantiene estado entre ejecuciones, como un notebook.
- `approval_func`: se llama ANTES de ejecutar. Permite que un humano (o una regla) apruebe.
- Eventos nuevos: `CodeGenerationEvent` y `CodeExecutionEvent`.

⚠️ SEGURIDAD: el código lo escribe un LLM y se ejecuta con tus permisos. Por eso esta práctica
   te pide aprobación antes de cada ejecución. Leé el código antes de aprobar. Para uso real,
   usá Docker.

▶️ Correr:  poetry run python practicas/m5-ecosistema/17_ejecucion_codigo.py
   Cuando te muestre el código, respondé "s" para ejecutarlo o "n" para rechazarlo.
"""

import asyncio

from autogen_agentchat.agents import ApprovalRequest, ApprovalResponse, CodeExecutorAgent
from autogen_agentchat.ui import Console
from autogen_ext.code_executors.local import LocalCommandLineCodeExecutor

from comun.modelos import cliente_groq
from comun.rutas import ruta_salida


# 1️⃣ Aprobación humana: se ejecuta solo si respondés "s".
def pedir_aprobacion(pedido: ApprovalRequest) -> ApprovalResponse:
    print("\n" + "═" * 60 + "\n🔍 Código a ejecutar:\n" + pedido.code + "\n" + "═" * 60)
    respuesta = input("¿Ejecutar? (s/n): ").strip().lower()
    if respuesta == "s":
        return ApprovalResponse(approved=True, reason="Aprobado por el usuario")
    return ApprovalResponse(approved=False, reason="El usuario rechazó la ejecución")


async def main() -> None:
    cliente = cliente_groq()

    # 2️⃣ El ejecutor corre los scripts dentro de salidas/m5/codigo (archivos que genere, incluidos).
    carpeta = ruta_salida("m5/codigo/.keep").parent
    ejecutor = LocalCommandLineCodeExecutor(work_dir=carpeta, timeout=30)

    programador = CodeExecutorAgent(
        "programador",
        code_executor=ejecutor,
        model_client=cliente,  # sin model_client, solo ejecuta código que le pasen otros agentes
        approval_func=pedir_aprobacion,
        max_retries_on_error=2,
        system_message=(
            "Resolvés tareas escribiendo UN bloque de código ```python``` que use solo la librería "
            "estándar. Después de ver el resultado de la ejecución, explicalo en 2 oraciones."
        ),
    )

    await Console(
        programador.run_stream(
            task=(
                "Calculá cuántos días hábiles (lunes a viernes) hay entre hoy y el 31 de diciembre "
                "de este año, y guardá el resultado en un archivo resultado.txt."
            )
        )
    )
    print(f"\n📂 Mirá los archivos generados en: {carpeta}")

    await cliente.close()


# 🧪 EJERCICIO 1: respondé "n" a la aprobación. ¿Qué hace el agente con el rechazo?
# 🧪 EJERCICIO 2: pedile una tarea que falle (ej. leer un archivo que no existe) y mirá cómo
#    reintenta con `max_retries_on_error`.
# 🧪 EJERCICIO 3 (Docker): reemplazá el ejecutor por
#    `DockerCommandLineCodeExecutor(work_dir=carpeta)` (requiere `poetry add "autogen-ext[docker]"`
#    y Docker corriendo) y usalo como `async with ejecutor:`.

if __name__ == "__main__":
    asyncio.run(main())
