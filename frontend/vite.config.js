import { fileURLToPath, URL } from 'node:url';
import { defineConfig } from 'vite';

const repoRoot = fileURLToPath(new URL('..', import.meta.url));
const outDir = fileURLToPath(new URL('../dist', import.meta.url));

export default defineConfig({
  root: repoRoot,
  base: '/Continuity-Works/',
  build: {
    outDir,
    emptyOutDir: true,
  },
});
