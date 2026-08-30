import React, { useEffect, useMemo, useRef, useState } from 'react';
import { useMachine } from '@xstate/react';
import { html } from '../lib/html.js';
import {
  pipelineMachine,
  PHASE_LABELS,
  PIPELINE_PHASES,
  nextPhaseLabel,
} from '../state/pipelineMachine.js';
import {
  CONTROL_MODULES,
  DEFAULT_CONTROLS,
  buildGenerateRequest,
} from '../config/controlSchema.js';
import { DEFAULT_API_BASE_URL } from '../config/runtime.js';
import { StructureForgeApiClient } from '../services/apiClient.js';
import {
  buildDemoPhaseEvents,
  playSerializedEvents,
  serializeApiResponseToEvents,
} from '../services/streamService.js';
import { Viewport } from './Viewport.js';

const PACE_OPTIONS = [
  [1200, 'Deliberate — 1.2 s/event'],
  [700, 'Readable — 0.7 s/event'],
  [350, 'Fast review — 0.35 s/event'],
  [120, 'Diagnostic — 0.12 s/event'],
];

function PhaseRail({ phase }) {
  const currentIndex = PIPELINE_PHASES.indexOf(phase);
  return html`
    <nav className="phase-rail" aria-label="StructureForge pipeline phases">
      ${PIPELINE_PHASES.map((item, index) => {
        const className = [
          'phase-step',
          item === phase ? 'active' : '',
          index < currentIndex ? 'complete' : '',
        ].filter(Boolean).join(' ');
        return html`
          <div className=${className} key=${item}>
            <span className="phase-index">${String(index + 1).padStart(2, '0')}</span>
            <span>${PHASE_LABELS[item]}</span>
          </div>
        `;
      })}
    </nav>
  `;
}

function ControlPanel({ controls, phase, onChange }) {
  return html`
    <aside className="panel controls-panel">
      <div className="panel-heading">
        <span className="eyebrow">Constraint injection</span>
        <h2>Modules</h2>
        <p>Optional menus expose the same decisions an API caller can supply programmatically.</p>
      </div>
      <div className="module-list">
        ${CONTROL_MODULES.map((module, index) => {
          const editable = module.editableStates.includes(phase);
          return html`
            <details className="module-card" open=${index < 2} key=${module.id}>
              <summary>
                <span>${module.title}</span>
                <span className=${`lock-state ${editable ? 'editable' : 'locked'}`}>
                  ${editable ? 'editable' : 'locked'}
                </span>
              </summary>
              <p>${module.description}</p>
              <fieldset disabled=${!editable}>
                ${module.fields.map((field) => html`
                  <label className="field" key=${field.key}>
                    <span>${field.label}</span>
                    ${field.type === 'select'
                      ? html`
                        <select
                          value=${controls[field.key]}
                          onChange=${(event) => onChange(field.key, event.target.value)}
                        >
                          ${field.options.map(([value, label]) => html`
                            <option value=${value} key=${value}>${label}</option>
                          `)}
                        </select>
                      `
                      : html`
                        <input
                          value=${controls[field.key]}
                          onChange=${(event) => onChange(field.key, event.target.value)}
                        />
                      `}
                  </label>
                `)}
              </fieldset>
            </details>
          `;
        })}
      </div>
    </aside>
  `;
}

function ProgressionLog({ logs }) {
  const feedRef = useRef(null);
  useEffect(() => {
    if (feedRef.current) feedRef.current.scrollTop = feedRef.current.scrollHeight;
  }, [logs]);

  return html`
    <section className="panel progression-panel">
      <div className="panel-heading">
        <span className="eyebrow">Explainable execution</span>
        <h2>Serialized Progression</h2>
        <p>Human-readable decision rationales, not raw hidden chain-of-thought.</p>
      </div>
      <div className="progression-feed" ref=${feedRef}>
        ${logs.length === 0 && html`
          <div className="feed-empty">
            Pipeline events will appear here one at a time: action, coordinate, and concise rationale.
          </div>
        `}
        ${logs.map((entry, index) => html`
          <article className=${`log-entry ${entry.severity || 'info'}`} key=${entry.id || index}>
            <div className="log-meta">
              <span>${entry.stage}</span>
              <span>${String(index + 1).padStart(3, '0')}</span>
            </div>
            <strong>${entry.message}</strong>
            ${entry.coordinate && html`
              <code>${entry.coordinate.x}, ${entry.coordinate.y}, ${entry.coordinate.z}</code>
            `}
            ${entry.rationale && html`<p>${entry.rationale}</p>`}
          </article>
        `)}
      </div>
    </section>
  `;
}

