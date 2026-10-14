"""Comprueba entradas representadas y direcciones de flechas; no solo ejecución."""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.text import Annotation
import numpy as np

from neurofisiologia import RodParameters, PhotonEvents, simulate
from neurofisiologia.analysis import compare_with_reference, poisson_ensemble
from neurofisiologia.plotting import (plot_circuit, plot_comparison, plot_currents,
    plot_kernel_events, plot_poisson_variability, plot_regions, plot_sensitivity,
    plot_topologies, plot_voltages)


TIME = np.linspace(0, 12000, 121)


def test_comparison_plot_represents_two_real_inputs():
    reference, modified = compare_with_reference(TIME, rate_hz=.6)
    figure, axes = plot_comparison(reference, modified)
    np.testing.assert_array_equal(axes[1].lines[0].get_ydata(), reference.photocurrent_pa)
    np.testing.assert_array_equal(axes[1].lines[1].get_ydata(), modified.photocurrent_pa)
    assert not np.array_equal(axes[1].lines[0].get_ydata(), axes[1].lines[1].get_ydata())
    assert len(axes[2].lines) == 6
    figure.canvas.draw()
    plt.close(figure)


def test_temporal_circuit_has_no_fake_zero_current_arrows():
    result = simulate(TIME, stimulus=PhotonEvents.from_times([1000]))
    figure, axis = plot_circuit(result=result, time_ms=0)
    assert not [text for text in axis.texts if isinstance(text, Annotation)]
    assert len(figure.axes) == 2  # Estado enlazado con su línea temporal.
    plt.close(figure)
    figure, axis = plot_circuit(result=result, time_ms=2000)
    arrows = [text for text in axis.texts if isinstance(text, Annotation)]
    assert len(arrows) == 3
    # O es más negativo: referencia O→I e I→T negativa; foto también negativa.
    assert all(arrow.xy[0] < arrow.xyann[0] for arrow in arrows)
    figure.canvas.draw()
    plt.close(figure)


def test_delta_view_removes_each_membranes_own_rest():
    reference, modified = compare_with_reference(TIME, modified_parameters=RodParameters(reversal_mv=(-45,-40,-35)))
    figure, axes = plot_comparison(reference, modified, voltage_view='delta')
    for line in axes[2].lines:
        assert abs(line.get_ydata()[0]) < 1e-12
    assert 'reposo propio' in axes[2].get_ylabel()
    plt.close(figure)


def test_catalogue_figures_render_and_export_svg(tmp_path):
    stimulus = PhotonEvents.from_times([1000])
    result = simulate(TIME, stimulus=stimulus)
    ensemble = {.3: poisson_ensemble(TIME, .3, [2026, 2027])}
    figures = [plot_regions()[0], plot_circuit()[0], plot_kernel_events(result)[0],
        plot_voltages(result)[0], plot_currents(result)[0],
        plot_topologies(TIME, stimulus)[0],
        plot_sensitivity([0,.1], [0,.1], [[0,0],[0,3]])[0],
        plot_poisson_variability(ensemble, (2026,2027))[0]]
    for index, figure in enumerate(figures):
        figure.canvas.draw()
        path = tmp_path/f'figure-{index}.svg'
        figure.savefig(path)
        assert '<svg' in path.read_text()
        plt.close(figure)
