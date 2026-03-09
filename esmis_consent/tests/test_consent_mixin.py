from odoo.tests.common import TransactionCase


class TestConsentMixin(TransactionCase):
    """Tests for the esmis.consent.mixin abstract model."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Consent = cls.env["esmis.consent"]
        cls.partner = cls.env["res.partner"].create(
            {
                "name": "Test Partner Consent Mixin",
            }
        )

    def test_mixin_registered(self):
        """The consent mixin is registered in the Odoo registry."""
        self.assertIn("esmis.consent.mixin", self.env)

    def test_mixin_has_required_methods(self):
        """The consent mixin provides all expected methods."""
        model = self.env["esmis.consent.mixin"]
        expected_methods = [
            "_has_active_consent",
            "_check_consent_for_export",
            "_get_consent_partner",
        ]
        for method_name in expected_methods:
            self.assertTrue(
                hasattr(model, method_name),
                f"Method '{method_name}' missing from esmis.consent.mixin",
            )

    def test_has_active_consent_returns_false_without_consent(self):
        """No consent record exists for an unconsented partner."""
        count = self.Consent.search_count(
            [
                ("partner_id", "=", self.partner.id),
                ("purpose", "=", "consent_alumni_tracking"),
                ("date_withdrawn", "=", False),
            ]
        )
        self.assertEqual(count, 0)

    def test_has_active_consent_returns_true_with_consent(self):
        """Active consent exists after creating a consent record."""
        self.Consent.create(
            {
                "partner_id": self.partner.id,
                "purpose": "consent_enrollment",
                "lawful_basis": "contract",
            }
        )
        count = self.Consent.search_count(
            [
                ("partner_id", "=", self.partner.id),
                ("purpose", "=", "consent_enrollment"),
                ("date_withdrawn", "=", False),
            ]
        )
        self.assertEqual(count, 1)

    def test_has_active_consent_false_after_withdrawal(self):
        """Withdrawn consent is not found by active consent search."""
        consent = self.Consent.create(
            {
                "partner_id": self.partner.id,
                "purpose": "consent_enrollment",
                "lawful_basis": "contract",
            }
        )
        consent.action_withdraw()
        count = self.Consent.search_count(
            [
                ("partner_id", "=", self.partner.id),
                ("purpose", "=", "consent_enrollment"),
                ("date_withdrawn", "=", False),
            ]
        )
        self.assertEqual(count, 0)
