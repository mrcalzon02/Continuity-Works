import { createMachine } from 'xstate';

export const PIPELINE_PHASES = [
  'idle',
  'prompting',
  'drafting',
  'auditing',
  'rebuilding',
  'finalizing',
];

export const PHASE_LABELS = {
  idle: 'Idle',
  prompting: 'Prompting',
  drafting: 'Drafting',
  auditing: 'Auditing',
  rebuilding: 'Rebuilding',
  finalizing: 'Finalizing',
};

export const pipelineMachine = createMachine({
  id: 'structureforge-pipeline',
  initial: 'idle',
  states: {
    idle: {
      on: { BEGIN: 'prompting' },
    },
    prompting: {
      on: {
        START_DRAFT: 'drafting',
        RESET: 'idle',
      },
    },
    drafting: {
      on: {
        ADVANCE: 'auditing',
        RESET: 'idle',
      },
    },
    auditing: {
      on: {
        ADVANCE: 'rebuilding',
        RESET: 'idle',
      },
    },
    rebuilding: {
      on: {
        ADVANCE: 'finalizing',
        RESET: 'idle',
      },
    },
    finalizing: {
      on: {
        COMPLETE: 'idle',
        RESET: 'idle',
      },
    },
  },
});

export function nextPhaseLabel(phase) {
  const next = {
    drafting: 'Begin Audit',
    auditing: 'Apply Rebuild',
    rebuilding: 'Finalize + Validate',
    finalizing: 'Finish Session',
  };
  return next[phase] ?? 'Advance';
}
