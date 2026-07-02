"""
convertir_docx_a_markdown.py
────────────────────────────
Script STANDALONE para convertir archivos .docx a Markdown (.md).

IMPORTANTE: Este script es completamente independiente del pipeline de
predicción (dashboard_tesis.py / modelo_prediccion.py). No importa ni
modifica ningún módulo del proyecto.

Uso básico:
    python convertir_docx_a_markdown.py
    python convertir_docx_a_markdown.py --entrada ruta/archivo.docx
    python convertir_docx_a_markdown.py --entrada ruta/archivo.docx --salida salida.md

Dependencia requerida (instalar una sola vez):
    pip install markitdown
"""

import sys
import os
import argparse
from pathlib import Path
from datetime import datetime


def verificar_dependencia() -> bool:
    """Verifica que markitdown esté instalado. Si no, muestra instrucciones."""
    try:
        from markitdown import MarkItDown  # noqa: F401
        return True
    except ImportError:
        print("=" * 60)
        print("ERROR: La librería 'markitdown' no está instalada.")
        print()
        print("Instálala con:")
        print("    pip install markitdown")
        print()
        print("Si usas el entorno virtual del proyecto:")
        print("    .venv\\Scripts\\pip install markitdown   (Windows)")
        print("    .venv/bin/pip install markitdown        (Linux/macOS)")
        print("=" * 60)
        return False


def convertir(ruta_entrada: Path, ruta_salida: Path) -> bool:
    """
    Convierte un archivo .docx a Markdown y lo guarda en ruta_salida.

    Parámetros
    ----------
    ruta_entrada : Path
        Ruta al archivo .docx de origen.
    ruta_salida : Path
        Ruta donde se guardará el archivo .md resultante.

    Retorna
    -------
    bool
        True si la conversión fue exitosa, False en caso contrario.
    """
    from markitdown import MarkItDown

    if not ruta_entrada.exists():
        print(f"ERROR: No se encontró el archivo: {ruta_entrada}")
        return False

    if ruta_entrada.suffix.lower() != ".docx":
        print(f"ADVERTENCIA: El archivo '{ruta_entrada.name}' no tiene extensión .docx.")
        print("  Se intentará convertir de todas formas...")

    print(f"Convirtiendo: {ruta_entrada.name}")
    print(f"Destino     : {ruta_salida}")
    print()

    try:
        md = MarkItDown()
        resultado = md.convert(str(ruta_entrada))
        contenido_md = resultado.text_content

        # Encabezado de metadatos al inicio del archivo generado
        encabezado = (
            f"<!-- Generado automáticamente por convertir_docx_a_markdown.py -->\n"
            f"<!-- Origen  : {ruta_entrada.name} -->\n"
            f"<!-- Fecha   : {datetime.now().strftime('%Y-%m-%d %H:%M')} -->\n\n"
        )

        ruta_salida.parent.mkdir(parents=True, exist_ok=True)
        ruta_salida.write_text(encabezado + contenido_md, encoding="utf-8")

        tam_kb = ruta_salida.stat().st_size / 1024
        lineas = contenido_md.count("\n") + 1

        print("✓ Conversión exitosa.")
        print(f"  Líneas generadas : {lineas:,}")
        print(f"  Tamaño del .md   : {tam_kb:.1f} KB")
        print(f"  Archivo guardado : {ruta_salida.resolve()}")
        return True

    except Exception as e:
        print(f"ERROR durante la conversión: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Convierte un archivo .docx a Markdown (.md).",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Ejemplos:\n"
            "  python convertir_docx_a_markdown.py\n"
            "  python convertir_docx_a_markdown.py --entrada AvanceProductoFinal_Zurita.docx\n"
            "  python convertir_docx_a_markdown.py --entrada doc.docx --salida resultado.md\n"
        ),
    )
    parser.add_argument(
        "--entrada", "-i",
        type=str,
        default=None,
        help=(
            "Ruta al archivo .docx a convertir. "
            "Si no se indica, se busca 'AvanceProductoFinal_Zurita.docx' en el "
            "directorio del script y en el escritorio."
        ),
    )
    parser.add_argument(
        "--salida", "-o",
        type=str,
        default=None,
        help=(
            "Ruta del archivo .md resultante. "
            "Por defecto se crea en el mismo directorio que el .docx "
            "con el mismo nombre pero extensión .md."
        ),
    )

    args = parser.parse_args()

    # ── Verificar dependencia ────────────────────────────────────────────────
    if not verificar_dependencia():
        sys.exit(1)

    # ── Resolver ruta de entrada ─────────────────────────────────────────────
    if args.entrada:
        ruta_entrada = Path(args.entrada)
    else:
        # Buscar el .docx de la tesis en ubicaciones conocidas
        candidatos = [
            Path(__file__).parent / "AvanceProductoFinal_Zurita.docx",
            Path(__file__).parent.parent / "AvanceProductoFinal_Zurita.docx",
            Path(os.path.expanduser("~")) / "Desktop" / "Tesis" / "AvanceProductoFinal_Zurita.docx",
        ]
        ruta_entrada = next((p for p in candidatos if p.exists()), None)

        if ruta_entrada is None:
            print("No se encontró 'AvanceProductoFinal_Zurita.docx' automáticamente.")
            print("Especifica la ruta con: --entrada ruta/al/archivo.docx")
            sys.exit(1)

        print(f"Archivo detectado automáticamente: {ruta_entrada}")

    # ── Resolver ruta de salida ──────────────────────────────────────────────
    if args.salida:
        ruta_salida = Path(args.salida)
    else:
        ruta_salida = ruta_entrada.with_suffix(".md")

    # ── Ejecutar conversión ──────────────────────────────────────────────────
    # Forzar UTF-8 en la consola de Windows (evita UnicodeEncodeError con cp1252)
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    print()
    print("=" * 60)
    print("  CONVERSOR DOCX -> MARKDOWN")
    print("=" * 60)
    exito = convertir(ruta_entrada, ruta_salida)
    print("=" * 60)

    sys.exit(0 if exito else 1)


if __name__ == "__main__":
    main()
