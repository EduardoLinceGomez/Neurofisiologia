"""Figuras con unidades y procedencia; no contienen datos experimentales crudos."""

import matplotlib.pyplot as plt

from .model import SimulationResult


def plot_simulation(result: SimulationResult, *, title="Bastón O-I-T"):
    """Eventos efectivos, corriente impuesta y potenciales simulados."""
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
