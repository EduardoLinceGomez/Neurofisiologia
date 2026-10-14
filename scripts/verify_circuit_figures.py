"""Regenera evidencia F1/F5 con signos y parámetros adversariales en outputs/."""

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from neurofisiologia import PhotonEvents, RodParameters, simulate
from neurofisiologia.plotting import plot_circuit


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    output = root / "outputs/auditoria_circuito"
    output.mkdir(parents=True, exist_ok=True)
    parameters = {
        "negativo": RodParameters(),
        "positivo": RodParameters(reversal_mv=(40, 40, 40)),
        "cero": RodParameters(reversal_mv=(0, 0, 0)),
        "mixto": RodParameters(capacitance_pf=(200, .5, 123.456),
            leak_ns=(.001, 2, .123456), reversal_mv=(-123.456, 12.3456, 0),
            g_oi_ns=0, g_it_ns=1.23456),
    }
    times = np.linspace(0, 12000, 601)
    # La misma entrada en todos los casos; solo cambian C/g/E indicados.
    stimulus = PhotonEvents.from_times([1000])
    for case, params in parameters.items():
        result = simulate(times, params, stimulus)
        for time in (None, 0, 3440, 12000):
            kwargs = {} if time is None else {"result": result, "time_ms": time}
            figure, _ = plot_circuit(params, **kwargs)
            name = f"F1_{case}" if time is None else f"F5_{case}_{time}ms"
            figure.savefig(output / f"{name}.png", dpi=150)
            with plt.rc_context({"svg.fonttype": "none"}):
                figure.savefig(output / f"{name}.svg")
            plt.close(figure)
    print(f"16 PNG y 16 SVG de auditoría generados en {output}")


if __name__ == "__main__":
    main()
