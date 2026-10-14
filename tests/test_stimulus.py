import numpy as np
import pytest

from neurofisiologia import PhotonEvents, photon_kernel, poisson_events


def test_kernel_causality_normalization_and_peak():
    u = np.linspace(-2200, 22000, 11001)
    h = photon_kernel(u)
    assert photon_kernel(-1) == 0
    assert photon_kernel(0) == 0
    assert photon_kernel(2200) == pytest.approx(1)
    assert np.all((h >= 0) & (h <= 1))
    assert u[np.argmax(h)] == pytest.approx(2200)
    assert photon_kernel(1e308, 1e-10) == 0


def test_photocurrent_negative_and_additive():
    events = PhotonEvents((1000, 1000), (1.2, 0.8))
    assert events.current(900) == 0
    assert events.current(3200) == pytest.approx(-2)
    assert events.current(np.array([900, 3200])).shape == (2,)
    np.testing.assert_array_equal(PhotonEvents().current([0, 1000]), [0, 0])


def test_seeded_poisson_is_deterministic_without_changing_global_rng():
    global_state = np.random.get_state()
    first = poisson_events(0.3, 10000, seed=2026, start_ms=1000)
    second = poisson_events(0.3, 10000, seed=2026, start_ms=1000)
    assert first == second
    assert first != poisson_events(0.3, 10000, seed=2027, start_ms=1000)
    assert len(first.times_ms) > 0
    # Una ventana Poisson puede estar vacía incluso con tasa positiva.
    assert all(1000 <= t < 11000 for t in first.times_ms)
    assert list(first.times_ms) == sorted(first.times_ms)
    after = np.random.get_state()
    np.testing.assert_array_equal(global_state[1], after[1])
    assert global_state[2:] == after[2:]


def test_poisson_rate_units_and_count_statistics():
    # 2 eventos/s durante 3000 ms: media y varianza teóricas = 6.
    counts = np.array([len(poisson_events(2, 3000, seed=s).times_ms) for s in range(400)])
    assert abs(counts.mean() - 6) < 0.5
    assert abs(counts.var() - 6) < 1.4


@pytest.mark.parametrize("rate,duration", [(0, 1000), (1, 0)])
def test_zero_rate_or_duration_is_darkness(rate, duration):
    assert poisson_events(rate, duration, seed=1).times_ms == ()


def test_positive_rate_can_generate_an_empty_window():
    assert poisson_events(0.3, 10000, seed=1979).times_ms == ()


@pytest.mark.parametrize("kwargs", [
    {"rate_hz": -1}, {"duration_ms": -1}, {"start_ms": np.nan},
    {"seed": -1}, {"seed": None}, {"amplitude_pa": -1},
])
def test_invalid_poisson_inputs(kwargs):
    options = {"rate_hz": 1, "duration_ms": 1000, "seed": 1979}
    options.update(kwargs)
    with pytest.raises(ValueError):
        poisson_events(**options)


@pytest.mark.parametrize("times,amps,peak", [
    ((2, 1), (1, 1), 2200), ((1,), (), 2200), ((-1,), (1,), 2200),
    ((np.nan,), (1,), 2200), ((1,), (-1,), 2200), ((1,), (np.inf,), 2200),
    ((), (), 0), ((), (), np.nan),
])
def test_invalid_events(times, amps, peak):
    with pytest.raises(ValueError):
        PhotonEvents(times, amps, peak)


def test_nonfinite_kernel_times_are_rejected():
    with pytest.raises(ValueError):
        photon_kernel(np.inf)
