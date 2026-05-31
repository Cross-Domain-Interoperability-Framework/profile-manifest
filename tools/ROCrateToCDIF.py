#!/usr/bin/env python3
"""
RO-Crate to CDIF JSON-LD Converter

Converts an RO-Crate 1.2 JSON-LD document (flattened @graph) into a CDIF-compliant
nested JSON-LD document suitable for validation against CDIF schemas.

Key mappings performed:
  - Finds the root Dataset entity in @graph
  - Resolves all @id references to inline nested objects
  - Maps hasPart DataDownload items to schema:distribution
  - Creates schema:subjectOf from the RO-Crate metadata descriptor
  - Compacts output with CDIF-prefixed context (schema:, prov:, etc.)

Usage:
    python ROCrateToCDIF.py input-rocrate.jsonld -o output-cdif.json
    python ROCrateToCDIF.py input-rocrate.jsonld -o output.json --profile complete
    python ROCrateToCDIF.py input-rocrate.jsonld -o output.json -v --validate
"""

import json
import argparse
import sys
from pathlib import Path
from pyld import jsonld

# Configure the requests-based document loader
jsonld.set_document_loader(jsonld.requests_document_loader())

SCRIPT_DIR = Path(__file__).parent

# CDIF profile URIs
CDIF_PROFILES = {
    "discovery": "https://w3id.org/cdif/profiles/cdifDiscovery/1.0",
    "complete": "https://w3id.org/cdif/profiles/cdifComplete/1.0",
}

# Output context for CDIF compaction — uses prefixed namespaces
CDIF_OUTPUT_CONTEXT = {
    "schema": "http://schema.org/",
    "dcterms": "http://purl.org/dc/terms/",
    "prov": "http://www.w3.org/ns/prov#",
    "dqv": "http://www.w3.org/ns/dqv#",
    "dcat": "http://www.w3.org/ns/dcat#",
    "geosparql": "http://www.opengis.net/ont/geosparql#",
    "spdx": "http://spdx.org/rdf/terms#",
    "time": "http://www.w3.org/2006/time#",
    "sf": "http://www.opengis.net/ont/sf#",
    "cdi": "http://ddialliance.org/Specification/DDI-CDI/1.0/RDF/",
    "csvw": "http://www.w3.org/ns/csvw#",
    "nxs": "https://manual.nexusformat.org/classes/",
}

# Properties that should always be arrays per the CDIF schema
ARRAY_PROPERTIES = {
    "schema:contributor",
    "schema:distribution",
    "schema:license",
    "schema:conditionsOfAccess",
    "schema:keywords",
    "schema:additionalType",
    "schema:sameAs",
    "schema:provider",
    "schema:funding",
    "schema:variableMeasured",
    "schema:spatialCoverage",
    "schema:temporalCoverage",
    "schema:relatedLink",
    "schema:publishingPrinciples",
    "schema:encodingFormat",
    "schema:potentialAction",
    "schema:httpMethod",
    "schema:contentType",
    "schema:query-input",
    "prov:wasGeneratedBy",
    "prov:wasDerivedFrom",
    "prov:used",
    "dqv:hasQualityMeasurement",
    "dcterms:conformsTo",
    "cdi:hasPhysicalMapping",
    "cdi:uses",
}

# RO-Crate type strings that indicate DataDownload (may appear unprefixed or prefixed)
DATADOWNLOAD_TYPES = {"DataDownload", "schema:DataDownload", "http://schema.org/DataDownload"}

# Frame for extracting the root Dataset
FRAME_TEMPLATE = {
    "@type": "http://schema.org/Dataset",
    "@embed": "@always",
}


def _build_entity_index(graph):
    """Build a dict mapping @id -> entity object from the @graph array."""
    index = {}
    for entity in graph:
        eid = entity.get("@id")
        if eid:
            index[eid] = entity
    return index


