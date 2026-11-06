"""Visualización interactiva mínima para la sección de umbral."""

from __future__ import annotations

import numpy as np
import matplotlib.pyplot as plt

from .analisis import AnalizadorUDBasico
from .cache.almacenamiento_npz import CacheUmbralNPZ
from .modelos.sistema_ud import SistemaUDBasico


class VisualizadorUmbralInteractivo:
    """Construye un widget interactivo a partir de un caché NPZ.

    La figura se crea una sola vez y luego se actualizan sus artistas para
    reducir el flickering en Jupyter / VS Code.
    """

    def __init__(self, cache: CacheUmbralNPZ, modelo: SistemaUDBasico) -> None:
        self.cache = cache
        self.modelo = modelo
        self.analizador = AnalizadorUDBasico(modelo)

    def construir(self):
        """Construye y muestra el widget interactivo.

        Returns
        -------
        ipywidgets.VBox
            Contenedor con controles y figura.
        """
        import ipywidgets as widgets
        from IPython.display import display

        plt.ioff()
        amplitudes = [float(valor) for valor in self.cache.amplitudes]
        duraciones = [float(valor) for valor in self.cache.duraciones]

        selector_amplitud = widgets.SelectionSlider(
            options=amplitudes,
            value=amplitudes[min(2, len(amplitudes) - 1)],
            description="J_F",
            continuous_update=False,
            style={"description_width": "initial"},
            layout=widgets.Layout(width="280px"),
        )
        selector_duracion = widgets.SelectionSlider(
            options=duraciones,
            value=duraciones[min(1, len(duraciones) - 1)],
            description="duracion (ms)",
            continuous_update=False,
            style={"description_width": "initial"},
            layout=widgets.Layout(width="280px"),
        )
        control_inicio = widgets.FloatSlider(
            value=10.0,
            min=0.0,
            max=20.0,
            step=float(self.cache.dt),
            description="inicio (ms)",
            continuous_update=False,
            style={"description_width": "initial"},
            layout=widgets.Layout(width="320px"),
        )

        fig, ejes = plt.subplots(2, 2, figsize=(10.5, 7.5))
        ax_v, ax_w, ax_j, ax_fase = ejes.ravel()
        ax_v.set(xlabel="t (ms)", ylabel="v (mV)", title="Potencial transmembranal")
        ax_w.set(xlabel="t (ms)", ylabel="w", title="Compuerta lenta")
        ax_j.set(xlabel="t (ms)", ylabel="J_F", title="Forzamiento externo")
        ax_fase.set(xlabel="v (mV)", ylabel="w", title="Plano fase")
        ax_v.grid(True)
        ax_w.grid(True)
        ax_j.grid(True)
        ax_fase.grid(True)
        ax_fase.set_xlim(-90, 60)
        ax_fase.set_ylim(-0.05, 1.05)

        linea_v, = ax_v.plot([], [], lw=2)
        linea_w, = ax_w.plot([], [], lw=2)
        linea_j, = ax_j.plot([], [], lw=2)
        linea_trayectoria, = ax_fase.plot([], [], lw=2, label="trayectoria")
        linea_nv, = ax_fase.plot([], [], ls="--", lw=2, label="N_v")
        linea_nw, = ax_fase.plot([], [], ls=":", lw=2, label="N_w")
        linea_umbral, = ax_fase.plot([], [], lw=1.5, label="T(v)")
        texto = ax_v.text(0.02, 0.95, "", transform=ax_v.transAxes, va="top")
        ax_fase.legend(loc="best")
        fig.tight_layout()

        v_malla = np.linspace(-90.0, 60.0, 600)

        def actualizar(*_):
            amplitud = float(selector_amplitud.value)
            duracion = float(selector_duracion.value)
            inicio_ms = float(control_inicio.value)
            datos = self.cache.trayectoria(amplitud=amplitud, duracion=duracion, inicio_ms=inicio_ms)
            resumen = self.analizador.resumen_pulso(datos["t"], datos["v"], umbral_v=0.0)
            linea_v.set_data(datos["t"], datos["v"])
            linea_w.set_data(datos["t"], datos["w"])
            linea_j.set_data(datos["t"], datos["j_f"])
            linea_trayectoria.set_data(datos["v"], datos["w"])
            linea_nv.set_data(v_malla, self.modelo.nullclina_v(v_malla, j_f=amplitud))
            linea_nw.set_data(v_malla, self.modelo.nullclina_w(v_malla))
            linea_umbral.set_data(v_malla, self.analizador.curva_umbral(v_malla, j_f=amplitud))
            texto.set_text(
                f"pulso: {'si' if resumen.hay_pulso else 'no'}\n"
                f"v_max = {resumen.v_max:.2f} mV\n"
                f"t_max = {resumen.t_v_max:.2f} ms"
            )
            ax_v.set_xlim(float(datos["t"][0]), float(datos["t"][-1]))
            ax_v.set_ylim(float(np.min(datos["v"]) - 5.0), float(np.max(datos["v"]) + 5.0))
            ax_w.set_xlim(float(datos["t"][0]), float(datos["t"][-1]))
            ax_w.set_ylim(-0.05, 1.05)
            ax_j.set_xlim(float(datos["t"][0]), float(datos["t"][-1]))
            ax_j.set_ylim(float(np.min(datos["j_f"]) - 1.0), float(np.max(datos["j_f"]) + 1.0))
            fig.canvas.draw_idle()

        selector_amplitud.observe(actualizar, names="value")
        selector_duracion.observe(actualizar, names="value")
        control_inicio.observe(actualizar, names="value")

        contenedor = widgets.VBox([
            widgets.HTML("<h3>Demo mínima: sistema UD-básico</h3>"),
            widgets.HTML(
                "<p>Las trayectorias de umbral se leen desde un caché NPZ. "
                "Cambiar el inicio del pulso solo desplaza los datos, sin resimular.</p>"
            ),
            widgets.HBox([selector_amplitud, selector_duracion, control_inicio]),
            fig.canvas,
        ])
        display(contenedor)
        actualizar()
        return contenedor
