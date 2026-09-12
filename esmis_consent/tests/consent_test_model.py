"""A concrete model used only by this module's tests.

`esmis.consent.mixin` is an AbstractModel and no module inherits it yet, so
its behaviour cannot be exercised without a concrete record carrying a
`partner_id`. This builds the smallest such model for the duration of a test
class, the same way `Registry.load()` would build it for an installed module.
"""

from odoo import fields, models
from odoo.orm import model_classes

TEST_MODEL_NAME = "esmis.consent.test.record"


class ConsentTestRecord(models.Model):
    """Minimal PII-processing record: a partner, and the mixin's helpers."""

    _name = TEST_MODEL_NAME
    _inherit = "esmis.consent.mixin"
    _description = "Consent Test Record"

    name = fields.Char(required=True)
    partner_id = fields.Many2one(comodel_name="res.partner")


def build_test_model(env):
    """Register `ConsentTestRecord`, create its table, and give it an ACL."""
    registry = env.registry
    cr = env.cr

    if TEST_MODEL_NAME not in registry.models:
        model_classes.add_to_registry(registry, ConsentTestRecord)
        registry._setup_models__(cr)
        registry.init_models(cr, [TEST_MODEL_NAME], dict(env.context, update_custom_fields=True))

    _grant_access(env)
    return TEST_MODEL_NAME


def _grant_access(env):
    """Give the model an ACL, the way ir.model.access.csv would.

    A model built at runtime has no access rules, so every operation raises
    AccessError for a non-superuser. Fixing the ACL is the project's rule;
    reaching for sudo() in a consent test would be doubly wrong, since
    RA 10173 consent must never be bypassed with sudo().
    """
    model = env["ir.model"]._get(TEST_MODEL_NAME)
    access = env["ir.model.access"]
    if access.search_count([("model_id", "=", model.id)]):
        return
    access.create(
        {
            "name": f"{TEST_MODEL_NAME}.user",
            "model_id": model.id,
            "group_id": env.ref("base.group_user").id,
            "perm_read": True,
            "perm_write": True,
            "perm_create": True,
            "perm_unlink": True,
        }
    )
    access.call_cache_clearing_methods()
