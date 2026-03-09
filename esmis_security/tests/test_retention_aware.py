from odoo.tests.common import TransactionCase


class TestRetentionAware(TransactionCase):
    """Tests for the esmis.retention.aware abstract mixin."""

    def test_mixin_registered(self):
        """The retention aware mixin is registered in the Odoo registry."""
        self.assertIn("esmis.retention.aware", self.env)

    def test_mixin_has_required_fields(self):
        """The mixin provides all expected fields."""
        model = self.env["esmis.retention.aware"]
        expected_fields = [
            "legal_hold",
            "legal_hold_reason",
            "legal_hold_set_by",
        ]
        for field_name in expected_fields:
            self.assertIn(
                field_name,
                model._fields,
                f"Field '{field_name}' missing from esmis.retention.aware",
            )

    def test_legal_hold_default_false(self):
        """The legal_hold field defaults to False."""
        field = self.env["esmis.retention.aware"]._fields["legal_hold"]
        default = field.default
        if callable(default):
            default = default(self.env["esmis.retention.aware"])
        self.assertFalse(default)
