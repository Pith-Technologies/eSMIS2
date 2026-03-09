from odoo.tests.common import TransactionCase


class TestAuditMixin(TransactionCase):
    """Tests for the esmis.audit.mixin abstract model."""

    def test_mixin_registered(self):
        """The audit mixin is registered in the Odoo registry."""
        self.assertIn("esmis.audit.mixin", self.env)

    def test_mixin_has_required_fields(self):
        """The mixin provides all expected fields."""
        model = self.env["esmis.audit.mixin"]
        expected_fields = [
            "legal_hold",
            "legal_hold_reason",
            "legal_hold_set_by",
            "archived_date",
            "archived_by_id",
            "archive_reason",
        ]
        for field_name in expected_fields:
            self.assertIn(
                field_name,
                model._fields,
                f"Field '{field_name}' missing from esmis.audit.mixin",
            )

    def test_legal_hold_default_false(self):
        """The legal_hold field defaults to False."""
        field = self.env["esmis.audit.mixin"]._fields["legal_hold"]
        default = field.default
        if callable(default):
            default = default(self.env["esmis.audit.mixin"])
        self.assertFalse(default)

    def test_mixin_has_required_methods(self):
        """The mixin provides all expected methods."""
        model = self.env["esmis.audit.mixin"]
        expected_methods = [
            "action_archive",
            "action_set_legal_hold",
            "action_remove_legal_hold",
        ]
        for method_name in expected_methods:
            self.assertTrue(
                hasattr(model, method_name),
                f"Method '{method_name}' missing from esmis.audit.mixin",
            )

    def test_mixin_inherits_mail_thread(self):
        """The audit mixin inherits mail.thread."""
        model = self.env["esmis.audit.mixin"]
        self.assertIn("mail.thread", model._inherit if isinstance(model._inherit, list) else [model._inherit])
