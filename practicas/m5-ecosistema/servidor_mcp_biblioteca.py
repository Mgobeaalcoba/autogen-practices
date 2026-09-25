"""Servidor MCP de ejemplo para la práctica 18.

Un servidor MCP (Model Context Protocol) expone herramientas con un protocolo ESTÁNDAR: cualquier
cliente compatible (AutoGen, Claude Desktop, IDEs...) puede usarlas sin saber cómo están hechas.

Este servidor no se corre a mano: lo lanza la práctica 18 como subproceso y se comunica con él
por stdin/stdout.
"""

from mcp.server.fastmcp import FastMCP

servidor = FastMCP("biblioteca")

LIBROS = {
    "rayuela": {"autor": "Julio Cortázar", "anio": 1963, "disponible": True},
    "ficciones": {"autor": "Jorge Luis Borges", "anio": 1944, "disponible": False},
    "el tunel": {"autor": "Ernesto Sabato", "anio": 1948, "disponible": True},
    "martin fierro": {"autor": "José Hernández", "anio": 1872, "disponible": True},
}


@servidor.tool()
def buscar_libro(titulo: str) -> str:
    """Busca un libro por título y devuelve autor, año y si está disponible para préstamo."""
    libro = LIBROS.get(titulo.strip().lower())
    if libro is None:
        return f"No encontré '{titulo}'. Catálogo: {', '.join(LIBROS)}"
    estado = "disponible" if libro["disponible"] else "prestado"
    return f"{titulo.title()} — {libro['autor']} ({libro['anio']}), {estado}."


@servidor.tool()
def libros_de_autor(autor: str) -> str:
    """Lista los libros del catálogo cuyo autor contiene el texto indicado."""
    encontrados = [t.title() for t, d in LIBROS.items() if autor.lower() in d["autor"].lower()]
    return ", ".join(encontrados) or f"No hay libros de '{autor}' en el catálogo."


if __name__ == "__main__":
    servidor.run()  # por defecto usa transporte stdio
