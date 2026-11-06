"""Aceptación física y numérica de M0, independiente del laboratorio de bastón."""
from dataclasses import replace
import numpy as np
import pytest

from neurofisiologia.retina_on_off import (
    M0Parameters, LightStep, LightProtocol, release_fraction, synaptic_conductances,
    photocurrent_pa, background_equilibrium, constant_light_equilibrium,
    current_components, rhs, simulate_m0,
)


@pytest.mark.parametrize("change", [
    {"capacitance_pf": (0,30,30)}, {"leak_ns": (1,-1,1)},
    {"leak_ns": (1,1)}, {"leak_reversal_mv": (-40,np.nan,-60)},
    {"synaptic_reversal_mv": (-60,0)}, {"g_on_max_ns": -1},
    {"g_off_max_ns": np.inf}, {"light_gain_pa": 0}, {"release_slope_mv": 0},
    {"release_half_mv": np.nan}, {"capacitance_pf": (20,np.inf,30)},
])
def test_invalid_parameters(change):
    with pytest.raises(ValueError): replace(M0Parameters(), **change)


@pytest.mark.parametrize("args", [(1,1,1), (2,1,1), (0,1,-.1), (0,np.inf,1)])
def test_invalid_steps(args):
    with pytest.raises(ValueError): LightStep(*args)


def test_light_is_absolute_nonnegative_and_order_independent():
    protocol = LightProtocol(steps=(LightStep(5,7,0), LightStep(1,3,2)))
    t = np.array([0,1,2,3,5,6,7])
    expected = np.array([1,2,2,1,0,0,1])
    np.testing.assert_array_equal(protocol.illumination(t), expected)
    np.testing.assert_array_equal(protocol.illumination(t[::-1]), expected[::-1])
    assert float(protocol.illumination(7)) == 1
    with pytest.raises(ValueError): LightProtocol(background=0)
    with pytest.raises(ValueError): LightProtocol(steps=(LightStep(1,3,2),LightStep(2,4,0)))
    with pytest.raises(ValueError): protocol.illumination([np.nan])
    with pytest.raises(ValueError): photocurrent_pa(-1,1)


def test_release_and_conductances_are_monotone_and_bounded():
    p = M0Parameters()
    r = release_fraction(np.linspace(-100,20,1001),p)
    assert np.all(np.diff(r)>0)
    g = synaptic_conductances(r,p)
    assert np.all(np.diff(g[0])<0) and np.all(np.diff(g[1])>0)
    extreme = release_fraction([-1e300,0,1e300],p)
    assert np.all(np.isfinite(extreme)) and np.all((extreme>=0)&(extreme<=1))
    assert np.all(g>=0)
    assert float(release_fraction(p.release_half_mv,p)) == .5
    with pytest.raises(ValueError): synaptic_conductances([-.1])
    with pytest.raises(ValueError): release_fraction([np.inf])


def test_background_is_true_equilibrium_with_active_synapses():
    p = replace(M0Parameters(),g_on_max_ns=.8,g_off_max_ns=.3,
                leak_reversal_mv=(-43,-65,-57),synaptic_reversal_mv=(5,-2))
    eq = background_equilibrium(p)
    assert eq[0] == -43
    assert np.all(eq[1:]>np.array(p.leak_reversal_mv[1:]))
    assert np.all(eq[1:]<np.array(p.synaptic_reversal_mv))
    np.testing.assert_allclose(rhs(0,eq,p,LightProtocol(background=2)),0,atol=1e-14)
    result = simulate_m0([0,1,1000],p,LightProtocol(background=2))
    np.testing.assert_allclose(result.voltage_mv, np.repeat(eq[:,None],3,axis=1),atol=1e-12)
    np.testing.assert_allclose(constant_light_equilibrium(2,2,p),eq)


