# CDIF Manifest Profile

**Draft, August 2026.** Merged from `CDIF Manifest Profile-V1-smr.docx`
(overview, requirements, conceptual model, RO-Crate implementation) and
`KindsOfAggregateResources.md` (the taxonomy of aggregate resources,
here §3). Worked JSON-LD scaffolding for every pattern in §3 is in
[`demoExamples/`](demoExamples/).

---

## 1. Overview

Within the set of FAIR functions supported by the CDIF guidelines is a
practical need to construct packages of interdependent resources. FAIR
does not directly address this need, but experience has shown that the
interlinked nature of data and metadata resources demands that meaningful
packages can be assembled for different purposes.

This requirement appears in different forms. Researchers must be able to
collect and group the various resources involved in their research, so
that sense can be made of it for the purposes of replication,
comprehension, and reuse. Archives and repositories have a requirement
for packages of related resources to be submitted and stored, and these
form the basis for dissemination. There is the popular concept of a FAIR
Digital Object (FDO) which can be anything FAIR — even an atomic metadata
item — but in practical terms requires that coherent packages be
assembled to support practical use.

In a networked scenario, it may not always be the case that every
required resource is stored at the same location or is found within the
same repository (even a distributed one). In such a case, the idea of a
"package" is not so much a physical assembly as it is a list of needed
resources and the addresses — local or otherwise — which can be used to
retrieve them. Different scenarios of use will impose different
restrictions on how such packages need to be stored, but in their most
basic form, they are a list of resources and locations: a manifest.

What CDIF offers as a core profile to support packaging is exactly this:
the core items which make up a manifest. This model can be implemented in
different ways — it could be an RO-Crate, a Frictionless Data Package,
etc. At the core of all such specifications is a very simple construct
which is presented here, along with an implementation in RO-Crate.

This document outlines the basic requirement, the kinds of aggregate
resource the model has to cover, the conceptual model, and the specific
implementation.

## 2. Requirements

1. A manifest must allow for the retrieval of complete packages of
   related resources sufficient to support the FAIR use of a data or
   metadata object.

2. It must contain a listing of each of its component parts, along with
   needed identifiers, descriptors, typing, and characterization so that
   both humans and machines can understand its relationship to other
   parts of the package.

3. It must provide information sufficient to retrieve each of its
   component parts within the context of the system or network on which
   it is located. (Typically, this will mean web addresses for FAIR
   resources.)

4. It must be self-describing, according to whatever packaging protocol
   or standard it conforms to or uses, so that a receiving system can
   determine how to process it. Ideally, it will be useable by any
   application which supports the type of packaging which was used to
   implement the CDIF model — that is, it will not require a CDIF-aware
   application to unpack.

5. It must be identifiably a conforming instance of a CDIF Manifest
   profile, so that receiving systems can understand how to operate on it
   if they support the CDIF profile.

Functioning as an FDO is **not** a requirement out of the starting gate.
That should be added later, once we can figure out what it means. It is
not a business requirement.

## 3. Kinds of aggregate resource

The requirements above say a manifest lists parts and how to reach them.
What varies — and what the model has to accommodate — is what the parts
*are* to each other. Five dimensions discriminate the cases:

| dimension | question |
|---|---|
| Homogeneity | Do the parts share content type, format, and data structure? |
| Closure | Is the set of parts closed, or open-ended? |
| Accessibility | Are the parts independently retrievable? |
| Distribution | Are the parts potentially under different stewardship? |
| Granularity | Do the parts represent the same information, at the same processing level? |

The patterns below are the combinations that occur in practice. Each
names the scaffolding example that shows how it is expressed.

### 3.1 Parts of different kinds, independently accessible

A Dataset that has other Resources as parts; each part has one or more
distributions that are a WebAPI or a DataDownload. The parts are
individually accessible and may have different content types, formats and
data structures, but all relate to the aggregate.

