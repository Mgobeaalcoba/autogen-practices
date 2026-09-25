"""Verificación rápida del repo, sin gastar cuota de Groq.

1. Compila todos los .py (detecta errores de sintaxis).
2. Corre las prácticas que funcionan sin LLM (replay y core).

▶️ Correr:  poetry run python -m comun.verificar
"""

import os
import py_compile
import subprocess
import sys

from comun.rutas import RAIZ

CARPETAS = ["comun", "clase-01-debate", "practicas"]
# Prácticas que no llaman a Groq: se pueden correr en CI o sin API key.
SIN_LLM = [
    "practicas/m5-ecosistema/19_cache_y_replay.py",
    "practicas/m6-core/22_mensajes_directos.py",
    "practicas/m6-core/23_publicar_suscribir.py",
]


def main() -> int:
    errores = 0

    print("1️⃣ Compilando...")
    archivos = sorted(p for carpeta in CARPETAS for p in (RAIZ / carpeta).rglob("*.py"))
    for archivo in archivos:
        try:
            py_compile.compile(str(archivo), doraise=True)
        except py_compile.PyCompileError as error:
            errores += 1
            print(f"   ❌ {archivo.relative_to(RAIZ)}: {error.msg}")
    print(f"   {len(archivos)} archivos revisados.")

    print("2️⃣ Corriendo prácticas sin LLM...")
    entorno = {**os.environ, "GROQ_API_KEY": ""}  # garantiza que no se llame a Groq
    for practica in SIN_LLM:
        try:
            resultado = subprocess.run(
                [sys.executable, practica], cwd=RAIZ, env=entorno, capture_output=True, text=True, timeout=60
            )
            ok = resultado.returncode == 0
            detalle = "" if ok else f"\n{resultado.stderr[-800:]}"
        except subprocess.TimeoutExpired:
            ok, detalle = False, " (timeout: ¿quedó colgado el runtime?)"
        errores += not ok
        print(f"   {'✅' if ok else '❌'} {practica}{detalle}")

    print("\n" + ("✅ Todo OK" if errores == 0 else f"❌ {errores} problema(s)"))
    return 1 if errores else 0


if __name__ == "__main__":
    sys.exit(main())
