#!/usr/bin/env python3
"""
Extract biomarker data from CIViC JSON format and convert to TSV.
"""

import json
import re
import sys
from typing import Dict, List, Any

def extract_biomarker_data(record: Dict[str, Any]) -> List[Dict[str, str]]:
    """Extract biomarker information from a single JSON record."""
    rows = []
    
    # Extract base information
    biomarker_name = record.get('name', '')
    feature_names = record.get('feature_names', biomarker_name)
    
    # Get assessed entity information
    gene_identifiers = record.get('gene_identifiers', [])
    if gene_identifiers:
        assessed_entity = gene_identifiers[0].get('symbol', '')
        assessed_entity_id = f"NCBI:{gene_identifiers[0].get('entrez_id', '')}"
    else:
        assessed_entity = record.get('geneSymbol', '')
        assessed_entity_id = f"NCBI:{record.get('entrez_id', '')}" if record.get('entrez_id') else ''
    
    assessed_entity_type = 'gene'
    
    # Get association data
    association = record.get('association', {})
    
    # Get condition information
    phenotypes = association.get('phenotypes', [])
    condition = ''
    condition_id = ''
    if phenotypes:
        condition = phenotypes[0].get('term', '').replace(' (disease)', '')
        mondo_id = phenotypes[0].get('id', '')
        if mondo_id:
            condition_id = mondo_id
    
    # Get evidence items
    evidence_items = association.get('evidence', [])
    
    # Get CIViC source
    source_link = association.get('source_link', '')
    civic_id = ''
    if 'civic' in record:
        civic_evidence = record['civic'].get('evidence_items', [])
        if civic_evidence:
            civic_id = f"CIViC:{civic_evidence[0].get('id', '')}"
    
    # Get variant name for biomarker description
    variant_name = association.get('variant_name', '')

    # Build biomarker description
    biomarker_description = f"{assessed_entity} {variant_name}" if variant_name else feature_names

    # If biomarker looks like 'GENE A123B' (amino acid substitution), append 'sequence variation'
    if re.match(r"^[A-Z]+\s+[A-Z]\d+[A-Z]$", biomarker_description):
        biomarker_description += " sequence variation"

    # Determine biomarker role from response type
    response_type = association.get('response_type', '')
    role_mapping = {
        'resistant': 'risk',
        'sensitive': 'prognostic',
        'response': 'prognostic'
    }
    best_biomarker_role = role_mapping.get(response_type, 'risk' if response_type else '')
    
    # Process each evidence item
    for evidence_item in evidence_items:
        evidence_description = evidence_item.get('description', '')
        evidence_type = evidence_item.get('evidenceType', {})
        
        # Get publication URLs
        info = evidence_item.get('info', {})
        publications = info.get('publications', [])
        evidence_source = publications[0] if publications else ''
       
        # Convert PubMed URL to PubMed:<id> format
        if isinstance(evidence_source, str):
            match = re.search(r'pubmed/(\d+)', evidence_source)
            if match:
                evidence_source = f"PubMed:{match.group(1)}"
 
        # Create row for PubMed evidence
        if evidence_source:
            row = {
                'biomarker_id': '',
                'biomarker': biomarker_description,
                'assessed_biomarker_entity': assessed_entity,
                'assessed_biomarker_entity_id': assessed_entity_id,
                'assessed_entity_type': assessed_entity_type,
                'condition': condition,
                'condition_id': condition_id,
                'exposure_agent': '',
                'exposure_agent_id': '',
                'best_biomarker_role': best_biomarker_role,
                'specimen': '',
                'specimen_id': '',
                'loinc_code': '',
                'evidence_source': evidence_source,
                'evidence': evidence_description,
                'tag': ''
            }
            if not condition_id.startswith(("DOID:", "MONDO:")):
                continue
            rows.append(row)
        
        # Create row for CIViC evidence if available
        if civic_id:
            row = {
                'biomarker_id': '',
                'biomarker': biomarker_description,
                'assessed_biomarker_entity': assessed_entity,
                'assessed_biomarker_entity_id': assessed_entity_id,
                'assessed_entity_type': assessed_entity_type,
                'condition': condition,
                'condition_id': condition_id,
                'exposure_agent': '',
                'exposure_agent_id': '',
                'best_biomarker_role': best_biomarker_role,
                'specimen': '',
                'specimen_id': '',
                'loinc_code': '',
                'evidence_source': civic_id,
                'evidence': '',
                'tag': ''
            }
            if not condition_id.startswith(("DOID:", "MONDO:")):
                continue
            rows.append(row)
    
    # If no evidence items, create at least one row
    if not rows:
        row = {
            'biomarker_id': '',
            'biomarker': biomarker_description,
            'assessed_biomarker_entity': assessed_entity,
            'assessed_biomarker_entity_id': assessed_entity_id,
            'assessed_entity_type': assessed_entity_type,
            'condition': condition,
            'condition_id': condition_id,
            'exposure_agent': '',
            'exposure_agent_id': '',
            'best_biomarker_role': best_biomarker_role,
            'specimen': '',
            'specimen_id': '',
            'loinc_code': '',
            'evidence_source': civic_id if civic_id else '',
            'evidence': association.get('description', ''),
            'tag': ''
        }
        if not condition_id.startswith(("DOID:", "MONDO:")):
            return rows
        rows.append(row)
    
    return rows

def process_json_file(input_file: str, output_file: str):
    """Process the JSON file and write TSV output."""
    
    # Define column headers
    headers = [
        'biomarker_id', 'biomarker', 'assessed_biomarker_entity', 
        'assessed_biomarker_entity_id', 'assessed_entity_type', 
        'condition', 'condition_id', 'exposure_agent', 'exposure_agent_id',
        'best_biomarker_role', 'specimen', 'specimen_id', 'loinc_code',
        'evidence_source', 'evidence', 'tag'
    ]
    
    all_rows = []
    
    # Read and process JSON file
    with open(input_file, 'r') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            
            try:
                record = json.loads(line)
                rows = extract_biomarker_data(record)
                all_rows.extend(rows)
            except json.JSONDecodeError as e:
                print(f"Error parsing JSON line: {e}", file=sys.stderr)
                continue
    
    # Write TSV output
    with open(output_file, 'w') as f:
        # Write header
        f.write('\t'.join(headers) + '\n')
        
        # Write data rows with sequential biomarker_id
        for idx, row in enumerate(all_rows, start=1):
            row['biomarker_id'] = str(idx)
            values = [str(row.get(header, '') or '') for header in headers]
            f.write('\t'.join(values) + '\n')
    
    print(f"Processed {len(all_rows)} rows and wrote to {output_file}")

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: python script.py <input_json_file> <output_tsv_file>")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    
    process_json_file(input_file, output_file)
