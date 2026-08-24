import React, { useMemo, useState } from 'react';
import { html } from '../lib/html.js';
import { DEFAULT_API_BASE_URL } from '../config/runtime.js';
import { StructureForgeApiClient } from '../services/apiClient.js';

const TOOL_DEFINITIONS = [
  {
    id: 'content-package',
    label: 'Content Package',
    short: 'PKG',
    endpoint: '/v1/minecraft/content-package',
    newest: true,
    description: 'Compose a linked structure/content bundle with books, loot, recipes, advancements, tags, and pack metadata.',
    example: {
      target_version: '1.20.5',
      package_id: 'structuresmith:manual_demo',
      books: [
        {
          name: 'field_notes',
          title: 'Field Notes',
          author: 'StructureSmith',
          pages: ['Manual content package generated from StructureForge.'],
        },
      ],
      loot_tables: [
        {
          name: 'evidence',
          table_id: 'structuresmith:chests/manual_demo',
          guaranteed: [{ id: 'minecraft:paper', count: 1 }],
        },
      ],
      bindings: [
        { type: 'book_as_guaranteed_loot', book: 'field_notes', loot_table: 'evidence' },
      ],
      manifest: {},
    },
  },
  {
    id: 'advancement',
    label: 'Advancement',
    short: 'ADV',
    endpoint: '/v1/minecraft/advancement',
    newest: true,
    description: 'Generate progression/discovery advancements with criteria, display metadata, rewards, and version-aware paths.',
    example: {
      target_version: '1.20.5',
      advancement_id: 'structuresmith:manual/first_discovery',
      display: {
        title: 'First Discovery',
        description: 'Find your first StructureSmith evidence item.',
        icon: 'minecraft:compass',
        frame: 'task',
      },
      criteria: {
        found_item: { trigger: 'minecraft:inventory_changed', conditions: {} },
      },
    },
  },
  {
    id: 'tag',
    label: 'Tag',
    short: 'TAG',
    endpoint: '/v1/minecraft/tag',
    newest: true,
    description: 'Build datapack tags for items, blocks, fluids, entity types, functions, and game events.',
    example: {
      target_version: '1.21',
      tag_id: 'structuresmith:building_stone',
      registry: 'block',
      replace: false,
      values: ['minecraft:stone', 'minecraft:stone_bricks', 'minecraft:deepslate_bricks'],
    },
  },
  {
    id: 'manifest',
    label: 'Datapack Manifest',
    short: 'PACK',
    endpoint: '/v1/minecraft/datapack-manifest',
    newest: true,
    description: 'Generate a gated pack.mcmeta using exact bundled datapack metadata or an explicit pack-format override.',
    example: {
      target_version: '1.20.5',
      description: 'StructureSmith manual datapack output',
    },
  },
  {
    id: 'book',
    label: 'Book',
    short: 'BK',
    endpoint: '/v1/minecraft/book',
    description: 'Assemble version-aware written books, including post-1.20.5 item components.',
    example: {
      target_version: '1.20.5',
      title: 'Containment Log',
      author: 'StructureSmith',
      pages: ['Entry one', { text: 'Entry two', bold: true }],
    },
  },
  {
    id: 'loot',
    label: 'Loot Table',
    short: 'LT',
    endpoint: '/v1/minecraft/loot-table',
    description: 'Generate weighted and guaranteed loot pools with mod-aware resource-ID gates.',
    example: {
      target_version: '1.20.5',
      table_id: 'structuresmith:chests/manual_evidence',
      items: [{ id: 'minecraft:iron_ingot', weight: 4, min_count: 1, max_count: 3 }],
      guaranteed: [{ id: 'minecraft:paper', count: 1 }],
    },
  },
  {
    id: 'recipe',
    label: 'Recipe',
    short: 'RC',
    endpoint: '/v1/minecraft/recipe',
    description: 'Generate shaped, shapeless, cooking, and stonecutting recipes across supported format boundaries.',
    example: {
      target_version: '1.20.5',
      recipe_id: 'structuresmith:manual/stone_mix',
      type: 'crafting_shapeless',
      ingredients: ['minecraft:stone', 'minecraft:gravel'],
      result: { id: 'minecraft:cobblestone', count: 2 },
    },
  },
  {
    id: 'registry',
    label: 'Registry Probe',
    short: 'ID',
    endpoint: '/v1/minecraft/registry/probe',
    description: 'Check a vanilla or modded resource location against the project inventory and confidence gates.',
    example: {
      id: 'minecraft:chest',
      kind: 'item',
      id_policy: 'namespace',
    },
  },
  {
    id: 'icon',
    label: 'Icon',
    short: 'ICO',
    endpoint: '/v1/minecraft/icon',
    description: 'Assign a semantic Minecraft item icon or deterministic SVG badge fallback.',
    example: {
      subject: 'advancement',
      target_version: '1.20.5',
      mode: 'auto',
    },
  },
  {
    id: 'version',
    label: 'Version',
    short: 'VER',
    endpoint: '/v1/minecraft/version',
    description: 'Resolve bundled compatibility metadata without guessing unknown DataVersion values.',
    example: { version: '1.20.5' },
  },
];

function pretty(value) {
  return JSON.stringify(value, null, 2);
}

function gateStatus(result) {
  if (result?.gate?.status) return result.gate.status;
  if (result?.accepted === true) return 'PASS';
  if (result?.accepted === false) return 'FAIL';
  if (result) return 'OK';
  return 'IDLE';
}