This is the core data plus supporting resources that might not be data in
the same sense — a codebook, a data dictionary, a quality report, a
methodology document, provenance records, a thumbnail or browse image, a
readme. These are not alternative representations or parts of the same
structure; they are different kinds of resource that together constitute
the complete intellectual package. The RO-Crate model handles this by
typing entities differently (File, CreativeWork, MediaObject) while
keeping them all in `hasPart`.

→ [`demoExamples/01-heterogeneous-parts.json`](demoExamples/01-heterogeneous-parts.json)

### 3.2 Federated or distributed parts

The same shape as §3.1, but the parts are hosted by different
organizations at different URLs, with potentially different access
protocols. No single distribution gives you the whole Dataset. Examples:
a federated SPARQL endpoint, a distributed STAC catalog, a multi-node
ESGF climate archive.

The metadata challenge is describing the whole while the parts are
independently managed and may have different availability, access
policies, and update schedules — so those properties belong on each part,
not on the aggregate.

→ [`demoExamples/02-federated-distributed.json`](demoExamples/02-federated-distributed.json)

### 3.3 A closed collection of like files

A Dataset that is a collection of files with the same content type and
structure. Glob naming, one description of the data structure, one
distribution with a URL template and parameters to reach individual
items.

Examples: a set of images, all the same size, with a progression of
related subjects; an X-ray computed tomography dataset.

→ [`demoExamples/03-homogeneous-collection-static.json`](demoExamples/03-homogeneous-collection-static.json)

### 3.4 A collection that grows

As §3.3, but the dataset accumulates new parts — records, granules,
files, entries — over time. The dataset identity is stable while its
contents change. At any point there is a definable set of parts, but the
set is not closed, and parts may arrive asynchronously.

The metadata challenge is describing the dataset as a whole (temporal
coverage, update frequency) while the parts are still accumulating. DCAT
addresses this with `dcat:DatasetSeries` and `dcterms:accrualPeriodicity`.
Examples: a series of asynchronous heliophysics burst event data; a
monitoring station producing daily files; a satellite mission
accumulating orbit-by-orbit data; a long-running sensor network; monthly
government employment statistics.

→ [`demoExamples/04-growing-collection-series.json`](demoExamples/04-growing-collection-series.json)
— **and see §7, gap 1.** CDIF currently defines neither of the two
properties this pattern needs.

### 3.5 A single archive file

A dataset distributed as one file archive: one dataset, one distribution,
parts not individually accessible on the web but having location paths
within the archive. Each part can carry a full description. Parts may be
homogeneous or heterogeneous.

Examples: OSIRIS-REx or NASA PDS bundles; NeXus/HDF5 files holding
multiple `entry` objects that are separately usable datasets, possibly
with different data structures.

This is the case the CDIF Manifest profile is built around. Parts are
typed `schema:MediaObject` and **must not** be typed
`schema:DataDownload`, because there is no URL to retrieve them from.

→ [`demoExamples/05-archive-bundle.json`](demoExamples/05-archive-bundle.json)

### 3.6 One content, several representations

A dataset with multiple distributions, where the distributions are
different representations of the same content: a geologic map in
shapefile and geopackage and several spatial reference systems; tabular
data in Excel and CSV.

Each distribution is a complete, interchangeable copy. A consumer picks
one; nothing is assembled.

→ [`demoExamples/06-multiple-representations.json`](demoExamples/06-multiple-representations.json)

### 3.7 Multi-resolution and multi-scale

The same data at multiple levels of detail or aggregation. The parts
represent the same content at different granularities, not different
content.

This is **distinct from §3.6**: information content genuinely differs
between levels, because coarser resolution loses detail. OGC Tiles and
STAC handle this with asset roles and resolution metadata. Examples: a
tiled image pyramid (COG/GeoTIFF overviews, map tile sets at zoom
levels); multi-resolution climate model output; a point cloud at
different decimation levels; daily, weekly, monthly and annual climate
statistics.

→ [`demoExamples/07-multi-resolution.json`](demoExamples/07-multi-resolution.json)

### 3.8 Subsets generated on demand