def _find_root_dataset(graph):
    """Find the root Dataset entity in the @graph.

    Heuristic: look for the entity that the metadata descriptor's 'about' points to,
    or fall back to the first Dataset entity.
    """
    dataset_types = {"Dataset", "schema:Dataset",
                     "http://schema.org/Dataset", "https://schema.org/Dataset"}

    # First, find what the metadata descriptor points to
    about_id = None
    for entity in graph:
        eid = entity.get("@id", "")
        if eid in ("ro-crate-metadata.json", "ro-crate-metadata.jsonld"):
            about = entity.get("about", {})
            if isinstance(about, dict):
                about_id = about.get("@id")
            elif isinstance(about, str):
                about_id = about
            break

    # Find the referenced dataset, or first Dataset
    fallback = None
    for entity in graph:
        etype = entity.get("@type", [])
        if isinstance(etype, str):
            etype = [etype]
        if dataset_types.intersection(etype):
            if entity.get("@id") == about_id:
                return entity
            if fallback is None:
                fallback = entity

    return fallback


def _find_metadata_descriptor(graph):
    """Find the RO-Crate metadata descriptor entity."""
    for entity in graph:
        eid = entity.get("@id", "")
        if eid in ("ro-crate-metadata.json", "ro-crate-metadata.jsonld"):
            return entity
    return None


def _has_datadownload_type(entity):
    """Check if an entity has a DataDownload @type."""
    etype = entity.get("@type", [])
    if isinstance(etype, str):
        etype = [etype]
    return bool(DATADOWNLOAD_TYPES.intersection(etype))


def convert_rocrate_to_cdif(doc, profile="complete", verbose=False):
    """Convert an RO-Crate document to CDIF JSON-LD.

    Steps:
    1. Expand the document to resolve all prefixes
    2. Frame around schema:Dataset to get a nested structure
    3. Compact with CDIF output context
    4. Post-process: map hasPart DataDownloads to distribution,
       create subjectOf from metadata descriptor, normalize arrays
    """
    if verbose:
        print("Step 1: Expanding document...", file=sys.stderr)
    expanded = jsonld.expand(doc)

    if verbose:
        print("Step 2: Framing around schema:Dataset...", file=sys.stderr)
    framed = jsonld.frame(expanded, FRAME_TEMPLATE)

    if verbose:
        print("Step 3: Compacting with CDIF context...", file=sys.stderr)
    compacted = jsonld.compact(framed, CDIF_OUTPUT_CONTEXT)

    # Extract main dataset from @graph if present
    result = compacted
    if "@graph" in compacted and isinstance(compacted["@graph"], list):
        dataset = _pick_main_dataset(compacted["@graph"])
        if dataset:
            result = {"@context": compacted.get("@context"), **dataset}

    if verbose:
        print("Step 4: Post-processing...", file=sys.stderr)

    # Map hasPart DataDownloads → distribution
    result = _move_downloads_to_distribution(result)

    # Create subjectOf from original @graph metadata descriptor
    # (also moves includedInDataCatalog from top-level into subjectOf)
    result = _create_subject_of(result, doc, profile)

    # Remove includedInDataCatalog from top level (belongs in subjectOf only)
    result.pop("schema:includedInDataCatalog", None)

    # Remove from top-level hasPart any items already inside distribution.hasPart
    result = _dedup_haspart_from_distribution(result)

    # Normalize: remove nulls, ensure arrays, normalize @type
    result = _normalize(result)

    return result


def _pick_main_dataset(graph):
    """From a framed @graph, pick the main dataset entity."""
    # Prefer the one with distribution or hasPart
    for item in graph:
        if item.get("schema:distribution") or item.get("schema:hasPart"):
            return item
    # Fallback: first with schema:url, or just first
    for item in graph:
        if item.get("schema:url"):
            return item
    return graph[0] if graph else None


