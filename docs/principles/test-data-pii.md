# Test Data and PII

Rules for handling personally identifiable information in test data, demo data, and development
environments. These rules implement the patterns from [PII Handling Best Practices](../research/pii-handling-best-practices.md)
Section 8 and support compliance with RA 10173 (Data Privacy Act).

---

## 1. General Rule

Never use real student data in test or demo environments. All PII in test fixtures must be
synthetic. This applies to unit tests, integration tests, demo data modules, and any seed data
loaded into development or staging databases.

---

## 2. Synthetic Data Generation

Use the Python `faker` library with the `fil_PH` locale for Philippine-realistic fake data:

```python
from faker import Faker

fake = Faker('fil_PH')

name = fake.name()                    # "Maria Santos"
address = fake.address()              # Philippine-format address
phone = fake.phone_number()           # "+63 9XX XXX XXXX"
email = fake.email()                  # "maria.santos@example.com"
```

For fields without `faker` support, use obviously fake but structurally valid data:

| Field | Fake Pattern |
|-------|-------------|
| PhilSys PSN | `"0000-0000-0001"` through `"0000-0000-9999"` |
| LRN | `"000000000001"` through `"000000009999"` |
| Student number | `"TEST-2025-00001"` |
| PWD ID | `"TEST-PWD-00001"` |

The `"0000-"` prefix for PhilSys and `"000000"` prefix for LRN are reserved for synthetic data.
Any real PSN or LRN will never begin with these prefixes, making contamination detectable.

For complete records, generate all required relations in one pass to avoid referential integrity
failures. Use a deterministic seed (`Faker.seed(42)`) for reproducible test runs.

---

## 3. Grade Test Data

Grades are Sensitive Personal Information (SPI). Even test grades must follow proper access
patterns — do not bypass ACL checks with `sudo()` in grade-related tests unless testing the
restriction itself.

Use standard Philippine grading scale values: `1.00`, `1.25`, `1.50`, `1.75`, `2.00`, `2.25`,
`2.50`, `2.75`, `3.00`, `5.00`.

Test GWA computation with known datasets where expected values are pre-calculated and hardcoded
in the test assertion. Do not compute the expected GWA dynamically in the test — that replicates
the bug instead of catching it.

---

## 4. Encrypted Field Testing

Test fixtures must go through the encryption pipeline. Do not write raw plaintext directly to
encrypted columns or bypass the ORM field compute/inverse pattern.

Tests must cover:

- **Round-trip**: encrypt a value, read it back, assert equality with the original.
- **Blind index search**: write a record, search by the encrypted field, assert the record is
  found.
- **Decryption correctness**: decrypted value matches the value that was written.
- **Key rotation**: encrypt with key A, rotate to key B, read the record, assert the value is
  still correct.

---

## 5. Demo Data Guidelines

Demo data modules follow these rules:

- Use `with_context(tracking_disable=True)` when creating demo records to suppress chatter
  notifications.
- Demo student names must be obviously fake: `"Demo Student Alpha"`, `"Demo Student Beta"`, etc.
- Demo national IDs use reserved prefixes: `"0000-"` for PhilSys, `"000000"` for LRN.
- Demo records must be complete — all required relations (enrollment, consent records, program
  assignment) must exist. Incomplete demo data breaks other tests that assume a clean state.
- Demo data should include variety to exercise UI rendering: different programs, year levels,
  academic standings, financial aid types, PWD flags, and solo parent flags.

---

## 6. Staging Environment

Staging databases must be masked copies of production, never raw copies.

The masking pipeline replaces all Tier 2 and Tier 3 fields with synthetic equivalents before the
database reaches staging:

| Field Type | Masking Strategy |
|-----------|-----------------|
| Names | Replace with `faker` names; preserve gender consistency |
| Addresses | Replace with `faker` addresses; preserve city distribution |
| Phone numbers | Replace digits; preserve format |
| Email | Replace with `{hash}@example.edu.ph` |
| National IDs | Replace with `"0000-"`-prefixed synthetic IDs |
| Dates of birth | Shift by a random per-record offset (preserves age distribution) |
| Free text / notes | Replace with lorem ipsum |
| Attachment files | Replace with placeholder files of the same size |

The masking pipeline must preserve referential integrity: the same `student_id` must always map
to the same fake name, so foreign key joins remain consistent after masking.

Never copy production encryption keys to staging. Staging must use its own key set so that a
staging compromise cannot decrypt production backups.

---

## 7. CI/CD Safeguards

- **Pre-commit hook**: reject test files containing strings that match real Philippine national
  ID patterns. Patterns that do not start with the reserved prefix `"0000"` (PSN) or `"000000"`
  (LRN) are flagged. Regex: `/\d{4}-\d{4}-\d{4}/` (PSN) and `/\d{12}/` (LRN) — any match not
  starting with the reserved prefix fails the commit.
- **No PII in git history**: if PII is accidentally committed, remove it with `git-filter-repo`
  or BFG before the branch is merged. Do not leave the data in history with a revert commit.
- **CI test runners** must not have credentials to access production databases. Docker images
  used in CI must not contain any PII-derived data.

---

## 8. Developer Access

Developers must not have direct access to production databases containing student PII.

If a production bug cannot be reproduced with synthetic data:

1. The DPO extracts a minimal, anonymized reproduction case.
2. The developer works with the anonymized data only.
3. The DPO verifies the anonymized data does not leak the original PII before sharing.

Emergency production access (e.g., a live data corruption incident) requires DPO approval and
must be logged in the audit system. Access is time-limited and revoked immediately after the
incident is resolved.

---

## Related Documents

- [PII Handling Best Practices](../research/pii-handling-best-practices.md) — source research,
  Section 8
- [Regulatory Compliance](regulatory-compliance.md) — RA 10173 obligations
- [Audit & Compliance](audit-compliance.md) — audit trail requirements
- [Error Handling & Logging](error-handling.md) — no PII in log messages
- [Testing](testing.md) — coverage targets and test patterns
