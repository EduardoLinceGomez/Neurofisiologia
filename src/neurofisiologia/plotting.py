"""Figuras con unidades y procedencia; no contienen datos experimentales crudos."""

import matplotlib.pyplot as plt
import numpy as np
from numpy.typing import NDArray
from matplotlib.figure import Figure
from matplotlib.axes import Axes
from matplotlib.patches import Circle, Ellipse, Rectangle
from matplotlib.ticker import MaxNLocator
from numpy.typing import ArrayLike

from .model import SimulationResult, dark_equilibrium, decompose_currents, simulate
from .parameters import RodParameters
from .stimulus import PhotonEvents, photon_kernel
from .analysis import response_metrics, voltage_deviation
from dataclasses import replace
from typing import Literal

REGION_COLORS = ("tab:blue", "tab:orange", "tab:green")


def _circuit_current(value: float) -> str:
    """pA firmados: no redondear una corriente pequeña con flecha a cero."""
    if value == 0:
        return "0.000"
    return f"{value:+.3e}" if 0 < abs(value) < .0005 or abs(value) >= 1e4 else f"{value:+.3f}"


def _conditions(parameters: RodParameters) -> str:
    return (f"C={parameters.capacitance_pf} pF; gL={parameters.leak_ns} nS; E={parameters.reversal_mv} mV\n"
            f"gOI={parameters.g_oi_ns:g}, gIT={parameters.g_it_ns:g} nS. Ilustrativos, no calibrados; curvas simuladas.")


def _finish(fig: Figure, purpose: str, parameters: RodParameters) -> None:
    fig.suptitle(purpose)
    fig.text(.5, .015, _conditions(parameters), ha="center", fontsize=9)
    engine = fig.get_layout_engine()
    if engine is not None:
        engine.set(rect=(0, .085, 1, .91))


def plot_regions() -> tuple[Figure, Axes]:
    """Mapa conceptual anatómico O,I,T de UNA célula, no a escala ni medición.

    I agrupa aquí segmento interno, cuerpo y conexión hacia T. Las regiones
    reales no tienen fronteras de voltaje discontinuas; los nodos son una
    discretización eléctrica. No contiene valores morfométricos ni canales.
    """
    fig, axis = plt.subplots(figsize=(11, 4), layout="constrained")
    axis.set(xlim=(0, 12), ylim=(-1, 4))
    axis.axis("off")
    axis.add_patch(Rectangle((.5, 1), 2, 1.5, fill=False, edgecolor=REGION_COLORS[0], lw=2))
    for x in np.linspace(.7, 2.3, 9):
        axis.plot([x, x], [1.15, 2.35], color=REGION_COLORS[0], lw=1)
    axis.plot([2.5, 3.5], [1.75, 1.75], color="gray", lw=2)
    axis.add_patch(Ellipse((5.2, 1.75), 3.4, 1.8, fill=False, edgecolor=REGION_COLORS[1], lw=2))
    axis.plot([6.9, 8.5], [1.75, 1.75], color="gray", lw=2)
    axis.add_patch(Ellipse((9.5, 1.75), 2, 1.8, fill=False, edgecolor=REGION_COLORS[2], lw=2))
    for x, title, text, color in (
        (1.5, "O · Outer segment", "Discos con pigmento\nEntrada óptica real", REGION_COLORS[0]),
        (5.2, "I · Inner segment", "Metabolismo y gradientes\nCuerpo agrupado en I", REGION_COLORS[1]),
        (9.5, "T · Synaptic terminal", "Salida sináptica real\nEn el modelo: solo V_T", REGION_COLORS[2]),
    ):
        axis.text(x, 3.15, title, ha="center", weight="bold", color=color)
        axis.text(x, .3, text, ha="center")
    axis.text(3, 2.15, "Cilio", ha="center", fontsize=9)
    axis.text(7.7, 2.15, "Conexión intracelular", ha="center", fontsize=9)
    axis.text(5.5, -.65, "Un bastón; tres nodos de aproximación. No son tres neuronas ni sinapsis O-I/I-T.", ha="center")
    fig.suptitle("Qué regiones se agrupan y qué se omite | Esquema anatómico conceptual, no a escala")
    return fig, axis


