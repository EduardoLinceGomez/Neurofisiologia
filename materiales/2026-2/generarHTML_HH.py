from pathlib import Path


def generar_html_hh_umbral(ruta_salida: str = "hh_umbral_interactivo.html") -> None:
    """
    Genera un archivo HTML autocontenido (salvo la carga de Plotly desde CDN)
    con una interfaz interactiva para estudiar el umbral de excitación en el
    modelo de Hodgkin-Huxley.

    El HTML contiene:
    - controles deslizantes para amplitud, inicio y duración del pulso,
    - gráfica de potencial de membrana,
    - gráfica de compuertas m, h, n,
    - gráfica de corrientes I_Na, I_K, I_L e I_ext,
    - plano reducido (V, n) con nullclines aproximadas,
    - resumen de detección de spike.

    Notas:
    - La simulación se ejecuta en JavaScript dentro del navegador.
    - Para mayor fluidez, se usa dt = 0.02 ms por defecto.
    - Si quieres más fidelidad, puedes cambiar DT a 0.01 dentro del HTML.
    """

    html = r"""<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Hodgkin-Huxley - Umbral de excitación</title>
  <script src="https://cdn.plot.ly/plotly-2.35.2.min.js"></script>
  <style>
    :root {
      --fondo: #0f172a;
      --panel: #111827;
      --panel-2: #1f2937;
      --texto: #e5e7eb;
      --subtexto: #cbd5e1;
      --borde: #334155;
      --acento: #60a5fa;
      --verde: #34d399;
      --amarillo: #fbbf24;
      --rosa: #f472b6;
      --gris: #94a3b8;
    }

    * {
      box-sizing: border-box;
    }

    body {
      margin: 0;
      padding: 0;
      font-family: Arial, Helvetica, sans-serif;
      background: var(--fondo);
      color: var(--texto);
    }

    .contenedor {
      max-width: 1500px;
      margin: 0 auto;
      padding: 20px;
    }

    .cabecera {
      margin-bottom: 18px;
    }

    .cabecera h1 {
      margin: 0 0 8px 0;
      font-size: 28px;
    }

    .cabecera p {
      margin: 0;
      color: var(--subtexto);
      line-height: 1.5;
    }

    .panel-controles {
      background: var(--panel);
      border: 1px solid var(--borde);
      border-radius: 14px;
      padding: 16px;
      margin-bottom: 18px;
    }

    .fila-controles {
      display: grid;
      grid-template-columns: repeat(3, minmax(260px, 1fr));
      gap: 18px;
    }

    .control {
      background: var(--panel-2);
      border: 1px solid var(--borde);
      border-radius: 12px;
      padding: 12px;
    }

    .control label {
      display: block;
      font-weight: bold;
      margin-bottom: 8px;
    }

    .control .valor {
      color: var(--acento);
      font-weight: bold;
      margin-left: 8px;
    }

    .control input[type="range"] {
      width: 100%;
    }

    .resumen {
      margin-top: 16px;
      background: var(--panel-2);
      border: 1px solid var(--borde);
      border-radius: 12px;
      padding: 12px;
      color: var(--subtexto);
      line-height: 1.6;
      white-space: pre-line;
    }

    .rejilla {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 18px;
    }

    .grafica {
      background: var(--panel);
      border: 1px solid var(--borde);
      border-radius: 14px;
      padding: 8px;
      min-height: 420px;
    }

    .pie {
      margin-top: 18px;
      color: var(--subtexto);
      font-size: 14px;
      line-height: 1.5;
    }

    @media (max-width: 1100px) {
      .fila-controles {
        grid-template-columns: 1fr;
      }

      .rejilla {
        grid-template-columns: 1fr;
      }
    }
  </style>
</head>
<body>
  <div class="contenedor">
    <div class="cabecera">
      <h1>Hodgkin-Huxley: Umbral de excitación</h1>
      <p>
        Interfaz interactiva en HTML para explorar el efecto de un pulso de corriente
        sobre el potencial de acción. La simulación se ejecuta directamente en el navegador.
      </p>
    </div>

    <div class="panel-controles">
      <div class="fila-controles">
        <div class="control">
          <label for="slider-amplitud">
            Amplitud de corriente
            <span class="valor" id="valor-amplitud">8.0</span> μA/cm²
          </label>
          <input id="slider-amplitud" type="range" min="0" max="20" step="0.5" value="8.0">
        </div>

        <div class="control">
          <label for="slider-inicio">
            Inicio del pulso
            <span class="valor" id="valor-inicio">10.0</span> ms
          </label>
          <input id="slider-inicio" type="range" min="2" max="20" step="0.5" value="10.0">
        </div>

        <div class="control">
          <label for="slider-duracion">
            Duración del pulso
            <span class="valor" id="valor-duracion">1.0</span> ms
          </label>
          <input id="slider-duracion" type="range" min="0.1" max="5" step="0.1" value="1.0">
        </div>
      </div>

      <div class="resumen" id="resumen">
        Calculando...
      </div>
    </div>

    <div class="rejilla">
      <div class="grafica" id="grafica-voltaje"></div>
      <div class="grafica" id="grafica-compuertas"></div>
      <div class="grafica" id="grafica-corrientes"></div>
      <div class="grafica" id="grafica-plano"></div>
    </div>

    <div class="pie">
      <strong>Nota:</strong> esta versión usa un paso temporal de 0.02 ms para que la interacción
      sea más fluida. Si prefieres más resolución, cambia la constante <code>DT</code> dentro del
      script JavaScript embebido.
    </div>
  </div>

  <script>
    // ============================================================
    // Parámetros del modelo
    // ============================================================
    const PARAMS = {
      Cm: 1.0,
      gNa: 120.0,
      gK: 36.0,
      gL: 0.3,
      ENa: 50.0,
      EK: -77.0,
      EL: -54.4,
      V_rest: -65.0
    };

    // Para mayor fluidez en HTML
    const T_MAX = 40.0;
    const DT = 0.02;

    // Rejilla para el plano reducido
    const V_GRID = linspace(-90, 60, 400);

    // ============================================================
    // Utilidades
    // ============================================================
    function linspace(a, b, n) {
      const out = new Array(n);
      const paso = (b - a) / (n - 1);
      for (let i = 0; i < n; i++) {
        out[i] = a + i * paso;
      }
      return out;
    }

    function argmax(arr) {
      let idx = 0;
      let maxVal = arr[0];
      for (let i = 1; i < arr.length; i++) {
        if (arr[i] > maxVal) {
          maxVal = arr[i];
          idx = i;
        }
      }
      return idx;
    }

    // ============================================================
    // Funciones alpha/beta
    // ============================================================
    function alpha_n(V) {
      const x = V + 55.0;
      if (Math.abs(x) < 1e-8) return 0.1;
      return 0.01 * x / (1.0 - Math.exp(-x / 10.0));
    }

    function beta_n(V) {
      return 0.125 * Math.exp(-(V + 65.0) / 80.0);
    }

    function alpha_m(V) {
      const x = V + 40.0;
      if (Math.abs(x) < 1e-8) return 1.0;
      return 0.1 * x / (1.0 - Math.exp(-x / 10.0));
    }

    function beta_m(V) {
      return 4.0 * Math.exp(-(V + 65.0) / 18.0);
    }

    function alpha_h(V) {
      return 0.07 * Math.exp(-(V + 65.0) / 20.0);
    }

    function beta_h(V) {
      return 1.0 / (1.0 + Math.exp(-(V + 35.0) / 10.0));
    }

    function x_inf(alpha, beta, V) {
      const a = alpha(V);
      const b = beta(V);
      return a / (a + b);
    }

    function m_inf(V) { return x_inf(alpha_m, beta_m, V); }
    function h_inf(V) { return x_inf(alpha_h, beta_h, V); }
    function n_inf(V) { return x_inf(alpha_n, beta_n, V); }

    // ============================================================
    // Estímulo
    // ============================================================
    function corriente_desde_pulsos(t, pulsos) {
      const I = new Array(t.length).fill(0.0);
      for (const pulso of pulsos) {
        const t0 = pulso[0];
        const dur = pulso[1];
        const amp = pulso[2];
        for (let i = 0; i < t.length; i++) {
          if (t[i] >= t0 && t[i] < t0 + dur) {
            I[i] += amp;
          }
        }
      }
      return I;
    }

    function compuertas_iniciales(V0) {
      return [m_inf(V0), h_inf(V0), n_inf(V0)];
    }

    // ============================================================
    // Lado derecho del sistema HH
    // ============================================================
    function hh_rhs(estado, Iext, params) {
      const V = estado[0];
      const m = estado[1];
      const h = estado[2];
      const n = estado[3];

      const gNa_t = params.gNa * Math.pow(m, 3) * h;
      const gK_t = params.gK * Math.pow(n, 4);

      const INa = gNa_t * (V - params.ENa);
      const IK = gK_t * (V - params.EK);
      const IL = params.gL * (V - params.EL);

      const dV = (Iext - INa - IK - IL) / params.Cm;
      const dm = alpha_m(V) * (1.0 - m) - beta_m(V) * m;
      const dh = alpha_h(V) * (1.0 - h) - beta_h(V) * h;
      const dn = alpha_n(V) * (1.0 - n) - beta_n(V) * n;

      return [dV, dm, dh, dn];
    }

    // ============================================================
    // Simulación HH con RK4
    // ============================================================
    function simular_hh(pulsos, t_max = T_MAX, dt = DT, params = PARAMS) {
      const nPasos = Math.floor(t_max / dt) + 1;
      const t = new Array(nPasos);
      for (let i = 0; i < nPasos; i++) {
        t[i] = i * dt;
      }

      const I = corriente_desde_pulsos(t, pulsos);

      const V = new Array(nPasos);
      const m = new Array(nPasos);
      const h = new Array(nPasos);
      const n = new Array(nPasos);

      V[0] = params.V_rest;
      const iniciales = compuertas_iniciales(V[0]);
      m[0] = iniciales[0];
      h[0] = iniciales[1];
      n[0] = iniciales[2];

      for (let k = 0; k < nPasos - 1; k++) {
        const y = [V[k], m[k], h[k], n[k]];

        const k1 = hh_rhs(y, I[k], params);

        const y2 = [
          y[0] + 0.5 * dt * k1[0],
          y[1] + 0.5 * dt * k1[1],
          y[2] + 0.5 * dt * k1[2],
          y[3] + 0.5 * dt * k1[3]
        ];
        const k2 = hh_rhs(y2, I[k], params);

        const y3 = [
          y[0] + 0.5 * dt * k2[0],
          y[1] + 0.5 * dt * k2[1],
          y[2] + 0.5 * dt * k2[2],
          y[3] + 0.5 * dt * k2[3]
        ];
        const k3 = hh_rhs(y3, I[k], params);

        const y4 = [
          y[0] + dt * k3[0],
          y[1] + dt * k3[1],
          y[2] + dt * k3[2],
          y[3] + dt * k3[3]
        ];
        const k4 = hh_rhs(y4, I[Math.min(k + 1, nPasos - 1)], params);

        V[k + 1] = y[0] + (dt / 6.0) * (k1[0] + 2*k2[0] + 2*k3[0] + k4[0]);
        m[k + 1] = clamp01(y[1] + (dt / 6.0) * (k1[1] + 2*k2[1] + 2*k3[1] + k4[1]));
        h[k + 1] = clamp01(y[2] + (dt / 6.0) * (k1[2] + 2*k2[2] + 2*k3[2] + k4[2]));
        n[k + 1] = clamp01(y[3] + (dt / 6.0) * (k1[3] + 2*k2[3] + 2*k3[3] + k4[3]));
      }

      const gNa_t = new Array(nPasos);
      const gK_t = new Array(nPasos);
      const gL_t = new Array(nPasos).fill(params.gL);

      const INa = new Array(nPasos);
      const IK = new Array(nPasos);
      const IL = new Array(nPasos);

      for (let i = 0; i < nPasos; i++) {
        gNa_t[i] = params.gNa * Math.pow(m[i], 3) * h[i];
        gK_t[i] = params.gK * Math.pow(n[i], 4);

        INa[i] = gNa_t[i] * (V[i] - params.ENa);
        IK[i] = gK_t[i] * (V[i] - params.EK);
        IL[i] = params.gL * (V[i] - params.EL);
      }

      return {
        t: t,
        I: I,
        V: V,
        m: m,
        h: h,
        n: n,
        INa: INa,
        IK: IK,
        IL: IL,
        gNa_t: gNa_t,
        gK_t: gK_t,
        gL_t: gL_t,
        params: params
      };
    }

    function clamp01(x) {
      if (x < 0.0) return 0.0;
      if (x > 1.0) return 1.0;
      return x;
    }

    // ============================================================
    // Resumen del spike
    // ============================================================
    function resumen_spike(data, t_inicio = 0.0) {
      const t = data.t;
      const V = data.V;

      let indices = [];
      for (let i = 0; i < t.length; i++) {
        if (t[i] >= t_inicio) {
          indices.push(i);
        }
      }

      if (indices.length === 0) {
        return { picoV: NaN, picoT: NaN, spike: false };
      }

      const Vsub = indices.map(i => V[i]);
      const idxLocal = argmax(Vsub);
      const idx = indices[idxLocal];

      const picoV = V[idx];
      const picoT = t[idx];
      const spike = picoV > 0.0;

      return {
        picoV: picoV,
        picoT: picoT,
        spike: spike
      };
    }

    // ============================================================
    // Nullclines aproximadas en el plano (V, n)
    // ============================================================
    function vn_nullclines(Iext, params, V_grid) {
      const n_nc = new Array(V_grid.length);
      const v_nc = new Array(V_grid.length);

      for (let i = 0; i < V_grid.length; i++) {
        const V = V_grid[i];
        n_nc[i] = n_inf(V);

        const numerador =
          Iext
          - params.gNa * Math.pow(m_inf(V), 3) * h_inf(V) * (V - params.ENa)
          - params.gL * (V - params.EL);

        const denominador = params.gK * (V - params.EK);

        const valor = numerador / denominador;
        if (valor >= 0.0 && Number.isFinite(valor)) {
          v_nc[i] = Math.pow(valor, 0.25);
        } else {
          v_nc[i] = null;
        }
      }

      return [n_nc, v_nc];
    }

    // ============================================================
    // Controles HTML
    // ============================================================
    const sliderAmplitud = document.getElementById("slider-amplitud");
    const sliderInicio = document.getElementById("slider-inicio");
    const sliderDuracion = document.getElementById("slider-duracion");

    const valorAmplitud = document.getElementById("valor-amplitud");
    const valorInicio = document.getElementById("valor-inicio");
    const valorDuracion = document.getElementById("valor-duracion");

    const resumen = document.getElementById("resumen");

    // ============================================================
    // Layouts de Plotly
    // ============================================================
    const colores = {
      azul: "#60a5fa",
      verde: "#34d399",
      amarillo: "#fbbf24",
      rosa: "#f472b6",
      gris: "#94a3b8",
      fondo: "#111827",
      papel: "#0f172a",
      texto: "#e5e7eb",
      subtexto: "#cbd5e1",
      borde: "#334155"
    };

    function layoutBase(titulo, xTitulo, yTitulo, xRango = null, yRango = null) {
      return {
        title: { text: titulo, font: { color: colores.texto } },
        paper_bgcolor: colores.fondo,
        plot_bgcolor: colores.fondo,
        font: { color: colores.texto },
        margin: { l: 60, r: 20, t: 50, b: 55 },
        xaxis: {
          title: xTitulo,
          gridcolor: "rgba(148,163,184,0.15)",
          zerolinecolor: "rgba(148,163,184,0.15)"
        },
        yaxis: {
          title: yTitulo,
          gridcolor: "rgba(148,163,184,0.15)",
          zerolinecolor: "rgba(148,163,184,0.15)"
        },
        legend: {
          bgcolor: "rgba(0,0,0,0)",
          bordercolor: "rgba(0,0,0,0)"
        }
      };
    }

    const layoutVoltaje = layoutBase(
      "Potencial de membrana",
      "tiempo (ms)",
      "V (mV)"
    );
    layoutVoltaje.xaxis.range = [0, 40];
    layoutVoltaje.yaxis.range = [-90, 60];
    layoutVoltaje.shapes = [];

    const layoutCompuertas = layoutBase(
      "Variables de compuerta",
      "tiempo (ms)",
      "valor"
    );
    layoutCompuertas.xaxis.range = [0, 40];
    layoutCompuertas.yaxis.range = [0, 1];

    const layoutCorrientes = layoutBase(
      "Corrientes iónicas y estímulo",
      "tiempo (ms)",
      "corriente (μA/cm²)"
    );
    layoutCorrientes.xaxis.range = [0, 40];
    layoutCorrientes.yaxis.range = [-250, 250];

    const layoutPlano = layoutBase(
      "Plano reducido (V, n)",
      "V (mV)",
      "n"
    );
    layoutPlano.xaxis.range = [-90, 60];
    layoutPlano.yaxis.range = [0, 1];

    // ============================================================
    // Inicialización de figuras
    // ============================================================
    Plotly.newPlot("grafica-voltaje", [], layoutVoltaje, {responsive: true, displaylogo: false});
    Plotly.newPlot("grafica-compuertas", [], layoutCompuertas, {responsive: true, displaylogo: false});
    Plotly.newPlot("grafica-corrientes", [], layoutCorrientes, {responsive: true, displaylogo: false});
    Plotly.newPlot("grafica-plano", [], layoutPlano, {responsive: true, displaylogo: false});

    // ============================================================
    // Actualización
    // ============================================================
    let animacionPendiente = false;

    function solicitarActualizacion() {
      if (!animacionPendiente) {
        animacionPendiente = true;
        requestAnimationFrame(() => {
          animacionPendiente = false;
          actualizar();
        });
      }
    }

    function actualizar() {
      const amp = parseFloat(sliderAmplitud.value);
      const t0 = parseFloat(sliderInicio.value);
      const dur = parseFloat(sliderDuracion.value);

      valorAmplitud.textContent = amp.toFixed(1);
      valorInicio.textContent = t0.toFixed(1);
      valorDuracion.textContent = dur.toFixed(1);

      const data = simular_hh([[t0, dur, amp]], T_MAX, DT, PARAMS);
      const info = resumen_spike(data, t0);

      // -------------------------
      // Gráfica de voltaje
      // -------------------------
      const trazasVoltaje = [
        {
          x: data.t,
          y: data.V,
          type: "scatter",
          mode: "lines",
          name: "V(t)",
          line: { color: colores.azul, width: 2.5 }
        }
      ];

      const layoutVoltajeLocal = JSON.parse(JSON.stringify(layoutVoltaje));
      layoutVoltajeLocal.shapes = [
        {
          type: "line",
          x0: t0, x1: t0, y0: -90, y1: 60,
          line: { color: colores.gris, width: 1.5, dash: "dash" }
        },
        {
          type: "line",
          x0: t0 + dur, x1: t0 + dur, y0: -90, y1: 60,
          line: { color: colores.gris, width: 1.5, dash: "dash" }
        }
      ];

      Plotly.react("grafica-voltaje", trazasVoltaje, layoutVoltajeLocal, {
        responsive: true,
        displaylogo: false
      });

      // -------------------------
      // Gráfica de compuertas
      // -------------------------
      const trazasCompuertas = [
        {
          x: data.t, y: data.m,
          type: "scatter", mode: "lines",
          name: "m",
          line: { color: colores.azul, width: 2 }
        },
        {
          x: data.t, y: data.h,
          type: "scatter", mode: "lines",
          name: "h",
          line: { color: colores.rosa, width: 2 }
        },
        {
          x: data.t, y: data.n,
          type: "scatter", mode: "lines",
          name: "n",
          line: { color: colores.verde, width: 2 }
        }
      ];

      Plotly.react("grafica-compuertas", trazasCompuertas, layoutCompuertas, {
        responsive: true,
        displaylogo: false
      });

      // -------------------------
      // Gráfica de corrientes
      // -------------------------
      const trazasCorrientes = [
        {
          x: data.t, y: data.INa,
          type: "scatter", mode: "lines",
          name: "I_Na",
          line: { color: colores.azul, width: 2 }
        },
        {
          x: data.t, y: data.IK,
          type: "scatter", mode: "lines",
          name: "I_K",
          line: { color: colores.verde, width: 2 }
        },
        {
          x: data.t, y: data.IL,
          type: "scatter", mode: "lines",
          name: "I_L",
          line: { color: colores.rosa, width: 2 }
        },
        {
          x: data.t, y: data.I,
          type: "scatter", mode: "lines",
          name: "I_ext",
          line: { color: colores.amarillo, width: 2, dash: "dash" }
        }
      ];

      Plotly.react("grafica-corrientes", trazasCorrientes, layoutCorrientes, {
        responsive: true,
        displaylogo: false
      });

      // -------------------------
      // Plano reducido (V, n)
      // -------------------------
      const nullclines = vn_nullclines(amp, PARAMS, V_GRID);
      const n_nc = nullclines[0];
      const v_nc = nullclines[1];

      const trazasPlano = [
        {
          x: data.V, y: data.n,
          type: "scatter", mode: "lines",
          name: "trayectoria",
          line: { color: colores.azul, width: 2.5 }
        },
        {
          x: V_GRID, y: n_nc,
          type: "scatter", mode: "lines",
          name: "dn/dt = 0",
          line: { color: colores.verde, width: 2, dash: "dash" }
        },
        {
          x: V_GRID, y: v_nc,
          type: "scatter", mode: "lines",
          name: "dV/dt = 0 (aprox.)",
          line: { color: colores.amarillo, width: 2, dash: "dot" }
        },
        {
          x: [data.V[0]], y: [data.n[0]],
          type: "scatter", mode: "markers",
          name: "inicio",
          marker: { color: colores.rosa, size: 8 }
        }
      ];

      Plotly.react("grafica-plano", trazasPlano, layoutPlano, {
        responsive: true,
        displaylogo: false
      });

      // -------------------------
      // Resumen
      // -------------------------
      const spikeTexto = info.spike ? "sí" : "no";
      resumen.textContent =
        "spike: " + spikeTexto + "\n" +
        "V pico = " + info.picoV.toFixed(2) + " mV\n" +
        "t pico = " + info.picoT.toFixed(2) + " ms";
    }

    // ============================================================
    // Eventos
    // ============================================================
    sliderAmplitud.addEventListener("input", solicitarActualizacion);
    sliderInicio.addEventListener("input", solicitarActualizacion);
    sliderDuracion.addEventListener("input", solicitarActualizacion);

    // ============================================================
    // Primera actualización
    // ============================================================
    actualizar();
  </script>
</body>
</html>
"""

    ruta = Path(ruta_salida)
    ruta.write_text(html, encoding="utf-8")
    print(f"HTML generado en: {ruta.resolve()}")


if __name__ == "__main__":
    generar_html_hh_umbral()