def _move_downloads_to_distribution(result):
    """Move DataDownload items from schema:hasPart to schema:distribution.

    In RO-Crate, files are listed in hasPart. In CDIF, DataDownload items
    belong in schema:distribution. Non-DataDownload items stay in hasPart.
    """
    has_part = result.get("schema:hasPart")
    if not has_part:
        return result

    if isinstance(has_part, dict):
        has_part = [has_part]

    downloads = []
    remaining = []

    for item in has_part:
        if isinstance(item, dict):
            etype = item.get("@type", [])
            if isinstance(etype, str):
                etype = [etype]
            if DATADOWNLOAD_TYPES.intersection(etype):
                downloads.append(item)
            else:
                remaining.append(item)
        else:
            remaining.append(item)

    if downloads:
        # Get existing distributions
        existing = result.get("schema:distribution", [])
        if isinstance(existing, dict):
            existing = [existing]
        elif existing is None:
            existing = []

        # Merge, deduplicating by @id
        all_dists = existing + downloads
        seen_ids = set()
        deduped = []
        for d in all_dists:
            did = d.get("@id") if isinstance(d, dict) else None
            if did and did in seen_ids:
                continue
            if did:
                seen_ids.add(did)
            deduped.append(d)

        result["schema:distribution"] = deduped

        if remaining:
            result["schema:hasPart"] = remaining
        else:
            del result["schema:hasPart"]

    return result


def _collect_ids(obj):
    """Recursively collect all @id values from a nested structure."""
    ids = set()
    if isinstance(obj, dict):
        if "@id" in obj:
            ids.add(obj["@id"])
        for v in obj.values():
            ids.update(_collect_ids(v))
    elif isinstance(obj, list):
        for item in obj:
            ids.update(_collect_ids(item))
    return ids


def _dedup_haspart_from_distribution(result):
    """Remove top-level hasPart items that already appear inside distribution.hasPart.

    When an RO-Crate is flattened, archive component files end up both in the root
    Dataset's hasPart and inside the DataDownload's hasPart. After framing back to
    CDIF, both locations get populated. This removes the duplicates from the top level.
    Also removes the subjectOf/catalog record entity from hasPart if present.
    """
    has_part = result.get("schema:hasPart")
    if not has_part:
        return result

    if isinstance(has_part, dict):
        has_part = [has_part]

    # Collect @ids of all items nested inside distribution hasPart
    dist_child_ids = set()
    distributions = result.get("schema:distribution", [])
    if isinstance(distributions, dict):
        distributions = [distributions]
    for dist in distributions:
        if isinstance(dist, dict):
            dist_parts = dist.get("schema:hasPart", [])
            if isinstance(dist_parts, dict):
                dist_parts = [dist_parts]
            for part in dist_parts:
                if isinstance(part, dict) and "@id" in part:
                    dist_child_ids.add(part["@id"])

    # Also collect @id of subjectOf (catalog record shouldn't be in hasPart)
    subject_of = result.get("schema:subjectOf")
    if isinstance(subject_of, dict) and "@id" in subject_of:
        dist_child_ids.add(subject_of["@id"])

    # Also exclude the DataDownload distribution itself from hasPart
    for dist in distributions:
        if isinstance(dist, dict) and "@id" in dist:
            dist_child_ids.add(dist["@id"])

    # Filter top-level hasPart
    filtered = []
    for item in has_part:
        item_id = item.get("@id") if isinstance(item, dict) else None
        if item_id and item_id in dist_child_ids:
            continue
        filtered.append(item)

    if filtered:
        result["schema:hasPart"] = filtered
    elif "schema:hasPart" in result:
        del result["schema:hasPart"]

    return result