def plot_simulation(result: SimulationResult, *, title: str = "Bastón O-I-T") -> tuple[Figure, NDArray]:
    """Devuelve figura y tres ejes: eventos ms, corriente pA y V simulado mV.

    Consume SimulationResult, orden O,I,T, sin reinterpretar las EDO. C/g/E
    son ilustrativos; no contiene una traza experimental ni spikes.
    """
    fig, axes = plt.subplots(3, 1, figsize=(10, 8), sharex=True,
                             gridspec_kw={"height_ratios": [1, 2, 3]})
    if result.stimulus.times_ms:
        axes[0].eventplot(result.stimulus.times_ms, colors="tab:purple")
    else:
        axes[0].text(0.5, 0.5, "Oscuridad: sin eventos", ha="center",
                     transform=axes[0].transAxes)
    axes[0].set(yticks=[], ylabel="Eventos\nefectivos", ylim=(-0.5, 2.5))
    axes[1].plot(result.time_ms, result.photocurrent_pa, color="tab:purple",
                 label="I_photo impuesta (fenomenológica)")
    axes[1].set_ylabel("Variación de corriente (pA)")
    axes[1].legend(loc="best")
    for voltage, label in zip(result.voltage_mv, ("O: externo", "I: interno", "T: terminal")):
        axes[2].plot(result.time_ms, voltage, label=label)
    axes[2].set_ylabel("Potencial simulado (mV)")
    axes[2].legend(loc="best")
    for ax in axes:
        ax.set_xlabel("Tiempo (ms)")
        ax.set_xlim(result.time_ms[0], result.time_ms[-1])
        ax.grid(alpha=0.25)
    fig.suptitle(title + " | Simulación pasiva, sin canales activos")
    fig.text(0.5, 0.015,
             "C, g y E ilustrativos, no calibrados. Forma de corriente aproximada; "
             "no son registros experimentales.", ha="center", fontsize=9)
    fig.tight_layout(rect=(0, 0.045, 1, 0.95))
    return fig, axes


def plot_comparison(reference: SimulationResult, modified: SimulationResult, *,
                      voltage_view: Literal["V", "delta"] = "V",
                      modified_condition: str = "") -> tuple[Figure, NDArray]:
    """Entradas y V (mV) de dos escenarios sobre t (ms), sin mezclar estímulos.

    Referencia discontinua y modificada continua. Si cambian los eventos se
    advierte variabilidad residual; el mismo color identifica O,I,T en ambas.
    C, g y E son ilustrativos. No contiene trazas experimentales.
    La referencia está destinada a compare_with_reference (escenario canónico).
    voltage_view='delta' resta el reposo propio de cada membrana: útil al
    cambiar E. modified_condition declara los controles de entrada escogidos.
    """
    if voltage_view not in ("V", "delta"):
        raise ValueError("voltage_view debe ser V o delta")
    fig, axes = plt.subplots(3, 1, figsize=(11, 8), sharex=True, layout="constrained")
    for result, label, style, y, color in (
        (reference, "Referencia fija", "--", 1, "0.45"),
        (modified, "Modificada", "-", 0, "tab:purple"),
    ):
        axes[0].eventplot(result.stimulus.times_ms, lineoffsets=y, linelengths=.5, colors=color)
        axes[1].plot(result.time_ms, result.photocurrent_pa, style, color=color, label=label)
        voltages = result.voltage_mv if voltage_view == "V" else voltage_deviation(result)
        for voltage, region, region_color in zip(voltages, "OIT", ("tab:blue", "tab:orange", "tab:green")):
            axes[2].plot(result.time_ms, voltage, style, color=region_color, label=f"{region}: {label}")
    axes[0].set(yticks=[0, 1], yticklabels=["Modificada", "Referencia fija"],
                ylabel="Eventos efectivos", ylim=(-.6, 1.6),
                xlim=(reference.time_ms[0], reference.time_ms[-1]))
    axes[1].set_ylabel("I_photo impuesta (pA)")
    axes[2].set_ylabel("V simulado (mV)" if voltage_view == "V" else "ΔV respecto del reposo propio (mV)")
    for axis in axes:
        axis.set_xlabel("Tiempo (ms)")
        axis.grid(alpha=.2)
    axes[1].legend()
    axes[2].legend(ncol=2)
    same_times = reference.stimulus.times_ms == modified.stimulus.times_ms
    condition = "Mismos tiempos de eventos" if same_times else "Realizaciones distintas: hay variabilidad aleatoria residual"
    reference_info = f"Referencia: A=1.2 pA, pico=2200 ms, 0.3 eventos/s, semilla 2026"
    title = "Referencia fija frente a controles | " + condition + "\n"+reference_info
    if modified_condition:
        title += "\nModificada: "+modified_condition
    _finish(fig, title, modified.parameters)
    return fig, axes


