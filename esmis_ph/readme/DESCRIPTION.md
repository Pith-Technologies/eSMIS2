# eSMIS — Philippines

Philippine-specific extensions for the eSMIS Student Management Information System.

## What this module adds

### Philippine Student Fields

Extends `res.partner` (student records) with fields required for Philippine HEI compliance:

- **Middle Name Before Marriage** — maiden surname used as middle name after marriage per PH naming convention
- **Name Suffixes** (Many2many) — Jr., Sr., II, III, IV, PhD, MD, EdD, LLB, CPA, RN
- **Ethnicity** — ethno-linguistic group per CHED HEMIS classification
- **Religion** — religious affiliation per PSA census classifications
- **Solo Parent** — RA 8972/11861 status flag for scholarship eligibility
- **4Ps Beneficiary** — Pantawid Pamilyang Pilipino Program flag

### Philippine Name Format

Overrides the student display name to use the standard Philippine format:

```
LAST NAME, FIRST NAME M. SUFFIX
```

Where `M.` is the middle initial derived from the maiden name (if set) or middle name.

### PSGC Geographic Hierarchy

Implements the Philippine Standard Geographic Code (PSGC) hierarchy:

| Model | Description |
|-------|-------------|
| `esmis.psgc.region` | 17 administrative regions |
| `esmis.psgc.province` | ~82 provinces and HUCs |
| `esmis.psgc.city.municipality` | ~1,600 cities and municipalities |
| `esmis.psgc.barangay` | ~42,000 barangays (bulk-loaded via hook) |

### Philippine Address Format

Extends `esmis.address` with PSGC cascading dropdowns (region → province → city/municipality → barangay). When a region is selected, addresses are formatted as:

```
Street 1, Street 2, Barangay, City/Municipality, Province, Region, ZIP
```

### Vocabulary Seed Data

| Namespace | Contents |
|-----------|----------|
| `urn:esmis:name-suffix` | 11 name suffixes |
| `urn:esmis:ethnicity-ph` | 14 ethno-linguistic groups |
| `urn:esmis:religion-ph` | 14 religious affiliations |
| `urn:esmis:identifier-type-ph` | 8 PH government ID types |

## Dependencies

- `esmis_student` — student partner model and display name hook
- `esmis_address` — base address model

## Regulatory Compliance

- **RA 10173** (Data Privacy Act) — ethnicity and religion classified as PII Tier 1
- **RA 8972/11861** (Solo Parent Act) — is_solo_parent flag
- **RA 7277/10754** (PWD Rights) — addressed in esmis_student
- **CHED HEMIS** — ethnicity and religion fields align with HEMIS demographic reporting
