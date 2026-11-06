"""Figuras originales y experimentos M0: no redefinen las EDO."""
from __future__ import annotations

from dataclasses import replace
from pathlib import Path
from collections.abc import Sequence

import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.axes import Axes
from matplotlib.patches import Circle, FancyBboxPatch
import numpy as np

from .retina_on_off import (M0Parameters, M0Result, LightProtocol, LightStep,
                           background_equilibrium, release_fraction,
                           synaptic_conductances, simulate_m0)

COLORS = ("#475569", "#00796b", "#b54708")
LABELS = ("Cono", "ON", "OFF")
PARAMETER_LABELS = {
    "k_L": "Ganancia luz (pA/u. L)", "C_cono": "C cono (pF)",
    "C_ON": "C ON (pF)", "C_OFF": "C OFF (pF)",
    "gL_cono": "Fuga cono (nS)", "gL_ON": "Fuga ON (nS)",
    "gL_OFF": "Fuga OFF (nS)", "gmax_ON": "Máximo ON (nS)",
    "gmax_OFF": "Máximo OFF (nS)",
}


def pulse_protocol(contrast: float = 0.5) -> LightProtocol:
    """Pulso relativo a L0=1, de 100 a 300 ms; contraste >= -1."""
    return LightProtocol(steps=(LightStep(100.0, 300.0, 1.0+contrast),))


def paired_light_experiment(contrast: float = 0.5) -> tuple[M0Result, M0Result]:
    """Incremento y decremento de igual magnitud; solo cambia L, 0<=contraste<=1."""
    if not np.isfinite(contrast) or not 0 <= contrast <= 1:
        raise ValueError("El contraste pareado debe estar entre 0 y 1")
    times = np.linspace(0, 600, 601)
    return (simulate_m0(times, protocol=pulse_protocol(contrast)),
            simulate_m0(times, protocol=pulse_protocol(-contrast)))


def parameter_comparison(parameter: str = "C_ON", factor: float = 1.0) -> tuple[M0Result, M0Result]:
    """Referencia canónica fija y modificación de un solo parámetro por factor.

    Misma iluminación de incremento en ambos casos. Cada delta V usa el
    equilibrio de su propia membrana; la referencia nunca sigue los controles.
    """
    if parameter not in PARAMETER_LABELS or not np.isfinite(factor) or factor <= 0:
        raise ValueError("Se requiere un parámetro reconocido y factor positivo")
    reference_parameters = M0Parameters()
    if parameter in ("k_L", "gmax_ON", "gmax_OFF"):
        name = {"k_L": "light_gain_pa", "gmax_ON": "g_on_max_ns", "gmax_OFF": "g_off_max_ns"}[parameter]
        modified = replace(reference_parameters, **{name: getattr(reference_parameters, name)*factor})
    else:
        family, cell = parameter.split("_")
        name = "capacitance_pf" if family == "C" else "leak_ns"
        values = list(getattr(reference_parameters, name))
        values[{"cono": 0, "ON": 1, "OFF": 2}[cell]] *= factor
        modified = replace(reference_parameters, **{name: tuple(values)})
    times = np.linspace(0, 600, 601)
    protocol = pulse_protocol()
    return simulate_m0(times, reference_parameters, protocol), simulate_m0(times, modified, protocol)


def save_figure(figure: Figure, name: str, output_dir: str | Path = "outputs/retina_on_off") -> None:
    """Exporta PNG/SVG bajo outputs/ por defecto; no guarda en el notebook fuente."""
    folder = Path(output_dir)
    folder.mkdir(parents=True, exist_ok=True)
    for extension in ("png", "svg"):
        figure.savefig(folder/f"{name}.{extension}", dpi=150, bbox_inches="tight")


def _decorate(ax: Axes, ylabel: str) -> None:
    ax.set_ylabel(ylabel)
    ax.grid(alpha=0.2)
    ax.spines[["top", "right"]].set_visible(False)
    ax.tick_params(labelsize=9)


def _traces(result: M0Result) -> list[list[tuple[np.ndarray, str, str]]]:
    return [[(result.illumination, "L", COLORS[0])],
            [(result.photo_pa, "ΔI foto", COLORS[0])],
            [(result.voltage_mv[0], "Cono", COLORS[0])],
            [(result.release, "r", "#6d28d9")],
            [(result.conductance_ns[i], LABELS[i+1], COLORS[i+1]) for i in range(2)],
            [(result.voltage_mv[i], LABELS[i], COLORS[i]) for i in (1, 2)],
            [(result.delta_voltage_mv[i], LABELS[i], COLORS[i]) for i in range(3)]]


