"""Comprueba callbacks de widgets y la alternativa sin widgets, sin editar la fuente."""

import argparse
from pathlib import Path

import nbformat
from nbclient import NotebookClient


CHECKS = '''
if "controls" in globals():
    sliders = {child.description: child for child in controls.children
               if hasattr(child, "description") and hasattr(child, "value")}
    def run_comparison(amplitude, coupling, rate):
        sliders["Factor A"].value = amplitude
        sliders["Factor g"].value = coupling
        sliders["Eventos/s"].value = rate
        controls.update()
        assert controls.result is not None, "El callback debe producir una simulación"
        return controls.result
else:
    def run_comparison(amplitude, coupling, rate):
        return compare_parameters(amplitude, coupling, rate)

zero = run_comparison(1, 0, 0)
np.testing.assert_allclose(zero.voltage_mv, -40, atol=1e-8, rtol=0)
assert zero.stimulus.times_ms == ()
isolated_control = run_comparison(1, 0, 0.3)
assert isolated_control.voltage_mv[0].min() < -40
np.testing.assert_allclose(isolated_control.voltage_mv[1:], -40, atol=1e-8, rtol=0)
high_control = run_comparison(2, 3, 0.6)
assert high_control.parameters.g_oi_ns == 3*p.g_oi_ns
assert all(a == 2*amplitude_pa for a in high_control.stimulus.amplitudes_pa)
assert np.all(np.isfinite(high_control.voltage_mv))
print("Tres comparaciones verificadas: oscuridad, desacoplamiento y valores máximos.")
'''


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--kernel", default="python3")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    source = root / "notebooks/01_baston_tres_compartimentos.ipynb"
    output_dir = root / "outputs"
    output_dir.mkdir(exist_ok=True)
    for variant in ("controles", "sin_widgets"):
        notebook = nbformat.read(source, as_version=4)
        if variant == "sin_widgets":
            for cell in notebook.cells:
                if cell.cell_type == "code" and "import ipywidgets as widgets" in cell.source:
                    cell.source = cell.source.replace(
                        "import ipywidgets as widgets",
                        'raise ImportError("Ausencia de widgets simulada para verificación")',
                    )
        notebook.cells.append(nbformat.v4.new_code_cell(CHECKS))
        NotebookClient(notebook, timeout=180, kernel_name=args.kernel,
                       resources={"metadata": {"path": str(root)}}).execute()
        nbformat.write(notebook, output_dir / f"validacion_{variant}.ipynb")
        print(f"Validación {variant}: completada sin errores")


if __name__ == "__main__":
    main()