def plot_circuit(parameters: RodParameters = RodParameters(), *,
                  result: SimulationResult | None = None,
                  time_ms: float | None = None) -> tuple[Figure, Axes]:
    """F1/F5: circuito vectorial equivalente, no anatómico y no a escala.

    Las flechas rojas representan solo las corrientes axiales: orientación
    positiva de referencia sin result, o sentido efectivo en la muestra más
    cercana al tiempo (ms) con result. Se omiten si |I|≤1e-10 pA. La foto
    se rotula como variación algebraica entrante en O, nunca como flujo
    iónico saliente. V instantáneo y E de reversión (mV) se distinguen.
    Cada nodo tiene C (pF), fuga (nS) y fuente ideal E con polaridad explícita
    según su signo respecto del exterior 0 mV; E=0 no tiene polaridad.
    C/g/E son constantes e ilustrativos. No hay sinapsis ni datos medidos.
    """
    if result is not None:
        parameters = result.parameters
        if time_ms is None or not np.isfinite(time_ms) or not result.time_ms[0] <= time_ms <= result.time_ms[-1]:
            raise ValueError("El tiempo seleccionado debe pertenecer al intervalo simulado")
        index = int(np.argmin(abs(result.time_ms-time_ms)))
        components = decompose_currents(result.time_ms[index], result.voltage_mv[:, index], parameters, result.stimulus)
    if result is None:
        fig, axis = plt.subplots(figsize=(14, 8), layout="constrained")
    else:
        fig, panels = plt.subplots(2, 1, figsize=(14, 11), layout="constrained",
                                   gridspec_kw={"height_ratios": [4, 1.4]})
        axis, timeline = panels
        for j, color in enumerate(REGION_COLORS):
            timeline.plot(result.time_ms, result.voltage_mv[j], color=color, label="OIT"[j])
            timeline.scatter(result.time_ms[index], result.voltage_mv[j, index], color=color, s=20)
        timeline.axvline(result.time_ms[index], color="black", ls=":", label="Muestra seleccionada")
        timeline.set(xlabel="Tiempo (ms)", ylabel="V simulado (mV)")
        timeline.legend(ncol=4, fontsize=9)
        timeline.grid(alpha=.2)
    positions = (2., 8., 14.)
    axis.set(xlim=(-2, 18), ylim=(-1.3, 9.4), aspect="equal")
    axis.axis("off")
    photo_label = ("I_photo(t) = −Σ A_k h(t − t_k)  [pA]" if result is None
                   else f"I_photo(t) = {_circuit_current(float(components['photocurrent_pa'][0]))} pA")
    axis.text(8, 8.25, "Entrada algebraica solo en O · corriente entrante positiva\n"
              + photo_label + "\nVariación de corriente entrante de oscuridad; no indica flujo iónico absoluto hacia fuera.",
              ha="center", va="center", fontsize=11, color="tab:purple",
              bbox={"boxstyle": "round,pad=0.6", "facecolor": "#faf6ff", "edgecolor": "tab:purple"},
              gid="photocurrent-algebraic")
    axis.plot([.9, 15.1], [0, 0], color="black")
    axis.text(8, -.45, "Referencia exterior: 0 mV · V: potencial interior instantáneo respecto del exterior",
              ha="center", va="center", fontsize=11, gid="exterior-reference")
    axis.text(8, -.95, "E: potencial de reversión de la fuga (fuente equivalente fija); no es V instantáneo",
              ha="center", va="center", fontsize=11, gid="reversal-definition")
    for region, x, color, capacitance, leak, reversal in zip("OIT", positions, REGION_COLORS,
            parameters.capacitance_pf, parameters.leak_ns, parameters.reversal_mv):
        axis.add_patch(Circle((x, 4.3), .18, facecolor=color, edgecolor="black"))
        axis.text(x, 6.75, region, color=color, ha="center", fontsize=16, weight="bold")
        if result is not None:
            j = "OIT".index(region)
            axis.text(x, 6.1, f"V_{region}={result.voltage_mv[j,index]:+.3f} mV", ha="center",
                      fontsize=12, gid=f"voltage-{region}")
            axis.text(x, 5.5, f"I neta={_circuit_current(float(components['net_current_pa'][j]))} pA", ha="center",
                      fontsize=11, gid=f"net-current-{region}")
        cap_branch = x-1.1
        axis.plot([x, cap_branch, cap_branch], [4.3, 4.3, 2.2], color="black")
        axis.plot([cap_branch-.4, cap_branch+.4], [2.2, 2.2], color="black")
        axis.plot([cap_branch-.4, cap_branch+.4], [2., 2.], color="black")
        axis.plot([cap_branch, cap_branch], [2., 0], color="black")
        axis.text(cap_branch-.15, 2.8, f"C={capacitance:g}\npF", ha="right", va="center", fontsize=11)
        branch = x+1.1
        axis.plot([x, branch, branch], [4.3, 4.3, 3.], color="black")
        axis.plot([branch, branch-.15, branch+.15, branch-.15, branch+.15, branch],
                  [3., 2.84, 2.68, 2.52, 2.36, 2.2], color="black")
        axis.plot([branch, branch], [2.2, 1.6], color="black")
        axis.add_patch(Circle((branch, 1.15), .45, fill=False, edgecolor="black",
                              gid=f"reversal-source-{region}"))
        if reversal == 0:
            axis.text(branch, 1.15, "0", ha="center", va="center", fontsize=12,
                      gid=f"source-zero-{region}")
        else:
            upper, lower = (("+", "−") if reversal > 0 else ("−", "+"))
            axis.text(branch, 1.35, upper, ha="center", va="center", fontsize=12,
                      gid=f"source-upper-{region}")
            axis.text(branch, .95, lower, ha="center", va="center", fontsize=12,
                      gid=f"source-lower-{region}")
        axis.plot([branch, branch], [.7, 0], color="black")
        axis.text(branch+.4, 2.65, f"gL={leak:g}\nnS", va="center", fontsize=11)
        reversal_label = f"{reversal:+g}" if reversal != 0 else "0"
        axis.text(branch+.65, 1.15, f"E={reversal_label}\nmV", va="center", fontsize=11,
                  gid=f"reversal-label-{region}")
    for left, right, conductance, name, key in (
        (positions[0], positions[1], parameters.g_oi_ns, "O→I", "axial_current_oi_pa"),
        (positions[1], positions[2], parameters.g_it_ns, "I→T", "axial_current_it_pa"),
    ):
        center = (left+right)/2
        axis.plot([left+.18, center-.5], [4.3, 4.3], color="black")
        axis.plot([center+.5, right-.18], [4.3, 4.3], color="black")
        if conductance == 0:
            axis.plot([center-.5, center-.15], [4.3, 4.3], color="black")
            axis.plot([center+.15, center+.5], [4.3, 4.3], color="black")
            axis.scatter([center-.15, center+.15], [4.3, 4.3], facecolors="white", edgecolors="black", s=20)
        else:
            axis.plot(np.linspace(center-.5, center+.5, 7),
                      [4.3, 4.42, 4.18, 4.42, 4.18, 4.42, 4.3], color="black")
        axis.text(center, 4.75, f"g_{name.replace('→','')}={conductance:g} nS"
                  + (" (abierto)" if conductance == 0 else ""), ha="center", fontsize=11)
        current = (1. if conductance > 0 else 0.) if result is None else float(components[key])
        label = f"I {name} (sentido +)" if result is None else f"I {name}={_circuit_current(current)} pA"
        axis.text(center, 3.25, label, ha="center", fontsize=11,
                  gid=f"axial-label-{name.replace('→','')}")
        if abs(current) > 1e-10:
            start, end = ((center-.6, center+.6) if current > 0 else (center+.6, center-.6))
            axis.annotate("", (end, 3.85), (start, 3.85),
                          arrowprops={"arrowstyle": "->", "color": "tab:red", "lw": 2},
                          gid=f"axial-arrow-{name.replace('→','')}")
    purpose = ("F1 · Almacenamiento, fuga y conexiones en una sola célula | Circuito equivalente, no a escala\n"
               "Flechas rojas: orientación axial positiva de referencia; no son corrientes medidas")
    if result is not None:
        purpose = (f"F5 · Corrientes y voltajes simulados | Muestra t={result.time_ms[index]:g} ms\n"
                   "Circuito equivalente, no a escala · flechas rojas: sentido axial efectivo; sin flecha si |I| ≤ 10⁻¹⁰ pA")
    _finish(fig, purpose, parameters)
    fig.texts[-1].set_text("C, gL, E y acoplamientos rotulados: constantes durante esta simulación.\n"
                           "Parámetros ilustrativos, no calibrados; esquema y curvas no son mediciones.")
    return fig, axis


