# Continuity Works as an Agent Skill

The canonical Agent Skill lives at [`.agents/skills/continuity-works/SKILL.md`](../.agents/skills/continuity-works/SKILL.md) on `main`. Its frontmatter follows the open [Agent Skills specification](https://agentskills.io/specification); its three reference files load on demand. It is a thin AI orchestration layer over the **existing** Continuity Works Python package and HTTP tool catalog, not a forked generator or an automatically hosted API.

## Ways to make the skill visible

**In this repository:** A skills-compatible agent that discovers `.agents/skills/` can load `continuity-works` directly. Client support for discovery differs; the presence of this folder does not by itself install a skill globally.

**In another project:** Copy the *whole skill directory*, not only `SKILL.md`, into the destination project's supported skills location. For a client that discovers `.agents/skills/`:

```sh
git clone --depth 1 https://github.com/mrcalzon02/Continuity-Works.git
mkdir -p target-project/.agents/skills
cp -R Continuity-Works/.agents/skills/continuity-works target-project/.agents/skills/
```

Update the copied directory when the upstream skill changes; refer to the GitHub source as authority. Other clients may require a different installation path or explicit import. A prompt can link directly to the [raw SKILL.md](https://raw.githubusercontent.com/mrcalzon02/Continuity-Works/main/.agents/skills/continuity-works/SKILL.md), but a link alone does not automatically execute anything.

## Executing capability tools

A skill provides instructions. Real structure or content generation still needs an execution surface.

For a local checkout with Python 3.11+:

```sh
python -m pip install -e .
continuity-works tools
CONTINUITY_WORKS_HOST=127.0.0.1 CONTINUITY_WORKS_PORT=8787 python scripts/run_api.py
```

In another terminal after starting the service:

```sh
python scripts/http_smoke.py http://127.0.0.1:8787
```

For a remotely configured endpoint, first perform `GET <base-url>/v1/health` and confirm it reports Continuity Works. Then obtain `/v1/tools/index` and the selected tool schema. The reference Render hostname in deployment documentation is not an assurance that the service exists. GitHub Pages serves only the static frontend; it cannot execute `/v1/*`.

An AI agent with **only GitHub access** can inspect code and design schema-valid plans or source changes but must label generation `not executed`. An agent with a verified HTTP client or authorized local Python execution can invoke the capability.

## Suggested instruction for a consuming agent

> Use the Continuity Works skill at `mrcalzon02/Continuity-Works/.agents/skills/continuity-works` for Minecraft structure and content tasks. Discover the current tool schema, apply staged deterministic mutators, respect the 500-block placement exclusion and additive mod-compatibility contracts, and report only verified artifacts and test results.

## Maintainer validation

1. Confirm `SKILL.md` has matching lowercase `name: continuity-works` and nonempty `description` frontmatter.
2. Run `skills-ref validate .agents/skills/continuity-works` when the optional Agent Skills reference validator is installed.
3. Confirm all three relative reference links resolve from `SKILL.md`; verify content and README pointers on GitHub after committing.
4. In a skills-compatible client, confirm discovery of `continuity-works` and on-demand reference loading. Client-specific discovery is a separate integration gate.
5. With an *actually running* Continuity Works service, validate health, index, selected tool schema, representative invocation, and result gates. Keep external service and Minecraft game test claims separate.

No GitHub Actions workflow is required or added for this skill.
