"""Ejecuta el notebook fuente y guarda evidencia exclusivamente en outputs/."""

import argparse
from pathlib import Path

import nbformat
from nbclient import NotebookClient


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--kernel", default="python3")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    source = root / "notebooks/01_baston_tres_compartimentos.ipynb"
    output = root / "outputs/01_baston_tres_compartimentos.executed.ipynb"
    output.parent.mkdir(parents=True, exist_ok=True)
    notebook = nbformat.read(source, as_version=4)
    nbformat.validate(notebook)
    if any(c.get("outputs") or c.get("execution_count") is not None
           for c in notebook.cells if c.cell_type == "code"):
        raise ValueError("El notebook fuente debe estar limpio, sin salidas")
    client = NotebookClient(notebook, timeout=180, kernel_name=args.kernel,
                            resources={"metadata": {"path": str(root)}})
    client.execute()
    nbformat.write(notebook, output)
    code_cells = sum(c.cell_type == "code" for c in notebook.cells)
    print(f"Notebook ejecutado sin errores: {code_cells} celdas de código; {output}")


if __name__ == "__main__":
    main()
