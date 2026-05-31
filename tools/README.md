# profile-manifest tools

Command-line converters and a validator that move metadata between **CDIF JSON-LD** (nested, `schema:`-prefixed — the form produced and validated by the CDIF manifest profile) and **RO-Crate 1.2** (flat `@graph`, unprefixed schema.org terms).

For the conceptual background — what RO-Crate is, how the property/structure mappings work, what is preserved on round-trip — see [`../docs/RO-Crate-relationship.md`](../docs/RO-Crate-relationship.md). This README is a short operational reference.

| Tool | Direction | Purpose |
|---|---|---|
| `ConvertToROCrate.py` | CDIF → RO-Crate | Expand/flatten/compact a CDIF document into RO-Crate 1.2 form |
| `ROCrateToCDIF.py` | RO-Crate → CDIF | Expand/frame/compact an RO-Crate document into nested CDIF form, with optional JSON Schema validation |
| `ValidateROCrate.py` | RO-Crate validator | Run structural + (optionally) SHACL checks against RO-Crate 1.2 requirements; can convert from CDIF first |

## Install

```bash
pip install -r requirements.txt
```

`pyld` is required for the converters. `jsonschema` is required only if you use `ROCrateToCDIF.py --validate`. `roc-validator` is optional; without it `ValidateROCrate.py` runs only its built-in structural checks (the rocrate-validator SHACL pass is skipped with a SKIP notice).

The converters need network access on first run to fetch the RO-Crate 1.2 context from `https://w3id.org/ro/crate/1.2/context`.

## ConvertToROCrate.py — CDIF → RO-Crate

```bash
# Convert and save
python ConvertToROCrate.py input.jsonld -o output-rocrate.jsonld

# Print to stdout
python ConvertToROCrate.py input.jsonld

# Show pipeline steps
python ConvertToROCrate.py input.jsonld -o output.jsonld -v
```

Pipeline: enrich `@context` with CDIF namespaces → expand → flatten → compact with the RO-Crate 1.2 context → inject the `ro-crate-metadata.json` descriptor and remap the root Dataset `@id` to `"./"` → unwrap `@list`, ensure `license`, ensure root `hasPart` covers all data entities.

## ROCrateToCDIF.py — RO-Crate → CDIF

```bash
# Convert
python ROCrateToCDIF.py input-rocrate.jsonld -o cdif-output.json

# Target the CDIF Discovery profile (default is "complete")
python ROCrateToCDIF.py input-rocrate.jsonld -o cdif-output.json --profile discovery

# Convert and validate against the CDIF JSON Schema
python ROCrateToCDIF.py input-rocrate.jsonld -o cdif-output.json --validate

# Use a custom schema
python ROCrateToCDIF.py input-rocrate.jsonld -o out.json --validate --schema path/to/schema.json
```

Options:
- `-o, --output FILE` — write CDIF output to a file (default: stdout)
- `--profile {discovery,complete}` — sets the `dcterms:conformsTo` URI inside `schema:subjectOf` (default `complete`)
- `--validate` — validate output against the CDIF JSON Schema
- `--schema FILE|URL` — custom schema (default: auto-select `CDIFCompleteSchema.json` / `CDIFDiscoverySchema.json` from a sibling `../../validation/` checkout, falling back to fetching from the `Cross-Domain-Interoperability-Framework/validation` repo on `main`)
- `-v, --verbose` — show progress messages

Pipeline: expand → frame around `schema:Dataset` → compact with the CDIF output context → move `DataDownload` entries from `hasPart` into `schema:distribution`, reconstruct `schema:subjectOf` from the RO-Crate metadata descriptor, lift `includedInDataCatalog` into `subjectOf`, deduplicate, normalize.

## ValidateROCrate.py — RO-Crate validator

```bash
# Convert CDIF to RO-Crate form and validate
python ValidateROCrate.py input.jsonld

# Validate a document already in @graph form
python ValidateROCrate.py input-rocrate.jsonld --no-convert

# Convert, validate, and keep the RO-Crate output
python ValidateROCrate.py input.jsonld -o output-rocrate.jsonld

# Skip the rocrate-validator SHACL pass
python ValidateROCrate.py input.jsonld --no-rocrate-validator

# Include RECOMMENDED-level checks from rocrate-validator
python ValidateROCrate.py input.jsonld --severity RECOMMENDED
```

Options:
- `-o, --output FILE` — write the converted RO-Crate to a file
- `--no-convert` — validate the input as-is (must already be in `@graph` form)
- `--no-rocrate-validator` — skip the SHACL pass
- `--severity {REQUIRED,RECOMMENDED,OPTIONAL}` — minimum severity reported by rocrate-validator (default `REQUIRED`)
- `-v, --verbose` — show detail lines for PASS results too

Built-in checks: `@context` present; `@graph` is an array; `ro-crate-metadata.json` descriptor present with `conformsTo`; root data entity `./` is a `Dataset`; root has `datePublished`; every entity has `@id` and `@type`; graph is flat (no nested entities); no `../` in `@id` values; root has `name`/`description`/`license` (WARN); `@context` references the RO-Crate 1.2 context (WARN).

The rocrate-validator pass requests the `ro-crate-1.2` profile and gracefully falls back to `ro-crate-1.1` if the installed `roc-validator` package doesn't ship the 1.2 profile.

Exit codes:
- `0` — all FAIL-level checks passed (warnings allowed)
- `1` — one or more FAIL-level checks failed, or an error occurred
