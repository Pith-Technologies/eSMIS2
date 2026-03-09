# Access Rights Principles

Security architecture for eSMIS using Odoo 19's `res.groups.privilege` system.

## Core Principles

1. **Least Privilege** - Users get minimum permissions needed
2. **Explicit Over Implicit** - All permissions defined in CSV/XML, no reliance on defaults
3. **Domain Isolation** - Each functional domain has its own group hierarchy
4. **Extension, Not Override** - Modules extend base groups, never modify them

## Three-Tier Architecture

```
TIER 1: ROLES (Composite)           ← Cross-domain, optional
├── role_esmis_field_officer
└── role_esmis_supervisor

TIER 2: FUNCTIONAL PRIVILEGES       ← User-facing, per domain
├── group_inventory_viewer
├── group_inventory_officer
└── group_inventory_manager

TIER 3: BASE PERMISSIONS            ← Technical, granular
├── group_inventory_read
├── group_inventory_write
└── group_inventory_create
```

## Group Hierarchy Pattern

```xml
<!-- Technical groups (Tier 3) -->
<record id="group_inventory_read" model="res.groups">
    <field name="name">Inventory: Read</field>
</record>

<!-- User-facing groups (Tier 2) inherit technical -->
<record id="group_inventory_officer" model="res.groups">
    <field name="name">Officer</field>
    <field name="privilege_id" ref="privilege_inventory_officer"/>
    <field name="implied_ids" eval="[
        Command.link(ref('group_inventory_read')),
        Command.link(ref('group_inventory_write')),
    ]"/>
</record>
```

## Permission Levels

| Level | Permissions | Use Case |
|-------|-------------|----------|
| Viewer | Read | View-only access |
| Officer | Read, Write, Create | Standard operational |
| Manager | + Admin functions | Supervisory |
| Admin | Full CRUD + Config | System administration |

### SIS-Specific Roles

These roles map to real positions in a Philippine higher education institution. Each entry notes the functional scope and whether it is campus-scoped or broader.

| Role | Level | Scope | Functional Access |
|------|-------|-------|-------------------|
| **Registrar** | Officer / Manager | Campus | Enrollment records, grades, TOR, graduation, curriculum |
| **Admissions Officer** | Officer | Campus | Application evaluation, admission decisions |
| **Faculty** | Officer | Department | Grade entry for own sections only |
| **Financial Aid Officer** | Officer | Campus | Scholarship awards, eligibility, subsidy tracking |
| **Cashier / Finance** | Officer | Campus | Payment processing, fee assessment, refunds |
| **Student (Self)** | Viewer | Own records | Own grades, schedule, balance, document requests |
| **Parent / Guardian** | Viewer | Linked student | Linked student records only, with student consent |
| **Counselor** | Officer | Assigned students | Counseling records for assigned students (Restricted classification) |
| **Department Chair** | Manager | Department | Faculty loads, section management, grade distributions |
| **Dean** | Manager | College | College-level reports, grade change approvals, faculty assignments |
| **VP Academic Affairs / President** | Admin | System-wide | All-campus dashboards and reports |
| **CHED Reporter** | Viewer | System-wide | Read access for HEMIS/eCAV exports |

### Sensitive Field Access

Certain fields carry heightened privacy obligations and must be restricted beyond normal role access. Access is granted only to the named roles:

| Field / Record Type | Classification | Permitted Roles |
|---------------------|----------------|-----------------|
| National ID (PhilSys), PWD ID, Solo Parent ID | Tier 3 / SPI | Admissions Officer, Registrar |
| Student grades (`grade_value`, cumulative GWA) | Tier 3 / SPI | Faculty (own sections only), Registrar, Student (self only) |
| Disciplinary records | Tier 3 / SPI | Registrar, Student Affairs |
| Counseling notes | Tier 3 / SPI — Restricted per ADR-005 | Counselor only |
| Health / medical records | Tier 3 / SPI | Clinic staff only |
| Financial records | Tier 2 / Confidential | Finance, Financial Aid Officer |

Never expose these fields to roles not listed here, even for read access. Do not include them in list views or exports without explicit access checks.

> **MFA requirement:** All users accessing Tier 3 / SPI fields must authenticate with
> multi-factor authentication per NPC Circular 2023-06 (compliance deadline March 30,
> 2025). MFA enforcement is handled at the authentication layer, not in record rules.

