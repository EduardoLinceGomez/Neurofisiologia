"""Regresiones para comparaciones auténticas, independientes de los controles."""

import numpy as np
import pytest
from dataclasses import replace

from neurofisiologia import PhotonEvents, RodParameters, SimulationResult, simulate
from neurofisiologia.analysis import (
    modal_times_ms, poisson_ensemble, rc_step_response, response_metrics,
    sensitivity_map, variation_of_constants, voltage_deviation,
)

from neurofisiologia.analysis import compare_with_reference


TIME_MS = np.linspace(0, 16000, 401)


def test_only_amplitude_changes_modified_response_not_reference():
    original, unchanged = compare_with_reference(TIME_MS)
    reference, modified = compare_with_reference(TIME_MS, amplitude_pa=2.4)
    np.testing.assert_array_equal(reference.voltage_mv, original.voltage_mv)
    assert reference.stimulus == original.stimulus
    assert modified.stimulus.times_ms == reference.stimulus.times_ms
    assert modified.parameters == reference.parameters
    assert not np.allclose(reference.photocurrent_pa, modified.photocurrent_pa)
    np.testing.assert_allclose(modified.voltage_mv + 40,
                               2*(reference.voltage_mv + 40), atol=2e-6, rtol=0)
    np.testing.assert_array_equal(original.voltage_mv, unchanged.voltage_mv)


def test_only_rate_changes_input_and_response_not_reference():
    original, _ = compare_with_reference(TIME_MS)
    reference, modified = compare_with_reference(TIME_MS, rate_hz=0.6)
    np.testing.assert_array_equal(reference.voltage_mv, original.voltage_mv)
    assert reference.stimulus == original.stimulus
    assert reference.stimulus.times_ms != modified.stimulus.times_ms
    assert set(modified.stimulus.amplitudes_pa) == {1.2}
    assert modified.parameters == reference.parameters
    assert not np.allclose(reference.photocurrent_pa, modified.photocurrent_pa)
    assert not np.allclose(reference.voltage_mv, modified.voltage_mv)


def test_zero_modified_rate_does_not_erase_reference_events():
    reference, modified = compare_with_reference(TIME_MS, rate_hz=0)
    assert len(reference.stimulus.times_ms) == 3
    assert modified.stimulus.times_ms == ()
    np.testing.assert_allclose(modified.voltage_mv, -40, atol=1e-12)
    assert reference.voltage_mv[0].min() < -40


def test_seed_membrane_and_peak_controls_do_not_change_reference():
    expected, _ = compare_with_reference(TIME_MS)
    reference, modified = compare_with_reference(TIME_MS, seed=7, t_peak_ms=1000,
                                                  modified_parameters=RodParameters(g_it_ns=0))
    np.testing.assert_array_equal(reference.voltage_mv, expected.voltage_mv)
    assert reference.stimulus == expected.stimulus
    assert modified.parameters.g_it_ns == 0
    assert modified.stimulus.t_peak_ms == 1000


def test_metrics_define_signed_minima_lags_and_transmission():
    time = np.array([0, 100, 200, 300])
    delta = np.array([[0, -2, -1, -.1], [0, -.5, -1, -.4], [0, 0, -.25, -.5]])
    artificial = SimulationResult(time, -40+delta, np.zeros(4), RodParameters(), PhotonEvents())
    measures = response_metrics(artificial)
    np.testing.assert_allclose(measures['min_delta_mv'], [-2, -1, -.5])
    np.testing.assert_array_equal(measures['time_min_ms'], [100, 200, 300])
    assert measures['delay_i_ms'] == 100
    assert measures['delay_t_ms'] == 200
    assert measures['transmission_ratio'] == pytest.approx(.25, rel=1e-12)


