#!/bin/bash
sed -i 's/CL_/CO:/g' mw_loinc_biomarkers.tsv

# Also replace LOINC_ and DOID_