### Multi-Campus Scoping

- All campus-scoped roles are restricted via `company_id` record rules. A Registrar at Campus A cannot access enrollment records at Campus B.
- System-level roles (VP Academic Affairs, President, CHED Reporter) use `[(1, '=', 1)]` domain rules that bypass campus isolation.
- See `multi-campus-architecture.md` for the full record rule design.

## Reference Data Models

Reference data models contain shared lookup values used across the system (like countries, currencies, or vocabulary codes). These MUST be readable by all internal users.

### Principle

**Reference data = readable by all internal users (`base.group_user`)**

This ensures that any module or user can display reference data without requiring additional group memberships.

### Reference Data Models

| Model | Module | Purpose |
|-------|--------|---------|
| `res.country` | base | Country codes |
| `res.currency` | base | Currency codes |
| `esmis.vocabulary` | esmis_vocabulary | Vocabulary definitions |
| `esmis.vocabulary.code` | esmis_vocabulary | Vocabulary code values |

### ACL Pattern

```csv
# Reference data: read-only for all internal users
access_esmis_vocabulary_user,esmis.vocabulary user,model_esmis_vocabulary,base.group_user,1,0,0,0
access_esmis_vocabulary_code_user,esmis.vocabulary.code user,model_esmis_vocabulary_code,base.group_user,1,0,0,0
```

Write/create/delete permissions remain restricted to domain-specific groups (Vocabulary Officer, Manager).

## Where Groups Are Defined

| What | Where | Why |
|------|-------|-----|
| Category hierarchy | `esmis_security` | Consistent UI |
| Admin group | `esmis_security` | Always needed |
| Inventory groups | `esmis_inventory` | Only when installed |
| Vocabulary groups | `esmis_vocabulary` | Only when installed |
| Composite roles | `esmis_roles` (optional) | For pre-built role combinations |

## Record Rules

### Required Patterns

All record rules MUST follow these requirements:

1. **Never use empty domains** - `domain_force=[]` is forbidden with write/create/unlink permissions
2. **Always specify groups OR use global** - Rules without group specification apply to ALL users
3. **Use explicit "see all" pattern** - When validators need full access, use `[(1, '=', 1)]` not `[]`
4. **Wrap in noupdate** - Record rules should use `<data noupdate="1">` wrapper

### Common Patterns

```xml
<!-- Company-based access (REQUIRED for multi-company models) -->
<record id="rule_model_company" model="ir.rule">
    <field name="name">Model: Multi-Company Access</field>
    <field name="model_id" ref="module.model_name"/>
    <field name="domain_force">[
        '|', ('company_id', '=', False), ('company_id', 'in', company_ids)
    ]</field>
    <field name="global">True</field>
</record>

<!-- Own records only -->
<field name="domain_force">[('create_uid', '=', user.id)]</field>

<!-- Validators see all (explicit pattern - NEVER use empty []) -->
<field name="domain_force">[(1, '=', 1)]</field>
```

### Anti-Patterns (DO NOT USE)

```xml
<!-- BAD: Empty domain with write permissions -->
<field name="domain_force">[]</field>
<field name="perm_write">1</field>

<!-- BAD: Global rule with write permissions (allows ANY user to write) -->
<record id="rule_something" model="ir.rule">
    <field name="global">True</field>
    <field name="perm_write">1</field>  <!-- Dangerous! Use group restriction instead -->
</record>

<!-- BAD: No group specification (applies to everyone) -->
<record id="rule_something" model="ir.rule">
    <field name="domain_force">[...]</field>
    <!-- Missing groups field OR global="True" -->
</record>

<!-- BAD: Destructively modifying base Odoo groups (changing name, category, removing implied groups) -->
<record id="base.group_user" model="res.groups">
    <field name="name">Changed Name</field>  <!-- Don't do this -->
</record>

<!-- GOOD: Extending base.group_system implied_ids (standard Odoo pattern) -->
<record id="base.group_system" model="res.groups">
    <field name="implied_ids" eval="[Command.link(ref('group_esmis_myfeature_manager'))]"/>
</record>
```

## Settings Admin Inheritance (REQUIRED)

