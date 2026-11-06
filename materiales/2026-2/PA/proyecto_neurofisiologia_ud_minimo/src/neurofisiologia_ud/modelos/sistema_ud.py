"""Sistema UD-básico con notación consistente con las notas del curso."""

from __future__ import annotations

from dataclasses import asdict, dataclass
import numpy as np


@dataclass(frozen=True)
class ParametrosUDBasico:
    """Parámetros del sistema UD-básico.

    La notación sigue las ecuaciones (2.30)-(2.39) de las notas.
    Todos los potenciales están en milivolts y todas las corrientes están
    normalizadas por la capacitancia de membrana.
    """

    a_ud: float = 0.01
    a_dn: float = 10.0
    a_up: float = 2.0
    a_w: float = 0.1
    v_ud: float = -60.0
    v_up: float = 60.0
    v_dn: float = -80.0
    v_m: float = -20.0
    v_w: float = 0.0
    s_m: float = 0.22
    s_w: float = 0.11
    b_w: float = 0.35
    v_busqueda_min: float = -90.0
    v_busqueda_max: float = 60.0

    def como_diccionario(self) -> dict[str, float]:
        """Devuelve una copia serializable de los parámetros."""
        return asdict(self)


class SistemaUDBasico:
    """Implementa el sistema UD-básico de dos variables (v, w).

    Ecuaciones principales
    ----------------------
    dw/dt = alpha(v) - rho(v) w
    dv/dt = J_F - J_UD(v) - J_U(v) - J_D(v, w)

    con
    J_U(v)  = a_up * S_m(v) * (v - v_up)
    J_D(v,w)= a_dn * w * (v - v_dn)
    J_UD(v) = a_ud * (v - v_ud)
    """

    def __init__(self, parametros: ParametrosUDBasico | None = None) -> None:
        self.parametros = parametros or ParametrosUDBasico()

    def S_m(self, v: np.ndarray | float) -> np.ndarray | float:
        """Estado estacionario de activación de la corriente J_U.

        Implementa S_m(v) = 1 / (1 + exp((v_m - v) * s_m)).
        """
        p = self.parametros
        return 1.0 / (1.0 + np.exp((p.v_m - v) * p.s_m))

    def alpha(self, v: np.ndarray | float) -> np.ndarray | float:
        """Tasa de activación de w.

        Implementa alpha(v) = a_w * exp(s_w * b_w * (v - v_w)).
        """
        p = self.parametros
        return p.a_w * np.exp(p.s_w * p.b_w * (v - p.v_w))

    def beta(self, v: np.ndarray | float) -> np.ndarray | float:
        """Tasa de desactivación de w.

        Implementa beta(v) = a_w * exp(s_w * (b_w - 1) * (v - v_w)).
        """
        p = self.parametros
        return p.a_w * np.exp(p.s_w * (p.b_w - 1.0) * (v - p.v_w))

    def rho(self, v: np.ndarray | float) -> np.ndarray | float:
        """Suma de tasas rho(v) = alpha(v) + beta(v)."""
        return self.alpha(v) + self.beta(v)

    def S_w(self, v: np.ndarray | float) -> np.ndarray | float:
        """Estado estacionario de w.

        Como dw/dt = alpha(v) - rho(v) w, entonces S_w(v) = alpha(v) / rho(v).
        """
        return self.alpha(v) / self.rho(v)

    def J_UD(self, v: np.ndarray | float) -> np.ndarray | float:
        """Corriente de goteo o corriente pequeña J_UD(v)."""
        p = self.parametros
        return p.a_ud * (v - p.v_ud)

    def J_U(self, v: np.ndarray | float) -> np.ndarray | float:
        """Corriente up que depende solo de v."""
        p = self.parametros
        return p.a_up * self.S_m(v) * (v - p.v_up)

    def D(self, v: np.ndarray | float) -> np.ndarray | float:
        """Factor lineal de la corriente down: D(v) = a_dn * (v - v_dn)."""
        p = self.parametros
        return p.a_dn * (v - p.v_dn)

    def J_D(self, v: np.ndarray | float, w: np.ndarray | float) -> np.ndarray | float:
        """Corriente down acoplada a la compuerta w."""
        return w * self.D(v)

    def H(self, v: np.ndarray | float, j_f: np.ndarray | float) -> np.ndarray | float:
        """Parte de dv/dt independiente de w.

        H(v) = J_F - J_U(v) - J_UD(v).
        """
        return j_f - self.J_U(v) - self.J_UD(v)

    def dv_dt(self, v: np.ndarray | float, w: np.ndarray | float, j_f: np.ndarray | float) -> np.ndarray | float:
        """Evalúa dv/dt = H(v) - w * D(v)."""
        return self.H(v, j_f) - self.J_D(v, w)

    def dw_dt(self, v: np.ndarray | float, w: np.ndarray | float) -> np.ndarray | float:
        """Evalúa dw/dt = alpha(v) - rho(v) * w."""
        return self.alpha(v) - self.rho(v) * w

    def actualizar_w_exponencial(self, w: np.ndarray | float, v: np.ndarray | float, dt: float) -> np.ndarray | float:
        """Actualiza w usando la solución exacta con v congelado en el paso.

        Si v es constante dentro del paso, entonces
        w_{n+1} = S_w(v) + (w_n - S_w(v)) * exp(-rho(v) * dt).
        """
        s_w = self.S_w(v)
        return s_w + (w - s_w) * np.exp(-self.rho(v) * dt)

    def nullclina_v(self, v: np.ndarray, j_f: float) -> np.ndarray:
        """Evalúa la nullclina de v: N_v(v) = H(v) / D(v)."""
        denominador = self.D(v)
        with np.errstate(divide="ignore", invalid="ignore"):
            salida = self.H(v, j_f) / denominador
        return salida

    def nullclina_w(self, v: np.ndarray) -> np.ndarray:
        """Evalúa la nullclina de w, que coincide con S_w(v)."""
        return self.S_w(v)

    def derivada_S_m(self, v: np.ndarray | float) -> np.ndarray | float:
        """Derivada de S_m con respecto a v."""
        s_m = self.S_m(v)
        return self.parametros.s_m * s_m * (1.0 - s_m)

    def jacobiana_vw(self, v: float, w: float, j_f: float) -> np.ndarray:
        """Devuelve la jacobiana en el orden de variables (v, w).

        La matriz devuelta es
            [[d(dv/dt)/dv, d(dv/dt)/dw],
             [d(dw/dt)/dv, d(dw/dt)/dw]].
        """
        p = self.parametros
        s_m = self.S_m(v)
        ds_m = self.derivada_S_m(v)
        dJ_u = p.a_up * (ds_m * (v - p.v_up) + s_m)
        alpha = self.alpha(v)
        beta = self.beta(v)
        d_alpha = p.s_w * p.b_w * alpha
        d_beta = p.s_w * (p.b_w - 1.0) * beta
        d_rho = d_alpha + d_beta
        return np.array(
            [
                [-p.a_ud - dJ_u - p.a_dn * w, -self.D(v)],
                [d_alpha - d_rho * w, -self.rho(v)],
            ],
            dtype=float,
        )

    def ecuacion_puntos_fijos(self, v: np.ndarray | float, j_f: float) -> np.ndarray | float:
        """Evalúa la ecuación escalar de puntos fijos.

        Un punto fijo satisface J_F = J_U(v*) + J_D(v*, S_w(v*)) + J_UD(v*).
        """
        return j_f - self.J_U(v) - self.J_UD(v) - self.D(v) * self.S_w(v)

    def _biseccion(self, funcion, a: float, b: float, j_f: float, tolerancia: float = 1e-10, max_iter: int = 80) -> float:
        fa = funcion(a, j_f)
        fb = funcion(b, j_f)
        if fa == 0.0:
            return a
        if fb == 0.0:
            return b
        if fa * fb > 0.0:
            raise ValueError("El intervalo no encierra una raíz.")
        izq = a
        der = b
        for _ in range(max_iter):
            medio = 0.5 * (izq + der)
            fm = funcion(medio, j_f)
            if abs(fm) < tolerancia or abs(der - izq) < tolerancia:
                return medio
            if fa * fm <= 0.0:
                der = medio
                fb = fm
            else:
                izq = medio
                fa = fm
        return 0.5 * (izq + der)

    def puntos_fijos(self, j_f: float = 0.0, n_malla: int = 16384) -> list[tuple[float, float]]:
        """Busca puntos fijos por inspección de signo y bisección.

        Returns
        -------
        list[tuple[float, float]]
            Lista de pares (v*, w*) ordenados por el voltaje.
        """
        p = self.parametros
        v_malla = np.linspace(p.v_busqueda_min, p.v_busqueda_max, n_malla)
        valores = self.ecuacion_puntos_fijos(v_malla, j_f)
        cambios = np.where(np.signbit(valores[:-1]) != np.signbit(valores[1:]))[0]
        puntos: list[tuple[float, float]] = []
        for indice in cambios:
            a = float(v_malla[indice])
            b = float(v_malla[indice + 1])
            raiz = self._biseccion(self.ecuacion_puntos_fijos, a, b, j_f=j_f)
            puntos.append((raiz, float(self.S_w(raiz))))
        if not puntos:
            indice = int(np.argmin(np.abs(valores)))
            v = float(v_malla[indice])
            puntos.append((v, float(self.S_w(v))))
        return sorted(puntos, key=lambda par: par[0])

    def punto_fijo_reposo(self, j_f: float = 0.0) -> tuple[float, float]:
        """Devuelve el punto fijo de menor voltaje para usar como reposo."""
        return self.puntos_fijos(j_f=j_f)[0]
