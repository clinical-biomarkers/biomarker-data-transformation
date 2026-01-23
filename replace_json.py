import json
import os
from pathlib import Path

def replace_assessed_entity_type(data, old_string, new_string):
    """
    Recursively search and replace string in assessed_entity_type fields.
    Returns True if any replacement was made.
    """
    modified = False
    
    if isinstance(data, dict):
        # Check if this dict has biomarker_component
        if 'biomarker_component' in data:
            biomarker_component = data['biomarker_component']
            
            # If it's a list, iterate through it
            if isinstance(biomarker_component, list):
                for component in biomarker_component:
                    if isinstance(component, dict) and 'assessed_entity_type' in component:
                        if component['assessed_entity_type'] == old_string:
                            component['assessed_entity_type'] = new_string
                            modified = True
                            print(f"  ✓ Replaced '{old_string}' with '{new_string}'")
        
        # Recurse through all dict values
        for value in data.values():
            if replace_assessed_entity_type(value, old_string, new_string):
                modified = True
    
    elif isinstance(data, list):
        # Recurse through list items
        for item in data:
            if replace_assessed_entity_type(item, old_string, new_string):
                modified = True
    
    return modified

def process_json_files(directory, old_string, new_string, backup=True):
    """
    Process all JSON files in a directory and replace the string.
    
    Args:
        directory: Path to directory containing JSON files
        old_string: String to search for
        new_string: String to replace with
        backup: If True, creates .bak files before modifying
    """
    directory = Path(directory)
    
    if not directory.exists():
        print(f"Error: Directory '{directory}' does not exist")
        return
    
    json_files = list(directory.glob('*.json'))
    
    if not json_files:
        print(f"No JSON files found in '{directory}'")
        return
    
    print(f"Found {len(json_files)} JSON file(s)")
    print(f"Searching for '{old_string}' and replacing with '{new_string}'...\n")
    
    modified_count = 0
    error_count = 0
    
    for json_file in json_files:
        print(f"Processing: {json_file.name}")
        
        try:
            # Read the JSON file
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Replace the string
            modified = replace_assessed_entity_type(data, old_string, new_string)
            
            if modified:
                # Create backup if requested
                if backup:
                    backup_file = json_file.with_suffix('.json.bak')
                    with open(backup_file, 'w', encoding='utf-8') as f:
                        json.dump(json.load(open(json_file, 'r')), f, indent=2)
                    print(f"  Backup created: {backup_file.name}")
                
                # Write the modified data back
                with open(json_file, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                
                modified_count += 1
                print(f"  ✓ File updated\n")
            else:
                print(f"  - No matches found\n")
        
        except json.JSONDecodeError as e:
            print(f"  ✗ Error: Invalid JSON - {e}\n")
            error_count += 1
        except Exception as e:
            print(f"  ✗ Error: {e}\n")
            error_count += 1
    
    print("=" * 50)
    print(f"Summary:")
    print(f"  Files processed: {len(json_files)}")
    print(f"  Files modified: {modified_count}")
    print(f"  Errors: {error_count}")

if __name__ == "__main__":
    # Configuration
    DIRECTORY = "/data/shared/biomarkerdb/generated/datamodel/merged/current/merged_json_updated"  # Change this to your directory path
    OLD_STRING = "Protein"         # String to search for
    NEW_STRING = "protein"      # String to replace with
    CREATE_BACKUP = False        # Set to False to skip backup creation
    
    process_json_files(DIRECTORY, OLD_STRING, NEW_STRING, backup=CREATE_BACKUP)
