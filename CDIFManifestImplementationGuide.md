# CDIF Manifest Profile — Implementation Guide


The **CDIF Manifest profile** (`cdifManifest`) — a simple profile to describe distributions that contain multiple files bundled in a single data download media object for distribution.

# Conformance

A resource conforms to the CDIF Manifest profile when its catalog record declares conformance to the profile identifier. The catalog record is carried on `schema:subjectOf` as a `dcat:CatalogRecord`:

```json
"schema:subjectOf": {
  "@type": ["schema:CreativeWork", "dcat:CatalogRecord"],
  "dcterms:conformsTo": [
    "https://w3id.org/cdif/manifest/1.0"
  ]
}
```

Other properties added in this profile are optional; conformance requires only that the constraints in the JSON Schema and SHACL rules are satisfied.

## Validation

Two validators ship with this repository:
- **JSON Schema** — `cdifManifestStructuredSchema.json` (Draft 2020-12), generated from the source register.
- **SHACL** — `manifestRules.shacl`, a self-contained shapes graph merged from every composing building block plus the profile-level shapes.

```bash
python FrameAndValidate.py examples/<file>.json --validate \
  --schema cdifManifestStructuredSchema.json --frame <frame.jsonld>
```

Validation is **open-world**: properties not described by the profile are allowed.

# Provenance of the artifacts

The schema and SHACL files are generated from the canonical source register, [metadataBuildingBlocks](https://github.com/Cross-Domain-Interoperability-Framework/metadataBuildingBlocks):

- `cdifManifestStructuredSchema.json` ← `tools/resolve_schema.py cdifManifest`
- `manifestRules.shacl` ← `tools/validate_shacl.py cdifManifest --emit-shapes`

Source profile directory: `_sources/profiles/cdifProfile/cdifManifest/`.

# Dataset Properties added by the CDIF Manifest Profile

## schema:Dataset {#sec-schema-dataset}

Profile module for archive distributions. Marks the catalog record as conformant to the CDIF manifest spec (https://w3id.org/cdif/manifest/1.0) and lets schema:distribution items carry schema:hasPart describing the component files inside an archive (ZIP, etc.). The base schema:distribution anyOf [DataDownload, WebAPI] contributed by cdifCore is preserved — this BB only adds property constraints, no new anyOf branch. (Merged from the previous cdifProfile/cdifArchive BB, which held only the $defs for ArchivePart; everything now lives here.)

### schema:subjectOf

- **Cardinality:** Optional
- **Content:** — "dcterms:conformsTo" includes    "https://w3id.org/cdif/manifest/1.0"

### schema:distribution

- **Cardinality:** Optional
- **Content:** —

# Class Definitions

TBD