def test_null_response_has_no_invented_time_or_lag():
    measures = response_metrics(simulate([0, 100, 1000]))
    assert np.all(np.isnan(measures['time_min_ms']))
    assert measures['delay_i_ms'] is None
    assert measures['delay_t_ms'] is None
    assert measures['transmission_ratio'] is None
    isolated = simulate(TIME_MS, RodParameters(g_it_ns=0), PhotonEvents.from_times([1000]))
    measures = response_metrics(isolated)
    assert measures['transmission_ratio'] == 0
    assert measures['delay_t_ms'] is None


def test_deviation_uses_coupled_rest_for_unequal_reversals():
    parameters = RodParameters(reversal_mv=(-45, -40, -35))
    result = simulate([0, 1000], parameters)
    np.testing.assert_allclose(voltage_deviation(result), 0, atol=1e-12)


def test_exact_rc_step_scale_and_sign():
    time = [0, 1000, 1400, 100000]
    voltage = rc_step_response(time, current_pa=-.3)
    np.testing.assert_allclose(voltage, [-40, -40, -40-6*(1-np.exp(-1)), -46])
    assert rc_step_response([1000], current_pa=0)[0] == -40


def test_modal_times_have_correct_uncoupled_units():
    np.testing.assert_allclose(modal_times_ms(RodParameters(g_oi_ns=0, g_it_ns=0)), [100, 150, 400])
    coupled = modal_times_ms()
    assert np.all(coupled > 0)
    assert np.all(np.diff(coupled) > 0)


def test_variation_of_constants_matches_ivp_with_input_and_initial_state():
    time = np.linspace(0, 9000, 19)
    parameters = RodParameters(reversal_mv=(-45, -40, -35))
    stimulus = PhotonEvents.from_times([1000, 4500])
    initial = [-42, -37, -38]
    quadrature = variation_of_constants(time, parameters, stimulus, initial_voltage_mv=initial)
    ivp = simulate(time, parameters, stimulus, initial_voltage_mv=initial)
    np.testing.assert_allclose(quadrature, ivp.voltage_mv, atol=2e-7, rtol=0)


def test_sensitivity_axes_metric_and_zero_connections():
    oi, it = [0, .05, .1], [0, .1]
    stimulus = PhotonEvents.from_times([1000])
    grid = sensitivity_map(oi, it, TIME_MS, stimulus)
    assert grid.shape == (2, 3)
    np.testing.assert_allclose(grid[0], 0, atol=1e-12)
    np.testing.assert_allclose(grid[:, 0], 0, atol=1e-12)
    result = simulate(TIME_MS, RodParameters(g_oi_ns=.05, g_it_ns=.1), stimulus)
    assert grid[1, 1] == pytest.approx(abs(response_metrics(result)['min_delta_mv'][2]))
    ratios = sensitivity_map([0, .1], [0, .1], TIME_MS, stimulus, metric='transmission_ratio')
    assert ratios[0, 1] == 0
    assert 0 < ratios[1, 1] < 1


def test_ensemble_is_reproducible_and_varies_between_seeds():
    first = poisson_ensemble(TIME_MS, .3, [2026, 2027, 2028])
    second = poisson_ensemble(TIME_MS, .3, [2026, 2027, 2028])
    for left, right in zip(first, second):
        assert left.stimulus == right.stimulus
        np.testing.assert_array_equal(left.voltage_mv, right.voltage_mv)
    assert first[0].stimulus != first[1].stimulus


@pytest.mark.parametrize('seeds', [[], [1, 1]])
def test_invalid_ensemble_is_rejected(seeds):
    with pytest.raises(ValueError):
        poisson_ensemble(TIME_MS, .3, seeds)


def test_invalid_analysis_inputs():
    with pytest.raises(ValueError):
        rc_step_response([0], capacitance_pf=0)
    with pytest.raises(ValueError):
        variation_of_constants([0, 0], RodParameters(), PhotonEvents())
    with pytest.raises(ValueError):
        sensitivity_map([.1, 0], [.1], TIME_MS, PhotonEvents())
    with pytest.raises(ValueError):
        sensitivity_map([.1], [.1], TIME_MS, PhotonEvents(), metric='unidades_inventadas')
