import React, { useMemo } from 'react';
import { Canvas } from '@react-three/fiber';
import { OrbitControls, PerspectiveCamera } from '@react-three/drei';
import { html } from '../lib/html.js';

const BLOCK_COLORS = {
  'minecraft:polished_andesite': '#87909a',
  'minecraft:oak_log': '#8a6848',
  'minecraft:stone_bricks': '#68727b',
  'minecraft:deepslate_tiles': '#39424c',
  'minecraft:iron_block': '#c6d0d7',
  'minecraft:glass': '#7dc7d7',
  'minecraft:barrel': '#9d6b38',
  'minecraft:chest': '#b77b2d',
  'minecraft:iron_door': '#aab6c1',
  'minecraft:redstone_lamp': '#d69b4f',
  'minecraft:stone_slab': '#7c858e',
};

function Voxel({ block }) {
  const color = BLOCK_COLORS[block.id] || '#7b8794';
  return html`
    <mesh position=${[block.x, block.y, block.z]} castShadow receiveShadow>
      <boxGeometry args=${[0.94, 0.94, 0.94]} />
      <meshStandardMaterial color=${color} roughness=${0.76} metalness=${0.04} />
    </mesh>
  `;
}

function Scene({ blocks }) {
  const center = useMemo(() => {
    if (!blocks.length) return [0, 1, 0];
    const total = blocks.reduce(
      (acc, block) => [acc[0] + block.x, acc[1] + block.y, acc[2] + block.z],
      [0, 0, 0],
    );
    return total.map((value) => value / blocks.length);
  }, [blocks]);

  // HTM is JSX-like but does not use JSX's <>...</> fragment shorthand.
  // Use an explicit React.Fragment so a scene render cannot invalidate the app root.
  return html`
    <${React.Fragment}>
      <color attach="background" args=${['#081019']} />
      <ambientLight intensity=${1.6} />
      <directionalLight position=${[8, 14, 10]} intensity=${2.2} castShadow />
      <directionalLight position=${[-8, 6, -6]} intensity=${0.8} />
      <${PerspectiveCamera} makeDefault position=${[14, 11, 14]} fov=${48} />
      <${OrbitControls}
        makeDefault
        target=${center}
        enableDamping=${true}
        dampingFactor=${0.08}
        minDistance=${5}
        maxDistance=${45}
      />
      <gridHelper args=${[36, 36, '#2b3b4b', '#16212d']} position=${[0, -0.52, 0]} />
      ${blocks.map(
        (block) => html`<${Voxel} key=${block.key} block=${block} />`,
      )}
    <//>
  `;
}

function webglAvailable() {
  if (typeof document === 'undefined') return false;
  try {
    const canvas = document.createElement('canvas');
    return Boolean(
      canvas.getContext('webgl2', { failIfMajorPerformanceCaveat: false })
      || canvas.getContext('webgl', { failIfMajorPerformanceCaveat: false }),
    );
  } catch (_error) {
    return false;
  }
}

class ViewportErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { error: null };
  }

  static getDerivedStateFromError(error) {
    return { error };
  }

  componentDidCatch(error, info) {
    console.error('StructureForge viewport failed safely:', error, info);
  }

  render() {
    if (!this.state.error) return this.props.children;
    return React.createElement(
      'div',
      { className: 'viewport-empty viewport-error', role: 'alert' },
      React.createElement('strong', null, '3D viewport unavailable'),
      React.createElement(
        'span',
        null,
        'The StructureForge controls remain usable. Reload after enabling WebGL or inspect the browser console for the renderer error.',
      ),
    );
  }
}

export function Viewport({ blocks, phase }) {
  const canRenderWebGL = useMemo(webglAvailable, []);

  return html`
    <section className="panel viewport-panel" aria-label="3D procedural assembly viewport">
      <div className="panel-heading compact-heading">
        <div>
          <span className="eyebrow">Live voxel assembly</span>
          <h2>3D Structure Viewport</h2>
        </div>
        <div className="viewport-meta">
          <span>${blocks.length} blocks</span>
          <span>${phase}</span>
        </div>
      </div>
      <div className="viewport-canvas">
        ${canRenderWebGL
          ? html`
            <${ViewportErrorBoundary}>
              <${Canvas} shadows dpr=${[1, 1.5]} gl=${{ antialias: true }}>
                <${Scene} blocks=${blocks} />
              <//>
            <//>
          `
          : html`
            <div className="viewport-empty viewport-error" role="alert">
              <strong>WebGL unavailable</strong>
              <span>The rest of StructureForge remains available without the 3D preview.</span>
            </div>
          `}
        ${canRenderWebGL && !blocks.length && html`
          <div className="viewport-empty">
            <strong>No geometry yet</strong>
            <span>Begin a session, lock constraints, then draft.</span>
          </div>
        `}
      </div>
      <div className="viewport-footer">
        Drag to orbit · wheel to zoom · geometry appears one serialized event at a time
      </div>
    </section>
  `;
}
