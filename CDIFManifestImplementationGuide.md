# CDIF Manifest Profile — Implementation Guide


The **CDIF Manifest profile** (`cdifManifest`) — a simple profile to describe distributions that contain multiple files bundled in a single data download media object for distribution.

# Conformance

A resource conforms to the CDIF Manifest profile when its catalog record declares conformance to the profile identifier. The catalog record is carried on `schema:subjectOf` as a `dcat:CatalogRecord`:

```json
"schema:subjectOf": {
  "@type": ["schema:CreativeWork", "dcat:CatalogRecord"],
  "dcterms:conformsTo": [
    "https://w3id.org/cdif/manifest/1.1"
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

Profile module for packages: the resources that make up a dataset and where to retrieve each of them. Marks the catalog record as conformant to the CDIF manifest spec (https://w3id.org/cdif/manifest/1.1) and declares `schema:hasPart` in the two places a package needs it — on the `schema:Dataset`, for parts that are independently accessible at their own addresses, and on a `schema:distribution` item, for component files inside an archive (ZIP, etc.) that have no address of their own. The base schema:distribution anyOf [DataDownload, WebAPI] contributed by cdifCore is preserved — this BB only adds property constraints, no new anyOf branch. (Merged from the previous cdifProfile/cdifArchive BB, which held only the $defs for ArchivePart; everything now lives here.)

### schema:subjectOf
- (required) conformance statement in the subjectOf/dcat:catalogRecord must include "dcterms:conformsTo" includes    "https://w3id.org/cdif/manifest/1.1"

### Which `schema:hasPart` is this?

`schema:hasPart` carries four different meanings in CDIF, with a different item shape in each. **What disambiguates them is the object the property sits on** — nothing in the property itself — so a consumer walking a graph has to track where it is.

| on this object | the parts are | shape |
|---|---|---|
| `schema:Dataset` | package members, independently accessible, each at its own address | `resourcePartItem` (this profile) |
| a `schema:distribution` item | component files inside an archive, with no address of their own | `archivePartItem` (this profile) |
| `schema:instrument` | sub-components of an instrument system | `InstrumentComponent` (instrument BB) |
| a bioschemas `ComputationalWorkflow` | sub-workflows and component tools | inline (bioschemas BB) |

The first two are the pair most easily confused. **The test is whether a part can be retrieved on its own.** If it can, it belongs on the Dataset and may be typed `schema:DataDownload`. If it can only be reached by unpacking something else, it belongs on the distribution and **must not** be typed `schema:DataDownload`, because there is nothing to download it from.

### schema:hasPart

The resources that make up the package, where each is **independently retrievable at its own address**. This is the networked case the profile exists for: a package is "not so much a physical assembly as a list of needed resources and the addresses which can be used to retrieve them".

- **Cardinality:** Optional
- **Content:** array of `resourcePartItem`

Type each part for what it is — `schema:Dataset` for data, `schema:CreativeWork` for a codebook, methods document or quality report, `schema:MediaObject` for a browse image. A part may carry its own `schema:distribution`, and may be typed `schema:DataDownload`; an archive part may not.

Where parts are under separate stewardship, put `schema:provider`, `schema:conditionsOfAccess` and `schema:dateModified` **on each part**, since those are exactly what differ and what a consumer needs before planning access.

Use `schema:about` on a part that describes another — a codebook, a data dictionary, a quality report, a metadata sidecar — so a consumer can tell *which* part it documents, rather than only that both are in the package. This is the same relationship OAI-ORE packages express with `cito:documents`; `schema:subjectOf` is its declared inverse.

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