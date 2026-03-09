# Financial Aid Patterns

Standardized patterns for financial aid programs, eligibility determination, discount stacking, and award lifecycle management.

## Program Types

### Government Programs

| Program | Legal Basis | Benefit |
|---------|-------------|---------|
| Free Higher Education | RA 10931 (Universal Access to Quality Tertiary Education Act) | Full tuition waiver for qualified students in SUCs/LUCs |
| Tertiary Education Subsidy (TES) | UniFAST / RA 10931 | Living allowance for financially disadvantaged students |
| DOST-SEI Scholarship | RA 2067 (Science Act) | Stipend + tuition for science and engineering programs |
| CHED Scholarship | Various CHED memoranda | Tuition credit or stipend depending on program type |

### Institutional Programs

- **Merit-based**: Awarded based on academic performance (GWA threshold)
- **Need-based**: Awarded based on demonstrated financial need
- **Athletic**: Awarded to varsity athletes in good standing
- **Departmental**: Defined and funded by a specific college or department

### External Programs

- **Private foundation scholarships**: Administered by the institution on behalf of a donor
- **LGU scholarships**: Funded by local government units; eligibility may require residency verification

### Statutory Discounts

| Discount | Legal Basis | Rate |
|----------|-------------|------|
| PWD Discount | RA 7277 (Magna Carta for Persons with Disability), amended by RA 10754 | 20% on tuition and fees |
| Solo Parent Discount | RA 8972 (Solo Parents' Welfare Act), amended by RA 11861 | Rate defined by institution per IRR |

---

## Eligibility Determination

Each financial aid program defines its eligibility criteria as domain expressions evaluated against the applicant's record.

### Free Tuition (RA 10931)

All of the following must be true:

1. Filipino citizen
2. No prior bachelor's degree earned (first-time bachelor's enrollee)
3. Enrolled in a State University or College (SUC) or Local University or College (LUC)
4. Meets the program's retention policy (GWA and unit load requirements)

### Tertiary Education Subsidy (TES)

1. Enrolled full-time
2. Household income below the poverty threshold
3. Household is a Listahanan-registered beneficiary or a 4Ps (Pantawid Pamilyang Pilipino Program) member — cross-reference with DSWD data
4. Meets retention requirements set by UniFAST

### PWD Discount

1. Possesses a valid PWD ID issued by the NCDA or local OSCA/PDAO
2. Currently enrolled

### Solo Parent Discount

1. Possesses a valid Solo Parent ID issued under RA 8972 / RA 11861
2. Dependent verification on file (child or dependents listed in the ID)
3. Currently enrolled

### Institutional Scholarships

1. GWA at or above the program-defined threshold
2. Currently enrolled with a full academic load (or meets the minimum units specified)
3. No active disciplinary hold
4. Satisfies any program-specific criteria (e.g., enrolled in a particular degree program, member of a particular organization)

### Rule Evaluation Pattern

Eligibility rules are stored as Odoo domain expressions on `esmis.financial.aid.program`. The engine evaluates them against the student record at application time and at each renewal period:

```python
def _check_eligibility(self, student):
    """Return True if the student meets this program's eligibility criteria."""
    domain = safe_eval(self.eligibility_domain) if self.eligibility_domain else []
    matching = self.env["esmis.student"].search(
        [("id", "=", student.id)] + domain, limit=1
    )
    return bool(matching)
```

---

## Application Order (Discount Stacking)

When a student qualifies for multiple benefits, apply them in the following order. Some programs are mutually exclusive; institutional rules take precedence for those cases.

| Step | Program Category | Applied To | Notes |
|------|-----------------|------------|-------|
| 1 | Free Tuition (RA 10931) | Full tuition balance | Waives tuition entirely; miscellaneous fees still apply |
| 2 | Government subsidies | Remaining assessed amount | TES living allowance is a stipend, not a tuition credit; DOST-SEI stipend is disbursed separately |
| 3 | Institutional scholarships | Remaining tuition or fees | May be a tuition credit or a periodic stipend |
| 4 | Statutory discounts | Remaining balance after steps 1–3 | PWD 20% applied to the post-discount balance |

### Mutual Exclusivity Rules

- A student receiving Free Tuition under RA 10931 cannot simultaneously receive another government tuition waiver for the same term.
- Institutional and statutory discounts (PWD, Solo Parent) may stack on top of government programs unless the program's guidelines explicitly prohibit it.
- The stacking engine must record which programs were applied and in which order for audit purposes.

---

## Award Workflow

```
[Draft] → [Evaluated] → [Approved] → [Disbursed] → [Completed]
              ↓               ↓
          [Ineligible]    [Rejected]
```

| State | Description |
|-------|-------------|
| `draft` | Award record created; eligibility not yet verified |
| `evaluated` | Eligibility rules have been run; result is recorded |
| `approved` | Authorized approver has confirmed the award |
| `disbursed` | Funds or tuition credit have been applied to the student ledger |
| `completed` | Term ended; award archived |
| `ineligible` | Student did not meet eligibility criteria (terminal for this term) |
| `rejected` | Approver rejected the award; reason recorded |

### Hook Methods

Extend the award lifecycle without modifying core logic:

```python
def _pre_evaluate_hook(self):
    """Called before eligibility rules are run."""

def _post_evaluate_hook(self):
    """Called after eligibility result is written."""

def _pre_disburse_hook(self):
    """Called before the award is posted to the student ledger."""

def _post_disburse_hook(self):
    """Called after disbursement; use for notifications and reporting."""
```

---

## Audit and Reporting

### Audit Trail

- Every state change is recorded in the chatter with the acting user, timestamp, and reason.
- Changes to award amounts after approval require a supervisor-level approval and a logged justification.
- The stacking order applied to each student for each term must be stored on the award record, not derived at runtime.

### Regulatory Reporting

| Report | Frequency | Recipient | Standard |
|--------|-----------|-----------|----------|
| UniFAST TES utilization report | Annual | CHED / UniFAST | UniFAST data format |
| Free Tuition beneficiary list | Per term | CHED Regional Office | RA 10931 IRR |
| COA audit support data | On demand | Commission on Audit | Government accounting standards for SUCs |
| PWD and Solo Parent discount register | Annual | Internal / DSWD | RA 7277, RA 8972 |

### COA Compliance for SUCs

- All financial aid disbursements must map to a COA object code.
- Tuition waivers are recorded as government subsidy revenue, not as a discount against gross tuition.
- Cash stipends (TES, DOST-SEI) are recorded as trust fund releases and must be liquidated within the regulatory period.

---

## Testing

### Eligibility Edge Cases

- Student who earned a prior bachelor's degree must be excluded from Free Tuition.
- Student with an expired PWD ID must be excluded from the PWD discount.
- Student who is both a 4Ps member and a PWD must receive both benefits in the correct stacking order.
- Student who drops below the GWA threshold mid-term must lose institutional scholarship eligibility for the following term (not the current term).

### Stacking Rules

- Verify that Free Tuition reduces the tuition balance to zero before institutional scholarships are applied.
- Verify that the PWD 20% discount is computed on the post-step-3 balance, not the original assessment.
- Verify that mutually exclusive programs do not both appear on the same award record.

### Exclusion Verification

- A non-Filipino student must not appear in the Free Tuition beneficiary list.
- A student with no Listahanan or 4Ps link must not receive TES.
- An institutional scholarship with a GWA requirement of 1.75 must reject a student whose GWA is 2.00.

---

**See also:** [Regulatory Compliance](regulatory-compliance.md), [Approval Workflows](approval-workflows.md), [Audit & Compliance](audit-compliance.md)
