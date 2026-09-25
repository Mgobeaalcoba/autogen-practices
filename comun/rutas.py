"""Rutas compartidas: dónde guardan sus archivos las prácticas."""

from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
# Todo lo que generan las prácticas (estado, código ejecutado, configs exportadas) va acá.
# La carpeta está en .gitignore: podés borrarla cuando quieras.
SALIDAS = RAIZ / "salidas"


def ruta_salida(nombre: str) -> Path:
    """Devuelve `salidas/<nombre>`, creando las carpetas que falten."""
    ruta = SALIDAS / nombre
    ruta.parent.mkdir(parents=True, exist_ok=True)
    return ruta