The distribution is a WebAPI with parameters that define the subset, and
the "parts" are ephemeral query results. A large dataset — a data cube, a
relational database, an SDMX data flow — where the parts do not exist as
pre-formed files but are generated on request: OPeNDAP subsetting, WCS
requests, SDMX queries, SPARQL endpoints.

The dataset is logically one thing with no pre-existing decomposition,
but access is always to a subset. **The partitioning is defined by a
consumer query, not by the producer.** The long-standing problem is how
to identify such subsets when they are inputs to subsequent analysis, so
that provenance is accurate and the analysis reproducible.

This section describes the *service*. **§3.11 describes a particular
result** drawn from it, which is where that identity problem is
addressed.

→ [`demoExamples/08-webapi-query-subsets.json`](demoExamples/08-webapi-query-subsets.json)

### 3.9 Versions

The same dataset at different points in its revision history — not
growing as in §3.4, but replaced or corrected. Version 1.0, 1.1, 2.0,
each a complete snapshot. The parts are temporal versions of the same
intellectual content.

The question is whether the versions constitute one dataset with multiple
states or multiple datasets with a lineage relationship. DataCite and
DCAT answer differently: DataCite uses `IsNewVersionOf` /
`IsPreviousVersionOf` relations between separate DOIs; DCAT 3 uses
`dcat:DatasetSeries` with `dcat:inSeries`.

→ [`demoExamples/09-versioned.json`](demoExamples/09-versioned.json), which
takes the DataCite reading. **See §7, gap 2.**

### 3.10 Derived and linked families

A raw dataset and its processed derivatives, maintaining identity
relationships: raw spectra → background-corrected spectra → normalized
spectra → fitted parameters. Each is a distinct dataset, but they are
linked by provenance.

This differs from §3.6 because the information content genuinely changes
at each processing step. PROV handles this with `prov:wasDerivedFrom`
chains; the CDIF `CreateAction` provenance chain captures the same
pattern and additionally records *what was done*.

→ [`demoExamples/10-derived-family.json`](demoExamples/10-derived-family.json)

### 3.11 A cited subset

§3.8 leaves a subset with no identity: the service is described, the
parameters are declared, but the *result* — the thing an analysis
actually consumed — cannot be referred to. This pattern gives it one.

A particular query result gets **its own metadata record with its own
`@id`**, separate from the resource it was drawn from. Three properties
carry the weight:

- **`prov:wasDerivedFrom`** names the source resource. Its
  `schema:identifier` is stable across revisions and names the
  intellectual intention; the subset record's `@id` names one state that
  was actually used. (See the CDIF Core implementation guide,
  *identifier and version identify different things*.)
- **`prov:wasGeneratedBy`** records the request. Its `schema:target` is
  the `EntryPoint` that was invoked and its `schema:additionalProperty`
  entries are the parameter *values supplied*, not the patterns they had
  to match. This mirrors the source's `schema:potentialAction`, which
  says what *can* be varied; here we say what *was*.
- **`schema:distribution`** carries `schema:contentUrl` — the request as
  issued, directly re-runnable — and **`spdx:checksum`**, the hash of
  what actually came back.

→ [`demoExamples/11-cited-subset.json`](demoExamples/11-cited-subset.json)

#### What this achieves, and what it does not

**It achieves citation and provenance.** The subset has an identifier, a
lineage, and a reproducible statement of how it was obtained.

**It does not achieve reproducibility on its own**, and a profile that
implied otherwise would be worse than one that said nothing. A request
URL identifies the *request*, not the *response*. Re-issued against a
live service it returns whatever the service holds now — and if the
source grows (§3.4) or is corrected (§3.9), that is different data.

The checksum is what makes this tolerable: it turns **silent divergence
into detectable divergence**. A later reader re-runs the query, hashes
the result, and knows at once whether they are looking at what was
originally used. They cannot recover the original bytes, but they are
not misled — which is the failure mode that matters.

