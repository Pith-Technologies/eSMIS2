"""Concrete models used only by this module's tests.

Every mixin in `esmis_security/models/mixins/` is abstract and none of them
has a concrete consumer yet, so their behaviour cannot be exercised without
records to run it against. These are built for the duration of a test class
the same way `Registry.load()` builds a model for an installed module.

`esmis.pii.access.log` is a stand-in. `_log_pii_access` writes to that model
when it is present and returns silently when it is not; the model itself
lives in an esmis_audit module that does not exist in this repository yet.
Supplying it here is what makes the audit trail observable at all - without
it the whole logging path is unreachable and untested.
"""

from odoo import fields, models
from odoo.orm import model_classes

AUDIT_MODEL = "esmis.audit.test.record"
RETENTION_MODEL = "esmis.retention.test.record"
PII_MODEL = "esmis.pii.test.record"
ACCESS_LOG_MODEL = "esmis.pii.access.log"


class PiiAccessLog(models.Model):
    """Stand-in for the access log `_log_pii_access` writes to.

    Field names mirror what the mixin writes. Nothing here stores a PII
    value, which is the point: the log records that an access happened, not
    what was read.
    """

    _name = ACCESS_LOG_MODEL
    _description = "PII Access Log (test double)"

    model_name = fields.Char()
    record_id = fields.Integer()
    field_name = fields.Char()
    access_type = fields.Char()
    user_id = fields.Many2one(comodel_name="res.users")


class AuditTestRecord(models.Model):
    """Minimal auditable record: archival tracking and legal hold."""

    _name = AUDIT_MODEL
    _inherit = "esmis.audit.mixin"
    _description = "Audit Test Record"

    name = fields.Char(required=True)
    active = fields.Boolean(default=True)


class RetentionTestRecord(models.Model):
    """Minimal retention-managed record: legal hold only."""

    _name = RETENTION_MODEL
    _inherit = "esmis.retention.aware"
    _description = "Retention Test Record"

    name = fields.Char(required=True)


class PiiTestRecord(models.Model):
    """A record carrying one field of each masking pattern and tier."""

    _name = PII_MODEL
    _inherit = "esmis.pii.aware"
    _description = "PII Test Record"

    name = fields.Char(required=True)
    national_id = fields.Char()
    first_name = fields.Char()
    diagnosis = fields.Char()
    unclassified_note = fields.Char()

    _pii_fields = {
        # Tier 3, group-restricted, keeps only the last four digits.
        "national_id": {
            "tier": 3,
            "masking_pattern": "last4",
            "groups": "base.group_system",
        },
        # Tier 2, no group restriction, keeps only the first letter.
        "first_name": {
            "tier": 2,
            "masking_pattern": "first_letter",
            "groups": None,
        },
        # Tier 3 with no recognised pattern: masked completely.
        "diagnosis": {
            "tier": 3,
            "masking_pattern": None,
            "groups": "base.group_system",
        },
    }


_ALL_MODELS = (PiiAccessLog, AuditTestRecord, RetentionTestRecord, PiiTestRecord)


def build_test_models(env):
    """Register every test model, create its table, and give it an ACL."""
    registry = env.registry
    cr = env.cr

    missing = [cls for cls in _ALL_MODELS if cls._name not in registry.models]
    if missing:
        for cls in missing:
            model_classes.add_to_registry(registry, cls)
        registry._setup_models__(cr)

    # init_models runs for every class, not just the ones just added. The
    # registry is process-wide and survives a test class, but the ir.model
    # rows it creates live in the transaction and are rolled back with it -
    # so the second test class would otherwise find no ir.model to hang an
    # ACL on, and ir_model_access.model_id would go in null.
    registry.init_models(
        cr,
        [cls._name for cls in _ALL_MODELS],
        dict(env.context, update_custom_fields=True),
    )

    for cls in _ALL_MODELS:
        _grant_access(env, cls._name)


def _grant_access(env, model_name):
    """Give a model an ACL, the way ir.model.access.csv would.

    A model built at runtime has no access rules, so every operation raises
    AccessError for a non-superuser. The project's rule is to fix the ACL
    rather than reach for sudo(); these tests need to run as ordinary users
    to mean anything, since a superuser passes every group check by default.
    """
    model = env["ir.model"]._get(model_name)
    access = env["ir.model.access"]
    if access.search_count([("model_id", "=", model.id)]):
        return
    access.create(
        {
            "name": f"{model_name}.user",
            "model_id": model.id,
            "group_id": env.ref("base.group_user").id,
            "perm_read": True,
            "perm_write": True,
            "perm_create": True,
            "perm_unlink": True,
        }
    )
    access.call_cache_clearing_methods()
