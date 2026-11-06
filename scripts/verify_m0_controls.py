"""Verifica la entrada pareada y nueve controles M0 con y sin widgets."""
from __future__ import annotations

import argparse

from execute_m0_notebook import execute_m0

CHECKS = r'''
canonical = simulate_m0(times, M0Parameters(), pulse_protocol())
if widgets is not None:
    def run_light(value):
        slider = next(c for c in light_controls.children if getattr(c, 'description', '') == '|ΔL|')
        slider.value = value
        light_controls.update()
        assert light_controls.result is not None
        return light_controls.result
    def run_parameter(name, value):
        fields = {c.description:c for c in parameter_controls.children if hasattr(c,'value')}
        fields['Parámetro'].value = name
        fields['Factor'].value = value
        parameter_controls.update()
        assert parameter_controls.result is not None
        return parameter_controls.result
else:
    run_light = compare_light
    run_parameter = compare_parameter
for contrast in (0, .25, 1):
    plus, minus = run_light(contrast)
    assert np.all(plus.illumination >= 0) and np.all(minus.illumination >= 0)
    assert plus.illumination[150] == 1+contrast
    assert minus.illumination[150] == 1-contrast
    assert np.all(np.isfinite(plus.voltage_mv)) and np.all(np.isfinite(minus.voltage_mv))
    if contrast:
        assert plus.delta_voltage_mv[1,250] > 0 > plus.delta_voltage_mv[2,250]
        assert minus.delta_voltage_mv[1,250] < 0 < minus.delta_voltage_mv[2,250]
    else:
        np.testing.assert_allclose(plus.delta_voltage_mv, 0, atol=1e-10)
for name in PARAMETER_LABELS:
    reference, modified = run_parameter(name, 2)
    np.testing.assert_array_equal(reference.voltage_mv, canonical.voltage_mv)
    np.testing.assert_array_equal(reference.illumination, canonical.illumination)
    np.testing.assert_array_equal(modified.illumination, reference.illumination)
    assert modified.parameters != reference.parameters
    assert not np.allclose(modified.voltage_mv, reference.voltage_mv)
    assert np.all(np.isfinite(modified.voltage_mv))
    if name.startswith('C_'):
        np.testing.assert_array_equal(modified.equilibrium_mv, reference.equilibrium_mv)
    if name == 'C_ON':
        assert modified.parameters.capacitance_pf == (20,60,30)
        np.testing.assert_allclose(modified.voltage_mv[[0,2]], reference.voltage_mv[[0,2]], atol=2e-7)
reference, same = run_parameter('C_ON', 1)
np.testing.assert_array_equal(reference.voltage_mv, same.voltage_mv)
print('Entrada pareada, nueve parámetros, reposos y referencia fija comprobados.')
'''


def main() -> None:
    """Repite el notebook completo y ejercita ambos caminos de interacción."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--kernel", default="python3")
    args = parser.parse_args()
    for without_widgets in (False, True):
        execute_m0(args.kernel, without_widgets=without_widgets, checks=CHECKS)


if __name__ == "__main__":
    main()