def plot_kernel_events(result: SimulationResult) -> tuple[Figure, NDArray]:
    """F2: h adimensional, eventos ms e I_photo impuesta pA; no datos crudos."""
    fig, axes = plt.subplots(3, 1, figsize=(10, 7), layout="constrained")
    elapsed = np.linspace(-500, 4*result.stimulus.t_peak_ms, 501)
    axes[0].plot(elapsed, photon_kernel(elapsed, result.stimulus.t_peak_ms), color="tab:purple")
    axes[0].axvline(result.stimulus.t_peak_ms, color="gray", ls="--", label=f"Máximo de h: {result.stimulus.t_peak_ms:g} ms")
    axes[0].set(xlabel="Tiempo desde un evento (ms)", ylabel="h (adimensional)")
    axes[0].legend()
    axes[1].eventplot(result.stimulus.times_ms, colors="tab:purple")
    axes[1].set(yticks=[], xlabel="Tiempo (ms)", ylabel="Eventos efectivos", xlim=(result.time_ms[0], result.time_ms[-1]))
    axes[2].plot(result.time_ms, result.photocurrent_pa, color="tab:purple", label="Entrada impuesta -Σ A h")
    axes[2].set(xlabel="Tiempo (ms)", ylabel="I_photo (pA)")
    axes[2].legend()
    for axis in axes:
        axis.grid(alpha=.2)
    _finish(fig, "F2 · Distinguir evento, forma temporal y corriente | Kernel fenomenológico", result.parameters)
    return fig, axes


