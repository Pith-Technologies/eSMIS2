from psycopg2 import IntegrityError

from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase
from odoo.tools import mute_logger


class TestApprovalDefinition(TransactionCase):
    """Tests for the esmis.approval.definition model."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.ApprovalDef = cls.env["esmis.approval.definition"]
        cls.model_partner = cls.env["ir.model"].search([("model", "=", "res.partner")], limit=1)

    def test_create_approval_definition(self):
        """An approval definition can be created with required fields."""
        definition = self.ApprovalDef.create(
            {
                "name": "Test Approval",
                "model_id": self.model_partner.id,
            }
        )
        self.assertTrue(definition)
        self.assertTrue(definition.active)

    @mute_logger("odoo.sql_db")
    def test_unique_model_constraint(self):
        """Only one approval definition per model is allowed."""
        self.ApprovalDef.create(
            {
                "name": "First Approval",
                "model_id": self.model_partner.id,
            }
        )
        with self.assertRaises(IntegrityError):
            self.ApprovalDef.with_context(testing=True).create(
                {
                    "name": "Second Approval",
                    "model_id": self.model_partner.id,
                }
            )
            self.env.cr.flush()

    def test_transient_model_rejected(self):
        """Approval definitions cannot target transient (wizard) models."""
        wizard_model = self.env["ir.model"].search([("transient", "=", True)], limit=1)
        if wizard_model:
            with self.assertRaises(ValidationError):
                self.ApprovalDef.create(
                    {
                        "name": "Wizard Approval",
                        "model_id": wizard_model.id,
                    }
                )
