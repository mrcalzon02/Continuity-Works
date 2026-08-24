function discoveredApiBase() {
  if (globalThis.STRUCTURESMITH_API_BASE_URL) return globalThis.STRUCTURESMITH_API_BASE_URL;
  if (typeof document !== 'undefined') {
    const meta = document.querySelector('meta[name="structuresmith-api"]');
    if (meta?.content) return meta.content;
  }
  return 'https://structuresmith-mrcalzon02-api.onrender.com';
}

export const DEFAULT_API_BASE_URL = discoveredApiBase().replace(/\/$/, '');
