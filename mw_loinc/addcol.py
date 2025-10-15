import csv

with open('mw_loinc_biomarkers.tsv', 'r', encoding='latin-1') as infile, \
     open('mw_loinc_biomarkers_with_tag.tsv', 'w', encoding='utf-8') as outfile:
    
    reader = csv.reader(infile, delimiter='\t')
    writer = csv.writer(outfile, delimiter='\t', lineterminator='\n')
    
    for i, row in enumerate(reader):
        if i == 0:
            row.append('tag')
        else:
            row.append('')
        writer.writerow(row)