function statusClass(status) {
  const normalized = String(status || '').toLowerCase();
  if (normalized === 'pass' || normalized === 'ok') return 'manual-status-pass';
  if (normalized === 'warn') return 'manual-status-warn';
  if (normalized === 'fail' || normalized === 'error') return 'manual-status-fail';
  if (normalized === 'running') return 'manual-status-running';
  return '';
}

export function ManualCapabilityWorkbench() {
  const [activeId, setActiveId] = useState(TOOL_DEFINITIONS[0].id);
  const activeTool = TOOL_DEFINITIONS.find((tool) => tool.id === activeId) || TOOL_DEFINITIONS[0];
  const [apiBase, setApiBase] = useState(DEFAULT_API_BASE_URL);
  const [requestText, setRequestText] = useState(pretty(TOOL_DEFINITIONS[0].example));
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');
  const [runState, setRunState] = useState('IDLE');
  const client = useMemo(() => new StructureForgeApiClient(apiBase), [apiBase]);

  const selectTool = (tool) => {
    setActiveId(tool.id);
    setRequestText(pretty(tool.example));
    setResult(null);
    setError('');
    setRunState('IDLE');
  };

  const resetExample = () => {
    setRequestText(pretty(activeTool.example));
    setResult(null);
    setError('');
    setRunState('IDLE');
  };

  const execute = async () => {
    setError('');
    setResult(null);
    setRunState('RUNNING');
    try {
      const body = JSON.parse(requestText);
      const response = await client.request(activeTool.endpoint, { method: 'POST', body });
      setResult(response);
      setRunState(gateStatus(response));
    } catch (executionError) {
      setError(executionError.message || String(executionError));
      setRunState('ERROR');
    }
  };

  const copyResult = async () => {
    if (!result || !navigator.clipboard) return;
    await navigator.clipboard.writeText(pretty(result));
  };

  const findingCount = result?.gate?.findings?.length || 0;

  return html`
    <section className="manual-workbench" aria-label="Manual StructureSmith capability tools">
      <div className="manual-workbench-heading">
        <div>
          <span className="eyebrow">Direct manual API access</span>
          <div className="manual-title-row">
            <h2>Manual Capability Workbench</h2>
            <span className="manual-count">${TOOL_DEFINITIONS.length} tools</span>
          </div>
          <p>Use StructureSmith content capabilities directly without leaving the web page. Edit the request JSON, execute it against the live API, and inspect the public validation gates.</p>
        </div>
        <label className="manual-api-field">
          <span>API base URL</span>
          <input value=${apiBase} onChange=${(event) => setApiBase(event.target.value)} />
        </label>
      </div>

      <div className="manual-tool-strip" role="tablist" aria-label="Manual capability selector">
        ${TOOL_DEFINITIONS.map((tool) => html`
          <button
            key=${tool.id}
            type="button"
            role="tab"
            aria-selected=${tool.id === activeId}
            className=${`manual-tool-button ${tool.id === activeId ? 'active' : ''}`}
            onClick=${() => selectTool(tool)}
          >
            <span className="manual-tool-icon">${tool.short}</span>
            <span className="manual-tool-label">${tool.label}</span>
            ${tool.newest && html`<span className="manual-new-badge">new</span>`}
          </button>
        `)}
      </div>

      <div className="manual-editor-shell">
        <div className="manual-editor-pane">
          <div className="manual-pane-heading">
            <div>
              <span className="manual-endpoint">POST ${activeTool.endpoint}</span>
              <h3>${activeTool.label}</h3>
              <p>${activeTool.description}</p>
            </div>
            <button type="button" className="secondary" onClick=${resetExample}>Reset example</button>
          </div>
          <label className="manual-json-label" htmlFor="manual-request-json">Request JSON</label>
          <textarea
            id="manual-request-json"
            className="manual-json-editor"
            spellCheck=${false}
            value=${requestText}
            onChange=${(event) => setRequestText(event.target.value)}
          ></textarea>
          <div className="manual-run-row">
            <button type="button" className="primary" disabled=${runState === 'RUNNING'} onClick=${execute}>
              ${runState === 'RUNNING' ? 'Executing…' : `Run ${activeTool.label}`}
            </button>
            <span className=${`manual-run-status ${statusClass(runState)}`}>${runState}</span>
            <span className="manual-endpoint-note">Calls the same public API used by AI clients.</span>
          </div>
        </div>

        <div className="manual-result-pane">
          <div className="manual-result-heading">
            <div>
              <span className="eyebrow">Response + public gates</span>
              <h3>Result</h3>
            </div>
            <div className="manual-result-actions">
              ${findingCount > 0 && html`<span className="manual-finding-count">${findingCount} findings</span>`}
              <button type="button" className="secondary" disabled=${!result} onClick=${copyResult}>Copy result</button>
            </div>
          </div>
          ${error && html`
            <div className="manual-error" role="alert">
              <strong>Request failed</strong>
              <span>${error}</span>
            </div>
          `}
          ${!error && !result && html`
            <div className="manual-result-empty">
              <strong>Ready for manual execution</strong>
              <span>The complete JSON artifact and gate report will appear here.</span>
            </div>
          `}
          ${result && html`<pre className="manual-result-json">${pretty(result)}</pre>`}
        </div>
      </div>
    </section>
  `;
}
