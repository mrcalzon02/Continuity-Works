export const DEFAULT_CONTROLS = {
  generatorProvider: 'native_modular_v1',
  structureType: 'laboratory',
  targetVersion: '1.20.1',
  footprint: '72x60',
  scale: '1.0',
  modularity: 'triple_fold',
  seed: '9001',
  auditProfile: 'purpose_and_mechanical',
  auditThreshold: '0.82',
  preservationMode: 'preserve_integration_contracts',
  validationProfile: 'shipping_gate',
  worldgenCheck: 'required',
  evidenceLootCheck: 'required',
  renderAngles: 'four_angle',
  damageStates: 'intact_and_ruined',
  renderCadence: 'audit_milestones',
  repairCeiling: '5',
  preserveShell: 'when_viable',
  circulationPriority: 'high',
  purposeKind: 'laboratory',
  culturalTheme: 'project_defined',
  requiredZones: 'entry, laboratory, utilities, storage, secure_core',
  infrastructureModule: 'inner_city_road',
  infrastructureVariant: 'urban',
  worldSeed: '9001',
  orientation: 'north_south',
  segmentLength: '64',
  innerCityRoadWidth: '6',
  terrainPadding: '5',
  highwayProfile: 'elevated_urban_water_crossing',
  laneCount: '4',
  laneWidth: '3',
  shoulderWidth: '1',
  medianWidth: '2',
  highwayElevated: 'true',
  supportSpacing: '12',
  deckThickness: '2',
  minClearance: '6',
  jigsawEnabled: 'true',
  jigsawPool: 'structuresmith:infrastructure',
  connectorWidth: '3',
  jigsawMaxDepth: '8',
  lostCitiesEnabled: 'false',
  lostCitiesSpawnModes: 'all',
  tileSpanChunks: '1',
  randomRadiusBlocks: '4096',
  randomSpacingBlocks: '256',
  randomSalt: '734287',
  purposeDepth: '3',
  facilityKind: 'auto',
};