Every module that defines security groups MUST extend `base.group_system` (`implied_ids`) to include its highest-privilege group. This ensures that members of the Administration/Settings group automatically have full access to all eSMIS features without needing to be manually added to each module's groups.

```xml
<!-- In your module's groups.xml, AFTER defining your groups -->
<record id="base.group_system" model="res.groups">
    <field name="implied_ids" eval="[
        Command.link(ref('group_esmis_myfeature_manager')),
    ]"/>
</record>
```

This is a standard Odoo pattern — `Command.link()` adds to the existing `implied_ids` without removing any. Only link the **top-level** group in each hierarchy; lower groups are inherited transitively.

## ACL File Format

### Superuser Access (REQUIRED)

Every custom `esmis.*` model MUST include a `base.group_system` ACL row with full CRUD permissions. This ensures the admin/superuser can always access all eSMIS models without needing domain-specific group membership. Place it as the first data row in the CSV.

```csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_esmis_mymodel_system,esmis.mymodel / System,model_esmis_mymodel,base.group_system,1,1,1,1
```

This does NOT apply to inherited Odoo models (e.g., `res.partner`) since they already have admin access from Odoo core.

### Entry ID Naming Convention (REQUIRED)

ACL entry IDs MUST follow the pattern: `access_{model}_{group}`

- `{model}` - Model name with underscores (e.g., `esmis_order`, `res_partner`)
- `{group}` - Short group identifier (e.g., `viewer`, `officer`, `manager`, `system`)

```csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_esmis_mymodel_system,esmis.mymodel / System,model_esmis_mymodel,base.group_system,1,1,1,1
access_res_partner_inventory_viewer,res.partner viewer,base.model_res_partner,group_inventory_viewer,1,0,0,0
access_res_partner_inventory_officer,res.partner officer,base.model_res_partner,group_inventory_officer,1,1,1,0
```

**Anti-patterns to avoid:**
- `user_access_esmis_api_log` - Don't prefix with user/manager
- `esmis_order_admin` - Don't use model name as ID prefix
- `report_details_esmis_admin` - Don't use report-style names

## Checklist

### Module Security Checklist

- [ ] Module depends on `esmis_security`
- [ ] Groups use `privilege_id` for user-facing groups
- [ ] Groups have `comment` field documentation
- [ ] `base.group_system` extended to imply the module's highest-privilege group
- [ ] ACL entries for all models
- [ ] Every custom `esmis.*` model has a `base.group_system` full CRUD row
- [ ] No duplicate group definitions
- [ ] No references to deprecated groups

### Record Rules Checklist

- [ ] All rules have non-empty `domain_force` (no `[]` with write permissions)
- [ ] All rules have explicit `groups` field OR `global="True"`
- [ ] Rules wrapped in `<data noupdate="1">`
- [ ] Campus-scoped models have campus isolation rules (via `company_id`)
- [ ] Role-based scoping rules for each functional group (viewer, officer, manager)
- [ ] Naming follows `rule_{model}_{purpose}` pattern

### New Model Security Checklist

When adding a new model with `company_id`, you MUST create:

1. **Campus isolation rule** (global, uses `company_id`):
```xml
<record id="rule_{model}_multi_company" model="ir.rule">
    <field name="name">Model: Multi-Company</field>
    <field name="model_id" ref="model_{model}"/>
    <field name="domain_force">[
        '|', ('company_id', '=', False), ('company_id', 'in', company_ids)
    ]</field>
    <field name="global" eval="True"/>
</record>
```

2. **Role-based scoping rules** for each access group:
```xml
<!-- Officer: Own records or assigned scope -->
<record id="rule_{model}_officer_scope" model="ir.rule">
    <field name="name">Model: Officer Scope</field>
    <field name="model_id" ref="model_{model}"/>
    <field name="domain_force">[
        '|', ('assigned_to', '=', user.id), ('create_uid', '=', user.id)
    ]</field>
    <field name="groups" eval="[(4, ref('group_officer'))]"/>
</record>

<!-- Manager: All records -->
<record id="rule_{model}_manager_all" model="ir.rule">
    <field name="name">Model: Manager All Access</field>
    <field name="model_id" ref="model_{model}"/>
    <field name="domain_force">[(1, '=', 1)]</field>
    <field name="groups" eval="[(4, ref('group_manager'))]"/>
</record>
```

