"""Invariantes físicos y referencias analíticas independientes del integrador."""

from dataclasses import replace

import numpy as np
import pytest
from scipy.integrate import quad
from scipy.linalg import expm

from neurofisiologia import (
    PhotonEvents, RodParameters, current_balance, dark_equilibrium,
    photon_kernel, rhs, simulate,
)
from neurofisiologia.model import conductance_matrix


def test_darkness_stays_at_rest():
    result = simulate(np.linspace(0, 10000, 101))
    np.testing.assert_allclose(result.voltage_mv, -40.0, atol=1e-12)
    np.testing.assert_array_equal(result.photocurrent_pa, 0)


def test_equilibrium_with_different_reversals():
    p = RodParameters(reversal_mv=(-45, -40, -35))
    equilibrium = dark_equilibrium(p)
    np.testing.assert_allclose(current_balance(0, equilibrium, p, PhotonEvents()),
                               0, atol=2e-15)
    result = simulate([0, 1000, 10000], p)
    np.testing.assert_allclose(result.voltage_mv, np.repeat(equilibrium[:, None], 3, axis=1))


def test_first_light_is_hyperpolarizing_and_causal():
    time = np.linspace(0, 12000, 601)
    result = simulate(time, stimulus=PhotonEvents.from_times([1000]))
    np.testing.assert_allclose(result.voltage_mv[:, time <= 1000], -40, atol=1e-7, rtol=0)
    assert result.voltage_mv[0].min() < -40.1
    assert np.max(result.voltage_mv + 40) < 1e-7
    assert result.photocurrent_pa.min() == pytest.approx(-1.2)
    assert np.all(result.voltage_mv[:, -1] > result.voltage_mv.min(axis=1))


def test_decoupled_inner_and_terminal_stay_dark():
    p = RodParameters(g_oi_ns=0, g_it_ns=0)
    result = simulate(np.linspace(0, 12000, 301), p, PhotonEvents.from_times([1000]))
    assert result.voltage_mv[0].min() < -40
    np.testing.assert_allclose(result.voltage_mv[1:], -40, atol=1e-12)


def test_outer_response_matches_independent_convolution():
    p = RodParameters(g_oi_ns=0, g_it_ns=0)
    stimulus = PhotonEvents.from_times([1000])
    time = np.array([0, 1000, 2200, 3200, 6000, 12000])
    result = simulate(time, p, stimulus)
    tau = p.capacitance_pf[0] / p.leak_ns[0]
    reference = []
    for t in time:
        integral = 0 if t <= 1000 else quad(
            lambda s: np.exp(-(t-s)/tau) * photon_kernel(s-1000),
            1000, t, epsabs=1e-9,
        )[0]
        reference.append(-40 - 1.2 / p.capacitance_pf[0] * integral)
    np.testing.assert_allclose(result.voltage_mv[0], reference, atol=2e-6, rtol=0)


def test_coupling_transmits_and_reduces_outer_deflection():
    time = np.linspace(0, 10000, 301)
    stimulus = PhotonEvents.from_times([1000])
    coupled = simulate(time, stimulus=stimulus)
    separate = simulate(time, RodParameters(g_oi_ns=0, g_it_ns=0), stimulus)
    assert coupled.voltage_mv[1].min() < -40.1
    assert coupled.voltage_mv[2].min() < -40.1
    assert coupled.voltage_mv[0].min() > separate.voltage_mv[0].min()
    # Si se interrumpe I-T, la terminal deja de recibir el estímulo.
    terminal_isolated = simulate(time, RodParameters(g_it_ns=0), stimulus)
    np.testing.assert_allclose(terminal_isolated.voltage_mv[2], -40, atol=1e-12)


def test_axial_currents_cancel_and_match_the_issue_equations():
    p = RodParameters(capacitance_pf=(2, 3, 4), leak_ns=(1, 2, 3),
                      reversal_mv=(-40, -42, -39), g_oi_ns=0.5, g_it_ns=0.25)
    v = np.array([-43., -41., -40.])
    net = current_balance(0, v, p, PhotonEvents())
    # C_O V'_O=3+1; C_I V'_I=-2-1+0.25; C_T V'_T=3-0.25.
    np.testing.assert_allclose(net, [4, -2.75, 2.75])
    assert net.sum() == pytest.approx((-np.asarray(p.leak_ns)*(v-p.reversal_mv)).sum())


