# Aggregate-resource patterns — CDIF scaffolding examples

Ten JSON-LD records, one per pattern in
[`../KindsOfAggregateResources.md`](../KindsOfAggregateResources.md).
Each shows **how the pattern is expressed** in CDIF — the entities and
properties that carry the distinction — not a realistic record. Values
are placeholders; the structure is the point.

All ten validate:

```bash
python FrameAndValidate.py docs/demoExamples/01-heterogeneous-parts.json \
    --validate --schema cdifManifestStructuredSchema.json \
    --frame cdifManifest-frame.jsonld
```

## The set

| file | pattern | the distinguishing move |
|---|---|---|
| [01-heterogeneous-parts.json](01-heterogeneous-parts.json) | §1 — parts of different kinds | `schema:hasPart`, each part **typed for what it is** (`Dataset` / `CreativeWork` / `MediaObject`) and carrying its own `schema:distribution` |
| [02-federated-distributed.json](02-federated-distributed.json) | §1, federated | same, but each part carries its **own** `schema:provider`, `schema:conditionsOfAccess`, `schema:dateModified` — those are what differ under separate stewardship |
| [03-homogeneous-collection-static.json](03-homogeneous-collection-static.json) | §2, closed | **no** `hasPart`. One distribution, one `cdi:isStructuredBy` for all files, a `schema:potentialAction` URL template to address them |
| [04-growing-collection-series.json](04-growing-collection-series.json) | §2, open-ended | as 03, plus open-ended `schema:temporalCoverage` (`2019-01-01/..`) and accrual — **see the gap below** |
| [05-archive-bundle.json](05-archive-bundle.json) | §3 — one archive | one `DataDownload` with `schema:hasPart`; parts are `schema:MediaObject` and **must not** be `DataDownload`, because there is no URL to fetch them from. `schema:about` links a sidecar to its data file |
| [06-multiple-representations.json](06-multiple-representations.json) | §4 — same content | several `schema:distribution` entries, **no** `hasPart`. Variables stated once on the dataset, because every distribution has the same ones |
| [07-multi-resolution.json](07-multi-resolution.json) | §5 — same content, different granularity | `hasPart` Datasets, **not** distributions — coarser levels lose detail, so the information content genuinely differs |
| [08-webapi-query-subsets.json](08-webapi-query-subsets.json) | subset access | **no** `hasPart` at all. A `WebAPI` distribution whose `potentialAction` declares what can be varied; `schema:result` describes what comes back |
| [09-versioned.json](09-versioned.json) | versions | complete snapshots linked by `prov:wasDerivedFrom` — contrast 04, which grows rather than being replaced |
| [10-derived-family.json](10-derived-family.json) | derived family | `prov:wasGeneratedBy` a `schema:CreateAction` whose `schema:object` is the input, so each link records what was *done*, not only what it came from |

## The distinctions worth not losing

Several patterns look alike in prose and are modelled differently. The
three that matter most:

**`hasPart` vs several `distribution`s.** Use `hasPart` when the parts
together *constitute* the dataset and no single one gives you the whole
(01, 02, 05, 07). Use multiple distributions when each is a complete,
interchangeable copy and a consumer picks exactly one (06). Getting this
backwards tells a consumer to download three files when one would do, or
one when they need three.

**Multiple representations (06) vs multi-resolution (07).** Both look
like "the same data, several forms". In 06 the information content is
identical and only the encoding differs, so they are distributions. In
07 coarser aggregation has *lost* something, so they are separate
Datasets. A consumer choosing between them in 07 is choosing what to
measure, not what to download.

**Growing (04) vs versioned (09).** Both change over time. In 04 the
contents accumulate and the identity is stable. In 09 each version is a
complete snapshot that replaces its predecessor. 09 takes the DataCite
reading — each version its own dataset with its own identifier, linked by
lineage — rather than the DCAT reading of one dataset with several
states. Both readings are defensible; the choice should be explicit.

## Gaps found while writing these

Two patterns need properties that **no CDIF building block defines**.
CDIF validation is open-world (no `additionalProperties: false`
anywhere), so the records below validate — but nothing in the profile
constrains or documents these terms, and no consumer is obliged to
understand them.

| term | needed by | status |
|---|---|---|
| `dcat:DatasetSeries` | 04 — typing an open-ended collection | not in any BB |
| `dcterms:accrualPeriodicity` | 04 — stating update frequency | not in any BB |
| `dcterms:isVersionOf`, `dcterms:replaces` | 09 — version lineage | not in any BB |
| `schema:isBasedOn` | 09 — named in the source doc | not in any BB |
| `schema:isPartOf` | inverse of `hasPart`, for a part pointing back at its aggregate | not in any BB |

`prov:wasDerivedFrom` **is** defined, and carries the version lineage in
09, so the versioning case is expressible today — just not in the DCAT
vocabulary the source document names. The accrual case in 04 is the real
hole: there is currently no CDIF-sanctioned way to say "this collection
grows, roughly daily", which is the one thing a consumer of an
open-ended dataset most needs to know.

Whether to adopt the DCAT terms, mint CDIF equivalents, or leave the
pattern undescribed is a profile decision, not one these examples make.
Files 04 and 09 flag the borrowed terms in their `schema:description`.

## One open question these do not answer

§Other of the source document asks how to identify a query-derived
subset (08) so that an analysis using it stays reproducible. Nothing
here solves it. The record describes the *service* and its parameters;
it does not give a subset an identity. A provenance trace that cites
"the result of this query at this time" needs either a server-minted
identifier for the response or a client-side record of the exact request
plus a content hash — neither of which the current profile has a place
for.

## A defect this work surfaced

`schema:about` was missing from `ARRAY_PROPERTIES` in
`FrameAndValidate.py`. Framing embeds the referenced node, which
collapses the single-item array to a bare object, and the schema
declares it an array — so **every sidecar reference failed validation**.
It was breaking 4 of the 8 records in `examples/`
(`adaPanalyticalXRD`, `adaPyrolysisGCMSBundle`, `exampleCdifManifest`,
`tof-htk9-f770-test`). Fixed; all 8 now pass.
