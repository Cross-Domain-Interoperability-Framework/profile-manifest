# AGENTS.md — AI Agent Guidance for CDIF Manifest (profile module)

## Project context

This repository publishes the **CDIF Manifest profile module** (`cdifManifest`). It carries the bytes-on-disk story for a dataset's distribution — file lists, integrity checksums (`spdx:Checksum`), archive structure, and download endpoints. Complements `cdifCore` / `cdifDiscovery`, which carry the conceptual story.

## Key files

- `CDIFManifestImplementationGuide.md` — implementation guide (auto-generated draft from the StructuredSchema; hand-curated content pending)
- `cdifManifestStructuredSchema.json` — JSON Schema (generated)
- `manifestRules.shacl` — merged SHACL shapes (generated)
- `cdifManifest-frame.jsonld` — JSON-LD frame used by `FrameAndValidate.py`
- `examples/` — validated JSON-LD examples
- `FrameAndValidate.py` — frame + JSON Schema validation

## Synced files (manual sync from metadataBuildingBlocks)

These are generated from the source register and must be re-synced when the source changes:

- `cdifManifestStructuredSchema.json` ← `python tools/resolve_schema.py cdifManifest -o <file>`
- `manifestRules.shacl` ← `python tools/validate_shacl.py cdifManifest --emit-shapes <file>`

Source profile dir: `metadataBuildingBlocks/_sources/profiles/cdifProfile/cdifManifest/`.

## Working materials (non-release)

`tools/` and `docs/` carry the prior packaging / RO-Crate exploration. These are kept for traceability but are not part of the release artifact set. The canonical release files are `cdifManifestStructuredSchema.json`, `manifestRules.shacl`, `cdifManifest-frame.jsonld`, `FrameAndValidate.py`, and `examples/`.

## Example conventions

1. `@context` declares explicit prefixes (`schema`, `dcterms`, `dcat`, `spdx`) — never `@vocab`.
2. `schema:distribution` carries `schema:DataDownload` (or `schema:WebAPI`) objects with `schema:contentUrl` and optional `spdx:checksum`.
3. `spdx:checksum` is a `spdx:Checksum` with `spdx:algorithm` (e.g. `"SHA-256"`) and `spdx:checksumValue` (hex string).
4. `@type` as arrays.
5. Never strip unknown properties — validation is open-world.

## Validation

```bash
python FrameAndValidate.py examples/<file>.json --validate \
  --schema cdifManifestStructuredSchema.json --frame cdifManifest-frame.jsonld
```

## Development branch

Active development for the 2026-06 review revision targets the `reviewRevision202606` branch; merged to `main` on release.
