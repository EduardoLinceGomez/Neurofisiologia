import numpy as np
import pytest

from neurofisiologia import PhotonEvents, RodParameters, decompose_currents, current_balance, rhs, simulate
from neurofisiologia.model import conductance_matrix, dark_equilibrium


def test_signed_currents_are_equal_and_opposite():
    p = RodParameters(g_oi_ns=.1, g_it_ns=.2)
    currents = decompose_currents(0, [-45, -42, -40], p, PhotonEvents())
    assert currents['axial_current_oi_pa'] == pytest.approx(-.3)
    assert currents['axial_current_it_pa'] == pytest.approx(-.4)
    np.testing.assert_allclose(currents['axial_current_pa'], [.3, .1, -.4])
    assert currents['axial_current_pa'].sum() == pytest.approx(0, abs=1e-15)


def test_breakdown_recomposes_rhs_and_solver_matrix_at_every_sample():
    p = RodParameters(reversal_mv=(-45, -40, -35))
    stimulus = PhotonEvents.from_times([1000, 4000])
    result = simulate(np.linspace(0, 10000, 101), p, stimulus)
    c = decompose_currents(result.time_ms, result.voltage_mv, p, stimulus)
    recomposed = c['leak_current_pa']+c['photocurrent_pa']+c['axial_oi_by_node_pa']+c['axial_it_by_node_pa']
    np.testing.assert_allclose(recomposed, c['net_current_pa'], atol=2e-15)
    np.testing.assert_allclose(c['axial_current_pa'].sum(axis=0), 0, atol=2e-15)
    independent_net = -conductance_matrix(p)@(result.voltage_mv-dark_equilibrium(p)[:, None])
    independent_net[0] += result.photocurrent_pa
    np.testing.assert_allclose(recomposed, independent_net, atol=2e-14, rtol=0)
    for i, t in enumerate(result.time_ms):
        np.testing.assert_allclose(current_balance(t, result.voltage_mv[:, i], p, stimulus), recomposed[:, i], atol=2e-15)
        np.testing.assert_allclose(rhs(t, result.voltage_mv[:, i], p, stimulus)*p.capacitance_pf, recomposed[:, i], atol=2e-15)


@pytest.mark.parametrize('time,voltage', [(np.inf, [-40]*3), ([0,1], [-40]*3), (0, [0,1]), ([[0]], [[0],[0],[0]])])
def test_invalid_current_shapes_are_rejected(time, voltage):
    with pytest.raises(ValueError):
        decompose_currents(time, voltage, RodParameters(), PhotonEvents())