### Odoo 19 Compatibility Checklist

- [ ] No `category_id` on `res.groups` records (only on `res.groups.privilege`)
- [ ] Use `user_ids` not `users` field
- [ ] Use `Command.link()` not tuple syntax `(4, ref())`
- [ ] Use `group_ids` not `groups_id` on menu records

## V2 Migration Notes

Since V2 allows breaking compatibility, the following legacy patterns should be removed:

1. **Deprecated group aliases** - Remove backward-compatibility groups that just imply new groups
2. **Duplicate group IDs** - Each group ID must be unique across all modules
3. **Namespace** - All XML IDs must use `esmis_*` prefix, all model references must use `esmis.*`
4. **Base group modifications** - Modules must not modify `base.group_user` or `base.group_erp_manager`
5. **Old XML ID prefixes** - Use `esmis_*` consistently for all XML IDs

## Demo & Test Environment

### Role-Based Demo Users

Demo environments should include users representing each role level to showcase access control:

| Login | Role | Purpose | Visibility |
|-------|------|---------|------------|
| `demo_viewer` | Viewer | Read-only demonstration | All records (read-only) |
| `demo_officer` | Officer | Field worker operations | Own records + team records |
| `demo_supervisor` | Supervisor | Approval workflows | Team records + approval actions |
| `demo_manager` | Manager | Full domain access | All records (full CRUD) |
| `admin` | Admin | System administration | Everything |

**Password:** All demo users use `demo` as password for easy access.

### Role Visibility Matrix

Record rules determine what each role can see:

| Module | User/Officer | Supervisor | Validator | Manager |
|--------|--------------|------------|-----------|---------|
| **Inventory** | Own records | Team records | - | All + config |
| **Orders** (planned) | Own orders | Team orders | - | All orders |
| **Vocabulary** | All (read) | All (read/write) | - | All + config |
| **Identifier** | Own records | All records | - | All + config |

### Menu Visibility Caching

**Critical:** Odoo caches menu visibility at login time based on user groups.

**Problem:** If groups are assigned after a user logs in, menus won't appear until logout/login.

**Solution for Demo Generators:**
```python
# 1. Assign groups FIRST, before any data creation
user.write({"group_ids": [Command.link(group_id)]})

# 2. Commit immediately
self.env.cr.commit()

# 3. Clear registry cache to invalidate menu visibility
self.env.registry.clear_cache()
```

**Solution for E2E Tests:**
- Ensure security groups are assigned in demo data XML (loaded at install)
- Or assign groups before test user logs in
- Never assume menus are visible without verifying group membership

### Demo Data Ownership

**Problem:** Demo data created by system users (OdooBot, scripts) is invisible to human users due to record rules.

**Anti-pattern:**
```python
# BAD: Data created by OdooBot won't be visible to admin
self.env["res.partner"].create({...})  # create_uid = OdooBot
```

**Correct patterns:**

```python
# GOOD: Create as the intended user
demo_officer = self.env.ref("esmis_inventory.demo_officer")
self.env["res.partner"].with_user(demo_officer).create({...})

# GOOD: Or assign manager group so admin can see all records
admin.write({"group_ids": [Command.link(manager_group.id)]})
```

### Demo Environment Checklist

- [ ] Role-based demo users created (viewer, officer, supervisor, manager)
- [ ] Each demo user has meaningful group assignments
- [ ] Demo data created under appropriate user context
- [ ] Menus visible for each role after fresh login
- [ ] Record rules verified (officer sees own, manager sees all)
- [ ] Approval workflows testable (officer creates, supervisor approves)

### Testing Access Rights

When writing E2E tests for access control:

```typescript
// Test role visibility
test("Inventory officer sees only own records", async () => {
  await loginAs("demo_officer");
  const records = await listView.getRowCount();
  // Officer should see limited records
});

test("Inventory manager sees all records", async () => {
  await loginAs("demo_manager");
  const records = await listView.getRowCount();
  // Manager should see all records
});
```

---

**Authoritative Sources:**
- [ADR-001: Access Rights Management](../architecture/decisions/ADR-001-access-rights-management.md) - Architecture decision

**See also:** [Naming Conventions](naming-conventions.md), [Module Architecture](module-architecture.md)
