const wait = (ms, signal) => new Promise((resolve, reject) => {
  const timer = setTimeout(resolve, ms);
  signal?.addEventListener('abort', () => {
    clearTimeout(timer);
    reject(new DOMException('Aborted', 'AbortError'));
  }, { once: true });
});

export async function playSerializedEvents(events, { paceMs = 700, signal, onEvent, onStatus }) {
  onStatus?.('playing');
  for (const event of events) {
    if (signal?.aborted) throw new DOMException('Aborted', 'AbortError');
    onEvent(event);
    await wait(event.delay_ms ?? paceMs, signal);
  }
  onStatus?.('ready');
}

export function normalizeStreamEvent(raw) {
  return {
    id: raw.id || crypto.randomUUID(),
    type: raw.type || 'rationale',
    stage: raw.stage || raw.phase || 'unknown',
    message: raw.message || raw.action || 'Pipeline update',
    rationale: raw.rationale || raw.reasoning_summary || raw.reasoning || raw.why || '',
    coordinate: raw.coordinate || raw.position || null,
    block: raw.block || null,
    image: raw.image || null,
    validation: raw.validation || null,
    severity: raw.severity || 'info',
    delay_ms: raw.delay_ms,
  };
}

export function connectSSE(url, handlers = {}) {
  const source = new EventSource(url);
  source.onopen = () => handlers.onStatus?.('connected');
  source.onerror = (error) => handlers.onError?.(error);
  source.onmessage = (message) => {
    try { handlers.onEvent?.(normalizeStreamEvent(JSON.parse(message.data))); }
    catch (error) { handlers.onError?.(error); }
  };
  return () => source.close();
}

export function connectWebSocket(url, handlers = {}) {
  const socket = new WebSocket(url);
  socket.onopen = () => handlers.onStatus?.('connected');
  socket.onerror = (error) => handlers.onError?.(error);
  socket.onclose = () => handlers.onStatus?.('closed');
  socket.onmessage = (message) => {
    try { handlers.onEvent?.(normalizeStreamEvent(JSON.parse(message.data))); }
    catch (error) { handlers.onError?.(error); }
  };
  return () => socket.close();
}

const say = (stage, message, rationale, severity = 'info') => normalizeStreamEvent({ type: 'rationale', stage, message, rationale, severity });
const block = (stage, x, y, z, id, message, rationale, delay_ms = 20) => normalizeStreamEvent({
  type: 'block', stage, coordinate: { x, y, z }, block: { id, op: 'add' }, message, rationale, delay_ms,
});
const gate = (stage, message, rationale, name, status) => normalizeStreamEvent({
  type: 'validation', stage, message, rationale, validation: { gate: name, status },
  severity: status === 'pass' ? 'info' : 'warning',
});