function AuditImageStrip({ images }) {
  const slots = ['oblique', 'plan', 'damage'];
  return html`
    <section className="panel audit-strip">
      <div className="panel-heading compact-heading">
        <div>
          <span className="eyebrow">Optional client visual evidence</span>
          <h2>Audit Image Viewports</h2>
        </div>
      </div>
      <div className="audit-grid">
        ${slots.map((slot) => {
          const image = images.find((item) => item.id === slot);
          return html`
            <figure className=${`audit-frame ${image ? 'ready' : ''}`} key=${slot}>
              ${image
                ? html`<img src=${image.url} alt=${`${image.label} StructureForge audit preview`} />`
                : html`
                  <div className="image-placeholder">
                    <span>${slot}</span>
                    <small>optional client-rendered frame</small>
                  </div>
                `}
              <figcaption>${image?.label || slot}</figcaption>
            </figure>
          `;
        })}
      </div>
    </section>
  `;
}

function RequestPreview({ request }) {
  return html`
    <details className="panel request-panel">
      <summary>API request preview</summary>
      <pre>${JSON.stringify(request, null, 2)}</pre>
    </details>
  `;
}

function applyBlockEvent(blocks, event) {
  if (event.type !== 'block' || !event.coordinate || !event.block) return blocks;
  const { x, y, z } = event.coordinate;
  const key = `${x}:${y}:${z}`;
  const withoutExisting = blocks.filter((block) => block.key !== key);
  if (event.block.op === 'remove') return withoutExisting;
  return [
    ...withoutExisting,
    { key, x, y, z, id: event.block.id, stage: event.stage },
  ];
}

