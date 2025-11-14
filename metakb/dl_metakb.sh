#!/bin/bash

cd /data/shared/biomarkerdb/downloads/raw/current

file_ids=(
  "1DpamQhQSNadKazzbFYcG5CwvVBlzh9eI"
  "1cyCo4ymeyXbNVaUH9OtNBR2LsbQsJW2t"
  "1IPhdgigvcq_nASm_hIK7qEKoCwVLnysc"
  "15wKGoyk1aMWEtl4lZlOAgF_PzldsuAba"
  "1BE4_MPHuF6FdWNak_PRV8gB9ZTqI2LrR"
  "14eqcEZ0cUM271yATc_ZIC5lriQirbf5Z"
  "1AGwDG90XZrbcqO5uG6NemH3q9-sswivJ"
)

for id in "${file_ids[@]}"; do
  gdown "https://drive.google.com/uc?id=$id"
done