export const CONTROL_MODULES = [
  {
    id: 'generator',
    title: 'StructureForge Generator',
    description: 'Spatial skeleton, Minecraft target, scale, and modularity.',
    editableStates: ['idle', 'prompting'],
    fields: [
      { key: 'generatorProvider', label: 'Generator provider', type: 'select', options: [
        ['native_modular_v1', 'Native Modular v1'],
        ['native_infrastructure_v1', 'Native Infrastructure v1'],
        ['donjon_compatible', 'donjon-compatible vocabulary'],
        ['project_provider', 'Registered project provider (backend extension)'],
      ]},
      { key: 'structureType', label: 'Structure type', type: 'select', options: [
        ['laboratory', 'Laboratory'], ['fortress', 'Fortress'], ['warehouse', 'Warehouse'],
        ['residence', 'Residence'], ['temple', 'Temple'], ['underground_complex', 'Underground complex'],
        ['ruin', 'Ruin'], ['infrastructure', 'Infrastructure'], ['road', 'Road'], ['highway', 'Highway'],
        ['civic', 'Civic facility'], ['industrial', 'Industrial facility'],
      ]},
      { key: 'targetVersion', label: 'Minecraft version', type: 'select', options: [
        ['1.12.2', '1.12.2 (layout only without legacy adapter)'], ['1.16.5', '1.16.5'],
        ['1.18.2', '1.18.2'], ['1.19.2', '1.19.2'], ['1.19.4', '1.19.4'],
        ['1.20.1', '1.20.1'], ['1.21', '1.21'], ['1.21.1', '1.21.1'],
      ]},
      { key: 'footprint', label: 'Preferred footprint', type: 'select', options: [
        ['32x32', '32 × 32'], ['48x48', '48 × 48'], ['72x60', '72 × 60'],
        ['96x96', '96 × 96'], ['128x96', '128 × 96'],
      ]},
      { key: 'scale', label: 'Scale multiplier', type: 'select', options: [
        ['0.75', '0.75× compact'], ['1.0', '1.0× standard'], ['1.5', '1.5× expanded'], ['2.0', '2.0× monumental'],
      ]},
      { key: 'modularity', label: 'Modularity', type: 'select', options: [
        ['triple_fold', 'Triple-fold macro / meso / micro'], ['room_graph', 'Room graph only'], ['linear', 'Linear / corridor-driven'],
      ]},
      { key: 'seed', label: 'Deterministic module seed', type: 'text' },
    ],
  },
  {
    id: 'infrastructure',
    title: 'StructureForge Infrastructure',
    description: 'Road/highway geometry, world-seed placement, jigsaw assembly, Lost Cities integration, and urban/rural facility variants. These fields mirror the public infrastructure_layout API schema.',
    editableStates: ['idle', 'prompting'],
    fields: [
      { key: 'infrastructureModule', label: 'Infrastructure module', type: 'select', options: [
        ['inner_city_road', 'Inner-city road'], ['highway', 'Highway'], ['civic_facility', 'Civic facility'], ['industrial_facility', 'Industrial facility'],
      ]},
      { key: 'infrastructureVariant', label: 'Context variant', type: 'select', options: [['urban', 'Urban'], ['rural', 'Rural']] },
      { key: 'worldSeed', label: 'World seed', type: 'text' },
      { key: 'orientation', label: 'Orientation', type: 'select', options: [['north_south', 'North / south'], ['east_west', 'East / west']] },
      { key: 'segmentLength', label: 'Segment length (blocks)', type: 'text' },
      { key: 'innerCityRoadWidth', label: 'Inner-city road width', type: 'select', options: [['6', '6 blocks — strict contract']] },
      { key: 'terrainPadding', label: 'Terrain padding / side', type: 'select', options: [['5', '5 blocks — strict contract']] },
      { key: 'highwayProfile', label: 'Highway derivative', type: 'select', options: [
        ['elevated_urban_water_crossing', 'Elevated urban / water crossing (reference-derived)'], ['surface_highway', 'Surface highway'],
      ]},
      { key: 'laneCount', label: 'Highway lane count', type: 'text' },
      { key: 'laneWidth', label: 'Lane width (blocks)', type: 'text' },
      { key: 'shoulderWidth', label: 'Shoulder width (blocks)', type: 'text' },
      { key: 'medianWidth', label: 'Median width (blocks)', type: 'text' },
      { key: 'highwayElevated', label: 'Elevated deck', type: 'select', options: [['true', 'Enabled'], ['false', 'Disabled']] },
      { key: 'supportSpacing', label: 'Pier/support spacing', type: 'text' },
      { key: 'deckThickness', label: 'Deck thickness', type: 'text' },
      { key: 'minClearance', label: 'Minimum clearance', type: 'text' },
      { key: 'jigsawEnabled', label: 'Jigsaw assembly', type: 'select', options: [['true', 'Enabled'], ['false', 'Disabled']] },
      { key: 'jigsawPool', label: 'Jigsaw target pool', type: 'text' },
      { key: 'connectorWidth', label: 'Jigsaw connector width', type: 'text' },
      { key: 'jigsawMaxDepth', label: 'Sequential jigsaw max depth', type: 'text' },
      { key: 'lostCitiesEnabled', label: 'Lost Cities compatibility', type: 'select', options: [['false', 'Disabled'], ['true', 'Enabled']] },
      { key: 'lostCitiesSpawnModes', label: 'Lost Cities spawn modes', type: 'select', options: [
        ['all', 'Tileable + randomized + sequential jigsaw'], ['tileable_grid', 'Tileable grid only'],
        ['randomized_coordinate', 'Randomized coordinate only'], ['sequential_jigsaw', 'Sequential jigsaw only'],
        ['tileable_and_jigsaw', 'Tileable + sequential jigsaw'],
      ]},
      { key: 'tileSpanChunks', label: 'Tile span (chunks)', type: 'text' },
      { key: 'randomRadiusBlocks', label: 'Random spawn radius', type: 'text' },
      { key: 'randomSpacingBlocks', label: 'Random spawn spacing', type: 'text' },
      { key: 'randomSalt', label: 'Random spawn salt', type: 'text' },
      { key: 'purposeDepth', label: 'Depth of purpose', type: 'select', options: [
        ['0', '0 — geometry only'], ['1', '1 — access + clearance'], ['2', '2 — functional zoning (minimum valid)'],
        ['3', '3 — ecosystem integration'], ['4', '4 — narrative + operational depth'],
      ]},
      { key: 'facilityKind', label: 'Facility kind / preset', type: 'text' },
    ],
  },
  {
    id: 'purpose', title: 'StructureForge Purpose Model',
    description: 'What this place is for, who built it, and which zones are mandatory.',
    editableStates: ['idle', 'prompting'], fields: [
      { key: 'purposeKind', label: 'Purpose', type: 'select', options: [
        ['laboratory', 'Research laboratory'], ['industrial', 'Industrial facility'], ['civic', 'Civic / public'],
        ['military', 'Military / defensive'], ['residential', 'Residential'], ['ritual', 'Ritual / cultural'],
        ['commercial', 'Commercial'], ['transport', 'Transport / circulation'],
      ]},
      { key: 'culturalTheme', label: 'Cultural / faction language', type: 'select', options: [
        ['project_defined', 'Project-defined'], ['neutral_vanilla', 'Neutral vanilla'], ['industrial_modern', 'Industrial modern'],
        ['fortified_utilitarian', 'Fortified utilitarian'], ['ruined_high_tech', 'Ruined high-tech'],
      ]},
      { key: 'requiredZones', label: 'Required zones', type: 'text' },
    ],
  },
  {
    id: 'auditor', title: 'StructureForge Auditor', description: 'Fitness-for-purpose, mechanical, contextual, and visual review policy.',
    editableStates: ['idle', 'prompting', 'drafting'], fields: [
      { key: 'auditProfile', label: 'Audit profile', type: 'select', options: [
        ['purpose_and_mechanical', 'Purpose + mechanical'], ['full_context', 'Full context + culture + mechanics'],
        ['visual_first', 'Visual review emphasis'], ['worldgen_preflight', 'Worldgen preflight'],
      ]},
      { key: 'auditThreshold', label: 'Fitness threshold', type: 'select', options: [
        ['0.70', '70% — prototype'], ['0.82', '82% — production candidate'], ['0.90', '90% — strict'], ['0.95', '95% — showcase'],
      ]},
      { key: 'preservationMode', label: 'Preservation contract', type: 'select', options: [
        ['preserve_integration_contracts', 'Preserve integration contracts'], ['preserve_major_identity', 'Preserve major identity'], ['audit_only', 'No mutation — audit only'],
      ]},
    ],
  },
  {
    id: 'repair', title: 'StructureForge Repair', description: 'How far the system may intervene after a failed audit.',
    editableStates: ['idle', 'prompting', 'drafting', 'auditing'], fields: [
      { key: 'repairCeiling', label: 'Rebuild ceiling', type: 'select', options: [
        ['0', '0 — Audit only'], ['1', '1 — Touch-up'], ['2', '2 — Refit'], ['3', '3 — Detail pass'],
        ['4', '4 — Functional rebuild'], ['5', '5 — Heavy rebuild'], ['6', '6 — Full recontextualization'],
      ]},
      { key: 'preserveShell', label: 'Existing shell', type: 'select', options: [['when_viable', 'Preserve when viable'], ['always', 'Preserve'], ['never', 'May replace']] },
      { key: 'circulationPriority', label: 'Circulation priority', type: 'select', options: [['normal', 'Normal'], ['high', 'High'], ['absolute', 'Hard gameplay gate']] },
    ],
  },
  {
    id: 'renderer', title: 'StructureForge Renderer', description: 'Audit image cadence and required visual evidence.',
    editableStates: ['idle', 'prompting', 'drafting', 'auditing'], fields: [
      { key: 'renderAngles', label: 'Audit angles', type: 'select', options: [['single', 'Single preview'], ['four_angle', 'Four-angle review'], ['six_angle', 'Six-angle + plan']] },
      { key: 'damageStates', label: 'Damage states', type: 'select', options: [['intact', 'Intact only'], ['intact_and_ruined', 'Intact + ruined'], ['multi_state', 'Intact + damaged + ruined']] },
      { key: 'renderCadence', label: 'Render cadence', type: 'select', options: [['audit_milestones', 'Audit milestones'], ['every_stage', 'Every pipeline stage'], ['manual', 'Manual capture']] },
    ],
  },
  {
    id: 'validator', title: 'StructureForge Validator', description: 'Shipping gates after geometry and narrative intent converge.',
    editableStates: ['idle', 'prompting', 'drafting', 'auditing', 'rebuilding'], fields: [
      { key: 'validationProfile', label: 'Validation profile', type: 'select', options: [['shipping_gate', 'Shipping gate'], ['mechanical_only', 'Mechanical only'], ['worldgen_runtime', 'Worldgen runtime candidate']] },
      { key: 'worldgenCheck', label: 'Worldgen placement', type: 'select', options: [['required', 'Required'], ['deferred', 'Deferred'], ['not_applicable', 'Not applicable']] },
      { key: 'evidenceLootCheck', label: 'Evidence loot', type: 'select', options: [['required', 'Guaranteed evidence chest required'], ['optional', 'Optional'], ['not_applicable', 'Not applicable']] },
    ],
  },
];