export function Dashboard() {
  const [snapshot, send] = useMachine(pipelineMachine);
  const phase = String(snapshot.value);
  const [controls, setControls] = useState(DEFAULT_CONTROLS);
  const [blocks, setBlocks] = useState([]);
  const [logs, setLogs] = useState([]);
  const [images, setImages] = useState([]);
  const [paceMs, setPaceMs] = useState(700);
  const [manualGate, setManualGate] = useState(true);
  const [stageReady, setStageReady] = useState(false);
  const [streamStatus, setStreamStatus] = useState('idle');
  const [mode, setMode] = useState('api');
  const [apiBase, setApiBase] = useState(DEFAULT_API_BASE_URL);
  const [apiStatus, setApiStatus] = useState('not checked');
  const runnerRef = useRef(null);
  const api = useMemo(() => new StructureForgeApiClient(apiBase), [apiBase]);
  const request = useMemo(() => buildGenerateRequest(controls), [controls]);

  const onControlChange = (key, value) => {
    setControls((current) => ({ ...current, [key]: value }));
  };

  const ingestEvent = (event) => {
    setLogs((current) => [...current, event]);
    if (event.type === 'block') setBlocks((current) => applyBlockEvent(current, event));
    if (event.type === 'image' && event.image) {
      setImages((current) => [
        ...current.filter((item) => item.id !== event.image.id),
        event.image,
      ]);
    }
  };

  const checkApi = async () => {
    if (!apiBase) {
      setApiStatus('enter a base URL');
      return;
    }
    setApiStatus('checking…');
    try {
      const result = await api.health();
      setApiStatus(result?.ok ? 'connected' : 'unexpected response');
    } catch (error) {
      setApiStatus(`unavailable: ${error.message}`);
    }
  };

  const getPhaseEvents = async (currentPhase, signal) => {
    if (mode === 'demo') {
      return buildDemoPhaseEvents(currentPhase, controls, blocks.length);
    }

    if (!apiBase) throw new Error('Live API mode needs an API base URL.');
    let payload;
    if (currentPhase === 'drafting') payload = await api.generate(request, signal);
    else if (currentPhase === 'auditing') payload = await api.audit(request, signal);
    else if (currentPhase === 'rebuilding') payload = await api.plan(request, signal);
    else if (currentPhase === 'finalizing') {
      payload = await api.minecraftVersion(controls.targetVersion, signal);
    }
    return serializeApiResponseToEvents(currentPhase, payload || {});
  };

  useEffect(() => {
    if (!['drafting', 'auditing', 'rebuilding', 'finalizing'].includes(phase)) return undefined;

    const controller = new AbortController();
    runnerRef.current = controller;
    setStageReady(false);
    setStreamStatus('preparing');

    (async () => {
      try {
        const events = await getPhaseEvents(phase, controller.signal);
        await playSerializedEvents(events, {
          paceMs,
          signal: controller.signal,
          onEvent: ingestEvent,
          onStatus: setStreamStatus,
        });
        setStageReady(true);
      } catch (error) {
        if (error.name === 'AbortError') return;
        ingestEvent({
          id: crypto.randomUUID(),
          type: 'rationale',
          stage: phase,
          severity: 'error',
          message: 'Stage execution could not continue.',
          rationale: error.message,
        });
        setStreamStatus('error');
        setStageReady(true);
      }
    })();

    return () => controller.abort();
  }, [phase]);

  useEffect(() => {
    if (!manualGate && stageReady) {
      const timer = setTimeout(() => {
        if (phase === 'finalizing') send({ type: 'COMPLETE' });
        else if (['drafting', 'auditing', 'rebuilding'].includes(phase)) send({ type: 'ADVANCE' });
      }, Math.max(500, paceMs));
      return () => clearTimeout(timer);
    }
    return undefined;
  }, [manualGate, stageReady, phase, paceMs, send]);

  const begin = () => {
    setBlocks([]);
    setLogs([]);
    setImages([]);
    setStageReady(false);
    send({ type: 'BEGIN' });
  };

  const reset = () => {
    runnerRef.current?.abort();
    setStageReady(false);
    setStreamStatus('idle');
    send({ type: 'RESET' });
  };

  const advance = () => {
    setStageReady(false);
    if (phase === 'finalizing') send({ type: 'COMPLETE' });
    else send({ type: 'ADVANCE' });
  };

  return html`
    <div className="app-shell">
      <header className="topbar">
        <div className="brand-lockup">
          <div className="brand-mark" aria-hidden="true">SF</div>
          <div>
            <div className="brand-line">
              <h1>StructureForge</h1>
              <span className="system-badge">Continuity Works API</span>
            </div>
            <p>Generate, audit, rebuild, and validate Minecraft structures with AI.</p>
          </div>
        </div>
        <div className="topbar-actions">
          <a href="https://github.com/mrcalzon02/Continuity-Works" target="_blank" rel="noreferrer">Repository</a>
          <a href="https://github.com/mrcalzon02/Continuity-Works/blob/main/README.md" target="_blank" rel="noreferrer">API Docs</a>
        </div>
      </header>

      <section className="session-toolbar">
        <div className="mode-group">
          <label>
            <span>Execution source</span>
            <select value=${mode} onChange=${(event) => setMode(event.target.value)} disabled=${phase !== 'idle' && phase !== 'prompting'}>
              <option value="demo">Interactive demo stream</option>
              <option value="api">Live API + serialized replay</option>
            </select>
          </label>
          <label className="api-field">
            <span>API base URL</span>
            <input
              placeholder="https://continuity-works-mrcalzon02-api.onrender.com"
              value=${apiBase}
              onChange=${(event) => setApiBase(event.target.value)}
              disabled=${mode !== 'api' || !['idle', 'prompting'].includes(phase)}
            />
          </label>
          <button className="secondary" onClick=${checkApi} disabled=${mode !== 'api'}>Check API</button>
          <span className="api-status">${apiStatus}</span>
        </div>
        <div className="pace-group">
          <label>
            <span>Narration pace</span>
            <select value=${paceMs} onChange=${(event) => setPaceMs(Number(event.target.value))}>
              ${PACE_OPTIONS.map(([value, label]) => html`<option value=${value} key=${value}>${label}</option>`)}
            </select>
          </label>
          <label className="toggle-row">
            <input type="checkbox" checked=${manualGate} onChange=${(event) => setManualGate(event.target.checked)} />
            <span>Pause after each stage</span>
          </label>
          <span className=${`stream-status status-${streamStatus}`}>${streamStatus}</span>
        </div>
      </section>

      <${PhaseRail} phase=${phase} />

      <main className="workspace-grid">
        <${ControlPanel}
          controls=${controls}
          phase=${phase}
          onChange=${onControlChange}
        />

        <div className="center-stack">
          <${Viewport} blocks=${blocks} phase=${PHASE_LABELS[phase]} />
          <${AuditImageStrip} images=${images} />
          <${RequestPreview} request=${request} />
        </div>

        <${ProgressionLog} logs=${logs} />
      </main>

      <footer className="command-dock">
        <div>
          <span className="eyebrow">Current phase</span>
          <strong>${PHASE_LABELS[phase]}</strong>
          <small>
            ${phase === 'idle' && 'Ready to begin a new structural reasoning session.'}
            ${phase === 'prompting' && 'Configure optional constraints, then lock them and draft.'}
            ${phase === 'drafting' && 'Building a legible first-pass structural skeleton.'}
            ${phase === 'auditing' && 'Testing purpose, mechanics, context, and optional client visual evidence.'}
            ${phase === 'rebuilding' && 'Applying the lowest sufficient intervention for failed gates.'}
            ${phase === 'finalizing' && 'Separating static success from optional client visual and runtime checks.'}
          </small>
        </div>
        <div className="dock-actions">
          ${phase === 'idle' && html`<button className="primary" onClick=${begin}>Begin Session</button>`}
          ${phase === 'prompting' && html`
            <button className="secondary" onClick=${reset}>Cancel</button>
            <button className="primary" onClick=${() => send({ type: 'START_DRAFT' })}>Lock Constraints + Draft</button>
          `}
          ${['drafting', 'auditing', 'rebuilding', 'finalizing'].includes(phase) && html`
            <button className="secondary" onClick=${reset}>Reset</button>
            <button className="primary" disabled=${!stageReady} onClick=${advance}>
              ${stageReady ? nextPhaseLabel(phase) : 'Stage in progress…'}
            </button>
          `}
        </div>
      </footer>
    </div>
  `;
}