def plot_causal_chain(results: Sequence[M0Result], titles: Sequence[str], *,
                      references: Sequence[M0Result] | None = None) -> Figure:
    """Siete filas con unidades: iluminación→corriente→cono→r→g→bipolares→delta V.

    Columnas comparables con límites compartidos por fila. Referencias opcionales
    discontinuas, modificaciones continuas; bases propias de cada condición.
    """
    if len(results) != len(titles) or not results or (references is not None and len(references) != len(results)):
        raise ValueError("Se requiere un título y, si procede, una referencia por resultado")
    fig, axes = plt.subplots(7, len(results), figsize=(6.5*len(results), 13),
                             sharex=True, sharey="row", squeeze=False, layout="constrained")
    units = ("L (adimensional)", "ΔI foto (pA)", "V cono (mV)", "r (fracción)",
             "g sináptica (nS)", "V bipolar (mV)", "ΔV desde reposo (mV)")
    for column, (result, title) in enumerate(zip(results, titles)):
        axes[0, column].set_title(title, fontsize=12, weight="bold")
        for row, traces in enumerate(_traces(result)):
            ax = axes[row, column]
            if references is not None:
                ref = references[column]
                for values, label, color in _traces(ref)[row]:
                    ax.plot(ref.time_ms, values, "--", color=color, alpha=.55, lw=2,
                            label=f"{label} · referencia fija", zorder=3,
                            drawstyle="steps-post" if row in (0, 1) else "default")
            for values, label, color in traces:
                ax.plot(result.time_ms, values, color=color, lw=1.7,
                        label=label+ (" · modificado" if references is not None else ""),
                        drawstyle="steps-post" if row in (0, 1) else "default")
            # Fondo no es oscuridad: L0>0. Las demás líneas marcan reposo real.
            baselines = {0: [result.protocol.background], 1: [0], 2: [result.equilibrium_mv[0]],
                         3: [float(release_fraction(result.equilibrium_mv[0], result.parameters))],
                         6: [0]}
            for baseline in baselines.get(row, []):
                ax.axhline(baseline, color="#64748b", lw=.7, ls=":")
            _decorate(ax, units[row] if column == 0 else "")
            if row in (4, 5, 6):
                # Reservar espacio fuera del eje: nunca tapar una recuperación.
                ax.legend(fontsize=8, loc="lower left", bbox_to_anchor=(0, 1.01),
                          ncol=2 if references is not None else 3, frameon=False)
        axes[-1, column].set_xlabel("Tiempo (ms)")
    fig.suptitle("M0 · Cadena causal simulada | parámetros ilustrativos, no calibrados", fontsize=14)
    if references is not None:
        fig.supxlabel("Continuo: modificado · Discontinuo: referencia fija · ΔV usa el reposo de cada condición", fontsize=10)
    else:
        fig.supxlabel("L y r no calibradas · Punteado: fondo/reposo · Tres células, sin spikes", fontsize=10)
    return fig


def plot_cone(results: Sequence[M0Result]) -> Figure:
    """Primera lectura: entrada de luz, variación de corriente y voltaje del cono."""
    fig, axes = plt.subplots(3, 1, figsize=(9, 7), sharex=True, layout="constrained")
    for result, label, color in zip(results, ("Más luz", "Menos luz"), ("#2563eb", "#b45309")):
        for ax, values, unit in zip(axes, (result.illumination, result.photo_pa, result.voltage_mv[0]),
                                   ("L (adimensional)", "ΔI foto (pA)", "V cono (mV)")):
            ax.plot(result.time_ms, values, label=label, color=color,
                    drawstyle="default" if ax is axes[2] else "steps-post")
            _decorate(ax, unit)
    axes[0].legend()
    axes[-1].set_xlabel("Tiempo (ms)")
    fig.suptitle("Del estímulo al cono · simulación ilustrativa, sin adaptación")
    return fig


