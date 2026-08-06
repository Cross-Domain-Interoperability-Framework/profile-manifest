# Relationship of CDIF Metadata Profiles to DataONE

## Overview

[DataONE](https://www.dataone.org/) federates ~3.4 million objects across
member repositories. It has been solving the aggregate-resource problem
in production for over a decade, and it solves it **differently from
CDIF in three respects that bear directly on the manifest profile**:

1. **Descriptive and structural metadata are separate objects,
   versioned independently** — an OAI-ORE resource map beside the
   science metadata, each with its own identifier and version chain.
2. Versioning uses **two identifier kinds at once**, denoting different
   things: one names the intellectual intention, the other names what
   was actually used.
3. Some aggregates are defined by a **stored query** rather than an
   enumerated membership list — a pattern absent from
   [`KindsOfAggregateResources.md`](KindsOfAggregateResources.md).

Note that §1 is narrower than "ORE aggregations differ from
`schema:Dataset` + `hasPart`". Mostly they do not: CDIF identifies its
aggregate, and `schema:subjectOf` already makes ORE's
description/described split. The independent versioning is the part that
is genuinely different.

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

### How this differs from `schema:Dataset` + `hasPart` — and how much

Less than it first appears. Two of the three apparent differences
dissolve on inspection; one is real.

**Not a difference: identifying the aggregate.** A CDIF
`schema:Dataset` has an `@id` and a `schema:identifier`, so the
aggregate is just as citable as an ORE aggregation. "This analysis used
package X" is expressible either way.

**Not a difference: separating the description from the thing
described.** ORE splits the `ore:ResourceMap` (a retrievable document)
from the `ore:Aggregation` (the set it describes), linked by
`ore:describes`. CDIF makes the same split with `schema:subjectOf` — the
catalog record is the document, the Dataset is the thing. Same move,
different vocabulary.

**The real difference: descriptive and structural metadata are separate
objects, versioned independently.** In DataONE the science metadata
(title, abstract, creators — an EML file) and the package structure
(what is in it — the ResourceMap) are two objects with two PIDs and two
version chains. Verified on the example package:

| object | PID | obsoletes | seriesId |
|---|---|---|---|
| EML science metadata | `…5c2190a36a8151c…` | `…a821c884b3b9e26…` | `doi:10.3334/CDIAC/OTG.NDP036` |
| ORE resource map | `…d181621a8fd7496…` | `…5698012fef393f1…` | *(none)* |

Different chains, and the DOI is on the descriptive object only. So a
repository can revise an abstract without reissuing the membership list,
or change what is in the package without touching the description, and
each revision is independently addressable.

In CDIF both live in one JSON-LD document, so any change to either
produces a new version of the whole record. Whether that matters depends
on whether membership churns independently of description — which for a
growing collection (§3.4) it certainly does.

**A third, weaker difference: graph versus tree.** `ore:aggregates` and
`ore:isAggregatedBy` are declared inverses, so a resource can sit in
several aggregations natively. Nested `hasPart` tends toward a tree, and
the same part in two datasets means either duplication or `@id`
references. CDIF can express the reference form, so this is a
serialization habit rather than a limit of the model.

### `cito:documents` and `schema:about` are the same relationship

They are, and the pairs are symmetric:

| | forward | inverse |
|---|---|---|
| CiTO | `cito:documents` — "The citing entity documents information about the cited entity" | `cito:isDocumentedBy` |
| schema.org | `schema:about` — "The subject matter of an object" | `schema:subjectOf` (declared `inverseOf`) |

`cito:documents` is the narrower term — documentation specifically,
rather than aboutness in general — but that is a specialization, not a
conflict. For the metadata-describes-data case they say the same thing,
in the same direction, with the same inverse available.

So **this is not a vocabulary gap; it is a scoping question.** CDIF
already has the right property, and already uses the `subjectOf` side of
it for the catalog-record relationship. What it does not have is
permission to use `schema:about` between *independently accessible*
parts. The manifest profile declares it only on archive parts, so the
§3.1 example
([`demoExamples/01-heterogeneous-parts.json`](demoExamples/01-heterogeneous-parts.json))
can say a codebook is *in* the package but not that it *describes* a
particular part of it.

> **Candidate change.** Allow `schema:about` on `schema:hasPart` members
> generally, not only on archive parts. No new term, no new semantics —
> just removing a scope restriction that has no motivation behind it.

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
citable series identifier).

### The two identifiers denote different kinds of thing

They are not two names for one resource at different granularities. They
answer different questions, and a record needs both because a reader has
both:

- **The series identifier names the intellectual intention** — what the
  dataset is *for*: its subject, content type, data model, format. It is
  what you cite when you mean "the Indian Ocean radiocarbon dataset",
  and it should keep resolving as the data is corrected and reissued,
  because the intention has not changed.
- **The version identifier names what was actually used** — the exact
  bytes that went into an analysis and therefore bear on its
  conclusions. It has to be immutable, because if it can change then a
  result cited against it is not reproducible.

Conflating them costs one of the two: cite only the series and the
analysis is not reproducible, because the content moved underneath it;
cite only the version and the reference rots, pointing at a superseded
snapshot when the reader wants the dataset.

Both DCAT and DataCite give one identifier per version and let citation
practice sort out the rest. DataONE makes the distinction structural, and
puts the DOI — the thing humans cite — on the intention rather than the
snapshot.

**For CDIF gap 2** this suggests the question is not which of DCAT or
DataCite to follow, but whether a record should carry both identifiers
with their roles distinguished. CDIF has `schema:identifier` and
`schema:version` but nothing that says *this identifier is stable across
revisions and that one is not*, so a consumer cannot tell which they have
been handed.

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
| aggregate membership | `schema:hasPart` | `ore:aggregates` / `ore:isAggregatedBy` |
| the aggregate itself | the `schema:Dataset`, identified | an `ore:Aggregation`, identified |
| description vs. the thing described | `schema:subjectOf` → catalog record | `ore:describes` → resource map |
| descriptive and structural metadata | one document, versioned together | two objects, versioned independently |
| metadata describes data | `schema:about` / `schema:subjectOf` — **archive parts only** | `cito:documents` / `cito:isDocumentedBy` — anywhere |
| part → whole | *(none)* | *(none — `isPartOf` unused)* |
| version chain | `prov:wasDerivedFrom` | `obsoletes` / `obsoletedBy` |
| identifier for the intellectual intention | *(not distinguished)* | `seriesId`, resolving to the head |
| identifier for what was actually used | *(not distinguished)* | immutable PID per object |
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