Genuine reproducibility needs one more thing, and it is not in the
metadata's gift: **the source service must be versioned or timestamped**,
so the query can be re-executed *as of* the original moment. Where that
holds, record the retrieval time (`schema:startTime` on the activity)
and the pair is sufficient.

State the ceiling explicitly wherever this pattern is used, so that a
consumer does not read a subset record as a reproducibility guarantee
when it is only a divergence check.

#### Relationship to the RDA recommendation

The [RDA Data Citation Working
Group](https://www.rd-alliance.org/group/data-citation-wg/outcomes/data-citation-recommendation.html)
addresses the same problem and inverts the identification: assign the
persistent identifier to a **timestamped query** against **versioned
source data**, rather than to the result. Re-executing with the original
timestamp returns what the study used; re-executing with the current
timestamp returns the same selection with corrections applied.
[DataCite 4.5](https://datacite-metadata-schema.readthedocs.io/en/4.5/guidance/dynamic-datasets/)
gives corresponding citation guidance.

The trade is clear. The RDA approach actually reproduces, but only
because it requires the store to support versioned re-execution — a
substantial demand on the service. The pattern here needs nothing from
the server and works against any parameterised endpoint, at the cost of
detecting rather than preventing divergence. **Where a service does
implement the RDA recommendations, prefer them**, and use this record
shape to carry the query PID and its timestamp.

### Distinctions that are easy to lose

Three pairs read alike in prose and must be modelled differently. A
record that confuses them still validates.

- **`hasPart` versus several distributions.** Use `hasPart` when the
  parts together constitute the dataset and no single one gives you the
  whole (§3.1, §3.2, §3.5, §3.7). Use several distributions when each is
  a complete interchangeable copy and a consumer picks exactly one
  (§3.6).
- **§3.6 versus §3.7.** Identical content in a different encoding is a
  distribution. Content that has lost detail through aggregation is a
  separate Dataset.
- **§3.4 versus §3.9.** Both change over time. §3.4 accumulates under a
  stable identity; §3.9 replaces one complete snapshot with another.

## 4. Conceptual model

| element | | description |
|---|---|---|
| Protocol conformance statement | **R** | What protocol is used to constitute the package being described, and to which the supplied information conforms (RO-Crate, Frictionless Data, etc.) |
| Package identification | **R** | A unique identifier for the package, according to a known scheme |
| Package name | O | A human-readable name for the package, to help distinguish it from others |
| Package description | O | A human-readable description of the package, its contents and purpose |
| Package date | O | The date of creation of the package (may include time) |
| Package creator | O | Information about the creator of the package, for attribution. May contain contact information |
| Location information | **R** | Information needed to resolve item locations, such as a root directory |
| Typed item list | **R** | The items which are the parts of the package. Each has an ID and a location, local or networked, with the package's location information sufficient to resolve it. Items may be categorized by types meaningful to the packaging mechanism (MIME types, etc.) and/or semantically (e.g. "data entities", "context entities") |
| Licensing information | O | Under IP law an assemblage can be licensed differently from its constituent parts. This license is for the package; parts may carry their own |

**R** = required, **O** = optional.

## 5. RO-Crate implementation

> **Incomplete in the source document.** The bullets below are what
> `CDIF Manifest Profile-V1-smr.docx` contains; it ends with three empty
> list items. Nothing has been invented to fill them.

- A flattened, condensed JSON-LD file, per the RO-Crate 1.2
  specification.
- `@type` of `CreativeWork`, as in RO-Crate 1.2. (`schema:Collection` is
  tempting, but we need none of its properties, so `CreativeWork` is
  appropriate.)
- `ro-crate-metadata.json` as the graph `@id`; the file is named
  `ro-crate-metadata.json` and appears in the root, per the RO-Crate 1.2
  specification.
- *(to be completed)*

See [`RO-Crate-relationship.md`](RO-Crate-relationship.md) for the wider
comparison.

## 6. CDIF JSON-LD implementation

The profile module is `cdifManifest`; a conforming record declares
`https://w3id.org/cdif/manifest/1.1` in
`schema:subjectOf` → `dcterms:conformsTo`. The release artifacts are
`cdifManifestStructuredSchema.json` (JSON Schema),
`manifestRules.shacl` (SHACL) and `cdifManifest-frame.jsonld` (frame),
all in the repository root.

Validate a record with:

```bash
python FrameAndValidate.py <record>.json --validate --schema cdifManifestStructuredSchema.json --frame cdifManifest-frame.jsonld
```

Ten scaffolding records — one per pattern in §3, all validating — are in
[`demoExamples/`](demoExamples/), with a README covering the modelling
choices.

## 7. Gaps and open questions

**Gap 1 — no way to say a collection grows.** §3.4 needs
`dcat:DatasetSeries` typing and `dcterms:accrualPeriodicity`. **Neither
is defined by any CDIF building block.** CDIF validation is open-world,
so a record using the DCAT terms passes, but nothing in the profile
constrains or documents them and no consumer is obliged to understand
them. This is the most consequential gap: update frequency is the single
thing a consumer of an open-ended dataset most needs to know.

**Gap 2 — version lineage is expressible, but not in the named
vocabulary.** `schema:isBasedOn`, `dcterms:isVersionOf` and
`dcterms:replaces` are undefined in CDIF. `prov:wasDerivedFrom` **is**
defined and carries the lineage in the §3.9 example, so the pattern works
today — just not in the DCAT/DataCite terms §3.9 names. Also absent:
`schema:isPartOf`, so a part cannot point back at its aggregate.

Whether to adopt the DCAT terms, mint CDIF equivalents, or leave these
patterns undescribed is a profile decision.

**Gap 3 — partly closed; the remainder is not a metadata problem.**
§3.11 gives a query-derived subset an identity, a lineage and a record of
the request that produced it, all in existing CDIF vocabulary. That is
enough to **cite** a subset and to trace its provenance.

What it does not give is reproducibility, and the reason is instructive:
a request URL identifies the request, not the response, so re-issuing it
against a live service returns whatever the service now holds. The
`spdx:checksum` reduces this from silent to detectable — a reader can
tell they got something different — but recovering the original bytes
requires the **source service** to support versioned or timestamped
re-execution. No metadata property can supply that.

So the remaining gap belongs to service implementers rather than to this
profile. Where a service does implement the
[RDA Data Citation recommendations](https://www.rd-alliance.org/group/data-citation-wg/outcomes/data-citation-recommendation.html),
the §3.11 record shape can carry the query PID and its timestamp and the
problem is solved outright.

**Open — one dataset or many?** §3.9 raises it and this document does not
settle it: are versions one dataset in several states, or several
datasets in a lineage? The example takes the DataCite reading. Both are
defensible; the choice should be made explicitly rather than by default.

---

## Editorial note

Merged and lightly copy-edited from the two source documents. Changes
beyond formatting:

- Typographic corrections carried over from the docx: *radable* →
  readable, *charaterization* → characterization, *procssing* →
  processing, *govenment* → government, *separatly* → separately, and
  "The **data** of the creation of the package" → *date*.
- The conceptual model became a table; requirement 5's trailing note on
  FDOs became a sentence rather than a parenthetical.
- Two of the taxonomy's items were split, because each described two
  cases the model treats differently. Item 1 became §3.1 and §3.2 (its
  own text introduces the federated case with "Includes…", and the
  federated case puts provider and access properties on the parts rather
  than the aggregate). Item 2 became §3.3 and §3.4 — it states outright
  that "there are two cases here", closed and open-ended, and only the
  second needs accrual metadata. Its examples were divided accordingly.
  So §3.n does not map one-to-one onto the source's numbering.
- The taxonomy's cross-reference in the versioning paragraph read "not
  growing (#5)", but growing collections were item 2 of that document and
  #5 was multi-resolution. Corrected here to §3.4.
- The RO-Crate section's three empty bullets are marked *(to be
  completed)* rather than dropped, since their absence is itself the
  state of the work.
