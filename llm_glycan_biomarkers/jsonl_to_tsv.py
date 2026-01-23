#!/usr/bin/env python3
"""
Convert JSONL biomarker data to TSV format.
"""

import json
import csv
import sys
from pathlib import Path


def should_skip_record(record):
    """Check if a record should be skipped based on criteria."""
    # Check screening decision
    if record.get('screening', {}).get('decision') != 'RELEVANT':
        return True
    
    # Check relations exist
    relations = record.get('relations', [])
    if not relations:
        return True
    
    return False


def is_valid_relation(relation):
    """Check if a relation has all required non-null fields."""
    return (relation.get('direction') is not None and
            relation.get('protein_name') is not None and
            relation.get('glycan_name') is not None and
            relation.get('protein_id') is not None and
            relation.get('disease_id') is not None and
            relation.get('specimen', {}).get('mapped_id') is not None)


def format_biomarker(direction, protein_name, glycan_name):
    """Format biomarker field."""
    match direction:
        case "increased" | "decreased":
            return f"{direction} level of {glycan_name} on {protein_name}"
        case "absent":
            return f"absence of {glycan_name} on {protein_name}"
        case "novel_presence":
            return f"presence of {glycan_name} on {protein_name}"
        case "associated":
            return f"{glycan_name} {direction} with {protein_name}"
        case _:
            # Default case for any other direction value
            return f"{direction} level of {glycan_name} on {protein_name}"

def format_evidence(evidence_sentences):
    """Concatenate evidence sentences."""
    if not evidence_sentences:
        return ""
    return " ".join([sent.get('sentence', '') for sent in evidence_sentences])


def process_jsonl_to_tsv(input_file, output_file):
    """Convert JSONL file to TSV format."""
    
    # TSV headers
    headers = [
        'biomarker_id',
        'biomarker',
        'assessed_biomarker_entity',
        'assessed_biomarker_entity_id',
        'assessed_entity_type',
        'condition',
        'condition_id',
        'exposure_agent',
        'exposure_agent_id',
        'best_biomarker_role',
        'specimen',
        'specimen_id',
        'loinc_code',
        'evidence_source',
        'evidence',
        'tag'
    ]
    
    rows = []
    biomarker_id = 1
    
    # Read JSONL file
    with open(input_file, 'r', encoding='utf-8') as f:
        for line in f:
            if not line.strip():
                continue
            
            try:
                record = json.loads(line)
            except json.JSONDecodeError as e:
                print(f"Error parsing JSON: {e}", file=sys.stderr)
                continue
            
            # Skip if doesn't meet criteria
            if should_skip_record(record):
                continue
            
            pmid = record.get('pmid', '')
            
            # Process each relation
            for relation in record.get('relations', []):
                # Skip invalid relations
                if not is_valid_relation(relation):
                    continue
                
                # Extract fields
                direction = relation['direction']
                protein_name = relation['protein_name']
                glycan_name = relation['glycan_name']
                protein_id = relation['protein_id']
                disease_name = relation.get('disease_name', '')
                disease_id = relation['disease_id']
                specimen_mapped_name = relation['specimen'].get('mapped_name', '')
                specimen_mapped_id = relation['specimen']['mapped_id']
                evidence_sentences = relation.get('evidence_sentences', [])
                
                # Build row
                row = {
                    'biomarker_id': str(biomarker_id),
                    'biomarker': format_biomarker(direction, protein_name, glycan_name),
                    'assessed_biomarker_entity': protein_name,
                    'assessed_biomarker_entity_id': f"UPKB:{protein_id}",
                    'assessed_entity_type': 'protein',
                    'condition': disease_name,
                    'condition_id': disease_id,
                    'exposure_agent': '',
                    'exposure_agent_id': '',
                    'best_biomarker_role': '',
                    'specimen': specimen_mapped_name.lower(),
                    'specimen_id': specimen_mapped_id,
                    'loinc_code': '',
                    'evidence_source': f"PubMed:{pmid}" if pmid else '',
                    'evidence': format_evidence(evidence_sentences),
                    'tag': 'assessed_biomarker_entity_id;assessed_biomarker_entiy;assessed_entity_type;biomarker;condition;specimen'
                }
                
                rows.append(row)
                biomarker_id += 1
    
    # Write TSV file
    with open(output_file, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=headers, delimiter='\t')
        writer.writeheader()
        writer.writerows(rows)
    
    print(f"Processed {biomarker_id - 1} biomarker records")
    print(f"Output written to: {output_file}")


def main():
    if len(sys.argv) != 3:
        print("Usage: python jsonl_to_tsv.py <input.jsonl> <output.tsv>")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    
    if not Path(input_file).exists():
        print(f"Error: Input file '{input_file}' not found")
        sys.exit(1)
    
    process_jsonl_to_tsv(input_file, output_file)


if __name__ == '__main__':
    main()
