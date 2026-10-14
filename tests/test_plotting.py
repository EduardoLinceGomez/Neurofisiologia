"""Comprueba entradas representadas y direcciones de flechas; no solo ejecución."""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.text import Annotation
import numpy as np
import pytest
from itertools import combinations
from dataclasses import replace

from neurofisiologia import RodParameters, PhotonEvents, simulate
from neurofisiologia.model import decompose_currents
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
    assert len(arrows) == 2
    # Solo axiales: O es más negativo, referencias O→I e I→T negativas.
    assert all(arrow.xy[0] < arrow.xyann[0] for arrow in arrows)
    figure.canvas.draw()
    plt.close(figure)


@pytest.mark.parametrize('reversals', [(-40., -40., -40.), (40., 40., 40.),
                                      (0., 0., 0.), (-123.456, 12.3456, 0.)])
def test_reversal_sources_show_polarity_relative_to_exterior(reversals):
    figure, axis = plot_circuit(RodParameters(reversal_mv=reversals))
    texts = {text.get_gid(): text for text in axis.texts if text.get_gid()}
    sources = {patch.get_gid(): patch for patch in axis.patches if patch.get_gid()}
    for region, reversal in zip('OIT', reversals):
        source = sources[f'reversal-source-{region}']
        assert source.center[1] > 0  # Otra terminal conectada al exterior y=0.
        reversal_label = f'{reversal:+g}' if reversal != 0 else '0'
        assert texts[f'reversal-label-{region}'].get_text() == f'E={reversal_label}\nmV'
        if reversal == 0:
            assert texts[f'source-zero-{region}'].get_text() == '0'
            assert f'source-upper-{region}' not in texts and f'source-lower-{region}' not in texts
        else:
            upper, lower = texts[f'source-upper-{region}'], texts[f'source-lower-{region}']
            assert upper.get_text() == ('+' if reversal > 0 else '−')
            assert lower.get_text() == ('−' if reversal > 0 else '+')
            assert upper.get_position()[1] > source.center[1] > lower.get_position()[1]
    assert '0 mV' in texts['exterior-reference'].get_text()
    assert 'no es V instantáneo' in texts['reversal-definition'].get_text()
    plt.close(figure)


@pytest.mark.parametrize('time_ms', [0, 1000, 3440, 12000])
@pytest.mark.parametrize('reversals', [(-40.,)*3, (40.,)*3, (0.,)*3, (-123.456, 12.3456, 0.)])
def test_photocurrent_is_algebraic_and_axial_arrows_follow_computed_signs(time_ms, reversals):
    parameters = RodParameters(reversal_mv=reversals)
    result = simulate(TIME, parameters, PhotonEvents.from_times([1000]))
    figure, axis = plot_circuit(result=result, time_ms=time_ms)
    index = np.argmin(abs(result.time_ms-time_ms))
    parts = decompose_currents(result.time_ms[index], result.voltage_mv[:, index], parameters, result.stimulus)
    texts = {text.get_gid(): text for text in axis.texts if text.get_gid()}
    photo = texts['photocurrent-algebraic']
    assert not isinstance(photo, Annotation)
    assert 'Variación de corriente entrante de oscuridad' in photo.get_text()
    assert 'no indica flujo iónico absoluto hacia fuera' in photo.get_text()
    label_value = float(photo.get_text().split('I_photo(t) = ')[1].split(' pA')[0])
    assert label_value == pytest.approx(float(parts['photocurrent_pa'][0]), abs=.0005)
    arrows = [text for text in axis.texts if isinstance(text, Annotation)]
    assert all(arrow.get_gid() in ('axial-arrow-OI', 'axial-arrow-IT') for arrow in arrows)
    for pair, key in [('OI', 'axial_current_oi_pa'), ('IT', 'axial_current_it_pa')]:
        current = float(parts[key])
        arrow = texts.get(f'axial-arrow-{pair}')
        if abs(current) <= 1e-10:
            assert arrow is None
        else:
            assert (arrow.xy[0] > arrow.xyann[0]) == (current > 0)
            label = texts[f'axial-label-{pair}'].get_text()
            shown = float(label.split('=')[1].split(' pA')[0])
            assert shown != 0  # No flecha con valor aparente cero por redondeo.
            assert shown == pytest.approx(current, abs=.0005)
    plt.close(figure)


def test_open_axial_connections_do_not_imply_current():
    parameters = RodParameters(g_oi_ns=0, g_it_ns=0, reversal_mv=(-40, 0, 40))
    for result in (None, simulate(TIME, parameters, PhotonEvents.from_times([1000]))):
        figure, axis = plot_circuit(parameters, result=result, time_ms=3440)
        assert not [text for text in axis.texts if isinstance(text, Annotation)]
        assert sum('(abierto)' in text.get_text() for text in axis.texts) == 2
        plt.close(figure)


@pytest.mark.parametrize('parameters', [RodParameters(),
    RodParameters(reversal_mv=(40, 40, 40)), RodParameters(reversal_mv=(0, 0, 0)),
    RodParameters(capacitance_pf=(200, .5, 123.456), leak_ns=(.001, 2, .123456),
                  reversal_mv=(-123.456, 12.3456, 0), g_oi_ns=0, g_it_ns=1.23456)])
@pytest.mark.parametrize('time_ms', [None, 0, 3440, 12000])
def test_circuit_labels_do_not_overlap_or_overflow(parameters, time_ms):
    result = None if time_ms is None else simulate(TIME, parameters, PhotonEvents.from_times([1000]))
    figure, axis = plot_circuit(parameters, result=result, time_ms=time_ms)
    figure.canvas.draw()
    renderer = figure.canvas.get_renderer()
    texts = [text for text in axis.texts if text.get_text()]
    boxes = [(text, text.get_window_extent(renderer)) for text in texts]
    for text, box in boxes:
        # Margen real entre rótulos y el borde; también comprobar el recuadro foto.
        patch = text.get_bbox_patch()
        if patch is not None:
            box = patch.get_window_extent(renderer)
        assert axis.bbox.contains(box.x0, box.y0) and axis.bbox.contains(box.x1, box.y1), text.get_text()
        assert text.get_fontsize() >= 11
    for (left, a), (right, b) in combinations(boxes, 2):
        assert not a.overlaps(b), (left.get_text(), right.get_text())
    for text in figure.texts:
        box = text.get_window_extent(renderer)
        assert figure.bbox.contains(box.x0, box.y0) and figure.bbox.contains(box.x1, box.y1)
    plt.close(figure)


def test_tiny_nonzero_axial_current_remains_visible_in_label():
    result = simulate(TIME, stimulus=PhotonEvents.from_times([1000]))
    # Estado de prueba pequeño: no añadir otro integrador ni alterar el resultado original.
    result = replace(result, voltage_mv=np.tile([[-40.0001], [-40.00005], [-40.]], (1, TIME.size)))
    figure, axis = plot_circuit(result=result, time_ms=3440)
    texts = {text.get_gid(): text for text in axis.texts if text.get_gid()}
    assert float(texts['axial-label-OI'].get_text().split('=')[1].split()[0]) == pytest.approx(-5e-6)
    assert texts['axial-arrow-OI'].xy[0] < texts['axial-arrow-OI'].xyann[0]
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