@pytest.mark.parametrize("contrast", [.1,.5,1,-.1,-.5,-1])
def test_signs_emerge_along_entire_causal_chain(contrast):
    p = M0Parameters(); protocol = LightProtocol(steps=(LightStep(100,400,1+contrast),))
    result = simulate_m0(np.linspace(0,900,901),p,protocol)
    k = 350; sign = np.sign(contrast)
    assert sign*result.photo_pa[k] < 0
    assert sign*result.delta_voltage_mv[0,k] < 0
    r0 = float(release_fraction(result.equilibrium_mv[0],p))
    assert sign*(result.release[k]-r0)<0
    g0 = synaptic_conductances(r0,p)
    assert sign*(result.conductance_ns[0,k]-g0[0])>0
    assert sign*(result.conductance_ns[1,k]-g0[1])<0
    assert sign*result.delta_voltage_mv[1,k]>0
    assert sign*result.delta_voltage_mv[2,k]<0
    np.testing.assert_allclose(result.voltage_mv[:,-1], result.equilibrium_mv,atol=1e-6)
    assert np.all(np.isfinite(result.voltage_mv))


def test_opposite_bipolar_derivatives_are_conductance_effects_not_voltage_forcing():
    p=M0Parameters(); eq=background_equilibrium(p)
    at_onset=rhs(100,eq,p,LightProtocol(steps=(LightStep(100,300,1.5),)))
    # Luz cambia primero el cono; no hay un término +/- luz añadido a bipolares.
    assert at_onset[0]<0
    np.testing.assert_allclose(at_onset[1:],0,atol=1e-14)
    voltage=eq.copy();voltage[0]-=5
    components=current_components(voltage,1,1,p)
    assert np.all(components['synaptic_pa'][1:]>0)  # ambas entradas catiónicas
    assert components['net_pa'][1]>0 and components['net_pa'][2]<0
    np.testing.assert_allclose(rhs(0,voltage,p,LightProtocol()), components['net_pa']/p.capacitance_pf)


@pytest.mark.parametrize("cell,name",[(1,'g_on_max_ns'),(2,'g_off_max_ns')])
def test_disconnection_is_specific_and_has_no_feedback_to_cone(cell,name):
    t=np.linspace(0,700,701);stim=LightProtocol(steps=(LightStep(100,300,1.5),))
    base=simulate_m0(t,protocol=stim)
    p=replace(M0Parameters(),**{name:0})
    result=simulate_m0(t,p,stim)
    np.testing.assert_allclose(result.voltage_mv[cell],p.leak_reversal_mv[cell],atol=1e-12)
    for i in {0,1,2}-{cell}:
        np.testing.assert_allclose(result.voltage_mv[i],base.voltage_mv[i],atol=2e-7)
    assert np.max(abs(result.delta_voltage_mv[3-cell]))>1


def test_constant_conductance_rc_exact_for_both_bipolars():
    p=M0Parameters();eq=background_equilibrium(p);initial=eq+np.array([0,7,-9])
    t=np.linspace(0,300,301)
    result=simulate_m0(t,p,initial_voltage_mv=initial)
    g=synaptic_conductances(release_fraction(eq[0],p),p)
    for i in (1,2):
        tau=p.capacitance_pf[i]/(p.leak_ns[i]+g[i-1])
        exact=eq[i]+(initial[i]-eq[i])*np.exp(-t/tau)
        np.testing.assert_allclose(result.voltage_mv[i],exact,atol=2e-7,rtol=0)


def test_cone_rc_exact_and_a_pulse_between_output_samples_is_not_skipped():
    p=M0Parameters();a,b=100.01,100.02
    t=np.array([0,100,100.03,101,200.])
    protocol=LightProtocol(steps=(LightStep(a,b,1.5),))
    result=simulate_m0(t,p,protocol,max_step_ms=10000)
    tau=p.capacitance_pf[0]/p.leak_ns[0]
    shift=-p.light_gain_pa*.5/p.leak_ns[0]
    exact=p.leak_reversal_mv[0]+np.where(t<=a,0,
        shift*(1-np.exp(-(np.minimum(t,b)-a)/tau))*np.exp(-np.maximum(t-b,0)/tau))
    np.testing.assert_allclose(result.voltage_mv[0],exact,atol=5e-8,rtol=0)
    assert result.delta_voltage_mv[0,2]<-1e-3


