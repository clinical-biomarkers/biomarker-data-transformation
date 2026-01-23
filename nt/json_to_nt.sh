#!/bin/bash

# Navigate to format-converter and activate virtual environment
cd /data/shared/repos/format-converter
source env/bin/activate

# Path variables
json_filepath="/data/shared/biomarkerdb/generated/datamodel/existing_data"
nt_filepath="/data/shared/biomarkerdb/generated/nt_2"

# Convert json files to nt
for filename in "$json_filepath"/*.json; do
    file_no_ext="$(basename "$filename" .json)"
    out_file="$nt_filepath/${file_no_ext}.nt"

    echo "Converting $filename to $out_file ..."
    python main.py "$filename" "$out_file"
    echo "Done!"
done
