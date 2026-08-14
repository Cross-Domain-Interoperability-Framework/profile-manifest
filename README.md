# CDIF Manifest (profile module)

This repository holds the published artifacts for the **CDIF Manifest profile module** — the `cdifManifest` building block from the [metadataBuildingBlocks](https://github.com/Cross-Domain-Interoperability-Framework/metadataBuildingBlocks) source register.

> **Scope.** `cdifManifest` documents how a dataset's content is packaged for distribution — file lists, integrity checksums (`spdx:Checksum`), archive structure, and download endpoints. It complements `cdifCore` and `cdifDiscovery` by carrying the bytes-on-disk story rather than the conceptual/structural one.

## Specification

- **[CDIFManifestImplementationGuide.md](CDIFManifestImplementationGuide.md)** — Implementation guide (auto-generated draft; hand-curated content pending).
- **[cdifManifestStructuredSchema.json](cdifManifestStructuredSchema.json)** — Resolved JSON Schema (Draft 2020-12) generated from the source register.
- **[manifestRules.shacl](manifestRules.shacl)** — Self-contained SHACL shapes, merged from every composing building block plus the profile-level shapes.
- **[cdifManifest-frame.jsonld](cdifManifest-frame.jsonld)** — JSON-LD frame used by `FrameAndValidate.py`.

## Examples

`examples/` holds JSON-LD examples illustrating archive-distribution manifests, RO-Crate-aligned packagings, and per-distribution checksums. Validate one with:

```bash
python FrameAndValidate.py examples/exampleCdifManifest.json --validate
```

`FrameAndValidate.py` frames the document against `cdifManifest-frame.jsonld`, array-wraps the multi-valued properties, then validates against the JSON Schema. Validation is open-world: unknown properties pass.

### One example reports on a different node, by design

Framing selects the node matching the frame's root `@type`, which here is `schema:Dataset`. **`examples/reliquaryTest202607.json` has a root typed `schema:Collection`**, so framing does not match it and the framed output describes a different node — `…/URIforTheMetadata` rather than the source's `…/morbcitationlist`.

That is expected. The example exists to exercise a non-Dataset root, and **the frame should not be widened to accommodate it** — a frame's job is to match the shape this profile actually publishes.

Worth knowing because a useful sanity check — frame every example and compare the framed `@id` against the source `@id` — flags this one. It is the only expected mismatch here. Anything else appearing in that check is a real problem: the validator would be reporting on something other than the document it was given, **and reporting PASS while doing so**. That selection lives in `pick_main_entity`, which is generated from the normative source in the [validation](https://github.com/Cross-Domain-Interoperability-Framework/validation) repo — fix it there, never in this copy, which carries a DO-NOT-EDIT banner and a drift hash that CI checks.

## RO-Crate interop

A separate set of converter scripts and the prior packaging exploration live under `tools/` and `docs/`. Those are working materials and not part of the release-artifact set.

## Synced from metadataBuildingBlocks

These generated artifacts are re-synced when the source register changes:

| file | source command |
|---|---|
| `cdifManifestStructuredSchema.json` | `python tools/resolve_schema.py cdifManifest -o cdifManifestStructuredSchema.json` |
| `manifestRules.shacl` | `python tools/validate_shacl.py cdifManifest --emit-shapes manifestRules.shacl` |

Source profile: `_sources/profiles/cdifProfile/cdifManifest/`.

## Changelog — reviewRevision202606 (updates since branched from `main`)

This release-review branch has diverged from `main` with the following updates,
synced from the CDIF **metadataBuildingBlocks** source (see
`git log main..reviewRevision202606` for the full per-commit history):

- **Populated from metadataBuildingBlocks** — `*StructuredSchema.json`, merged SHACL,
  JSON-LD frame, examples, and the normative `FrameAndValidate.py` generated from the
  building-block source; `Examples/` renamed to `examples/`.
- **CDIF v1.1** — profile conformance URIs migrated `/1.0` → `/1.1`.
- **License** standardized on CC-BY-4.0.
- **`@id`-reference tightening** — bare `{@id}` reference slots sealed
  (`additionalProperties: false` + `required: ['@id']`); a canonical `objectReference`
  building block introduced as the strict node reference.
- **`prov:used` wrapper reconciliation** — the base `generatedBy.prov:used` accepts
  role-keyed wrappers (`schema:instrument` / `bios:computationalTool` / `prov:reagent`)
  alongside string / `{@id}` / inline `prov:Entity`; profiles pin a wrapper's shape via
  a constraint-only `if/then` (never a narrowed `anyOf`).
- **`skos:notation` → single string** at concept level (consistent with the codelist
  single-notation design).
- **`FrameAndValidate.py`** (normative, drift-checked against
  `Cross-Domain-Interoperability-Framework/validation`) — two-frame root-`@type`
  selection, context-aware `schema:about`, `--conformance` detection, `cdif:`-`@id`
  re-expansion, and (2026-08) reference-collapse on all document types + blank-node
  dedupe + agent `schema:identifier` unwrap, so `@embed:@always`-framed documents
  validate against the tightened schemas.
- **Examples** conformed to the tightened schemas throughout (PrimaryKey →
  `cdi:ComponentPosition`, reference slots → `{@id}`, CVE `hasIntendedDataType` →
  string, `skos:notation` → string, `schema:additionalType` URI → `{@id}`).


## Development branch

Active work for the 2026-06 review revision is on the `reviewRevision202606` branch. `main` reflects the prior release state. New changes should target the review branch; it is merged to main on release.

## License

This work is licensed under [Creative Commons Attribution 4.0 International (CC BY 4.0)](LICENSE).
