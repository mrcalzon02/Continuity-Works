function discoveredApiBase() {
  if (globalThis.CONTINUITY_WORKS_API_BASE_URL) return globalThis.CONTINUITY_WORKS_API_BASE_URL;
  if (typeof document !== 'undefined') {
    const meta = document.querySelector('meta[name="continuity-works-api"]');
    if (meta?.content) return meta.content;
  }
  return 'https://continuity-works-mrcalzon02-api.onrender.com';
}

export const DEFAULT_API_BASE_URL = discoveredApiBase().replace(/\/$/, '');