def plot_transfer(parameters: M0Parameters = M0Parameters()) -> Figure:
    """Curvas algebraicas originales; una liberación, dos dependencias de apertura."""
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.5), layout="constrained")
    voltage = np.linspace(-70, -10, 401)
    fraction = np.linspace(0, 1, 401)
    axes[0].plot(voltage, release_fraction(voltage, parameters), color="#6d28d9")
    axes[0].scatter(parameters.leak_reversal_mv[0], release_fraction(parameters.leak_reversal_mv[0], parameters),
                    label="Fondo L0", color="black", zorder=3)
    axes[0].set(xlabel="V cono (mV)", title="Despolarizar el cono aumenta r")
    _decorate(axes[0], "r (fracción normalizada)")
    axes[0].legend()
    for i, values in enumerate(synaptic_conductances(fraction, parameters)):
        axes[1].plot(fraction, values, color=COLORS[i+1], label=LABELS[i+1])
    axes[1].set(xlabel="r (fracción normalizada)", title="Dos conductancias catiónicas no negativas")
    _decorate(axes[1], "g sináptica (nS)")
    axes[1].legend()
    fig.suptitle("Hipótesis algebraicas de M0 · no son curvas experimentales")
    return fig


def plot_voltage_experiments(results: Sequence[M0Result], titles: Sequence[str]) -> Figure:
    """Compara intervenciones en tres voltajes; cada columna usa su reposo correcto."""
    if len(results) != len(titles) or not results:
        raise ValueError("Se requiere un título por experimento")
    fig, axes = plt.subplots(2, len(results), figsize=(5*len(results), 6), sharex=True,
                             sharey="row", squeeze=False, layout="constrained")
    for column, (result, title) in enumerate(zip(results, titles)):
        axes[0, column].set_title(title)
        axes[0, column].plot(result.time_ms, result.illumination, color=COLORS[0], drawstyle="steps-post")
        for i in range(3):
            axes[1, column].plot(result.time_ms, result.delta_voltage_mv[i], label=LABELS[i], color=COLORS[i])
        axes[1, column].axhline(0, color="gray", lw=.6)
        axes[1, column].legend()
        axes[1, column].set_xlabel("Tiempo (ms)")
        _decorate(axes[0, column], "L (adimensional)" if column == 0 else "")
        _decorate(axes[1, column], "ΔV desde reposo (mV)" if column == 0 else "")
    fig.suptitle("Intervenciones M0 · simulación, parámetros ilustrativos y no calibrados")
    return fig


def plot_physiology() -> Figure:
    """Diagrama conceptual original: una señal química se ramifica a dos células."""
    fig, ax = plt.subplots(figsize=(11, 6), layout="constrained")
    ax.set(xlim=(0, 10), ylim=(0, 6)); ax.axis("off")
    boxes = [(3.3, 4.3, 3.4, 1, "CONO\nMás luz → V_C baja → r baja", COLORS[0]),
             (.3, 1.2, 4.1, 1.6, "BIPOLAR ON\nmGluR6 → control indirecto del canal\nMenos r → más g_ON → despolarización", COLORS[1]),
             (5.6, 1.2, 4.1, 1.6, "BIPOLAR OFF\niGluR (AMPA/kainato)\nMenos r → menos g_OFF → hiperpolarización", COLORS[2])]
    for x, y, width, height, text, color in boxes:
        ax.add_patch(FancyBboxPatch((x, y), width, height, boxstyle="round,pad=0.08", fc="white", ec=color, lw=2))
        ax.text(x+width/2, y+height/2, text, ha="center", va="center", fontsize=11, linespacing=1.6)
    for x in (2.35, 7.65):
        ax.annotate("", (x, 2.9), (5, 4.2), arrowprops={"arrowstyle": "->", "lw": 1.8, "linestyle": "--", "color": "#6d28d9"})
    ax.text(5, 3.1, "Glutamato: r\nmisma señal presináptica", ha="center", color="#6d28d9", fontsize=10)
    ax.text(5, .45, "Tres células distintas · un compartimento eléctrico por célula\nFlechas discontinuas: señal química; no corriente axial · esquema no a escala", ha="center", fontsize=10)
    ax.set_title("M0 · Separación de signos por el mecanismo postsináptico", fontsize=15)
    return fig


def _resistor(ax: Axes, x: float, top: float, bottom: float, label: str) -> None:
    center = (top+bottom)/2
    ax.plot([x,x], [top,center+.5], color="black")
    ax.plot([x,x-.12,x+.12,x-.12,x+.12,x], np.linspace(center+.5,center-.5,6), color="black")
    ax.plot([x,x], [center-.5,bottom], color="black")
    ax.text(x+.22,center,label,va="center",fontsize=9)


