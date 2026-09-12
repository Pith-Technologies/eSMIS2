# Testing Principles

Quality requirements for Odoo 19 module development.

## Coverage Target

**85% for every module.** One number rather than a tier table: the tiers were
never implemented in the gate, and classifying a module into a tier is an
argument that adds nothing a single floor does not already give.

### Current Coverage Gaps

> **Note:** Foundation modules (`esmis_vocabulary`) should
> maintain comprehensive test coverage as reference implementations.

### Enforcing Coverage

Coverage is enforced by `fail_under = 85` in `pyproject.toml` (`[tool.coverage.report]`).
`.github/workflows/ci.yml` runs `coverage report` per module against that setting and fails
the build for any module below it. Locally:

```bash
./scripts/test_single_module.sh esmis_vocabulary --coverage
```

## Test Types

| Type | Purpose | Example |
|------|---------|---------|
| Unit | Individual methods | Test validation logic |
| Integration | Module interactions | Test order workflow |
| API | Endpoints, auth, errors | Test REST API responses |
| E2E | User workflows via browser | Test order flow via UI |
| Performance | Scale requirements | Test with 10K records |

## Test Structure

```python
from odoo.tests import TransactionCase

class TestPartner(TransactionCase):

    def setUp(self):
        super().setUp()
        self.partner = self.env['res.partner'].create({
            'name': 'Test Partner',
        })

    def test_partner_has_default_identifiers(self):
        """Test that creating a partner generates default identifiers"""
        self.assertTrue(self.partner.identifier_ids)
```

## Pre-Merge Requirements

- [ ] All unit tests pass
- [ ] E2E smoke tests pass
- [ ] Coverage meets minimum
- [ ] No new linting errors
- [ ] API compatibility checks pass

## Migration Testing

- Test with production-like data volumes
- Verify foreign key integrity
- Check sequence continuity
- Validate index performance

## Performance Testing

```python
import time

def test_list_view_performance(self):
    """List view must load in < 2s with 10K records"""
    start = time.time()
    # Load list view
    duration = time.time() - start
    self.assertLess(duration, 2.0)
```

## E2E Testing (Playwright)

E2E tests live in `/e2e` and use Playwright with Page Object Model.

### Structure

```typescript
// Use page objects, not raw selectors
const odooPage = new OdooPage(page);
const listView = new ListView(page);

await odooPage.openApp("MyApp");
await odooPage.navigateMenu(["All Records"]);
await listView.ensureListView();
```

### Odoo 19 Patterns

| Pattern | Correct | Incorrect |
|---------|---------|-----------|
| Wait for page | `waitForPageLoad()` | `waitForLoadState("networkidle")` |
| Check rows exist | `waitForRows()` returns count | `isEmpty()` |
| Menu navigation | `["Records"]` (single level) | `["Records", "Records"]` |
| After navigation | Call `ensureListView()` | Assume list is visible |
| Form selector | `.o_action_manager .o_form_view.o_view_controller` | `.o_form_view` |
| List selector | Scoped to exclude x2many | Global `.o_list_view` |

### Anti-Patterns (Avoid)

```typescript
// BAD: Empty catch hides failures
try { await action(); } catch {}

// BAD: Fallback navigation masks broken menus
try { await navigateMenu(["A", "B"]); }
catch { await navigateMenu(["B"]); }

// BAD: networkidle hangs on Odoo longpoll
await page.waitForLoadState("networkidle");
```

### Running E2E Tests

```bash
cd e2e

# Run all tests
npx playwright test

# Run specific suite
npx playwright test tests/smoke.spec.ts

# Run by tag
npx playwright test --grep @workflow

# Debug mode
npx playwright test --debug
```

## Odoo Testing Quirks

Odoo's test framework overrides some Python unittest behaviors. Be aware of these differences:

### assertRaises Does NOT Support Tuples

**Wrong:**
```python
# This will fail with: TypeError: issubclass() arg 1 must be a class
with self.assertRaises((ValueError, UserError)):
    some_operation()
```

**Correct:**
```python
# Use a single exception type
with self.assertRaises(ValidationError):
    some_operation()

# For mixed exception types, use Exception as base
with self.assertRaises(Exception):
    some_operation()
```

This is enforced by pre-commit hook `no-assertraises-tuple`.

## Running Tests

```bash
# Single module
odoo-bin -d test_db -u esmis_vocabulary --test-enable --stop-after-init

# With coverage
coverage run odoo-bin ... && coverage report -m
```

## SIS-Specific Testing Requirements

### Regulatory Compliance

- Test that PII access requires documented consent capture (no consent → access denied)
- Test separate consent paths for minors (guardian consent) vs adults (self-consent)
- Test that consent records are immutable after the fact

### Multi-Campus Isolation

- Test that a Campus A officer cannot read, write, or search Campus B student records
- Test that a system administrator sees records across all campuses
- Test that cross-campus data does not leak through related models (e.g., grade lines, enrollment lines)

### Government Exports

- Test HEMIS export output format against the CHED-prescribed column layout
- Validate field types (e.g., date formats, numeric precision) and allowed value ranges
- Test that export wizards surface validation errors to the user before generating the file

### Financial Aid Eligibility

- Test free tuition criteria: Filipino citizen, no prior baccalaureate degree, enrolled in SUC/LUC
- Test PWD 20% discount application and that it stacks correctly with other aid (or is blocked per policy)
- Test stacking rules: which aid types can combine, which are mutually exclusive
- Test eligibility re-evaluation when student data changes mid-term

### Grade Workflows

- Test INC (Incomplete) grade resolution: deadline enforcement and grade replacement
- Test the grade change approval chain: faculty submits → department chair reviews → registrar approves
- Test GWA (General Weighted Average) computation accuracy across unit-weighted and non-weighted subjects
- Test that grade records become immutable after registrar approval

### Enrollment Validation

- Test prerequisite checks: enrollment blocked if prerequisite not passed
- Test schedule conflict detection: same student cannot enroll in two sections with overlapping schedules
- Test capacity enforcement: enrollment blocked when section reaches maximum seats

## Performance Testing Targets

These targets apply to production-like data volumes. Tests that cannot meet these targets should be flagged before merge.

| Operation | Target |
|-----------|--------|
| List views | < 2s load with 50,000+ student records |
| Student search (name, ID, email, national ID) | < 500ms |
| HEMIS export | < 5 minutes for 50,000+ students |
| Bulk grade import | < 2 minutes for 5,000+ grades |
| Financial aid batch eligibility evaluation | < 10 minutes for 10,000+ students |

Performance tests should use `time.time()` assertions (see the Performance Testing section above for the pattern) and must run against a seeded dataset, not an empty database.

---

**See also:** [Performance & Scalability](performance-scalability.md)
