# CDIF Manifest Profile — Implementation Guide

> **Draft.** This guide was auto-generated from the StructuredSchema. Edit freely — descriptions, ordering, and the introductory prose should be curated by hand.

# Purpose and scope

The **CDIF Manifest profile module** (`cdifManifest`) — see the source register description for the module's purpose. *(Replace this stub paragraph with a hand-written purpose statement.)*

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
- **Content:** —

### schema:distribution

- **Cardinality:** Optional
- **Content:** —

# Class Definitions

## LanguageTaggedValue {#sec-languagetaggedvalue}

An RDF literal value with a language tag, serialized as a JSON-LD value object. Inlined from skosConcept (the resolver does not preserve cross-file '#/$defs/...' fragment refs).

### @value

- **Cardinality:** Required
- **Content:** string
- **Description:** The text content.

### @language

- **Cardinality:** Optional
- **Content:** string
- **Description:** BCP 47 language tag (e.g. en, fr, de).

## ConceptRef {#sec-conceptref}

Reference (by URI) to a skos:Concept defined elsewhere. Used inside skos:broader / skos:narrower as the @id-reference alternative to an inline Concept.

### @id

- **Cardinality:** Required
- **Content:** string
- **Description:** URI of the referenced concept.
