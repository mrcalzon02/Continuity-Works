export class StructureForgeApiClient {
  constructor(baseUrl = '') {
    this.baseUrl = baseUrl.replace(/\/$/, '');
  }

  setBaseUrl(baseUrl) {
    this.baseUrl = (baseUrl || '').replace(/\/$/, '');
  }

  async request(path, { method = 'GET', body, signal } = {}) {
    if (!this.baseUrl) throw new Error('No StructureSmith API base URL configured.');
    const response = await fetch(`${this.baseUrl}${path}`, {
      method,
      signal,
      headers: body ? { 'Content-Type': 'application/json' } : undefined,
      body: body ? JSON.stringify(body) : undefined,
    });
    const payload = await response.json().catch(() => ({}));
    if (!response.ok) throw new Error(payload.message || payload.error || `HTTP ${response.status}`);
    return payload;
  }

  health(signal) { return this.request('/v1/health', { signal }); }
  tools(signal) { return this.request('/v1/tools', { signal }); }
  capabilities(signal) { return this.request('/v1/capabilities', { signal }); }
  generate(body, signal) { return this.request('/v1/generate', { method: 'POST', body, signal }); }
  audit(body, signal) { return this.request('/v1/audit', { method: 'POST', body, signal }); }
  plan(body, signal) { return this.request('/v1/plan', { method: 'POST', body, signal }); }
  dungeonLayout(body, signal) { return this.request('/v1/dungeon/layout', { method: 'POST', body, signal }); }
  infrastructureLayout(body, signal) { return this.request('/v1/infrastructure/layout', { method: 'POST', body, signal }); }
  minecraftVersion(version, signal) {
    return this.request('/v1/minecraft/version', { method: 'POST', body: { version }, signal });
  }
}
