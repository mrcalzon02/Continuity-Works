---
name: continuity-works
description: Use Continuity Works to discover, plan, generate, audit, refit, validate, or package Minecraft Java structures, procedural dungeons, roads, infrastructure, books, loot tables, recipes, advancements, tags, and biome-aware world-generation assets. Apply version- and mod-aware checks, deterministic seeds, additive compatibility, and spatial exclusion contracts. Use for Minecraft structure/content work that needs verified artifacts rather than invented IDs or untested placement claims.
compatibility: Read access to the Continuity Works repository is sufficient for planning. Execution requires Python 3.11+ with the repository installed, or a verified running Continuity Works HTTP API.
metadata:
  author: mrcalzon02
  repository: https://github.com/mrcalzon02/Continuity-Works
---

# Continuity Works

Use the existing Continuity Works implementation as the source of truth. This skill is an orchestration and discovery layer, **not** an alternative generator or a license to fabricate results.

Authoritative code: https://github.com/mrcalzon02/Continuity-Works (branch `main`).
See [tool selection](references/tools.md), [generation and mutators](references/generation.md), and [validation and evidence](references/validation.md) only when relevant to the active task.

## Activate for

Minecraft Java structure generation or refitting, dungeon layouts, roads or civic/industrial infrastructure, world-seed-based placements, structure families and jigsaws, version/mod-aware Minecraft content authoring, and auditing or validating those outputs.

Do not activate for unrelated generic writing or coding, and do not claim any new runtime capability merely because the skill exists.

## Pick an execution surface

1. **Existing running API:** Use a base URL supplied by the user or discovered from repository metadata. Before *any* write/generate operation, request `GET /v1/health` and verify the response identifies `Continuity Works`. If unavailable or incorrect, fail closed: do not call that host as an API. Never send `/v1/*` to the static GitHub Pages site. The Render hostname in repository documentation is a **candidate**, not proof of deployment.
2. **Local Python environment:** If the repository is checked out and execution is authorized, use `python -m pip install -e .`, `continuity-works tools`, or `from structure_capability import StructureCapability`. The internal module name is an implementation detail retained for compatibility.
3. **Repository/document access only:** Read current contracts and prepare request plans, manifests, or code changes. Clearly label them **not executed**. A GitHub URL alone is not a live tool invocation or a loaded skill in another client.

Do not silently substitute manual JSON guesses for an executable implementation.

## Minimize token and tool overhead

When the API is healthy, start with `GET /v1/tools/index` or `GET /v1/capabilities`; fetch `GET /v1/tools/{tool_name}`, `GET /v1/presets/{preset_id}`, or `GET /openapi.json` only when needed. The authoritative tool catalog is `GET /v1/tools`. Read an operation's published input schema and canonical route before invocation. Do not invent paths, request keys, version IDs, mod registries, or tool availability.

For a constrained model (even ~64 output tokens per decision), use a **short, staged decision record**: state identifier, chosen tool/preset, one validated mutator or action, gate/result, and next state. Keep durable structured state outside the model's tiny output window; use successive narrow calls rather than demanding a large all-at-once design. These records are action summaries, not private reasoning transcripts.

## Execution sequence

1. Identify target Minecraft version, loader, installed mods/registries, world seed, purpose, site/biome context, size envelope, and required output artifact. Resolve missing facts from the project before guessing.
2. Inventory the project and probe non-vanilla IDs. Select the narrowest published tool or preset for the task.
3. Build a purpose-first plan: required functions, entrances, access, circulation, verticality, culture/material rules, family links, and infrastructure dependencies.
4. Apply deterministic, reversible, schema-supported mutators in macro → meso → micro passes. Check fitness after each pass; preserve completed approved decisions.
5. Generate via the existing capability; inspect *actual returned* layout, NBT/pieces, content JSON, gates, IDs, and snapshots. A proposed artifact is not an emitted artifact.
6. Enforce the project's default **500-block structure exclusion/overlap contract** when placing or reserving independent structures. Only explicit, validated same-family/jigsaw relationships permit exceptions. If the selected runtime cannot enforce this contract, mark placement blocked or requiring an adapter/runtime test; never imply that this skill enforces worldgen itself.
7. Run applicable validation, compatibility, and real game placement checks before calling a result production-ready. See [validation](references/validation.md).
8. Report which API/Python tool actually ran, inputs/seed/version, generated artifacts and paths, validation outcomes, remaining runtime gates, and verifiable commit or deployment evidence when applicable.

## Hard invariants

- Compatibility overlays are **append-only, additive, and non-destructive**. Do not replace another mod's registries, roads, rails, or generation logic.
- Preserve seed reproducibility, version format boundaries, mod ID evidence, footprint/clearance, and explicitly reserved structure exclusion zones.
- Do not confuse generated design data with a successfully registered/spawned structure in Minecraft.
- Do not confuse a generated file with a pushed repository change, or a passing local test with an externally deployed service.
- No fake stubs, fake screenshots, invented success, implicit force pushes, or changes outside authorized project scope.
- Optional client-side previews do not replace mechanical validation, and server-side rendering is not required.

For actual CLI/API usage and external installation, see the repository's [Agent Skill guide](https://github.com/mrcalzon02/Continuity-Works/blob/main/docs/AGENT_SKILL.md).
