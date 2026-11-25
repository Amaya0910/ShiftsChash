import { useEffect, useState } from 'react';
import api from '../api/axios';

// Tiempo sin respuesta a partir del cual se avisa que el servidor está despertando
const AVISO_MS = 3000;

/**
 * D-09: el plan gratuito de Render apaga la API tras un rato sin tráfico.
 * Este hook la despierta con un ping a "/" al montar la página y devuelve
 * `despertando = true` si la respuesta tarda más de AVISO_MS, para que la
 * interfaz muestre un aviso en lugar de parecer bloqueada.
 */
export function useBackendWarmup() {
  const [despertando, setDespertando] = useState(false);

  useEffect(() => {
    let activo = true;
    const aviso = setTimeout(() => activo && setDespertando(true), AVISO_MS);

    api.get('/')
      .catch(() => {}) // solo es un ping; los errores reales los muestra cada formulario
      .finally(() => {
        clearTimeout(aviso);
        if (activo) setDespertando(false);
      });

    return () => {
      activo = false;
      clearTimeout(aviso);
    };
  }, []);

  return despertando;
}
