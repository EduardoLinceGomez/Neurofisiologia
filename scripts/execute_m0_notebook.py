"""Ejecuta el notebook M0 limpio, conservando toda evidencia bajo outputs/."""
from __future__ import annotations

import argparse
from pathlib import Path

import nbformat
from nbclient import NotebookClient


def execute_m0(kernel: str, *, without_widgets: bool = False, checks: str = "") -> Path:
    """Ejecuta una copia en memoria; opcionalmente fuerza ausencia de ipywidgets.

    Revisa también errores capturados en estados de widgets, no solo excepciones
    que se propaguen al cliente. Las sustituciones nunca se escriben a la fuente.
    """
    root = Path(__file__).resolve().parents[1]
    notebook = nbformat.read(root/"notebooks/03_cono_bipolares_on_off.ipynb", as_version=4)
    nbformat.validate(notebook)
    for cell in notebook.cells:
        if cell.cell_type == "code":
            if cell.outputs or cell.execution_count is not None:
                raise ValueError("El notebook M0 fuente debe estar sin salidas ni contadores")
            if without_widgets:
                cell.source = cell.source.replace("import ipywidgets as widgets",
                    'raise ImportError("Ausencia de widgets forzada para la comprobación")')
    if checks:
        notebook.cells.append(nbformat.v4.new_code_cell(checks))
    folder = root/"outputs/retina_on_off"
    folder.mkdir(parents=True, exist_ok=True)
    suffix = "sin_widgets" if without_widgets else "con_widgets"
    output = folder/f"03_m0_{'controles_' if checks else ''}{suffix}.executed.ipynb"
    NotebookClient(notebook, timeout=240, kernel_name=kernel,
                   resources={"metadata": {"path": str(root)}}).execute()
    nbformat.write(notebook, output)

    def has_error(value: object) -> bool:
        if isinstance(value, dict):
            return value.get("output_type") == "error" or any(has_error(v) for v in value.values())
        if isinstance(value, list):
            return any(has_error(v) for v in value)
        return False

    if has_error(notebook):
        raise RuntimeError("El notebook o un callback guardó una salida de error")
    images = sum(
        "image/png" in output.get("data", {})
        for cell in notebook.cells if cell.cell_type == "code"
        for output in cell.outputs
    )
    if images < 9:
        raise RuntimeError("Faltan figuras embebidas: no basta con exportarlas a disco")
    print(f"M0 {suffix}: {sum(c.cell_type == 'code' for c in notebook.cells)} celdas de código, sin errores; {output}", flush=True)
    return output


def main() -> None:
    """Ejecuta la variante habitual; --without-widgets comprueba el fallback."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--kernel", default="python3")
    parser.add_argument("--without-widgets", action="store_true")
    args = parser.parse_args()
    execute_m0(args.kernel, without_widgets=args.without_widgets)


if __name__ == "__main__":
    main()
