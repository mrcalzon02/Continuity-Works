const wait = (ms, signal) =>
  new Promise((resolve, reject) => {
    const timer = setTimeout(resolve, ms);
    signal?.addEventListener(
      'abort',
      () => {
        clearTimeout(timer);
        reject(new DOMException('Aborted', 'AbortError'));
      },
      { once: true },
    );
  });

export async function playSerializedEvents(events, options) {
  const {
    paceMs = 700,
    signal,
    onEvent,
    onStatus,
  } = options;

  onStatus?.('playing');
  for (const event of events) {
    if (signal?.aborted) throw new DOMException('Aborted', 'AbortError');
    onEvent(event);
    await wait(event.delay_ms ?? paceMs, signal);
  }
  onStatus?.('ready');
}

export function connectSSE(url, handlers = {}) {
  const source = new EventSource(url);
  source.onopen = () => handlers.onStatus?.('connected');
  source.onerror = (error) => handlers.onError?.(error);
  source.onmessage = (message) => {
    try {
      const raw = JSON.parse(message.data);
      handlers.onEvent?.(normalizeStreamEvent(raw));
    } catch (error) {
      handlers.onError?.(error);
    }
  };
  return () => source.close();
}

export function connectWebSocket(url, handlers = {}) {
  const socket = new WebSocket(url);
  socket.onopen = () => handlers.onStatus?.('connected');
  socket.onerror = (error) => handlers.onError?.(error);
  socket.onclose = () => handlers.onStatus?.('closed');
  socket.onmessage = (message) => {
    try {
      handlers.onEvent?.(normalizeStreamEvent(JSON.parse(message.data)));
    } catch (error) {
      handlers.onError?.(error);
    }
  };
  return () => socket.close();
}

export function normalizeStreamEvent(raw) {
  return {
    id: raw.id || crypto.randomUUID(),
    type: raw.type || 'rationale',
    stage: raw.stage || raw.phase || 'unknown',
    message: raw.message || raw.action || 'Pipeline update',
    rationale:
      raw.rationale || raw.reasoning_summary || raw.reasoning || raw.why || '',
    coordinate: raw.coordinate || raw.position || null,
    block: raw.block || null,
    image: raw.image || null,
    validation: raw.validation || null,
    severity: raw.severity || 'info',
    delay_ms: raw.delay_ms,
  };
}

function blockEvent(stage, x, y, z, block, message, rationale, op = 'add') {
  return normalizeStreamEvent({
    type: 'block',
    stage,
    message,
    rationale,
    coordinate: { x, y, z },
    block: { id: block, op },
  });
}

function rationale(stage, message, why, severity = 'info') {
  return normalizeStreamEvent({
    type: 'rationale',
    stage,
    message,
    rationale: why,
    severity,
  });
}

function svgPreview(label, subtitle, accent = '#79c0ff') {
  const svg = `
    <svg xmlns="http://www.w3.org/2000/svg" width="640" height="360" viewBox="0 0 640 360">
      <rect width="640" height="360" fill="#0b1118"/>
      <path d="M90 275 L320 90 L550 275 Z" fill="#162332" stroke="${accent}" stroke-width="4"/>
      <path d="M160 275 L320 145 L480 275" fill="none" stroke="#33495f" stroke-width="10"/>
      <rect x="284" y="215" width="72" height="60" fill="#0f1722" stroke="${accent}" stroke-width="3"/>
      <text x="28" y="44" fill="#e6edf3" font-family="system-ui, sans-serif" font-size="24" font-weight="700">${label}</text>
      <text x="28" y="76" fill="#9fb0c0" font-family="system-ui, sans-serif" font-size="16">${subtitle}</text>
      <text x="28" y="330" fill="${accent}" font-family="ui-monospace, monospace" font-size="14">STRUCTUREFORGE AUDIT FRAME</text>
    </svg>`;
  return `data:image/svg+xml;charset=utf-8,${encodeURIComponent(svg)}`;
}

