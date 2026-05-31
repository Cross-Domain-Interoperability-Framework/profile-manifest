# Relationship of CDIF Metadata Profiles to RO-Crate

## Overview

The [CDIFcomplete](https://github.com/Cross-Domain-Interoperability-Framework/metadataBuildingBlocks/tree/main/_sources/profiles/cdifProfiles/CDIFcomplete) building block profile produces JSON-LD metadata that shares a common vocabulary foundation with [RO-Crate](https://www.researchobject.org/ro-crate/) (Research Object Crate). Both systems build on [schema.org](https://schema.org) types and properties to describe datasets, files, people, and organizations.

This document describes the property-level correspondences, the structural differences, and the tools for converting between the two formats in both directions:

- **`ConvertToROCrate.py`** -- CDIF JSON-LD → RO-Crate 1.2 `@graph` form
- **`ROCrateToCDIF.py`** -- RO-Crate 1.2 `@graph` form → CDIF nested JSON-LD
- **`ValidateROCrate.py`** -- Validates RO-Crate structural conformance

All tools are in the `tools/` directory of this repository.

## What is RO-Crate?

RO-Crate is a community specification for packaging research data with structured metadata. An RO-Crate is a directory (or archive) containing a `ro-crate-metadata.json` file that describes the dataset and its constituent files using JSON-LD with schema.org vocabulary. Key characteristics:

- **Flat `@graph` structure** -- all entities (dataset, files, people, organizations) appear as top-level objects in a flat `@graph` array, cross-referenced by `@id`.
- **Metadata File Descriptor** -- a `CreativeWork` entity with `@id: "ro-crate-metadata.json"` that points to the Root Data Entity via `about`.
- **Root Data Entity** -- a `Dataset` entity (typically `@id: "./"`) describing the crate as a whole.
- **Data Entities** -- `File` (alias for `MediaObject`) and `Dataset` entities representing files and folders.
- **Contextual Entities** -- `Person`, `Organization`, `Place`, etc. entities referenced from the data entities.

See the [RO-Crate 1.2 specification](https://www.researchobject.org/ro-crate/specification/1.2/introduction.html) and [quick reference](https://www.researchobject.org/ro-crate/quick-reference) for details.

## Property Mapping: CDIFcomplete to RO-Crate

CDIFcomplete and RO-Crate both use schema.org as their primary vocabulary, so many properties map directly. The table below shows how metadata from the CDIFcomplete profile corresponds to RO-Crate Root Data Entity properties.

### Root Data Entity (Dataset)

| CDIF Property | RO-Crate Property | Notes |
|---|---|---|
| `@type: ["schema:Dataset", ...]` | `@type: "Dataset"` | RO-Crate requires `Dataset` |
| `schema:name` | `name` | Direct mapping |
| `schema:description` | `description` | Direct mapping |
| `schema:dateModified` | `datePublished` | RO-Crate requires `datePublished` (MUST); CDIF uses `dateModified`. Use `schema:datePublished` if present, fall back to `dateModified` |
| `schema:identifier` | `identifier` | CDIF uses structured `PropertyValue`; RO-Crate recommends DOI URI string |
| `schema:license` | `license` | CDIF array of either strings or {"@id": "..."} references; RO-Crate expects `{"@id": "..."}` reference to a contextual entity |
| `schema:url` | `url` | Direct mapping (landing page). CDIF requires either `url` or `distribution` |
| `schema:keywords` | `keywords` | CDIF allows mixed `DefinedTerm` objects and strings; RO-Crate expects strings or `DefinedTerm` references |
| `schema:creator` | `author` | CDIF uses `schema:creator` with `@list`; RO-Crate uses `author` with entity references |
| `schema:contributor` | `contributor` | CDIF wraps in `schema:Role`; RO-Crate uses flat entity references |
| `schema:funding` | `funder` / `funding` | CDIF uses `MonetaryGrant` with nested `funder`; RO-Crate uses contextual entity references |
| `schema:publisher` / `schema:provider` | `publisher` | Direct mapping via entity reference |
| `schema:spatialCoverage` | `spatialCoverage` | Both use `schema:Place` with `schema:geo` |
| `schema:temporalCoverage` | `temporalCoverage` | Direct mapping (ISO 8601 interval string) |
| `schema:version` | `version` | Direct mapping |
| `schema:distribution` | `hasPart` | **Structural difference** -- see below |
| `schema:subjectOf` | (metadata descriptor) | CDIF catalog record maps to/from the RO-Crate Metadata File Descriptor entity |
| `dcterms:conformsTo` | `conformsTo` | Profile declarations (inside `subjectOf`) move to Root Data Entity `conformsTo` |
| `prov:wasGeneratedBy` | -- | CDIF provenance; preserved as additional PROV-O properties |
| `schema:variableMeasured` | -- | CDIF data description; preserved as `variableMeasured` contextual entities |

### Data Entities (Files)

| CDIF Property | RO-Crate Property | Notes |
|---|---|---|
| `@type` (e.g., `["schema:MediaObject"]`) | `@type: "File"` | RO-Crate uses `File` (alias for `MediaObject`); additional types can be kept |
| `schema:name` | `name` | Filename within the archive |
| `schema:description` | `description` | Direct mapping |
| `schema:encodingFormat` | `encodingFormat` | CDIF stores as array; RO-Crate expects single MIME string |
| `schema:size` | `contentSize` | CDIF uses structured `QuantitativeValue`; RO-Crate expects byte count string |
| `spdx:checksum` | -- | No direct RO-Crate equivalent; preserved as additional property |
| `schema:additionalType` | `additionalType` | Domain-specific component types can be preserved |

### Contextual Entities (People, Organizations)

| CDIF Property | RO-Crate Property | Notes |
|---|---|---|
| `schema:Person` with `schema:name`, `schema:identifier` | `Person` with `name`, ORCID `@id` | RO-Crate prefers ORCID as `@id` rather than nested identifier |
| `schema:Organization` with `schema:name` | `Organization` with `name`, ROR `@id` | RO-Crate prefers ROR identifier as `@id` |
| `schema:Place` | `Place` | Instruments/labs map to contextual entities |

## Key Structural Differences

### 1. Nested vs. Flat Graph

The most significant difference is the document structure:

- **CDIF metadata** uses nested JSON-LD -- persons, organizations, files, and distributions are embedded inline within the dataset object.
- **RO-Crate** requires a **flat `@graph` array** where every entity is a top-level object referenced by `@id`.

Example -- a creator in CDIF metadata:
```json
{
  "schema:creator": {
    "@type": "schema:Person",
    "schema:name": "Analytica, Maria",
    "schema:identifier": "https://orcid.org/0000-0001-2345-6789"
  }
}
```

The same creator in RO-Crate:
```json
{
  "@id": "./",
  "@type": "Dataset",
  "author": [{"@id": "https://orcid.org/0000-0001-2345-6789"}]
}
```
```json
{
  "@id": "https://orcid.org/0000-0001-2345-6789",
  "@type": "Person",
  "name": "Analytica, Maria"
}
```

### 2. Distribution vs. hasPart

CDIF metadata supports two distribution patterns:

- **Multiple independent DataDownloads** -- each with its own `schema:contentUrl` (e.g., individual files accessible by URL)
- **Archive distribution** -- a single `DataDownload` (e.g., ZIP) with `schema:hasPart` containing `schema:MediaObject` components that are not individually accessible

RO-Crate puts files directly as top-level `File` entities in the `@graph`, referenced from the root `Dataset` via `hasPart`:

```json
{
  "@id": "./",
  "@type": "Dataset",
  "hasPart": [
    {"@id": "sample_001.tif"},
    {"@id": "methods.pdf"}
  ]
}
```

The CDIF schema requires either `schema:url` (a landing page) or `schema:distribution` (with `DataDownload`/`contentUrl`). At least one must be present.

### 3. Prefixed vs. Unprefixed Properties

CDIF metadata uses namespace-prefixed property names (e.g., `schema:name`, `schema:description`). RO-Crate uses unprefixed schema.org terms (e.g., `name`, `description`) resolved through its own `@context`.

### 4. Metadata File Descriptor / subjectOf

RO-Crate requires a special `CreativeWork` entity describing the metadata file itself. CDIF has an analogous `schema:subjectOf` object that describes the metadata record as a catalog entry.

The CDIF `schema:subjectOf` structure:
```json
{
  "schema:subjectOf": {
    "@type": ["schema:Dataset"],
    "schema:additionalType": ["dcat:CatalogRecord"],
    "@id": "ro-crate-metadata.json",
    "schema:about": {"@id": "./"},
    "dcterms:conformsTo": [
      {"@id": "https://w3id.org/cdif/profiles/cdifComplete/1.0"}
    ],
    "schema:includedInDataCatalog": {
      "@type": "schema:DataCatalog",
      "schema:name": "...",
      "schema:url": "..."
    }
  }
}
```

The converters map between this structure and the RO-Crate Metadata File Descriptor.

## Tools

### Prerequisites

```bash
pip install PyLD jsonschema
```

The scripts require network access on first run to fetch the RO-Crate 1.2 context from `https://w3id.org/ro/crate/1.2/context`.

### ConvertToROCrate.py -- CDIF to RO-Crate

Transforms CDIF JSON-LD (nested, `schema:`-prefixed) into RO-Crate 1.2 form (flat `@graph`, unprefixed schema.org terms).

```bash
# Convert and save
python tools/ConvertToROCrate.py input.jsonld -o output-rocrate.jsonld

# Verbose output
python tools/ConvertToROCrate.py input.jsonld -o output.jsonld -v
```

#### How the CDIF → RO-Crate Conversion Works

The pipeline has five stages using standard JSON-LD operations:

```
Input (nested CDIF JSON-LD with schema:-prefixed terms)
  |
  v
1. Enrich @context     -- merge CDIF namespace prefixes, normalize
   (_enrich_context)      schema to http:// (RO-Crate uses http://,
                          not https://)
  |
  v
2. Expand              -- resolve all prefixed terms to full IRIs
   (jsonld.expand)        e.g. schema:name -> http://schema.org/name
  |
  v
3. Flatten             -- decompose nested objects into a flat @graph
   (jsonld.flatten)       array with @id cross-references
  |
  v
4. Compact             -- re-compact with the RO-Crate 1.2 context;
   (jsonld.compact)       schema.org terms become unprefixed (name,
                          description); CDIF terms keep prefixes
                          (prov:, spdx:, cdi:, csvw:)
  |
  v
5. Inject & Remap      -- add ro-crate-metadata.json descriptor
   (convert_to_rocrate)   entity; remap root Dataset @id to "./"
  |
  v
Output (RO-Crate 1.2 @graph JSON-LD)
```

Because the conversion uses standard JSON-LD expand/flatten/compact operations, the underlying RDF graph is preserved losslessly. The only additions are the RO-Crate metadata descriptor entity and the `"./"` root `@id` convention.

### ROCrateToCDIF.py -- RO-Crate to CDIF

Converts an RO-Crate 1.2 document (flat `@graph`) into a CDIF-compliant nested JSON-LD document suitable for validation against CDIF schemas.

```bash
# Convert RO-Crate to CDIF
python tools/ROCrateToCDIF.py input-rocrate.jsonld -o cdif-output.json

# Convert targeting CDIF Discovery profile
python tools/ROCrateToCDIF.py input-rocrate.jsonld -o output.json --profile discovery

# Convert and validate against CDIF Complete schema
python tools/ROCrateToCDIF.py input-rocrate.jsonld -o output.json -v --validate

# Use a custom schema for validation
python tools/ROCrateToCDIF.py input-rocrate.jsonld -o output.json --validate --schema path/to/schema.json
```

**Options:**
- `-o, --output FILE` -- Write CDIF output to a file
- `--profile {discovery,complete}` -- CDIF profile for `conformsTo` in `subjectOf` (default: `complete`)
- `--validate` -- Validate output against the CDIF JSON Schema
- `--schema FILE` -- Custom schema path (default: auto-selects based on `--profile`)
- `-v, --verbose` -- Show progress messages

#### How the RO-Crate → CDIF Conversion Works

```
Input (RO-Crate 1.2 @graph JSON-LD)
  |
  v
1. Expand              -- resolve all terms to full IRIs
   (jsonld.expand)
  |
  v
2. Frame               -- nest entities into a tree rooted at
   (jsonld.frame)         schema:Dataset using @embed: @always
  |
  v
3. Compact             -- re-compact with CDIF output context;
   (jsonld.compact)       all terms become schema:-prefixed
  |
  v
4. Post-process        -- apply CDIF-specific mappings:
                          a) Move DataDownload items from hasPart
                             to schema:distribution
                          b) Create schema:subjectOf from the
                             RO-Crate metadata descriptor
                          c) Move includedInDataCatalog into subjectOf
                          d) Deduplicate distributions and hasPart
                          e) Normalize arrays and @type
  |
  v
Output (nested CDIF JSON-LD)
```

#### Key Mappings Performed

| RO-Crate | CDIF | Notes |
|---|---|---|
| `hasPart` with `DataDownload` entities | `schema:distribution` array | DataDownloads moved; non-DataDownload items stay in `hasPart` |
| Archive `DataDownload` with `hasPart` File refs | `schema:distribution` with nested `schema:hasPart` MediaObjects | Archive structure preserved after framing |
| `ro-crate-metadata.json` CreativeWork | `schema:subjectOf` catalog record | Created with `@type: ["schema:Dataset"]`, `additionalType: ["dcat:CatalogRecord"]` |
| -- | `dcterms:conformsTo` in `subjectOf` | Set to profile URI (e.g., `https://w3id.org/cdif/profiles/cdifComplete/1.0`) |
| `includedInDataCatalog` on root Dataset | `schema:includedInDataCatalog` inside `subjectOf` | Moved from top-level into the catalog record |

#### Handling Distribution Patterns

The converter handles both CDIF distribution patterns correctly:

1. **Multiple independent DataDownloads** (e.g., from Dataverse): In the RO-Crate, each file appears in `hasPart` as a separate entity with `@type: DataDownload` and its own `contentUrl`. The converter moves these into `schema:distribution` as separate DataDownload items.

2. **Archive distribution with parts** (e.g., a ZIP/TAR bundle whose component files are not independently accessible): In the RO-Crate, the archive `DataDownload` entity references component `File`/`MediaObject` entities via `hasPart`. After framing, the converter preserves the archive structure -- a single `DataDownload` in `schema:distribution` with nested `schema:hasPart` containing the component `MediaObject` entries.

The converter also deduplicates: when framing causes the same entity to appear in both `schema:distribution` and top-level `schema:hasPart`, duplicates are removed from the top level.

### ValidateROCrate.py -- RO-Crate Structural Validator

Validates an RO-Crate document (optionally converting from CDIF first) against RO-Crate 1.2 structural requirements.

```bash
# Convert CDIF to RO-Crate form and validate
python tools/ValidateROCrate.py input.jsonld

# Validate a document already in @graph form (skip conversion)
python tools/ValidateROCrate.py input-rocrate.jsonld --no-convert

# Convert, validate, and save the RO-Crate output
python tools/ValidateROCrate.py input.jsonld -o output-rocrate.json

# Verbose output
python tools/ValidateROCrate.py input.jsonld -v
```

**Options:**
- `-o, --output FILE` -- Write the converted RO-Crate JSON-LD to a file
- `--no-convert` -- Skip the conversion step; validate the input document as-is
- `-v, --verbose` -- Show detail messages for all checks, not just failures and warnings

**Exit codes:**
- `0` -- all FAIL-level checks passed (warnings are allowed)
- `1` -- one or more FAIL-level checks failed, or an error occurred

#### Validation Checks

| # | Level | Requirement |
|---|-------|-------------|
| 1 | FAIL | Top-level has `@context` |
| 2 | FAIL | Top-level has `@graph` as an array |
| 3 | FAIL | `@graph` contains metadata descriptor (`ro-crate-metadata.json` with `conformsTo`) |
| 4 | FAIL | `@graph` contains root dataset (`@id: "./"`, `@type` includes `Dataset`) |
| 5 | FAIL | Root dataset has `datePublished` (ISO 8601) |
| 6 | FAIL | All entities in `@graph` have `@id` |
| 7 | FAIL | All entities in `@graph` have `@type` |
| 8 | FAIL | No nested entities -- all cross-references use `{"@id": "..."}` |
| 9 | FAIL | No `../` in `@id` paths |
| 10 | WARN | Root dataset has `name` |
| 11 | WARN | Root dataset has `description` |
| 12 | WARN | Root dataset has `license` |
| 13 | WARN | `@context` references the RO-Crate 1.2 context URL |

## RO-Crate Bundles → cdifComplete (Archive Distribution)

RO-Crates that package files without workflow provenance — such as experiment result bundles, data archives, or repository exports — map naturally to the CDIF **cdifArchiveDistribution** building block pattern. In this pattern:

- The RO-Crate root Dataset becomes the CDIF `schema:Dataset` root.
- RO-Crate metadata (authors, dates, license, description) maps to root-level CDIF properties: `schema:creator` (with `@list`), `schema:datePublished`, `schema:license`, etc.
- The crate contents become `schema:hasPart` items inside a `schema:distribution` of type `schema:DataDownload`, where `schema:contentUrl` points to the downloadable archive (e.g., a Zenodo zip URL).
- Each component file is typed as `schema:MediaObject` with `schema:name`, `schema:encodingFormat` (MIME type), and optionally `schema:size` (as `schema:QuantitativeValue`). Component files must NOT be typed as `schema:DataDownload` since they are not independently accessible.

The `ROCrateToCDIF.py` converter handles this transformation. See `examples/MoonGen-experiment-results.cdif.json` for a validated example generated from a [pos MoonGen testbed RO-Crate](https://doi.org/10.5281/zenodo.16606355).

## Workflow Run RO-Crates (WRROC)

[Workflow Run RO-Crate](https://www.researchobject.org/workflow-run-crate/) (WRROC) profiles extend RO-Crate with provenance information about computational workflow executions. These include:

- **Process Run Crate** — single-step executions (`CreateAction`)
- **Workflow Run Crate** — multi-step workflow executions with `CreateAction` per step
- **Provenance Run Crate** — detailed retrospective provenance with CWL records

WRROC-to-CDIF conversion targets the **cdifProv** building block rather than cdifComplete, and is handled by tools in the [prov-context-quality](https://github.com/Cross-Domain-Interoperability-Framework/prov-context-quality) repository:

- **WRROCToCdifProv.py** — converts standard WRROC and ARC Workflow Run RO-Crate profiles to cdifProv `@graph` documents
- **galaxyROCrateToCDIF.py** — converts full Galaxy RO-Crate archives to cdifProv with per-step methodology detail (HowTo/HowToStep approach)
- **galaxyROCrateToCDIFActions.py** — multi-activity variant producing separate `prov:Activity` per workflow step with `prov:wasInformedBy` data-flow links

## Round-Trip Example

A complete round-trip demonstrating both conversions:

```bash
# Start with CDIF metadata (e.g., an archive distribution)
# Step 1: Convert CDIF → RO-Crate
python tools/ConvertToROCrate.py metadata.json -o metadata-rocrate.json -v

# Step 2: Convert RO-Crate → CDIF
python tools/ROCrateToCDIF.py metadata-rocrate.json -o metadata-roundtrip.json -v --validate
```

## What is Preserved, What is Lost

| Category | Preserved in RO-Crate | Notes |
|---|---|---|
| Dataset identity and description | name, description, datePublished, license, identifier, url, version, keywords | Core overlap between schemas |
| People and organizations | author, contributor, publisher with ORCID/ROR identifiers | Flattened from nested to entity references |
| Spatial and temporal coverage | spatialCoverage, temporalCoverage | Direct mapping |
| Funding | funding with funder references | MonetaryGrant as contextual entity |
| File inventory | hasPart with File entities, MIME types, sizes | Restructured from distribution/hasPart to flat graph |
| Profile conformance | conformsTo | Moved from subjectOf to Root Data Entity |
| CDIF catalog record (subjectOf) | Metadata descriptor + conformsTo | Reconstructed on reverse conversion |
| Analysis provenance | prov:wasGeneratedBy, prov:used | Preserved as additional PROV-O properties |
| Instrument/lab details | Contextual entities with prov:/nxs: properties | Preserved as additional linked data entities |
| CDIF variable descriptions | variableMeasured entities with cdi: properties | Preserved with DDI-CDI typing |
| CDIF physical mappings | cdi:hasPhysicalMapping on File entities | Preserved; not core RO-Crate but valid extension |
| CSV-W tabular properties | csvw:delimiter, csvw:header, etc. on File entities | Preserved; CSV-W is recognized in RO-Crate context |

Because both conversions use standard JSON-LD operations (expand/flatten/compact/frame), the underlying RDF graph is preserved losslessly. The only structural additions/removals are the RO-Crate metadata descriptor entity, the `"./"` root `@id` convention, and the CDIF `subjectOf` catalog record wrapper.

## References

- [RO-Crate 1.2 Specification](https://www.researchobject.org/ro-crate/specification/1.2/introduction.html)
- [RO-Crate Quick Reference](https://www.researchobject.org/ro-crate/quick-reference)
- [RO-Crate Root Data Entity](https://www.researchobject.org/ro-crate/specification/1.2/root-data-entity.html)
- [RO-Crate Data Entities](https://www.researchobject.org/ro-crate/specification/1.2/data-entities)
- [RO-Crate Metadata](https://www.researchobject.org/ro-crate/specification/1.2/metadata.html)
- [RO-Crate JSON-LD](https://www.researchobject.org/ro-crate/specification/1.2/appendix/jsonld.html)
- [CDIF Book: Schema.org Implementation](https://cross-domain-interoperability-framework.github.io/cdifbook/metadata/schemaorgimplementation.html)
- [CDIF Validation Repository](https://github.com/Cross-Domain-Interoperability-Framework/validation)
- [pyld JSON-LD Processor](https://github.com/digitalbazaar/pyld)