def test_dimensional_current_balance_in_si_units():
    p=M0Parameters();v=np.array([-45,-44,-50]);L=1.4
    comp=current_components(v,L,1,p)
    # F*V/s=A; convertir V/ms a V/s multiplica por 1 (mV/ms).
    v_si=v*1e-3;g_si=np.array(p.leak_ns)*1e-9;E_si=np.array(p.leak_reversal_mv)*1e-3
    net_si=-g_si*(v_si-E_si)
    net_si[0]+=-p.light_gain_pa*1e-12*(L-1)
    gs=synaptic_conductances(release_fraction(v[0],p),p)*1e-9
    net_si[1:]+=gs*(np.array(p.synaptic_reversal_mv)*1e-3-v_si[1:])
    np.testing.assert_allclose(comp['net_pa']*1e-12,net_si,atol=1e-25)
    protocol=LightProtocol(steps=(LightStep(0,10,L),))
    np.testing.assert_allclose(rhs(1,v,p,protocol),net_si/(np.array(p.capacitance_pf)*1e-12))


def test_capacitance_changes_time_but_not_equilibrium():
    p=M0Parameters();q=replace(p,capacitance_pf=(40,60,60));stim=LightProtocol(steps=(LightStep(0,1000,1.5),))
    t=np.linspace(0,800,801)
    fast=simulate_m0(t,p,stim);slow=simulate_m0(t,q,stim)
    np.testing.assert_allclose(background_equilibrium(p),background_equilibrium(q))
    np.testing.assert_allclose(fast.voltage_mv[:,:401],slow.voltage_mv[:,::2],atol=1e-7)
    np.testing.assert_allclose(fast.voltage_mv[:,-1],constant_light_equilibrium(1.5,parameters=p),atol=1e-7)


def test_gain_and_leak_change_constant_light_response():
    p=M0Parameters();base=constant_light_equilibrium(1.5,parameters=p)
    gain=constant_light_equilibrium(1.5,parameters=replace(p,light_gain_pa=20))
    leak=constant_light_equilibrium(1.5,parameters=replace(p,leak_ns=(2,1,1)))
    assert gain[0]<base[0]<leak[0]
    assert gain[1]>base[1]>leak[1]
    assert gain[2]<base[2]<leak[2]


def test_determinism_sampling_order_and_recovery_after_train():
    stim=LightProtocol(steps=(LightStep(100,200,1.5),LightStep(300,400,.5),LightStep(500,600,1.2)))
    t=np.linspace(0,1200,1201);a=simulate_m0(t,protocol=stim)
    stim.illumination(t[::-1])
    b=simulate_m0(t,protocol=stim)
    np.testing.assert_array_equal(a.voltage_mv,b.voltage_mv)
    np.testing.assert_allclose(a.voltage_mv[:,-1],a.equilibrium_mv,atol=1e-7)


def test_late_bipolar_peak_is_a_membrane_delay():
    result=simulate_m0(np.linspace(0,600,1201),protocol=LightProtocol(steps=(LightStep(100,150,1.5),)))
    cone_peak=result.time_ms[np.argmin(result.voltage_mv[0])]
    on_peak=result.time_ms[np.argmax(result.voltage_mv[1])]
    assert on_peak>cone_peak>=150


@pytest.mark.parametrize("times", [[0], [1,0], [0,0], [0,np.nan]])
def test_invalid_output_grid(times):
    with pytest.raises(ValueError):simulate_m0(times)


def test_history_and_initial_state_are_explicit():
    protocol=LightProtocol(steps=(LightStep(0,20,1.5),))
    with pytest.raises(ValueError):simulate_m0([10,30],protocol=protocol)
    with pytest.raises(ValueError):simulate_m0([0,30],initial_voltage_mv=[0,0])
    with pytest.raises(ValueError):simulate_m0([0,30],rtol=0)
    with pytest.raises(ValueError):simulate_m0([0,30],max_step_ms=-1)
    assert np.all(np.isfinite(simulate_m0([10,30],protocol=protocol,initial_voltage_mv=[-43,-46,-50]).voltage_mv))


def test_asymmetric_bipolars_preserve_signs_without_mirrored_voltages():
    p=replace(M0Parameters(),capacitance_pf=(20,50,15),leak_ns=(1,.8,1.5),
              g_on_max_ns=.7,g_off_max_ns=.3,synaptic_reversal_mv=(3,-5))
    out=simulate_m0(np.linspace(0,700,701),p,LightProtocol(steps=(LightStep(100,300,1.5),)))
    assert out.delta_voltage_mv[1,250]>0>out.delta_voltage_mv[2,250]
    assert not np.isclose(out.delta_voltage_mv[1,250],-out.delta_voltage_mv[2,250])
