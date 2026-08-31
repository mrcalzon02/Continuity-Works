# Aerospace Support Campus API

The deterministic aerospace support-campus generator is exposed through the existing Continuity Works capability boundary. It does not create a parallel server or alternate tool registry.

## Deliberate tool

Tool name:

`aerospace_support_campus_generate`

Tool-catalog schema version:

`1.4`

The contract is discoverable through the normal progressive-disclosure surfaces:

- `GET /v1/tools/index`
- `GET /v1/tools/aerospace_support_campus_generate`
- `POST /v1/resolve`
- `GET /v1/presets`

Built-in preset:

`layout.aerospace_support_campus`

The preset defaults to `standard` scale and deliberately leaves `seed` unresolved, so a client can select the capability first and request only the remaining required variable.

## Canonical HTTP route

`POST /v1/aerospace/support-campus`

The route is declared in the authoritative `PUBLIC_CAPABILITIES` publication matrix. `server.py` derives the executable route and its OpenAPI operation from that matrix and the tool catalog.

Request:

```json
{
  "scale": "heavy",
  "seed": "heavy-launch-campus-01"
}
```

Optional operator constraint:

```json
{
  "scale": "superheavy",
  "seed": 20260830,
  "corporate_language_id": "continuityworks:corporate/helium_orbital_works"
}
```

Supported scales:

- `micro`
- `light`
- `standard`
- `heavy`
- `superheavy`
- `megastructure`

`seed` may be a non-empty string or integer.

If `corporate_language_id` is omitted, the generator deterministically selects from the intersection of operator languages allowed by every facility in that scale template. An explicit operator outside that intersection is rejected.

## Response

The response is the direct result of the authoritative `SeededAerospaceSupportCampusGenerator` and contains:

- `graph` — the complete typed site graph;
- `report` — deterministic and validation metadata.

The report includes:

- `SEEDED_AEROSPACE_SUPPORT_CAMPUS` gate status;
- normalized seed and SHA-256 seed digest;
- scale and resolved operator;
- selected facility archetypes;
- seeded site context;
- node and edge counts;
- launch-anchor count;
- canonical SHA-256 campus fingerprint;
- network findings.

A successful result is not merely a generated list of buildings. The graph must first pass the aerospace support network validator, including launch-anchor reachability and scale-appropriate logistics/transport gates.

## StructureCapability method

Python clients can invoke the same implementation through:

```python
capability.aerospace_support_campus_generate({
    "scale": "heavy",
    "seed": "heavy-launch-campus-01",
})
```

`StructureCapability` lazily creates the seeded campus generator so ordinary capability initialization does not duplicate the Facility Library or network validator.

## Publication behavior

The tool is present in all of the existing machine-facing discovery mechanisms:

- JSON tool catalog;
- compact tool index;
- exact-tool contract;
- resolver/preset system;
- OpenAPI generation;
- discovery capability list;
- public serviceability matrix;
- canonical HTTP routing.

The publication matrix classifies the tool as API-first with `manual_ui = not_applicable`. This means its absence from a dedicated handwritten frontend widget does not make the server route unpublished. A future workbench control may consume the same live catalog without changing this tool contract.

## Validation boundary

Local/publication tests verify that the tool name, Python method, route, schema, OpenAPI operation, resolver preset, and publication matrix remain aligned.

External reachability is a separate deployment concern. Local serviceability must never be treated as proof that the public Render deployment has already updated to the newest repository commit.

No GitHub Actions are required by or introduced for this capability.
