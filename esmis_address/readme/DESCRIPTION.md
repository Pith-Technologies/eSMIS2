# eSMIS Address

Provides a structured address model (`esmis.address`) linked to Odoo contacts (`res.partner`).

## Features

- Multiple typed addresses per contact (permanent, mailing, current residence, emergency contact)
- One address per type per contact enforced via a unique constraint
- Primary address flag with automatic management — setting a new primary unflags the previous one
- Computed `address_text` field concatenating non-empty address components
- `primary_address_text` computed field on `res.partner` for quick access to the primary address
- "Addresses" tab injected into the standard partner form

## Address Types

Address types are managed via the `urn:esmis:address-type` vocabulary seeded at install:

| Code       | Display                   |
| ---------- | ------------------------- |
| permanent  | Permanent Address         |
| mailing    | Mailing Address           |
| residency  | Current Residence         |
| emergency  | Emergency Contact Address |

## Extensibility

Country-specific modules (e.g. `esmis_ph`) may extend `esmis.address` with locale-specific
geographic fields and override `_compute_address_text` to produce locale-appropriate formatting.
