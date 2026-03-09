from odoo.tests.common import TransactionCase


class TestApprovalMixin(TransactionCase):
    """Tests for the esmis.approval.mixin abstract model."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_submitter = cls.env["res.users"].create(
            {
                "name": "Test Submitter",
                "login": "test_submitter_approval",
                "password": "test_submitter_approval",
            }
        )
        cls.user_approver = cls.env["res.users"].create(
            {
                "name": "Test Approver",
                "login": "test_approver_approval",
                "password": "test_approver_approval",
            }
        )

    def test_mixin_registered(self):
        """The approval mixin is registered in the Odoo registry."""
        self.assertIn("esmis.approval.mixin", self.env)

    def test_mixin_has_required_fields(self):
        """The mixin provides all expected fields."""
        model = self.env["esmis.approval.mixin"]
        expected_fields = [
            "approval_state",
            "submitted_by_id",
            "submitted_date",
            "approved_by_id",
            "approved_date",
            "rejected_by_id",
            "rejected_date",
            "rejection_reason",
        ]
        for field_name in expected_fields:
            self.assertIn(
                field_name,
                model._fields,
                f"Field '{field_name}' missing from esmis.approval.mixin",
            )

    def test_approval_state_default(self):
        """The default approval_state is 'draft'."""
        field = self.env["esmis.approval.mixin"]._fields["approval_state"]
        default = field.default
        if callable(default):
            default = default(self.env["esmis.approval.mixin"])
        self.assertEqual(default, "draft")

    def test_mixin_has_required_methods(self):
        """The mixin provides all expected methods."""
        model = self.env["esmis.approval.mixin"]
        expected_methods = [
            "action_submit_for_approval",
            "action_approve",
            "action_reject",
            "action_reset_to_draft",
            "action_request_revision",
            "_on_submit",
            "_on_approve",
        ]
        for method_name in expected_methods:
            self.assertTrue(
                hasattr(model, method_name),
                f"Method '{method_name}' missing from esmis.approval.mixin",
            )
