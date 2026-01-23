#!/usr/bin/env python3
"""
Script to extract condition.recommended_name.id and name from JSON array(s)
into a dictionary format. Supports multiple input files.
"""

import json
import sys
from pathlib import Path
import glob


def extract_conditions_from_file(input_file):
    """
    Extract condition recommended names from a single JSON file.
    
    Args:
        input_file: Path to input JSON file
    
    Returns:
        Dictionary mapping condition IDs to names
    """
    conditions_dict = {}
    
    try:
        with open(input_file, 'r') as f:
            data = json.load(f)
        
        # Extract conditions into dictionary
        for item in data:
            if 'condition' in item and 'recommended_name' in item['condition']:
                rec_name = item['condition']['recommended_name']
                if 'id' in rec_name and 'name' in rec_name:
                    condition_id = rec_name['id']
                    condition_name = rec_name['name']
                    conditions_dict[condition_id] = condition_name
        
        print(f"Processed {input_file}: found {len(conditions_dict)} conditions")
    
    except Exception as e:
        print(f"Error processing {input_file}: {e}", file=sys.stderr)
    
    return conditions_dict


def extract_conditions_from_multiple(input_files, output_file=None):
    """
    Extract condition recommended names from multiple JSON files.
    
    Args:
        input_files: List of paths to input JSON files (can include wildcards)
        output_file: Optional path to output JSON file
    
    Returns:
        Dictionary mapping condition IDs to names (merged from all files)
    """
    # Expand wildcards and collect all files
    all_files = []
    for pattern in input_files:
        matched_files = glob.glob(pattern)
        if matched_files:
            all_files.extend(matched_files)
        else:
            # If no wildcard match, check if it's a direct file path
            if Path(pattern).exists():
                all_files.append(pattern)
            else:
                print(f"Warning: No files matched pattern '{pattern}'", file=sys.stderr)
    
    if not all_files:
        print("Error: No valid input files found")
        sys.exit(1)
    
    # Merge conditions from all files
    merged_conditions = {}
    
    for input_file in all_files:
        file_conditions = extract_conditions_from_file(input_file)
        merged_conditions.update(file_conditions)
    
    print(f"\nTotal unique conditions: {len(merged_conditions)}")
    
    # Output results
    if output_file:
        with open(output_file, 'w') as f:
            json.dump(merged_conditions, f, indent=2)
        print(f"Results written to {output_file}")
    else:
        print(json.dumps(merged_conditions, indent=2))
    
    return merged_conditions


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python extract_conditions.py <input_file(s)> [output_file]")
        print("\nExamples:")
        print("  Single file:    python extract_conditions.py data.json output.json")
        print("  Multiple files: python extract_conditions.py file1.json file2.json output.json")
        print("  Wildcard:       python extract_conditions.py data/*.json output.json")
        print("  Print to console: python extract_conditions.py data/*.json")
        sys.exit(1)
    
    # Check if last argument is the output file (doesn't end with .json or exists as input)
    args = sys.argv[1:]
    
    # If last arg doesn't look like a wildcard and would be new, treat it as output
    if len(args) > 1 and not any(c in args[-1] for c in ['*', '?', '[']):
        # Check if it exists as a file (then it's an input) or would be created (output)
        if Path(args[-1]).exists() and Path(args[-1]).suffix == '.json':
            # It exists, treat all as inputs
            input_files = args
            output_file = None
        else:
            # Likely an output file
            input_files = args[:-1]
            output_file = args[-1]
    else:
        input_files = args
        output_file = None
    
    extract_conditions_from_multiple(input_files, output_file)