def _source(ax: Axes, x: float, reversal: float, label: str) -> None:
    ax.plot([x,x], [3,2.75], color="black")
    ax.add_patch(Circle((x,2.4), .35, fill=False, color="black"))
    ax.plot([x,x], [2.05,.8], color="black")
    upper, lower = ("+", "−") if reversal > 0 else ("−", "+") if reversal < 0 else ("", "")
    ax.text(x,2.52,upper,ha="center",va="center",fontsize=10)
    ax.text(x,2.27,lower,ha="center",va="center",fontsize=10)
    if reversal == 0: ax.text(x,2.4,"0",ha="center",va="center",fontsize=10)
    ax.text(x+.44,2.4,f"{label}\n{reversal:g} mV",va="center",fontsize=9)


def plot_electrical(parameters: M0Parameters = M0Parameters()) -> Figure:
    """Tres RC independientes, con fuentes de reversión y sin cable intercelular.

    Las fuentes negativas tienen el polo positivo abajo; cero no lleva polaridad.
    La flecha de la fuente I_foto define corriente entrante positiva, no el signo
    de la variación para todos los estímulos. mGluR6 no se dibuja como resistor negativo.
    """
    fig, axes = plt.subplots(1, 3, figsize=(15, 6.5), layout="constrained")
    eq = background_equilibrium(parameters)
    for i, ax in enumerate(axes):
        ax.set(xlim=(0, 6.4), ylim=(0, 7)); ax.set_aspect("equal"); ax.axis("off")
        ax.set_title(f"{LABELS[i]} · una célula", color=COLORS[i], fontsize=14)
        ax.plot([.7,4.8],[5.8,5.8],color="black"); ax.plot([.7,4.8],[.8,.8],color="black")
        ax.scatter([2.5],[5.8],color=COLORS[i],zorder=3)
        ax.text(2.5,6.25,f"V* = {eq[i]:.1f} mV",ha="center",fontsize=11)
        # Rama capacitiva: dos placas separadas, no una conexión resistiva.
        ax.plot([.9,.9],[5.8,4],color="black"); ax.plot([.6,1.2],[4,4],color="black")
        ax.plot([.6,1.2],[3.7,3.7],color="black"); ax.plot([.9,.9],[3.7,.8],color="black")
        ax.text(.08,3.05,f"C\n{parameters.capacitance_pf[i]:g} pF",fontsize=9)
        _resistor(ax,2.4,5.8,3,f"gL\n{parameters.leak_ns[i]:g} nS")
        _source(ax,2.4,parameters.leak_reversal_mv[i],"E_L")
        if i:
            maximum = parameters.g_on_max_ns if i == 1 else parameters.g_off_max_ns
            if maximum == 0:
                ax.plot([4.8,4.8],[5.8,4.7],color="black")
                ax.plot([4.8,4.8],[4.1,3],color="black")
                ax.text(5.02,4.4,"g = 0\nabierta",fontsize=9,va="center")
            else:
                _resistor(ax,4.8,5.8,3,"g(r) ≥ 0\n(nS)")
            _source(ax,4.8,parameters.synaptic_reversal_mv[i-1],"E_syn")
            formula = "g_ON = gmax(1−r)" if i == 1 else "g_OFF = gmax·r"
            ax.text(3.1,.1,formula,ha="center",fontsize=10,color=COLORS[i])
        else:
            ax.plot([4.8,4.8],[5.8,3.6],color="black")
            ax.add_patch(Circle((4.8,3.1),.5,fill=False,color="black"))
            ax.annotate("", (4.8,3.45),(4.8,2.75),arrowprops={"arrowstyle":"->","color":"black"})
            ax.plot([4.8,4.8],[2.6,.8],color="black")
            ax.text(5.38,3.1,"ΔI foto\n(pA)",fontsize=9,va="center")
            ax.text(3.1,.1,"Flecha: convención entrante (+)",ha="center",fontsize=9)
        ax.text(3.6,1.05,"Exterior: 0 mV",fontsize=9,ha="center")
    fig.suptitle("Circuitos M0 · r(V_C) controla g_ON y g_OFF; no une los nodos con un cable",fontsize=14)
    fig.supxlabel("Esquema original no a escala · C, g y E ilustrativos · Equilibrio con fondo L0 > 0",fontsize=11)
    return fig