def test_dimensional_conversion_to_si():
    # 1 pF * 1 mV / 1 ms = 1 pA; 1 nS * 1 mV = 1 pA.
    assert 1e-12 * 1e-3 / 1e-3 == pytest.approx(1e-12, abs=0, rel=1e-12)
    assert 1e-9 * 1e-3 == pytest.approx(1e-12, abs=0, rel=1e-12)
    p = RodParameters(capacitance_pf=(2, 3, 4), leak_ns=(1, 1, 1),
                      g_oi_ns=0, g_it_ns=0)
    derivative = rhs(0, [-41, -40, -40], p, PhotonEvents())
    np.testing.assert_allclose(derivative, [0.5, 0, 0])
    derivative_si = 1e-9 * 1e-3 / (2e-12)  # V/s = mV/ms
    assert derivative[0] == pytest.approx(derivative_si)


def test_coupled_relaxation_matches_matrix_exponential():
    p = RodParameters(reversal_mv=(-45, -40, -35))
    equilibrium = dark_equilibrium(p)
    initial = equilibrium + [3, -2, 1]
    time = np.array([0., 10., 100., 1000., 5000.])
    matrix = -np.diag(1 / np.asarray(p.capacitance_pf)) @ conductance_matrix(p)
    assert np.all(np.linalg.eigvals(matrix).real < 0)
    reference = np.column_stack([equilibrium + expm(matrix*t)@(initial-equilibrium) for t in time])
    actual = simulate(time, p, initial_voltage_mv=initial).voltage_mv
    np.testing.assert_allclose(actual, reference, atol=2e-7, rtol=0)


def test_linear_superposition_of_coincident_events():
    time = np.linspace(0, 8000, 201)
    single = simulate(time, stimulus=PhotonEvents.from_times([1000]))
    double = simulate(time, stimulus=PhotonEvents.from_times([1000, 1000]))
    np.testing.assert_allclose(double.voltage_mv + 40, 2*(single.voltage_mv + 40), atol=2e-6)


def test_late_short_response_is_not_skipped_on_sparse_output_grid():
    p = RodParameters(capacitance_pf=(0.05, 0.05, 0.05), g_oi_ns=0, g_it_ns=0)
    stimulus = PhotonEvents.from_times([100], t_peak_ms=1)
    result = simulate([0, 99, 101, 103, 110], p, stimulus, max_step_ms=1e6)
    assert result.voltage_mv[0, 2] < -41
    np.testing.assert_allclose(result.voltage_mv[0, :2], -40, atol=1e-7)


@pytest.mark.parametrize("kwargs", [
    {"capacitance_pf": (0, 1, 1)}, {"leak_ns": (-1, 1, 1)},
    {"reversal_mv": (np.nan, -40, -40)}, {"capacitance_pf": (1, 2)},
    {"g_oi_ns": -1}, {"g_it_ns": np.inf},
])
def test_invalid_parameters_are_rejected(kwargs):
    with pytest.raises(ValueError):
        RodParameters(**kwargs)


@pytest.mark.parametrize("times", [[0], [0, 0], [1, 0], [0, np.nan], [[0, 1]]])
def test_invalid_output_grid_is_rejected(times):
    with pytest.raises(ValueError):
        simulate(times)


@pytest.mark.parametrize("kwargs", [
    {"rtol": 0}, {"atol": np.nan}, {"max_step_ms": -1},
    {"initial_voltage_mv": [0, 1]},
])
def test_invalid_solver_options_are_rejected(kwargs):
    with pytest.raises(ValueError):
        simulate([0, 1], **kwargs)


def test_parameters_are_immutable_and_can_be_replaced():
    p = RodParameters(capacitance_pf=[20, 15, 5])
    assert p.capacitance_pf == (20, 15, 5)
    assert replace(p, g_it_ns=0).g_it_ns == 0
    assert p.g_it_ns == 0.1
