"""Contrato de figuras, referencias y lectura de M0; backend sin pantalla."""
from dataclasses import replace
import inspect
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import nbformat

from neurofisiologia import retina_on_off as model
from neurofisiologia import retina_on_off_plotting as plotting


def test_causal_rows_match_model_data_with_units_and_shared_limits():
    plus,minus=plotting.paired_light_experiment()
    fig=plotting.plot_causal_chain([plus,minus],['Más luz','Menos luz'])
    axes=np.asarray(fig.axes).reshape(7,2)
    for j,result in enumerate((plus,minus)):
        for row,expected in enumerate((result.illumination,result.photo_pa,result.voltage_mv[0],result.release)):
            np.testing.assert_array_equal(axes[row,j].lines[0].get_ydata(),expected)
        for k in (0,1):
            np.testing.assert_array_equal(axes[4,j].lines[k].get_ydata(),result.conductance_ns[k])
            np.testing.assert_array_equal(axes[5,j].lines[k].get_ydata(),result.voltage_mv[k+1])
        for k in range(3):np.testing.assert_array_equal(axes[6,j].lines[k].get_ydata(),result.delta_voltage_mv[k])
    fig.canvas.draw()
    for row in range(7):
        assert axes[row,0].get_ylim()==axes[row,1].get_ylim()
        assert '(' in axes[row,0].get_ylabel()
    assert 'ms' in axes[6,0].get_xlabel()
    assert 'no calibrados' in fig._suptitle.get_text()
    plt.close(fig)


def test_reference_lines_are_fixed_and_distinguishable_from_modified():
    ref,changed=plotting.parameter_comparison('gL_ON',2)
    fixed,_=plotting.parameter_comparison('k_L',.25)
    np.testing.assert_array_equal(ref.voltage_mv,fixed.voltage_mv)
    fig=plotting.plot_causal_chain([changed],['Cambio de fuga'],references=[ref])
    lines=fig.axes[5].lines
    assert lines[0].get_linestyle()=='--' and 'referencia fija' in lines[0].get_label()
    assert lines[2].get_linestyle()=='-' and 'modificado' in lines[2].get_label()
    np.testing.assert_array_equal(lines[0].get_ydata(),ref.voltage_mv[1])
    np.testing.assert_array_equal(lines[2].get_ydata(),changed.voltage_mv[1])
    assert changed.equilibrium_mv[1]!=ref.equilibrium_mv[1]
    np.testing.assert_array_equal(fig.axes[6].lines[4].get_ydata(),changed.delta_voltage_mv[1])
    fig.canvas.draw()
    for ax in fig.axes[4:]:
        assert ax.get_legend().get_window_extent().y0 >= ax.get_window_extent().y1
    plt.close(fig)


def test_circuit_sources_polarity_zero_and_disconnection():
    p=replace(model.M0Parameters(),g_on_max_ns=0,leak_reversal_mv=(-40,-60,-50),synaptic_reversal_mv=(0,5))
    fig=plotting.plot_electrical(p)
    assert len(fig.axes)==3
    for ax in fig.axes:
        # Fuga negativa: polo positivo abajo; potencial negativo rotulado.
        signs=[t for t in ax.texts if t.get_text() in ('+','−')]
        assert signs[0].get_text()=='−' and signs[0].get_position()[1]>signs[1].get_position()[1]
    assert any('abierta' in t.get_text() for t in fig.axes[1].texts)
    assert any(t.get_text()=='0' for t in fig.axes[1].texts)
    off_signs=[t for t in fig.axes[2].texts if t.get_text() in ('+','−')]
    assert off_signs[-2].get_text()=='+' and off_signs[-1].get_text()=='−'
    plt.close(fig)


def test_diagrams_text_inside_canvas_without_text_collisions():
    for fig in (plotting.plot_physiology(),plotting.plot_electrical()):
        fig.canvas.draw();renderer=fig.canvas.get_renderer();frame=fig.bbox
        for ax in fig.axes:
            texts=[t for t in ax.texts if t.get_visible() and t.get_text()]
            boxes=[t.get_window_extent(renderer) for t in texts]
            for box in boxes:
                assert box.x0>=frame.x0 and box.y0>=frame.y0
                assert box.x1<=frame.x1 and box.y1<=frame.y1
            for i,box in enumerate(boxes):
                for other in boxes[i+1:]:assert not box.overlaps(other)
        plt.close(fig)


def test_m0_source_and_public_contract():
    for module in (model,plotting):
        for name,func in inspect.getmembers(module,inspect.isfunction):
            if name.startswith('_') or func.__module__!=module.__name__:continue
            assert func.__doc__
            sig=inspect.signature(func)
            assert sig.return_annotation!=inspect.Signature.empty,name
            assert all(p.annotation!=inspect.Parameter.empty for p in sig.parameters.values()),name
    root=Path(__file__).resolve().parents[1]
    nb=nbformat.read(root/'notebooks/03_cono_bipolares_on_off.ipynb',as_version=4)
    nbformat.validate(nb)
    for cell in nb.cells:
        if cell.cell_type=='code':
            assert not cell.outputs and cell.execution_count is None
            compile(cell.source,'M0','exec')
    prose='\n'.join(c.source for c in nb.cells if c.cell_type=='markdown')
    for mechanism in ('mGluR6','E_{syn','L0','calibrad','Predicción','Interpretación','glutamato'):
        assert mechanism in prose
