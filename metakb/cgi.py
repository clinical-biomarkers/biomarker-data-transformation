#!/usr/bin/env python3
"""
Maps CGI JSON entries to the biomarker data model structure.

Usage: python cgi_mapper.py cgi.vr.json output.json
"""

import json
import sys

def extract_pmid_from_url(url):
    """Extract PMID from PubMed URL."""
    if 'pubmed' in url:
        parts = url.rstrip('/').split('/')
        return parts[-1]
    return None

def map_cgi_to_data_model(cgi_entry, biomarker_id):
    """
    Maps a single CGI JSON entry to the nested data model structure.
    
    Parameters
    ----------
    cgi_entry : dict
        Single CGI JSON entry
    biomarker_id : str
        Sequential ID for the biomarker
    
    Returns
    -------
    dict
        Mapped data model structure with nested biomarker_component
    """
    
    # Extract key information with safe access
    features_list = cgi_entry.get('features', [])
    features = features_list[0] if features_list else {}
    
    gene_identifiers_list = cgi_entry.get('gene_identifiers', [])
    gene_identifiers = gene_identifiers_list[0] if gene_identifiers_list else {}
    
    association = cgi_entry.get('association', {})
    
    phenotypes_list = association.get('phenotypes', [])
    phenotypes = phenotypes_list[0] if phenotypes_list else {}
    
    # Extract and format evidence source
    evidence_source_str = association.get('publication_url', '')
    evidence_database = ""
    evidence_id = ""
    evidence_url = ""
    
    if evidence_source_str:
        pmid = extract_pmid_from_url(evidence_source_str)
        if pmid:
            evidence_database = "PubMed"
            evidence_id = pmid
            evidence_url = f"https://pubmed.ncbi.nlm.nih.gov/{pmid}"
        else:
            # If we can't parse it, use the original URL
            evidence_url = evidence_source_str
    
    # Build the biomarker component (nested structure)
    biomarker_component = {
        "biomarker": features.get('name'),  # e.g., "ABL1:T315I"
        
        "assessed_biomarker_entity": {
            "recommended_name": gene_identifiers.get('symbol'),  # e.g., "ABL1"
            "synonyms": []  # Add empty synonyms array as required by the schema
        },
        
        "assessed_biomarker_entity_id": f"NCBI:{gene_identifiers.get('entrez_id')}" if gene_identifiers.get('entrez_id') else "",
        
        "assessed_entity_type": "gene",
        
        "specimen": [],  # Empty array as per your requirements
        
        "evidence_source": [
            {
                "database": evidence_database,
                "id": evidence_id,
                "url": evidence_url,
                "evidence_list": [],
                "tags": [
                    {"tag": "biomarker"},
                    {"tag": "assessed_biomarker_entity_id"},
                    {"tag": "assessed_biomarker_entity"}
                ]
            }
        ] if evidence_url else []
    }
    
    # Build the top-level data model
    data_model = {
        "biomarker_id": biomarker_id,
        
        "biomarker_component": [biomarker_component],
        
        "condition": {
            "id": phenotypes.get('id', ''),  # e.g., "MONDO:0011996"
            "recommended_name": {
                "name": phenotypes.get('term', ''),  # e.g., "chronic myelogenous leukemia..."
                "description": phenotypes.get('description', ''),
                "id": phenotypes.get('id', ''),
                "resource": phenotypes.get('source', '').split('/')[-2] if phenotypes.get('source') else "",
                "url": phenotypes.get('source', '')
            },
            "synonyms": []  # Add empty synonyms array
        } if phenotypes.get('term') else None,
        
        "exposure_agent": None,
        
        "best_biomarker_role": [],
        
        "citation": [],  # Add empty citation array
        
        "evidence_source": [
            {
                "database": evidence_database,
                "id": evidence_id,
                "url": evidence_url,
                "evidence_list": [],
                "tags": [
                    {"tag": "condition"}
                ]
            }
        ] if evidence_url else []
    }
    
    # Remove None values
    if data_model["condition"] is None:
        del data_model["condition"]
    if data_model["exposure_agent"] is None:
        del data_model["exposure_agent"]
    
    return data_model


def process_cgi_file(input_file, output_file):
    """
    Process CGI JSON file and create mapped data model output.
    
    Parameters
    ----------
    input_file : str
        Path to input CGI JSON file
    output_file : str
        Path to output JSON file
    """
    
    # Read input file
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read().strip()
        
        # Handle different JSON formats
        if content.startswith('['):
            data = json.loads(content)
        else:
            # Try newline-delimited JSON
            data = []
            for line in content.split('\n'):
                if line.strip():
                    try:
                        data.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue
    
    # Map each entry
    mapped_data = []
    skipped_count = 0
    for idx, entry in enumerate(data, start=1):
        try:
            biomarker_id = str(idx)
            mapped_entry = map_cgi_to_data_model(entry, biomarker_id)
            mapped_data.append(mapped_entry)
        except Exception as e:
            print(f"Warning: Failed to process entry {idx}: {e}")
            skipped_count += 1
            continue
    
    # Write output
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(mapped_data, f, indent=2)
    
    print(f"Successfully processed {len(mapped_data)} entries")
    if skipped_count > 0:
        print(f"Skipped {skipped_count} entries due to errors")
    print(f"Output written to: {output_file}")


def main():
    if len(sys.argv) < 3:
        print("Usage: python cgi_mapper.py cgi.vr.json output.json")
        print("\nMaps CGI JSON entries to biomarker data model structure.")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    
    process_cgi_file(input_file, output_file)


if __name__ == '__main__':
    main()