def plot_voltages(result: SimulationResult) -> tuple[Figure, NDArray]:
    """F3: V y ΔV (mV), reposo y mínimos muestreados; tiempos en ms."""
    fig, axes = plt.subplots(2, 1, figsize=(11, 7), sharex=True, layout="constrained")
    rest = dark_equilibrium(result.parameters)
    deviations = voltage_deviation(result)
    measures = response_metrics(result)
    for j, (region, color) in enumerate(zip("OIT", REGION_COLORS)):
        axes[0].plot(result.time_ms, result.voltage_mv[j], color=color, label=region)
        axes[0].axhline(rest[j], color=color, ls=":", alpha=.6, label=f"Reposo {region}")
        axes[1].plot(result.time_ms, deviations[j], color=color, label=region)
        if np.isfinite(measures["time_min_ms"][j]):
            axes[1].scatter(measures["time_min_ms"][j], measures["min_delta_mv"][j], color=color, marker="x")
    axes[0].set_ylabel("V absoluto (mV)")
    axes[1].set_ylabel("ΔV respecto del reposo (mV)")
    axes[1].axhline(0, color="black", ls=":", lw=.7)
    for axis in axes:
        axis.set_xlabel("Tiempo (ms)")
        axis.legend(ncol=3)
        axis.grid(alpha=.2)
    _finish(fig, "F3 · Separar potencial absoluto y respuesta a luz | × = mínimo de ΔV muestreado", result.parameters)
    return fig, axes


