/**
 * Convierte el error de una petición a la API en un texto para mostrar.
 *
 * FastAPI devuelve `detail` como texto (400/404/409) o, en validaciones (422),
 * como una lista de objetos { msg, loc, ... }. Renderizar esa lista directamente
 * rompe React, así que aquí se reduce siempre a un string.
 *
 * @param {unknown} err - error lanzado por axios
 * @param {string} porDefecto - mensaje si la API no envía detalle
 * @returns {string}
 */
export function mensajeError(err, porDefecto) {
  const detail = err?.response?.data?.detail;
  if (typeof detail === 'string') return detail;
  if (Array.isArray(detail) && detail.length > 0) {
    return detail
      .map((d) => String(d?.msg ?? '').replace(/^Value error, /, ''))
      .filter(Boolean)
      .join('. ') || porDefecto;
  }
  return porDefecto;
}
