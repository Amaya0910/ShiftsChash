import { useState, useEffect } from 'react';

/**
 * Hook para detectar media queries
 * @param {string} query - Media query string (e.g., '(max-width: 768px)')
 * @returns {boolean} - true si la media query coincide
 */
export function useMediaQuery(query) {
  const [matches, setMatches] = useState(() => window.matchMedia(query).matches);

  useEffect(() => {
    const media = window.matchMedia(query);
    const listener = () => setMatches(media.matches);
    media.addEventListener('change', listener);
    return () => media.removeEventListener('change', listener);
  }, [query]);

  return matches;
}