def plot_currents(result: SimulationResult) -> tuple[Figure, NDArray]:
    """F4: corrientes entrantes por nodo (pA), neta y contribuciones O-I/I-T."""
    components = decompose_currents(result.time_ms, result.voltage_mv, result.parameters, result.stimulus)
    fig, axes = plt.subplots(3, 1, figsize=(11, 9), sharex=True, layout="constrained")
    for j, axis in enumerate(axes):
        for key, label, color, style in (
            ("photocurrent_pa", "Foto impuesta", "tab:purple", "-"),
            ("leak_current_pa", "Fuga", "tab:orange", "-"),
            ("axial_oi_by_node_pa", "Axial O-I", "tab:blue", "--"),
            ("axial_it_by_node_pa", "Axial I-T", "tab:green", ":"),
            ("net_current_pa", "Neta = suma", "black", "-"),
        ):
            axis.plot(result.time_ms, components[key][j], color=color, ls=style, label=label)
        axis.axhline(0, color="gray", lw=.5)
        axis.set(xlabel="Tiempo (ms)", ylabel=f"Corriente entrante en {'OIT'[j]} (pA)")
        axis.legend(ncol=3, fontsize=9)
        axis.grid(alpha=.2)
    _finish(fig, "F4 · Explicar dV/dt mediante suma de corrientes | Neta/C = dV/dt (mV/ms)", result.parameters)
    return fig, axes


def plot_topologies(time_ms: ArrayLike, stimulus: PhotonEvents,
                     parameters: RodParameters = RodParameters()) -> tuple[Figure, NDArray]:
    """F6: O aislado, O-I con T aislada y O-I-T, mismas C/gL/E/entrada.

    ΔV (mV) contra ms; los nodos aislados siguen presentes en las tres EDO
    pero permanecen en su reposo. No cambia la anatomía ni el modelo físico.
    """
    fig, axes = plt.subplots(1, 3, figsize=(13, 5), sharey=True, layout="constrained")
    for label, varied, style in (
        ("O aislado", replace(parameters, g_oi_ns=0, g_it_ns=0), ":"),
        ("Pareja O-I", replace(parameters, g_it_ns=0), "--"),
        ("Trío O-I-T", parameters, "-"),
    ):
        result = simulate(time_ms, varied, stimulus)
        for j, axis in enumerate(axes):
            axis.plot(result.time_ms, voltage_deviation(result)[j], style, color=REGION_COLORS[j], label=label)
    for j, axis in enumerate(axes):
        axis.set(title=f"Región {'OIT'[j]}", xlabel="Tiempo (ms)", ylabel="ΔV simulado (mV)")
        axis.legend(fontsize=9)
        axis.grid(alpha=.2)
        axis.set_xlim(result.time_ms[0], result.time_ms[-1])
        axis.xaxis.set_major_locator(MaxNLocator(nbins=4))
    _finish(fig, "F6 · Qué permite llegar a T | Misma entrada y parámetros locales; solo cambia acoplamiento", parameters)
    return fig, axes