def _create_subject_of(result, original_doc, profile):
    """Create schema:subjectOf from the RO-Crate metadata descriptor.

    The RO-Crate metadata descriptor (ro-crate-metadata.json) is a CreativeWork
    that describes the dataset. In CDIF, this maps to schema:subjectOf — a
    catalog record about the dataset.
    """
    # Don't overwrite if subjectOf already exists
    if result.get("schema:subjectOf"):
        return result

    # Get the dataset @id from the result
    dataset_id = result.get("@id", "./")

    # Look for metadata from the original RO-Crate document
    descriptor = None
    included_in_catalog = None

    if "@graph" in original_doc:
        graph = original_doc["@graph"]
        entity_index = _build_entity_index(graph)

        # Find the metadata descriptor
        descriptor = _find_metadata_descriptor(graph)

        # Find the root dataset to extract includedInDataCatalog
        root = _find_root_dataset(graph)
        if root:
            catalog_ref = root.get("includedInDataCatalog")
            if isinstance(catalog_ref, dict) and "@id" in catalog_ref:
                catalog_entity = entity_index.get(catalog_ref["@id"])
                if catalog_entity:
                    cat_url = catalog_entity.get("url", catalog_entity.get("schema:url", ""))
                    cat_name = catalog_entity.get("name", catalog_entity.get("schema:name", ""))
                    # Use URL as @id if available (avoids blank node IDs)
                    cat_id = cat_url or catalog_entity.get("@id", "")
                    included_in_catalog = {
                        "@id": cat_id,
                        "@type": "schema:DataCatalog",
                        "schema:name": cat_name,
                    }
                    if cat_url:
                        included_in_catalog["schema:url"] = cat_url
            elif isinstance(catalog_ref, dict):
                # Inline catalog object
                cat_url = catalog_ref.get("url", catalog_ref.get("schema:url", ""))
                cat_name = catalog_ref.get("name", catalog_ref.get("schema:name", ""))
                cat_id = cat_url or catalog_ref.get("@id", "")
                included_in_catalog = {
                    "@id": cat_id,
                    "@type": "schema:DataCatalog",
                    "schema:name": cat_name,
                }
                if cat_url:
                    included_in_catalog["schema:url"] = cat_url

    # Also check the compacted result for includedInDataCatalog
    if not included_in_catalog and result.get("schema:includedInDataCatalog"):
        cat = result["schema:includedInDataCatalog"]
        included_in_catalog = {
            "@id": cat.get("@id", ""),
            "@type": "schema:DataCatalog",
            "schema:name": cat.get("schema:name", ""),
        }
        if cat.get("schema:url"):
            included_in_catalog["schema:url"] = cat["schema:url"]
        # Remove from top-level (it belongs in subjectOf)
        del result["schema:includedInDataCatalog"]

    # Build the profile conformsTo URI
    profile_uri = CDIF_PROFILES.get(profile, CDIF_PROFILES["complete"])

    # Construct subjectOf
    subject_of = {
        "@type": ["schema:Dataset"],
        "schema:additionalType": ["dcat:CatalogRecord"],
        "@id": descriptor.get("@id", "ro-crate-metadata.json") if descriptor else "ro-crate-metadata.json",
        "schema:about": {"@id": dataset_id},
        "dcterms:conformsTo": [{"@id": profile_uri}],
    }

    if included_in_catalog:
        subject_of["schema:includedInDataCatalog"] = included_in_catalog

    result["schema:subjectOf"] = subject_of

    return result


def _normalize(obj):
    """Post-process: remove nulls, normalize @type to array, ensure array properties."""
    if isinstance(obj, list):
        return [_normalize(item) for item in obj if item is not None]

    if isinstance(obj, dict):
        result = {}
        for key, value in obj.items():
            if value is None:
                continue
            if key == "@context":
                result[key] = value
                continue

            new_value = _normalize(value)
            if new_value is None:
                continue

            # @type should always be an array
            if key == "@type" and isinstance(new_value, str):
                new_value = [new_value]

            # Wrap single values where schema expects arrays
            if key in ARRAY_PROPERTIES and not isinstance(new_value, list):
                new_value = [new_value]

            result[key] = new_value
        return result

    return obj


