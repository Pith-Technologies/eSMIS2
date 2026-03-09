from odoo.exceptions import UserError, ValidationError
from odoo.tests.common import TransactionCase


class TestConsent(TransactionCase):
    """Tests for the esmis.consent model."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Consent = cls.env["esmis.consent"]
        cls.partner = cls.env["res.partner"].create(
            {
                "name": "Test Partner",
            }
        )
        cls.partner_2 = cls.env["res.partner"].create(
            {
                "name": "Test Partner 2",
            }
        )

    def test_create_consent(self):
        """A consent record can be created with required fields."""
        consent = self.Consent.create(
            {
                "partner_id": self.partner.id,
                "purpose": "consent_enrollment",
                "lawful_basis": "contract",
            }
        )
        self.assertTrue(consent)
        self.assertTrue(consent.is_active)
        self.assertFalse(consent.date_withdrawn)

    def test_consent_is_active_computed(self):
        """is_active is True when date_withdrawn is not set."""
        consent = self.Consent.create(
            {
                "partner_id": self.partner.id,
                "purpose": "consent_enrollment",
                "lawful_basis": "contract",
            }
        )
        self.assertTrue(consent.is_active)

    def test_withdraw_consent(self):
        """Withdrawing consent sets date_withdrawn and is_active becomes False."""
        consent = self.Consent.create(
            {
                "partner_id": self.partner.id,
                "purpose": "consent_enrollment",
                "lawful_basis": "contract",
            }
        )
        consent.action_withdraw()
        self.assertFalse(consent.is_active)
        self.assertTrue(consent.date_withdrawn)

    def test_withdraw_already_withdrawn_raises(self):
        """Withdrawing an already-withdrawn consent raises UserError."""
        consent = self.Consent.create(
            {
                "partner_id": self.partner.id,
                "purpose": "consent_enrollment",
                "lawful_basis": "contract",
            }
        )
        consent.action_withdraw()
        with self.assertRaises(UserError):
            consent.action_withdraw()

    def test_active_consent_unique_per_partner_purpose(self):
        """Only one active consent per partner per purpose is allowed."""
        self.Consent.create(
            {
                "partner_id": self.partner.id,
                "purpose": "consent_enrollment",
                "lawful_basis": "contract",
            }
        )
        with self.assertRaises(ValidationError):
            self.Consent.create(
                {
                    "partner_id": self.partner.id,
                    "purpose": "consent_enrollment",
                    "lawful_basis": "contract",
                }
            )

    def test_withdrawn_consent_allows_new_for_same_purpose(self):
        """After withdrawing, a new consent for the same purpose can be created."""
        consent = self.Consent.create(
            {
                "partner_id": self.partner.id,
                "purpose": "consent_enrollment",
                "lawful_basis": "contract",
            }
        )
        consent.action_withdraw()
        new_consent = self.Consent.create(
            {
                "partner_id": self.partner.id,
                "purpose": "consent_enrollment",
                "lawful_basis": "contract",
            }
        )
        self.assertTrue(new_consent.is_active)

    def test_different_purposes_allowed(self):
        """Different purposes for the same partner are allowed simultaneously."""
        consent1 = self.Consent.create(
            {
                "partner_id": self.partner.id,
                "purpose": "consent_enrollment",
                "lawful_basis": "contract",
            }
        )
        consent2 = self.Consent.create(
            {
                "partner_id": self.partner.id,
                "purpose": "consent_ched_reporting",
                "lawful_basis": "legal_obligation",
            }
        )
        self.assertTrue(consent1.is_active)
        self.assertTrue(consent2.is_active)

    def test_different_partners_same_purpose(self):
        """Different partners can have active consent for the same purpose."""
        consent1 = self.Consent.create(
            {
                "partner_id": self.partner.id,
                "purpose": "consent_enrollment",
                "lawful_basis": "contract",
            }
        )
        consent2 = self.Consent.create(
            {
                "partner_id": self.partner_2.id,
                "purpose": "consent_enrollment",
                "lawful_basis": "contract",
            }
        )
        self.assertTrue(consent1.is_active)
        self.assertTrue(consent2.is_active)

    def test_evidence_type_required_for_consent_basis(self):
        """evidence_type is required when lawful_basis is 'consent'."""
        with self.assertRaises(ValidationError):
            self.Consent.create(
                {
                    "partner_id": self.partner.id,
                    "purpose": "consent_financial_aid",
                    "lawful_basis": "consent",
                }
            )

    def test_evidence_type_not_required_for_contract_basis(self):
        """evidence_type is not required when lawful_basis is 'contract'."""
        consent = self.Consent.create(
            {
                "partner_id": self.partner.id,
                "purpose": "consent_enrollment",
                "lawful_basis": "contract",
            }
        )
        self.assertTrue(consent)

    def test_parent_consent_field(self):
        """Parent consent can be recorded for minors."""
        consent = self.Consent.create(
            {
                "partner_id": self.partner.id,
                "purpose": "consent_enrollment",
                "lawful_basis": "contract",
                "is_parent_consent": True,
                "evidence_type": "written",
            }
        )
        self.assertTrue(consent.is_parent_consent)

    def test_scope_ids_relation(self):
        """Consent scopes can be added to a consent record."""
        consent = self.Consent.create(
            {
                "partner_id": self.partner.id,
                "purpose": "consent_enrollment",
                "lawful_basis": "contract",
            }
        )
        scope = self.env["esmis.consent.scope"].create(
            {
                "consent_id": consent.id,
                "resource_type": "esmis.student",
                "purpose": "Profile data processing",
            }
        )
        self.assertEqual(consent.scope_ids, scope)

    def test_consent_ordering(self):
        """Consent records are ordered by create_date desc (most recent first)."""
        self.assertEqual(self.Consent._order, "create_date desc")