export function buildDemoPhaseEvents(phase, controls, blockCount = 0) {
  const events = [];
  const wall = controls.culturalTheme === 'ruined_high_tech'
    ? 'minecraft:deepslate_tiles'
    : 'minecraft:stone_bricks';
  const support = 'minecraft:oak_log';
  const floor = 'minecraft:polished_andesite';

  if (phase === 'drafting') {
    events.push(
      rationale(
        phase,
        'Locked the purpose contract and target version.',
        `${controls.structureType} on Minecraft ${controls.targetVersion}; mandatory circulation and required zones will drive the first-pass massing.`,
      ),
      rationale(
        phase,
        'Creating a readable structural skeleton before detail.',
        'Macro massing is established first so room purpose and traversal can be audited before decorative block density hides planning defects.',
      ),
    );

    for (let x = -5; x <= 5; x += 1) {
      events.push(
        blockEvent(
          phase,
          x,
          0,
          -4,
          floor,
          `Placing foundation edge at ${x},0,-4.`,
          'This establishes the north footprint boundary and gives later walls a stable, inspectable reference line.',
        ),
        blockEvent(
          phase,
          x,
          0,
          4,
          floor,
          `Placing foundation edge at ${x},0,4.`,
          'This establishes the south footprint boundary while preserving an eight-block interior depth for circulation.',
        ),
      );
    }
    for (let z = -3; z <= 3; z += 1) {
      events.push(
        blockEvent(
          phase,
          -5,
          0,
          z,
          floor,
          `Closing west foundation edge at -5,0,${z}.`,
          'The perimeter is closed before vertical construction so the audit can compare footprint against the requested size envelope.',
        ),
        blockEvent(
          phase,
          5,
          0,
          z,
          floor,
          `Closing east foundation edge at 5,0,${z}.`,
          'The perimeter is closed symmetrically to keep the draft legible; later rebuilding may intentionally break symmetry for function or context.',
        ),
      );
    }

    [
      [-5, -4],
      [5, -4],
      [-5, 4],
      [5, 4],
    ].forEach(([x, z]) => {
      for (let y = 1; y <= 4; y += 1) {
        events.push(
          blockEvent(
            phase,
            x,
            y,
            z,
            support,
            `Raising support at ${x},${y},${z}.`,
            'Corner supports make load-bearing intent visually explicit and define a reliable vertical datum for the first roof and wall pass.',
          ),
        );
      }
    });

    [-4, -2, 0, 2, 4].forEach((x) => {
      if (x !== 0) {
        events.push(
          blockEvent(
            phase,
            x,
            1,
            -4,
            wall,
            `Drafting north wall bay at ${x},1,-4.`,
            'The center bay is intentionally left open as a provisional entrance so the circulation audit has a concrete route to evaluate.',
          ),
        );
      }
    });

    events.push(
      rationale(
        phase,
        'Draft skeleton is ready for an independent audit.',
        'The footprint, supports, entrance, and basic envelope now exist without pretending the structure is finished architecture.',
      ),
    );
  }

  if (phase === 'auditing') {
    events.push(
      rationale(
        phase,
        'Checking mechanical validity before aesthetics.',
        'A visually attractive rebuild is irrelevant if the structure cannot preserve placement, traversal, version, and integration contracts.',
      ),
      rationale(
        phase,
        'Entrance route passes, but interior program is under-specified.',
        'The draft communicates an envelope but not yet a laboratory: utilities, storage, secure core, and work zones need architectural evidence.',
        'warning',
      ),
      normalizeStreamEvent({
        type: 'image',
        stage: phase,
        message: 'Generated oblique audit frame.',
        rationale: 'Oblique review exposes massing, entrance hierarchy, and missing secondary volumes more clearly than a plan alone.',
        image: {
          id: 'oblique',
          label: 'Oblique',
          url: svgPreview('Oblique Audit', `${blockCount} visible blocks · massing review`),
        },
      }),
      normalizeStreamEvent({
        type: 'image',
        stage: phase,
        message: 'Generated plan audit frame.',
        rationale: 'Plan review isolates circulation and zone adjacency so decorative detail cannot conceal a broken functional layout.',
        image: {
          id: 'plan',
          label: 'Plan',
          url: svgPreview('Plan Audit', 'entry → lab → secure core', '#8ee8c2'),
        },
      }),
      normalizeStreamEvent({
        type: 'image',
        stage: phase,
        message: 'Generated damage-state audit frame.',
        rationale: 'A ruin-oriented project must remain readable after damage; this frame reserves a later visual gate for that condition.',
        image: {
          id: 'damage',
          label: 'Damage state',
          url: svgPreview('Damage-State Audit', 'readability under partial destruction', '#f2cc60'),
        },
      }),
      rationale(
        phase,
        `Audit score 0.76 is below the requested ${controls.auditThreshold} threshold.`,
        'The lowest sufficient intervention is a functional rebuild: preserve the shell and entrance datum, but add program-specific volumes and clearer circulation.',
        'warning',
      ),
    );
  }

  if (phase === 'rebuilding') {
    events.push(
      rationale(
        phase,
        `Selecting intervention level ${controls.repairCeiling} as the maximum, not the automatic target.`,
        'The rebuild changes only the failed functional evidence while preserving geometry that already satisfies the draft and integration contracts.',
      ),
    );

    [
      [-3, 1, 0, 'minecraft:iron_block', 'utility spine'],
      [-3, 2, 0, 'minecraft:iron_block', 'utility spine'],
      [0, 1, 2, 'minecraft:glass', 'laboratory partition'],
      [0, 2, 2, 'minecraft:glass', 'laboratory partition'],
      [3, 1, 0, 'minecraft:barrel', 'storage zone'],
      [3, 1, 2, 'minecraft:chest', 'evidence / secure storage'],
      [0, 1, -3, 'minecraft:iron_door', 'controlled access'],
      [0, 2, -3, 'minecraft:redstone_lamp', 'entrance hierarchy'],
    ].forEach(([x, y, z, block, purpose]) => {
      events.push(
        blockEvent(
          phase,
          x,
          y,
          z,
          block,
          `Adding ${purpose} at ${x},${y},${z}.`,
          `This block is not decorative filler; it is placed to make the ${purpose} legible as part of the requested ${controls.purposeKind} program.`,
        ),
      );
    });

    events.push(
      rationale(
        phase,
        'Functional rebuild complete; preserved shell remains recognizable.',
        'The new zones fix the failed audit without escalating to full recontextualization.',
      ),
    );
  }

  if (phase === 'finalizing') {
    events.push(
      rationale(
        phase,
        'Applying final validation gates to the rebuilt candidate.',
        'Mechanical validity, purpose evidence, target-version compatibility, and required shipping checks are evaluated separately so one success cannot mask another failure.',
      ),
    );

    [-4, -2, 0, 2, 4].forEach((x) => {
      events.push(
        blockEvent(
          phase,
          x,
          4,
          0,
          'minecraft:stone_slab',
          `Adding roof datum at ${x},4,0.`,
          'The roof pass closes the massing while remaining sparse enough for a final visual review to identify silhouette problems.',
        ),
      );
    });

    events.push(
      normalizeStreamEvent({
        type: 'validation',
        stage: phase,
        message: 'Mechanical parse / placement contract: PASS',
        rationale: 'The candidate remains within the demonstration envelope and uses version-safe vanilla block identifiers.',
        validation: { gate: 'mechanical', status: 'pass' },
      }),
      normalizeStreamEvent({
        type: 'validation',
        stage: phase,
        message: 'Purpose-fitness review: PASS WITH VISUAL REVIEW REQUIRED',
        rationale: 'Required functional evidence is now present, but automated generation does not grant its own final visual approval.',
        validation: { gate: 'purpose', status: 'review' },
      }),
      normalizeStreamEvent({
        type: 'validation',
        stage: phase,
        message: 'Worldgen runtime placement: DEFERRED',
        rationale: 'Static browser visualization cannot substitute for a controlled fresh-world runtime placement test.',
        validation: { gate: 'worldgen', status: 'deferred' },
      }),
      rationale(
        phase,
        'Candidate is finalized for external visual and runtime review.',
        'The page deliberately stops short of self-certifying a shipping structure when runtime placement and human visual review remain unresolved.',
      ),
    );
  }

  return events;
}

export function serializeApiResponseToEvents(phase, payload) {
  const events = [
    rationale(
      phase,
      `Received ${phase} response from the StructureSmith API.`,
      'The current HTTP API is synchronous, so the interface replays response milestones at a readable pace until a native SSE/WebSocket stream is available.',
    ),
  ];

  const layout = payload?.generated_layout || payload?.layout || payload?.plan || null;
  const fitness = layout?.fitness || payload?.fitness || payload?.audit || null;
  if (fitness) {
    events.push(
      rationale(
        phase,
        'API returned a fitness / audit result.',
        JSON.stringify(fitness).slice(0, 360),
      ),
    );
  }

  const artifact = payload?.structure_artifact || payload?.artifact || null;
  if (artifact) {
    events.push(
      rationale(
        phase,
        'API produced or referenced a structure artifact.',
        JSON.stringify(artifact).slice(0, 360),
      ),
    );
  }

  events.push(
    rationale(
      phase,
      'Response replay complete.',
      'Future native stream events can use the same normalized event contract without replacing the viewport, progression log, or state machine.',
    ),
  );
  return events;
}
