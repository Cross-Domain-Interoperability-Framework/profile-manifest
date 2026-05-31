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


# Dataset Properties added by the CDIF Manifest Profile

## schema:Dataset {#sec-schema-dataset}

Profile module for archive distributions. Marks the catalog record as conformant to the CDIF manifest spec (https://w3id.org/cdif/manifest/1.0) and lets schema:distribution items carry schema:hasPart describing the component files inside an archive (ZIP, etc.). The base schema:distribution anyOf [DataDownload, WebAPI] contributed by cdifCore is preserved — this BB only adds property constraints, no new anyOf branch. (Merged from the previous cdifProfile/cdifArchive BB, which held only the $defs for ArchivePart; everything now lives here.)

### schema:subjectOf
- (required) conformance statement in the subjectOf/dcat:catalogRecord must include "dcterms:conformsTo" includes    "https://w3id.org/cdif/manifest/1.0"

### schema:distribution
If the DataDownload type is application/zip (might need more general way to identify bundled packages of files), then the DataDownload must have hasPart properties that are schema:MediaObject instances describing the contained files. 
- **Cardinality:** Optional

# Class Definitions

## MediaObject

### /@type
-  (Required) May include additional types for categorization.  type: array of string, must contain "schema:MediaObject", may not contain "schema:DataDownload" since the media objects in the package are not independently downloadable.
### schema:name":
- (Required) locator for the mediaObject within the package. If Some package components are remote (external to the package) this must be a resolvable locator (e.g. http URI). Type: string
### schema:description
- Description of the file content. Type: string
### schema:encodingFormat
- Type(s) of the media object. type: array of string. MIME type is expected, other classifiers  may be included
### schema:size
- File size as a schema:QuantitativeValue value, with a numeric value and unit of measure: type: schema:QuantitativeValue.
### schema:about
- For metadata sidecar files, references the data file this metadata describes. type: array of object reference to the @id of the data file described by this sidecar.
### spdx:checksum
- checksum object contains string value calculated algorithmically from the mediaObject content to allow determination if the object has been corrupted. type: spdx:Checksum object.


## schema:QuantitativeValue"
- object that specifies a numeric value and units of measure
### schema:value":
- (required) numeric value. type: number
### schema:unitText":
- Unit of measure for size (e.g. 'byte'). type: string

				
## spdx:Checksum

### spdx:algorithm
- (Required) Name or identifier for the algorithm used to calculate the checksum. type: string
### spdx:checksumValue
- (required) the checksum string. type: string

# Provenance of the artifacts

The schema and SHACL files are generated from the canonical source register, [metadataBuildingBlocks](https://github.com/Cross-Domain-Interoperability-Framework/metadataBuildingBlocks):

- `cdifManifestStructuredSchema.json` ← `tools/resolve_schema.py cdifManifest`
- `manifestRules.shacl` ← `tools/validate_shacl.py cdifManifest --emit-shapes`

Source profile directory: `_sources/profiles/cdifProfile/cdifManifest/`.