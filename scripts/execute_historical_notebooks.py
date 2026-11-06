"""Comprueba copias de los históricos; todas las salidas quedan en outputs/."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys

import nbformat
from nbclient import NotebookClient


def numerical_warning_cells(notebook) -> list[int]:
    """Localiza advertencias numéricas emitidas, sin certificar todas las salidas."""
    return [
        i for i, cell in enumerate(notebook.cells)
        if any(
            output.get("output_type") == "stream"
            and re.search(r"RuntimeWarning:.*(?:overflow|invalid value|divide by zero)",
                          output.get("text", ""))
            for output in cell.get("outputs", [])
        )
    ]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--kernel", default="python3")
    parser.add_argument("--notebook", choices=("hh", "proyecto", "ud", "apuntes"))
    parser.add_argument("--timeout", type=int, default=300, help="Segundos por celda")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    archive = root / "materiales/2026-2"
    output = root / "outputs/consolidacion_2026-2"
    workspace = output / "trabajo"
    manifest = json.loads((archive / "procedencia.json").read_text())
    for entry in manifest["archivos"]:
        relative = Path(entry["destino"])
        if relative.is_absolute() or ".." in relative.parts:
            raise ValueError(f"Ruta fuera del archivo histórico: {relative}")
        destination = workspace / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(archive / relative, destination)

    package = workspace / "PA/proyecto_neurofisiologia_ud_minimo"
    env = os.environ.copy()
    env["PYTHONPATH"] = os.pathsep.join(
        [str(package / "src"), env.get("PYTHONPATH", "")]
    ).rstrip(os.pathsep)
    env["MPLBACKEND"] = "Agg"
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    notebooks = {
        "hh": workspace / "hodgkin_huxley_laboratorio_interactivo.ipynb",
        "proyecto": workspace / "Proyecto/proyecto1.ipynb",
        "ud": package / "notebooks/01_demo_sistema_ud.ipynb",
        "apuntes": workspace / "tarea2/tarea2.ipynb",
    }
    selected = [args.notebook] if args.notebook else list(notebooks)
    if "ud" in selected:
        subprocess.run(
            [sys.executable, str(package / "scripts/construir_cache_umbral.py")],
            cwd=workspace, env=env, check=True,
        )
    if "hh" in selected:
        subprocess.run(
            [sys.executable, str(workspace / "generarHTML_HH.py")],
            cwd=workspace, env=env, check=True,
        )
    results = {}
    for key in selected:
        path = notebooks[key]
        notebook = nbformat.read(path, as_version=4)
        nbformat.validate(notebook)
        result = {"celdas_codigo": sum(c.cell_type == "code" for c in notebook.cells)}
        try:
            if result["celdas_codigo"]:
                NotebookClient(
                    notebook, timeout=args.timeout, kernel_name=args.kernel,
                    resources={"metadata": {"path": str(path.parent)}},
                ).execute(env=env)
                # Los errores dentro de callbacks de widgets pueden almacenarse
                # como salidas sin propagarse como una excepción de ejecución.
                errors = [o for c in notebook.cells for o in c.get("outputs", [])
                          if o.get("output_type") == "error"]
                if errors:
                    raise RuntimeError(f"{len(errors)} salidas de error en callbacks")
                result["estado"] = "ejecutado sin errores"
                warning_cells = numerical_warning_cells(notebook)
                if warning_cells:
                    result["celdas_advertencias_numericas"] = warning_cells
                    result["estado"] = "ejecutado con advertencias numéricas; requiere revisión"
            else:
                result["estado"] = "estructura válida; apuntes sin código"
        except Exception as error:
            result["estado"] = "falló; no reproducido completamente"
            result["error"] = str(error)
        nbformat.write(notebook, output / f"{key}.executed.ipynb")
        results[key] = result
        print(f"{key}: {result['estado']}; {result['celdas_codigo']} celdas de código", flush=True)
    report = output / (f"resultado-{args.notebook}.json" if args.notebook else "resultado.json")
    report.write_text(json.dumps(results, ensure_ascii=False, indent=2) + "\n")
    return int(any("error" in result or "celdas_advertencias_numericas" in result
                   for result in results.values()))


if __name__ == "__main__":
    raise SystemExit(main())