def _load_schema(schema_path):
    """Load a JSON Schema from a local path or URL."""
    if schema_path.startswith(("http://", "https://")):
        import urllib.request
        print(f"Fetching schema: {schema_path}", file=sys.stderr)
        with urllib.request.urlopen(schema_path) as resp:
            return json.loads(resp.read().decode("utf-8"))
    else:
        print(f"Loading schema: {schema_path}", file=sys.stderr)
        with open(schema_path, "r", encoding="utf-8") as f:
            return json.load(f)


def validate_against_schema(framed, schema_path):
    """Validate framed document against JSON Schema."""
    from jsonschema import Draft202012Validator

    schema = _load_schema(schema_path)

    validator = Draft202012Validator(schema)
    errors = list(validator.iter_errors(framed))

    return {"valid": len(errors) == 0, "errors": errors}


def main():
    parser = argparse.ArgumentParser(
        description="Convert RO-Crate JSON-LD to CDIF JSON-LD",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Convert RO-Crate to CDIF and save
  python ROCrateToCDIF.py my-rocrate.jsonld -o cdif-output.json

  # Convert with verbose output
  python ROCrateToCDIF.py my-rocrate.jsonld -o cdif-output.json -v

  # Convert and validate against CDIF Complete schema
  python ROCrateToCDIF.py my-rocrate.jsonld -o cdif-output.json -v --validate

  # Convert targeting CDIF Discovery profile
  python ROCrateToCDIF.py my-rocrate.jsonld -o cdif-output.json --profile discovery
""",
    )
    parser.add_argument("input", help="Input RO-Crate JSON-LD file")
    parser.add_argument("-o", "--output", help="Write CDIF output to file")
    parser.add_argument("-v", "--verbose", action="store_true", help="Show progress")
    parser.add_argument(
        "--profile",
        choices=["discovery", "complete"],
        default="complete",
        help="CDIF profile for conformsTo (default: complete)",
    )
    parser.add_argument(
        "--validate",
        action="store_true",
        help="Validate output against CDIF schema",
    )
    parser.add_argument(
        "--schema",
        default=None,
        help="Path to JSON Schema for validation (default: auto-select based on profile)",
    )

    args = parser.parse_args()

    try:
        if args.verbose:
            print(f"Loading: {args.input}", file=sys.stderr)
        with open(args.input, "r", encoding="utf-8") as f:
            doc = json.load(f)

        cdif = convert_rocrate_to_cdif(doc, profile=args.profile, verbose=args.verbose)

        if args.output:
            with open(args.output, "w", encoding="utf-8") as f:
                json.dump(cdif, f, indent=2)
            if args.verbose:
                print(f"CDIF output written to: {args.output}", file=sys.stderr)
        elif not args.validate:
            print(json.dumps(cdif, indent=2))

        if args.validate:
            if args.schema:
                schema_path = args.schema
            else:
                # Try local sibling validation repo first, fall back to GitHub
                validation_dir = SCRIPT_DIR / ".." / ".." / "validation"
                schema_filenames = {
                    "discovery": "CDIFDiscoverySchema.json",
                    "complete": "CDIFCompleteSchema.json",
                }
                filename = schema_filenames[args.profile]
                local_path = (validation_dir / filename).resolve()
                if local_path.exists():
                    schema_path = str(local_path)
                else:
                    schema_path = (
                        "https://raw.githubusercontent.com/"
                        "Cross-Domain-Interoperability-Framework/validation/"
                        f"refs/heads/main/{filename}"
                    )
                    if args.verbose:
                        print(f"Local schema not found, fetching from GitHub", file=sys.stderr)

            result = validate_against_schema(cdif, schema_path)
            if result["valid"]:
                print("Validation PASSED", file=sys.stderr)
            else:
                print("Validation FAILED", file=sys.stderr)
                for error in result["errors"]:
                    path = (
                        "/" + "/".join(str(p) for p in error.absolute_path)
                        if error.absolute_path
                        else "/"
                    )
                    print(f"  - {path}: {error.message}", file=sys.stderr)
                sys.exit(1)

        if args.verbose:
            print("Done!", file=sys.stderr)

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
