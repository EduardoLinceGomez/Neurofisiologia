"""Cuatro escenarios reproducibles; ejecutable como módulo."""

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from .model import simulate
from .plotting import plot_simulation
from .stimulus import PhotonEvents, poisson_events


def example_stimuli() -> dict[str, PhotonEvents]:
    return {
        "oscuridad": PhotonEvents(),
        "foton_individual": PhotonEvents.from_times([1000.0]),
        "varios_fotones": PhotonEvents.from_times([1000.0, 4000.0, 6500.0]),
        "poisson_tenue": poisson_events(0.3, 10000.0, seed=2026, start_ms=1000.0),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=Path("outputs"))
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    time_ms = np.linspace(0, 16000, 801)
    for name, stimulus in example_stimuli().items():
        result = simulate(time_ms, stimulus=stimulus)
        fig, _ = plot_simulation(result, title=name.replace("_", " "))
        path = args.output_dir / f"{name}.png"
        fig.savefig(path, dpi=160)
        plt.close(fig)
        print(f"{name}: {len(stimulus.times_ms)} eventos; mínimo V_O = "
              f"{result.voltage_mv[0].min():.3f} mV; figura: {path}")


if __name__ == "__main__":
    main()