function boolValue(value) {
  return value === true || value === 'true' || value === 'enabled';
}

function spawnModes(value) {
  if (value === 'all') return ['tileable_grid', 'randomized_coordinate', 'sequential_jigsaw'];
  if (value === 'tileable_and_jigsaw') return ['tileable_grid', 'sequential_jigsaw'];
  return [value];
}

export function buildGenerateRequest(controls) {
  const [preferredWidth, preferredDepth] = controls.footprint.split('x').map(Number);
  const isInfrastructure = controls.generatorProvider === 'native_infrastructure_v1';
  const generationKind = isInfrastructure ? 'infrastructure' : controls.generatorProvider === 'project_provider' ? 'project_provider' : 'modular_dungeon';

  let layout = {
    seed: Number(controls.seed) || 0,
    size: { preferred_width: preferredWidth, preferred_depth: preferredDepth },
    modularity: { triple_fold: controls.modularity === 'triple_fold', macro_module: 12, meso_module: 4, micro_module: 1 },
  };

  if (controls.generatorProvider === 'donjon_compatible') {
    layout.classic_donjon_options = {
      dungeon_layout: 'none', room_layout: 'scattered', corridor_layout: 'bent',
      n_cols: Math.max(9, Math.round(preferredWidth / 3)), n_rows: Math.max(9, Math.round(preferredDepth / 3)), remove_deadends: 50,
    };
  }

  if (isInfrastructure) {
    layout = {
      module_type: controls.infrastructureModule,
      variant: controls.infrastructureVariant,
      seed: Number(controls.seed) || 0,
      world_seed: Number(controls.worldSeed) || 0,
      orientation: controls.orientation,
      segment_length: Number(controls.segmentLength),
      facility_kind: controls.facilityKind === 'auto' ? null : controls.facilityKind,
      road: { width: Number(controls.innerCityRoadWidth), terrain_padding: Number(controls.terrainPadding) },
      highway: {
        profile: controls.highwayProfile, lane_count: Number(controls.laneCount), lane_width: Number(controls.laneWidth),
        shoulder_width: Number(controls.shoulderWidth), median_width: Number(controls.medianWidth), elevated: boolValue(controls.highwayElevated),
        support_spacing: Number(controls.supportSpacing), deck_thickness: Number(controls.deckThickness), min_clearance: Number(controls.minClearance),
      },
      jigsaw: { enabled: boolValue(controls.jigsawEnabled), pool: controls.jigsawPool, connector_width: Number(controls.connectorWidth), max_depth: Number(controls.jigsawMaxDepth) },
      lost_cities: { enabled: boolValue(controls.lostCitiesEnabled), spawn_modes: spawnModes(controls.lostCitiesSpawnModes), tile_span_chunks: Number(controls.tileSpanChunks) },
      random_spawn: { radius_blocks: Number(controls.randomRadiusBlocks), spacing_blocks: Number(controls.randomSpacingBlocks), salt: Number(controls.randomSalt) },
      purpose: { depth: Number(controls.purposeDepth) },
    };
  }

  const infrastructurePurpose = controls.infrastructureModule === 'civic_facility' ? 'civic' : controls.infrastructureModule === 'industrial_facility' ? 'industrial' : 'transport';

  return {
    structure_id: `interactive:${isInfrastructure ? controls.infrastructureModule : controls.structureType}_${controls.seed}`,
    structure_type: isInfrastructure ? controls.infrastructureModule : controls.structureType,
    target_version: controls.targetVersion,
    scale: Number(controls.scale),
    grade: Number(controls.repairCeiling),
    purpose: {
      kind: isInfrastructure ? infrastructurePurpose : controls.purposeKind,
      required_zones: controls.requiredZones.split(',').map((zone) => zone.trim()).filter(Boolean),
    },
    theme: { name: controls.culturalTheme, culture: controls.culturalTheme === 'project_defined' ? null : controls.culturalTheme },
    context: { terrain: isInfrastructure ? (controls.infrastructureVariant === 'urban' ? 'urban' : 'rural') : 'unknown' },
    generation: { kind: generationKind, materialize_nbt: !isInfrastructure && controls.targetVersion !== '1.12.2', materialization_mode: 'auto', layout },
    metadata: {
      purpose_depth: Number(controls.purposeDepth),
      ui_policy: {
        audit_profile: controls.auditProfile, audit_threshold: Number(controls.auditThreshold), preservation_mode: controls.preservationMode,
        validation_profile: controls.validationProfile, worldgen_check: controls.worldgenCheck, evidence_loot_check: controls.evidenceLootCheck,
      },
    },
  };
}
