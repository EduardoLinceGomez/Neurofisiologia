"""Comprueba callbacks de widgets y la alternativa sin widgets, sin editar la fuente."""

import argparse
from pathlib import Path

import nbformat
from nbclient import NotebookClient


CHECKS_01 = '''
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
baseline_fixed = last_comparison[0].voltage_mv.copy()
only_amplitude = run_comparison(2, 1, .3)
reference_a, modified_a = last_comparison
np.testing.assert_array_equal(reference_a.voltage_mv, baseline_fixed)
assert reference_a.stimulus.times_ms == modified_a.stimulus.times_ms
assert not np.allclose(reference_a.voltage_mv, modified_a.voltage_mv)
only_rate = run_comparison(1, 1, .6)
reference_r, modified_r = last_comparison
np.testing.assert_array_equal(reference_r.voltage_mv, baseline_fixed)
assert reference_r.stimulus.times_ms != modified_r.stimulus.times_ms
assert not np.allclose(reference_r.photocurrent_pa, modified_r.photocurrent_pa)
print("Cinco comparaciones verificadas; amplitud/tasa no alteran la referencia fija.")
'''

CHECKS_02 = r'''
if "input_controls" in globals():
    def run_input(amplitude, rate, peak=2200, seed=2026):
        fields = {c.description: c for c in input_controls.children if hasattr(c, "value")}
        for label, value in (("A (pA)", amplitude), ("Eventos/s", rate), ("Pico (ms)", peak), ("Semilla", seed)):
            fields[label].value = value
        input_controls.update()
        return input_controls.result
    def run_membrane(**changes):
        fields = {c.description: c for c in membrane_controls.children if hasattr(c, "value")}
        for label, value in changes.items():
            fields[label].value = value
        membrane_controls.update()
        return membrane_controls.result
else:
    def run_input(amplitude, rate, peak=2200, seed=2026):
        return input_experiment(amplitude, peak, rate, seed)
    def run_membrane(**changes):
        mapping = {"CO (pF)": "capacitance_o_pf", "gOI (nS)": "g_oi_ns", "gIT (nS)": "g_it_ns",
                   "gLO (nS)": "leak_o_ns", "CI (pF)": "capacitance_i_pf", "CT (pF)": "capacitance_t_pf",
                   "gLI (nS)": "leak_i_ns", "gLT (nS)": "leak_t_ns", "EO (mV)": "reversal_o_mv",
                   "EI (mV)": "reversal_i_mv", "ET (mV)": "reversal_t_mv", "Vista": "view"}
        return membrane_experiment(**{mapping[label]: value for label,value in changes.items()})

changed_a = run_input(2.4, .3)
reference, modified = input_comparison
baseline_values = reference.voltage_mv.copy()
assert reference.stimulus.times_ms == modified.stimulus.times_ms
assert not np.allclose(reference.voltage_mv, changed_a.voltage_mv)
changed_rate = run_input(1.2, .6)
np.testing.assert_array_equal(input_comparison[0].voltage_mv, baseline_values)
assert input_comparison[0].stimulus.times_ms != changed_rate.stimulus.times_ms
changed_peak_seed = run_input(1.2, .3, 1000, 7)
assert changed_peak_seed.stimulus.t_peak_ms == 1000
np.testing.assert_array_equal(input_comparison[0].voltage_mv, baseline_values)
changed_c = run_membrane(**{"CO (pF)": 40})
assert changed_c.parameters.capacitance_pf[0] == 40
assert not np.allclose(membrane_comparison[0].voltage_mv, changed_c.voltage_mv)
no_it = run_membrane(**{"gIT (nS)": 0})
assert response_metrics(no_it)["delay_t_ms"] is None
for label, attr, index, value in (("CI (pF)","capacitance_pf",1,30), ("CT (pF)","capacitance_pf",2,10),
    ("gLO (nS)","leak_ns",0,.08), ("gLI (nS)","leak_ns",1,.15), ("gLT (nS)","leak_ns",2,.08),
    ("EO (mV)","reversal_mv",0,-45), ("EI (mV)","reversal_mv",1,-42), ("ET (mV)","reversal_mv",2,-38),
    ("gOI (nS)","g_oi_ns",None,.2)):
    result = run_membrane(**{label: value})
    actual = getattr(result.parameters,attr)
    assert (actual if index is None else actual[index]) == value
    np.testing.assert_array_equal(membrane_comparison[0].voltage_mv, baseline_values)
run_membrane(**{"Vista": "V"})
run_membrane(**{"Vista": "delta"})
zero_currents = inspect_time(0)
assert np.max(abs(zero_currents["net_current_pa"])) < 1e-12
peak_currents = inspect_time(3440)
assert float(peak_currents["axial_current_oi_pa"]) < 0
if "reset_button" in globals():
    reset_button.click()
    assert membrane_controls.result.parameters == RodParameters()
    np.testing.assert_array_equal(input_comparison[0].voltage_mv, input_comparison[1].voltage_mv)
    fields = {c.description:c for c in time_controls.children if hasattr(c,"value")}
    fields["Tiempo (ms)"].value = 0
    time_controls.update()
    assert np.max(abs(time_controls.result["net_current_pa"])) < 1e-12
    fields["Tiempo (ms)"].value = 3440
    time_controls.update()
print("Entrada, membrana, parámetros avanzados, tiempo y reinicio verificados.")
'''


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--kernel", default="python3")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    source_names = ("01_baston_tres_compartimentos", "02_estudio_guiado_baston")
    output_dir = root / "outputs"
    output_dir.mkdir(exist_ok=True)
    for name in source_names:
        for variant in ("controles", "sin_widgets"):
            notebook = nbformat.read(root / f"notebooks/{name}.ipynb", as_version=4)
            if variant == "sin_widgets":
                for cell in notebook.cells:
                    if cell.cell_type == "code" and "import ipywidgets as widgets" in cell.source:
                        cell.source = cell.source.replace(
                            "import ipywidgets as widgets",
                            'raise ImportError("Ausencia de widgets simulada para verificación")',
                        )
            notebook.cells.append(nbformat.v4.new_code_cell(CHECKS_01 if name.startswith("01") else CHECKS_02))
            NotebookClient(notebook, timeout=180, kernel_name=args.kernel,
                           resources={"metadata": {"path": str(root)}}).execute()
            nbformat.write(notebook, output_dir / f"validacion_{name}_{variant}.ipynb")
            print(f"Validación {name} / {variant}: completada sin errores")


if __name__ == "__main__":
    main()
