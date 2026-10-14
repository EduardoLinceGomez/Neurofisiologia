"""Ejecuta el notebook fuente y guarda evidencia exclusivamente en outputs/."""

import argparse
from pathlib import Path

import nbformat
from nbclient import NotebookClient


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--kernel", default="python3")
    parser.add_argument("--notebook", choices=("01", "02"), help="Por defecto ejecuta ambos")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    names = {"01": "01_baston_tres_compartimentos", "02": "02_estudio_guiado_baston"}
    selected = [names[args.notebook]] if args.notebook else names.values()
    for name in selected:
        source = root / f"notebooks/{name}.ipynb"
        output = root / f"outputs/{name}.executed.ipynb"
        output.parent.mkdir(parents=True, exist_ok=True)
        notebook = nbformat.read(source, as_version=4)
        nbformat.validate(notebook)
        if any(c.get("outputs") or c.get("execution_count") is not None
               for c in notebook.cells if c.cell_type == "code"):
            raise ValueError("El notebook fuente debe estar limpio, sin salidas")
        NotebookClient(notebook, timeout=180, kernel_name=args.kernel,
                       resources={"metadata": {"path": str(root)}}).execute()
        nbformat.write(notebook, output)
        code_cells = sum(c.cell_type == "code" for c in notebook.cells)
        print(f"Notebook ejecutado sin errores: {code_cells} celdas de código; {output}")


if __name__ == "__main__":
    main()
