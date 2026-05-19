# biomarker-extraction
Raw data extraction and transformation scripts

---

## Downloads

### Permissible Values via caDSR API (Recommended)

The caDSR API provides programmatic access to permissible values without requiring a browser session. Use the `/DataElement/{publicId}` endpoint with an explicit `Accept: application/json` header — without it, the server returns HTML.

```bash
curl -s -H "Accept: application/json" \
  "https://cadsrapi.cancer.gov/rad/NCIAPI.v1_0:NciApiRad/DataElement/5473?version=14" \
  -o de_5473.json
```

Permissible values are nested under `DataElement.ValueDomain.PermissibleValues` in the response. The full response also includes `ClassificationSchemes`, `AlternateNames`, and `ReferenceDocuments`, which appear before and after the permissible values in the JSON.

To extract and count permissible values:

```bash
jq '{count: (.DataElement.ValueDomain.PermissibleValues | length), first: .DataElement.ValueDomain.PermissibleValues[0]}' de_5473.json
```

### Permissible Values via Browser Export (Alternative)

The caDSR OneData UI at `cadsr.cancer.gov/onedata` offers an "Export to Excel" option under each data element's Permissible Values tab. The downloaded file (`od_001.xls`) contains the following columns:

| Column | Description |
|---|---|
| Permissible Value | The actual value |
| VM Long Name | Value Meaning long name |
| VM Public ID | Value Meaning public identifier |
| Concept Codes | Associated NCI Thesaurus concept codes |
| VM Definition | Value Meaning definition |
| Begin Date | Date the value became active |
| End Date | Date the value was retired (if applicable) |

The export requires an active browser session and cannot be replicated with `wget` or `curl` directly, as the download URLs contain short-lived session tokens.

1. Go to: https://cadsr.cancer.gov/onedata/dmdirect/NIH/NCI/CO/CDEDD?filter=CDEDD.ITEM_ID=5473%20and%20ver_nr=14
2. Click the notepad icon under "View" (2nd column)
3. Select "6. Permissible Values"
4. For bulk download go to "Delivery Options" and select "Export to Excel"

---