function svgPreview(label, subtitle, accent = '#79c0ff') {
  const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="640" height="360" viewBox="0 0 640 360">
  <rect width="640" height="360" fill="#0b1118"/><path d="M90 275 L320 90 L550 275 Z" fill="#162332" stroke="${accent}" stroke-width="4"/>
  <path d="M160 275 L320 145 L480 275" fill="none" stroke="#33495f" stroke-width="10"/>
  <text x="28" y="44" fill="#e6edf3" font-family="system-ui" font-size="24" font-weight="700">${label}</text>
  <text x="28" y="76" fill="#9fb0c0" font-family="system-ui" font-size="16">${subtitle}</text></svg>`;
  return `data:image/svg+xml;charset=utf-8,${encodeURIComponent(svg)}`;
}

function auditFrame(stage, id, label, subtitle, accent) {
  return normalizeStreamEvent({
    type: 'image', stage, message: `Generated ${label.toLowerCase()} audit frame.`,
    rationale: 'This is review evidence, not a substitute for fresh-world runtime validation.',
    image: { id, label, url: svgPreview(label, subtitle, accent) },
  });
}

function roadBlocks(stage, width = 6, padding = 5, length = 28) {
  const out = [];
  const total = width + padding * 2;
  const x0 = -Math.floor(total / 2);
  const road0 = x0 + padding;
  const road1 = road0 + width - 1;
  const half = Math.min(18, Math.max(8, Math.floor(length / 2)));
  for (let z = -half; z <= half; z += 1) {
    for (let i = 0; i < total; i += 1) {
      const x = x0 + i;
      const isRoad = x >= road0 && x <= road1;
      out.push(block(stage, x, 0, z, isRoad ? 'minecraft:gray_concrete' : 'minecraft:grass_block',
        isRoad ? 'Extending six-block roadbed.' : 'Reserving five-block terrain margin.',
        isRoad ? 'The road surface preserves the hard six-block width.' : 'The margin remains available for sidewalk, verge, utilities, retaining, frontage, or terrain blending.', 10));
    }
  }
  return out;
}

function highwayBlocks(stage, profile = {}) {
  const lanes = Number(profile.lane_count ?? 4);
  const laneWidth = Number(profile.lane_width ?? 3);
  const shoulders = Number(profile.shoulder_width ?? 1) * 2;
  const median = Number(profile.median_width ?? 2);
  const width = Math.max(8, Math.min(20, lanes * laneWidth + shoulders + median));
  const x0 = -Math.floor(width / 2);
  const out = [];
  for (let z = -14; z <= 14; z += 1) {
    for (let i = 0; i < width; i += 1) out.push(block(stage, x0 + i, 4, z, 'minecraft:stone',
      'Extending highway deck.', 'Deck width is serialized before the support rhythm so its cross-section remains inspectable.', 8));
  }
  const spacing = Math.max(5, Math.min(14, Number(profile.support_spacing ?? 12)));
  for (let z = -12; z <= 12; z += spacing) for (const x of [x0 + 2, x0 + width - 3]) for (let y = 0; y < 4; y += 1) {
    out.push(block(stage, x, y, z, 'minecraft:stone_bricks', 'Adding repeating pier.',
      'The pier rhythm preserves lower-level/water clearance while making the elevated reference language structurally legible.', 15));
  }
  return out;
}

function facilityBlocks(stage, moduleType, variant) {
  const industrial = moduleType === 'industrial_facility';
  const width = industrial ? 16 : 14;
  const depth = variant === 'rural' ? 12 : 10;
  const shell = industrial ? 'minecraft:stone_bricks' : 'minecraft:bricks';
  const out = [];
  const xh = Math.floor(width / 2), zh = Math.floor(depth / 2);
  for (let x = -xh; x <= xh; x += 1) for (const z of [-zh, zh]) out.push(block(stage, x, 0, z, shell,
    'Establishing facility envelope.', 'The shell follows the already-declared program and access contract.', 15));
  for (let z = -zh + 1; z < zh; z += 1) for (const x of [-xh, xh]) out.push(block(stage, x, 0, z, shell,
    'Closing facility envelope.', 'Perimeter geometry establishes frontage and service-access datums.', 15));
  const zones = industrial
    ? [['minecraft:iron_block', -4, 'workshop'], ['minecraft:barrel', 0, 'storage'], ['minecraft:yellow_concrete', 4, 'loading']]
    : [['minecraft:oak_planks', -4, 'public service'], ['minecraft:bookshelf', 0, 'records'], ['minecraft:iron_block', 4, 'utilities']];
  for (const [id, x, name] of zones) for (let z = -2; z <= 2; z += 1) out.push(block(stage, x, 1, z, id,
    `Marking ${name} zone.`, `${name} is represented as functional evidence rather than decorative filler.`, 30));
  return out;
}

function infrastructureDemo(phase, controls, blockCount) {
  const type = controls.infrastructureModule;
  if (phase === 'drafting') {
    const out = [
      say(phase, `Locked ${type} generation contract.`, `World seed ${controls.worldSeed}; module seed ${controls.seed}; ${controls.infrastructureVariant} context; ${controls.orientation} orientation.`),
      say(phase, 'Separating geometry from placement compatibility.', 'Jigsaw, Lost Cities, world-seed placement, and purpose depth remain explicit contracts while the viewport serializes physical assembly.'),
    ];
    if (type === 'inner_city_road') {
      out.push(say(phase, 'Applying hard 5 | 6 | 5 cross-section.', 'Five integration blocks, six roadbed blocks, five integration blocks: total module width sixteen.'));
      out.push(...roadBlocks(phase, Number(controls.innerCityRoadWidth), Number(controls.terrainPadding), Number(controls.segmentLength)));
    } else if (type === 'highway') {
      out.push(say(phase, `Applying ${controls.highwayProfile}.`, 'The visual reference informs deck, barrier, pier, and clearance language while dimensions remain explicit caller inputs.'));
      out.push(...highwayBlocks(phase, {
        lane_count: controls.laneCount, lane_width: controls.laneWidth, shoulder_width: controls.shoulderWidth,
        median_width: controls.medianWidth, support_spacing: controls.supportSpacing,
      }));
    } else {
      out.push(say(phase, `Programming ${controls.infrastructureVariant} ${type.replace('_', ' ')}.`, `Purpose depth ${controls.purposeDepth} requires functional zoning and access dependencies before a shell is accepted.`));
      out.push(...facilityBlocks(phase, type, controls.infrastructureVariant));
    }
    out.push(say(phase, 'Infrastructure draft ready for audit.', 'The visible assembly is inspectable; actual Lost Cities placement remains a later runtime gate.'));
    return out;
  }
  if (phase === 'auditing') return [
    say(phase, 'Auditing dimensions, purpose depth, and integration contracts.', `${blockCount} preview blocks are visible; jigsaw=${controls.jigsawEnabled}; Lost Cities=${controls.lostCitiesEnabled}.`),
    auditFrame(phase, 'oblique', 'Infrastructure Oblique', `${type} · structural rhythm`, '#79c0ff'),
    auditFrame(phase, 'plan', 'Infrastructure Plan', 'cross-section · zones · connectors', '#8ee8c2'),
    auditFrame(phase, 'damage', 'Integration Review', 'terrain · city grid · runtime boundary', '#f2cc60'),
    gate(phase, 'Static infrastructure contract: PASS candidate', 'Dimension, purpose, connector, and deterministic placement contracts are ready for final validation.', 'static_contract', 'pass'),
  ];
  if (phase === 'rebuilding') return [
    say(phase, 'Preserving a passing infrastructure contract.', 'The repair system applies the lowest sufficient intervention and does not cosmetically rewrite valid roads, connectors, or zones.'),
    say(phase, 'Reserving project materialization as a downstream concern.', 'Palette/detail adapters may change appearance without mutating world-seed, cross-section, jigsaw, or purpose invariants.'),
  ];
  if (phase === 'finalizing') {
    const lc = controls.lostCitiesEnabled === 'true';
    return [
      gate(phase, 'Dimensional infrastructure gate: PASS', 'Hard spatial invariants remain internally consistent.', 'dimensions', 'pass'),
      gate(phase, 'World-seed reproducibility gate: PASS', `Placement derives deterministically from world seed ${controls.worldSeed}, salt, module type, variant, and module seed.`, 'world_seed', 'pass'),
      gate(phase, 'Jigsaw contract gate: PASS candidate', 'Named endpoints/frontage/service connectors and maximum assembly depth are explicit.', 'jigsaw', 'pass'),
      gate(phase, lc ? 'Lost Cities fresh-world placement: RUNTIME REQUIRED' : 'Lost Cities integration: NOT REQUESTED',
        lc ? 'Static output cannot certify behavior inside the mod; a compatible fresh-world runtime test remains mandatory.' : 'The compatibility contract exists but the master toggle is disabled.',
        'lost_cities_runtime', lc ? 'deferred' : 'pass'),
      say(phase, 'Infrastructure candidate finalized for adapter/runtime review.', 'Static generation is complete without falsely promoting unresolved modded-world behavior to a shipping PASS.'),
    ];
  }
  return [];
}

function genericDemo(phase, controls, blockCount) {
  if (phase === 'drafting') {
    const out = [say(phase, 'Creating first-pass structural skeleton.', `${controls.structureType} on Minecraft ${controls.targetVersion}; purpose and circulation drive massing before detail.`)];
    for (let x = -5; x <= 5; x += 1) for (const z of [-4, 4]) out.push(block(phase, x, 0, z, 'minecraft:polished_andesite', 'Placing foundation edge.', 'The perimeter is established before vertical detail.', 35));
    for (let z = -3; z <= 3; z += 1) for (const x of [-5, 5]) out.push(block(phase, x, 0, z, 'minecraft:polished_andesite', 'Closing foundation edge.', 'The footprint remains visible for audit.', 35));
    for (const [x,z] of [[-5,-4],[5,-4],[-5,4],[5,4]]) for (let y = 1; y <= 4; y += 1) out.push(block(phase, x, y, z, 'minecraft:oak_log', 'Raising structural support.', 'Corner supports communicate the primary structural datum.', 35));
    out.push(say(phase, 'Draft skeleton ready for independent audit.', 'The draft remains intentionally incomplete so purpose failures are still visible.'));
    return out;
  }
  if (phase === 'auditing') return [
    say(phase, 'Checking mechanical validity before aesthetics.', `The draft contains ${blockCount} visible blocks and remains subject to purpose and circulation review.`),
    auditFrame(phase, 'oblique', 'Oblique Audit', 'massing and entrance hierarchy', '#79c0ff'),
    auditFrame(phase, 'plan', 'Plan Audit', 'circulation and zone adjacency', '#8ee8c2'),
    auditFrame(phase, 'damage', 'Damage-State Audit', 'readability under partial destruction', '#f2cc60'),
    say(phase, 'Program evidence requires refinement.', 'Utilities, storage, controlled access, and purpose-specific zones must remain legible.', 'warning'),
  ];
  if (phase === 'rebuilding') return [
    say(phase, `Applying intervention no higher than level ${controls.repairCeiling}.`, 'The system preserves geometry that already passes and changes only failed functional evidence.'),
    block(phase, -3, 1, 0, 'minecraft:iron_block', 'Adding utility spine.', 'This block communicates a required functional system.'),
    block(phase, 0, 1, 2, 'minecraft:glass', 'Adding functional partition.', 'The partition clarifies zone identity and circulation.'),
    block(phase, 3, 1, 0, 'minecraft:barrel', 'Adding storage evidence.', 'Storage is represented as program evidence rather than decoration.'),
  ];
  if (phase === 'finalizing') return [
    gate(phase, 'Mechanical contract: PASS', 'The candidate remains within the demonstration envelope.', 'mechanical', 'pass'),
    gate(phase, 'Purpose review: HUMAN VISUAL REVIEW REQUIRED', 'Automated generation does not grant its own final visual approval.', 'purpose', 'review'),
    gate(phase, 'Worldgen runtime placement: DEFERRED', 'A browser preview cannot substitute for controlled fresh-world placement.', 'worldgen', 'deferred'),
  ];
  return [];
}

export function buildDemoPhaseEvents(phase, controls, blockCount = 0) {
  return controls.generatorProvider === 'native_infrastructure_v1' ? infrastructureDemo(phase, controls, blockCount) : genericDemo(phase, controls, blockCount);
}

function infrastructureApiEvents(phase, generated) {
  const layout = generated.layout || {};
  const type = generated.module_type || 'infrastructure';
  const out = [say(phase, `API generated ${type} with ${generated.engine}.`, `Static fitness ${generated.fitness?.status || 'unknown'}; world seed ${generated.world_seed ?? 'not returned'}.`)];
  if (phase === 'drafting') {
    if (type === 'inner_city_road') out.push(...roadBlocks(phase, layout.roadbed_width ?? 6, layout.terrain_padding?.left ?? 5, layout.footprint_blocks?.[1] ?? 28));
    else if (type === 'highway') out.push(...highwayBlocks(phase, layout.profile || {}));
    else out.push(...facilityBlocks(phase, type, generated.variant || 'urban'));
  }
  const anchor = generated.spawn?.candidate_anchor;
  if (anchor) out.push(say(phase, `World-seed candidate anchor ${anchor.x}, ${anchor.z}.`, `The coordinate is snapped to ${generated.spawn.grid_snap_blocks} blocks using ${generated.spawn.derivation}.`));
  const grid = generated.lost_cities?.tileable_grid;
  if (grid?.enabled) out.push(say(phase, `Lost Cities tile reservation: ${grid.reservation_strategy}.`, `Required footprint is ${(grid.required_footprint_chunks || []).join(' × ')} chunks; requested span ${grid.requested_tile_span_chunks}.`));
  if (generated.jigsaw?.enabled) out.push(say(phase, `Jigsaw connectors ${generated.jigsaw.connectors?.length || 0}.`, `Pool ${generated.jigsaw.pool}; maximum depth ${generated.jigsaw.max_depth}.`));
  if (generated.lost_cities?.enabled) out.push(say(phase, `Lost Cities contract ${generated.lost_cities.adapter_status}.`, `Modes ${(generated.lost_cities.spawn_modes || []).join(', ')}. Runtime compatibility is not self-certified.`));
  if (generated.purpose) out.push(say(phase, `Purpose depth ${generated.purpose.depth}: ${generated.purpose.depth_label}.`, `Zones ${(generated.purpose.zones || []).join(', ') || 'none'}.`));
  return out;
}

export function serializeApiResponseToEvents(phase, payload) {
  const generated = payload?.generated_layout || payload?.layout || null;
  if (generated?.engine === 'native_infrastructure_v1') return [
    say(phase, `Received ${phase} response from StructureSmith.`, 'The synchronous result is replayed at human-readable pace until native server events are available.'),
    ...infrastructureApiEvents(phase, generated),
    say(phase, 'Infrastructure response replay complete.', 'Viewport and narration were reconstructed from the authoritative API result.'),
  ];
  const events = [say(phase, `Received ${phase} response from StructureSmith.`, 'The synchronous API response is replayed as milestones until a native SSE/WebSocket stream is available.')];
  const layout = payload?.generated_layout || payload?.layout || payload?.plan || null;
  const fitness = layout?.fitness || payload?.fitness || payload?.audit || null;
  if (fitness) events.push(say(phase, 'API returned a fitness/audit result.', JSON.stringify(fitness).slice(0, 360)));
  const artifact = payload?.structure_artifact || payload?.artifact || null;
  if (artifact) events.push(say(phase, 'API produced or referenced a structure artifact.', JSON.stringify(artifact).slice(0, 360)));
  events.push(say(phase, 'Response replay complete.', 'Future native stream events can use the same normalized event contract.'));
  return events;
}
