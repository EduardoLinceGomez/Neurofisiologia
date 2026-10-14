# Convenciones de trabajo

- Trabajar en este directorio existente y conservar los archivos locales. Inspeccionar
  estado, índice, remotos y diferencias antes de sincronizar; no usar reset, clean,
  force-push ni clonar encima del directorio.
- `Bibliografia/` es privada y local. No editar, mover, renombrar, borrar, copiar,
  versionar ni cargar sus documentos a servicios externos. No abrir su contenido
  salvo necesidad estricta y autorización explícita. Mantener `/Bibliografia/`
  en `.gitignore`; si hay archivos rastreados allí, detenerse y consultar.
- Usar fuentes públicas para documentar referencias. Distinguir datos experimentales
  de parámetros ilustrativos y no calibrados; registrar especie, figura/tabla,
  unidades y procedencia. No presentar trazas simuladas como mediciones.
- Esta etapa contiene solo un bastón pasivo O-I-T con fotocorriente impuesta.
  Mantener las ecuaciones del Issue #1 y el acoplamiento axial simétrico. No añadir
  conos, amacrinas, canales activos, bioquímica, liberación sináptica ni spikes.
- Convención: corriente entrante positiva; la variación fotosensible es negativa.
  Unidades internas: ms, mV, pF, nS, pA. Los eventos fotónicos no son spikes.
- Separar parámetros, estímulos y EDO en `src/neurofisiologia/`. El notebook consume
  esa implementación; no duplicar el modelo en celdas.
- Figuras: ejes con unidades, leyenda, supuestos y rótulos que identifiquen simulación
  y referencia experimental. Guardar productos generados en `outputs/` (ignorado).
- Validar con pytest y ejecutar el notebook completo antes de publicar cambios.
  Mantener el notebook fuente sin salidas ni rutas personales.
- Para el laboratorio del Issue #3, seguir la decisión 0001 y el plan 02,
  ejecutar ambos notebooks y comprobar callbacks con/sin widgets. La referencia
  canónica es independiente de los controles; al cambiar tasa se muestran las
  dos entradas y su variabilidad. `decompose_currents` orienta J_OI positiva
  O→I y J_IT positiva I→T; por nodo se suman corrientes entrantes antes de /C.
- Publicar únicamente ramas autorizadas y PR en borrador. No fusionar ni activar
  auto-merge sin una instrucción posterior expresa del usuario.
