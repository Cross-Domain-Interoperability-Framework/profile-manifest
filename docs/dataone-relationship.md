# Relationship of CDIF Metadata Profiles to DataONE

## Overview

[DataONE](https://www.dataone.org/) federates ~3.4 million objects across
member repositories. It has been solving the aggregate-resource problem
in production for over a decade, and it solves it **differently from
CDIF in three respects that bear directly on the manifest profile**:

1. A package is a **first-class object with its own identifier** —
   an OAI-ORE aggregation — not a property of the dataset.
2. Versioning uses **two identifier kinds at once**: a stable series
   identifier plus a chain of immutable per-version identifiers.
3. Some aggregates are defined by a **stored query** rather than an
   enumerated membership list — a pattern absent from
   [`KindsOfAggregateResources.md`](KindsOfAggregateResources.md).

This document records what was observed by querying the live API in
August 2026, and what it implies for the gaps in
[`CDIF-ManifestProfile202608.md`](CDIF-ManifestProfile202608.md) §7.
Example records are in [`dataoneExamples/`](dataoneExamples/).

## The API

`search.dataone.org` is a client-rendered front end (MetacatUI) over the
Coordinating Node REST API. **Scraping landing pages returns nothing** —
`curl … | grep ld+json` finds no markup, because DataONE injects
schema.org server-side through a separate proxy
([metacatui-ssr](https://github.com/amoeba/metacatui-ssr)). Query the API
instead. No key is required.

| endpoint | returns |
|---|---|
| `https://cn.dataone.org/cn/v2/query/solr/?q=…&wt=json` | the search index behind the portal |
| `https://cn.dataone.org/cn/v2/meta/{pid}` | system metadata (identifiers, checksum, version chain) |
| `https://cn.dataone.org/cn/v2/object/{pid}` | the object bytes — science metadata, data, or a resource map |
| `https://cn.dataone.org/cn/v2/resolve/{pid}` | locations holding a copy |

Counts observed 2026-08-06, useful as a sense of which mechanisms are
actually used:

| Solr field | objects | meaning |
|---|--:|---|
| *(total)* | 3,365,371 | |
| `formatId` | 3,365,371 | every object declares its format |
| `seriesId` | 1,291,582 | participates in a version series |
| `resourceMap` | 1,244,930 | belongs to an ORE package |
| `isDocumentedBy` | 1,073,884 | is described by a metadata record |
| `obsoletes` | 744,514 | supersedes an earlier version |
| `documents` | 216,021 | is a metadata record describing data |
| `collectionQuery` | 2,070 | membership defined by a query |
| `isPartOf` | **0** | not used |

That last row is worth noting: DataONE does not use `isPartOf`, and
neither does CDIF define it. Nothing in either model lets a part point
back at its aggregate.

## 1. Packages are OAI-ORE aggregations

A CDIF record nests parts inside the thing they belong to, via
`schema:hasPart` on the Dataset or on a distribution. DataONE does not.
The Solr record carries a `resourceMap` identifier pointing at a
**separate RDF document** that describes the package:

```
ore:describes        ResourceMap  →  Aggregation
ore:aggregates       Aggregation  →  each of the 12 members
ore:isAggregatedBy   the inverse
cito:documents       the EML metadata file  →  each data object
cito:isDocumentedBy  the inverse
```

`dataoneExamples/resource-map.ore.rdf` is a real one: 66 triples, 12
members, for the dataset *Indian Ocean Radiocarbon: Data from the INDIGO
1, 2, and 3 Cruises*.

### Why the indirection matters

**The package is citable and versionable in its own right.** The
aggregation has a PID, so you can obsolete a package without touching its
members, and you can say "this analysis used package X" rather than
enumerating twelve files. In CDIF the aggregate is the Dataset and
`hasPart` is a property of it — there is no separate thing to identify.

**`cito:documents` is an explicit metadata-describes-data edge, and CDIF
has no equivalent.** In the aggregation above, one EML file `documents`
all twelve data objects. The CDIF §3.1 example
([`demoExamples/01-heterogeneous-parts.json`](demoExamples/01-heterogeneous-parts.json))
types a codebook as `schema:CreativeWork` and leaves its relationship to
the data implicit — a consumer can see the codebook is *in* the package
but not that it *describes* a particular part of it.

The manifest profile's `schema:about` on archive parts is the closest
thing, and it is the right shape, but it only applies **inside** an
archive distribution. There is no way to say "this codebook describes
that dataset" when both are independently accessible parts.

> **Candidate change.** Allow `schema:about` on `schema:hasPart` members
> generally, not only on archive parts. It is already in the profile
> vocabulary, already means the right thing, and would close a real gap
> in §3.1 and §3.2.

## 2. Versioning: two identifier kinds, deliberately

`CDIF-ManifestProfile202608.md` §3.9 poses the question as either/or:
one dataset in several states (DCAT), or several datasets in a lineage
(DataCite). **DataONE answers "both", and gives each answer its own
identifier type.**

Observed on `doi:10.3334/CDIAC/OTG.NDP036`:

```
seriesId  doi:10.3334/CDIAC/OTG.NDP036      ← stable; cite this
   2018-08-13   ess-dive-a821c884b3b9e26…
   2018-08-23   ess-dive-5c2190a36a8151c…    obsoletes ↑
   2021-04-30   ess-dive-7503a102cb11fa8…    obsoletes ↑   ← head
```

- Every version has its **own immutable PID**. Content at a PID never
  changes, so a provenance trace citing one is reproducible forever.
- The **`seriesId` is the citable identifier**, and
  `GET /cn/v2/meta/{seriesId}` returns the head — 2021-04-30 here. A
  citation stays current without being rewritten.
- `obsoletes` / `obsoletedBy` form the chain, so the full history is
  walkable in both directions.

`dataoneExamples/system-metadata-seriesHead.xml` is the head record
resolved from the DOI; note that its `identifier` and `seriesId` differ,
which is the whole point.

This is a third model, distinct from both that §3.9 names. It is not
DCAT's `dcat:DatasetSeries`/`inSeries` (which groups peer datasets), and
not DataCite's `IsNewVersionOf` between peer DOIs (which has no single
citable series identifier). It separates **the identifier you cite** from
**the identifier you reproduce from** — a distinction neither of the
other two makes, and one worth considering for CDIF gap 2.

## 3. Query-defined collections

This pattern is **not in the CDIF taxonomy** and should probably be added.

DataONE Portals (`formatId https://purl.dataone.org/portals-1.0.0`,
2,070 objects) define membership by a stored Solr query rather than a
list. The *Distributed Biological Observatory* portal, for example:

```
(((readPermission:CN=DBO,DC=dataone,DC=org) AND (-obsoletedBy:* AND formatType:METADATA)))
```

Read that as: every current (`-obsoletedBy:*`) metadata record the DBO
group can read. Membership is **evaluated at read time**. Add a dataset
to the group and the collection grows, with nothing edited.

### How this differs from the patterns already in the taxonomy

- Not §3.4 (a collection that grows): there, parts accumulate under a
  producer's control and the *rule* for what belongs is implicit. Here
  the rule is the definition, and it is explicit and machine-actionable.
- Not §3.8 (subsets generated on demand): there the partitioning is
  chosen by the **consumer's** query. Here it is fixed by the
  **producer** and is stable, citable, and the same for everyone —
  it just isn't enumerated.

So the taxonomy's closure dimension needs a third value. It currently
asks "closed or open?"; this is a case where the set is neither
enumerated nor open-ended, but *derived*. A useful discriminator is
**who defines membership, and when it is evaluated**:

| | membership defined by | evaluated |
|---|---|---|
| §3.3 closed collection | producer, enumerated | at publication |
| §3.4 growing collection | producer, implicit | continuously |
| **query-defined** | **producer, as a query** | **at read time** |
| §3.8 on-demand subset | consumer, as a query | per request |

A query-defined collection is reproducible in a way §3.8 is not — the
query is stored and public — but is still not *stable*, because the same
query returns different members over time. Citing one for provenance
needs the query **and** an evaluation timestamp. Which is the same
unsolved problem as gap 3, one step less severe.

## 4. What DataONE does not solve either

**Accrual cadence.** Nothing in the field list states how often a growing
collection updates. `seriesId` handles *replacement*, not
*accumulation*; a growing collection is represented as an ORE aggregation
that gets re-issued. So **CDIF gap 1 is a gap in DataONE too** — there is
no equivalent of `dcterms:accrualPeriodicity` anywhere in the observed
schema. This is evidence the gap is genuinely hard rather than an
oversight in CDIF, but not a reason to leave it open.

**Subset identity.** The `collectionQuery` mechanism above shows the
same shortfall as CDIF gap 3: a query is recorded, but a *result* is
never given an identifier.

## 5. Summary of correspondences

| concept | CDIF | DataONE |
|---|---|---|
| aggregate membership | `schema:hasPart` on the Dataset or distribution | `ore:aggregates` on a separately identified `ore:Aggregation` |
| the package itself | not separately identified | a Resource Map object with its own PID |
| metadata describes data | `schema:about` (archive parts only) | `cito:documents` / `cito:isDocumentedBy` |
| part → whole | *(none)* | *(none — `isPartOf` unused)* |
| version chain | `prov:wasDerivedFrom` | `obsoletes` / `obsoletedBy` |
| citable identity across versions | *(none)* | `seriesId`, resolving to the head |
| per-version identity | `schema:identifier` per record | immutable PID per object |
| integrity | `spdx:checksum` | `checksum` + `checksumAlgorithm` in system metadata |
| query-defined membership | *(none)* | `collectionQuery` |
| update cadence | *(none — gap 1)* | *(none)* |

## 6. Reproducing the examples

```bash
curl "https://cn.dataone.org/cn/v2/query/solr/?q=formatType:METADATA+AND+resourceMap:*+AND+seriesId:*&rows=1&wt=json"
```

| file in `dataoneExamples/` | fetched from |
|---|---|
| `solr-metadata-record.json` | `/cn/v2/query/solr/?q=id:"ess-dive-5c2190a36a8151c-20180823T161526189609"` |
| `resource-map.ore.rdf` | `/cn/v2/object/ess-dive-d181621a8fd7496-20180823T161536711920` |
| `system-metadata-seriesHead.xml` | `/cn/v2/meta/doi:10.3334/CDIAC/OTG.NDP036` |
| `portal-collection-query.json` | `/cn/v2/query/solr/?q=collectionQuery:*&rows=1` |

## References

- [DataONE](https://www.dataone.org/)
- [OAI-ORE specification](https://www.openarchives.org/ore/1.0/toc)
- [CiTO, the Citation Typing Ontology](https://sparontologies.github.io/cito/current/cito.html)
- [science-on-schema.org](https://github.com/ESIPFed/science-on-schema.org)
  — the schema.org guidance DataONE follows for harvest
- [DataONE api-documentation#11 — harmonize ORE, schema.org and CodeMeta in DataONE packages](https://github.com/DataONEorg/api-documentation/issues/11)
  — the same tension, open upstream
- [metacatui-ssr](https://github.com/amoeba/metacatui-ssr) — why landing
  pages carry no JSON-LD when fetched directly
- [`RO-Crate-relationship.md`](RO-Crate-relationship.md) — the sibling
  comparison