def plot_sensitivity(g_oi_ns: ArrayLike, g_it_ns: ArrayLike, values: ArrayLike, *,
                       parameters: RodParameters = RodParameters(),
                       metric_label: str = "|mínimo ΔV_T| (mV)") -> tuple[Figure, Axes]:
    """F7: celdas evaluadas de un barrido, sin interpolación ni extrapolación.

    g_OI (x), g_IT (y), nS; colors = values [filas IT, columnas OI]. La
    etiqueta especifica magnitud/unidad. Una × marca valores base.
    """
    values_oi, values_it, grid = np.asarray(g_oi_ns), np.asarray(g_it_ns), np.asarray(values)
    if grid.shape != (len(values_it), len(values_oi)):
        raise ValueError("values debe tener filas g_IT y columnas g_OI")
    fig, axis = plt.subplots(figsize=(8, 6), layout="constrained")
    mesh = axis.pcolormesh(values_oi, values_it, grid, shading="nearest", cmap="viridis")
    fig.colorbar(mesh, ax=axis, label=metric_label)
    axis.scatter(parameters.g_oi_ns, parameters.g_it_ns, marker="x", s=90, color="white", label="Valores base")
    axis.set(xlabel="g_OI (nS)", ylabel="g_IT (nS)",
             xlim=(values_oi.min(), values_oi.max()), ylim=(values_it.min(), values_it.max()))
    axis.legend(loc="upper left", facecolor="0.2", labelcolor="white")
    _finish(fig, "F7 · Medir sensibilidad en una región evaluada | Escala de color lineal; misma entrada", parameters)
    return fig, axis


def plot_poisson_variability(ensembles: dict[float, tuple[SimulationResult, ...]],
                              seeds: tuple[int, ...]) -> tuple[Figure, NDArray]:
    """F8: primera realización y media±DE de ΔV_T, no intervalos de confianza.

    Tasas (eventos efectivos/s), semilla de primera entrada y número de
    realizaciones se rotulan. Eventos/corrientes individuales no equivalen
    a un efecto puro de tasa. Se conservan A, C, fugas, E y acoplamientos.
    """
    if not ensembles or any(len(results) != len(seeds) or not results for results in ensembles.values()):
        raise ValueError("Cada tasa debe tener una realización por semilla")
    fig, axes = plt.subplots(3, 1, figsize=(11, 8), sharex=True, layout="constrained")
    for row, (rate, results) in enumerate(ensembles.items()):
        result = results[0]
        color = f"C{row}"
        label = f"{rate:g} eventos/s"
        axes[0].eventplot(result.stimulus.times_ms, lineoffsets=row, linelengths=.5, colors=color)
        axes[1].plot(result.time_ms, result.photocurrent_pa, color=color, label=label+f"; semilla {seeds[0]}")
        terminal = np.stack([voltage_deviation(r)[2] for r in results])
        mean, std = terminal.mean(axis=0), terminal.std(axis=0, ddof=1) if len(results)>1 else np.zeros_like(terminal[0])
        axes[2].plot(result.time_ms, mean, color=color, label=label+f"; media de {len(results)} realizaciones")
        axes[2].fill_between(result.time_ms, mean-std, mean+std, alpha=.2, color=color, label="±1 DE muestral")
    axes[0].set(yticks=range(len(ensembles)), yticklabels=[f"{r:g}/s" for r in ensembles],
                ylabel="Eventos efectivos", xlim=(result.time_ms[0], result.time_ms[-1]))
    axes[1].set_ylabel("I_photo de una realización (pA)")
    axes[2].set_ylabel("ΔV_T simulado (mV)")
    for axis in axes:
        axis.set_xlabel("Tiempo (ms)")
        axis.grid(alpha=.2)
    axes[1].legend(fontsize=9)
    axes[2].legend(fontsize=9)
    _finish(fig, "F8 · Separar tasa y variabilidad | Banda = dispersión entre semillas, NO medición ni IC", result.parameters)
    return fig, axes
