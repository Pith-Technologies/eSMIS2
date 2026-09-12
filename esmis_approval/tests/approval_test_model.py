"""A concrete model used only by this module's tests.

`esmis.approval.mixin` is an AbstractModel with no table of its own, and no
module inherits it yet, so its state machine cannot be exercised without a
concrete record to run it against. This file defines the smallest such model
and registers it in the registry for the duration of a test class.

The model is never installed: it is built in `setUpClass` and the registry is
restored by `TransactionCase`'s own class cleanup, which reloads the registry
whenever a test class has invalidated it.
"""

from odoo import fields, models
from odoo.orm import model_classes

TEST_MODEL_NAME = "esmis.approval.test.record"


class ApprovalTestRecord(models.Model):
    """Minimal approvable record: a name and whatever the mixin provides."""

    _name = TEST_MODEL_NAME
    _inherit = "esmis.approval.mixin"
    _description = "Approval Test Record"

    name = fields.Char(required=True)

    # Set by tests to observe that the mixin calls its hooks.
    hook_calls = fields.Char(default="")

    def _on_submit(self):
        """Record that the pre-submit hook ran, in order."""
        for record in self:
            record.hook_calls = (record.hook_calls or "") + "submit;"

    def _on_approve(self):
        """Record that the post-approve hook ran, in order."""
        for record in self:
            record.hook_calls = (record.hook_calls or "") + "approve;"


def build_test_model(env):
    """Register `ApprovalTestRecord` and create its table.

    Returns the model's name. Safe to call once per test class; calling it
    again for a model already in the registry simply re-runs setup.
    """
    registry = env.registry
    cr = env.cr

    # Registry.load() instantiates a module's model classes and adds them to
    # the registry. That ran before this test file was imported, so the class
    # has to be added the same way Registry.load() would have added it.
    if TEST_MODEL_NAME not in registry.models:
        model_classes.add_to_registry(registry, ApprovalTestRecord)
        registry._setup_models__(cr)
        registry.init_models(cr, [TEST_MODEL_NAME], dict(env.context, update_custom_fields=True))

    _grant_access(env)
    return TEST_MODEL_NAME


def _grant_access(env):
    """Give the model an ACL, the way ir.model.access.csv would.

    A model built at runtime has no access rules, so every operation raises
    AccessError for a non-superuser. The project's rule is to fix the ACL
    rather than reach for sudo(), and this is that fix: the tests then run as
    ordinary users, which is the only way the four-eyes rule can be exercised
    honestly.
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


__all__ = ["ApprovalTestRecord", "TEST_MODEL_NAME", "build_test_model"]
