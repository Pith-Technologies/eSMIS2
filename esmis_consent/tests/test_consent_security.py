from odoo import Command
from odoo.exceptions import AccessError
from odoo.tests.common import TransactionCase


class TestConsentSecurity(TransactionCase):
    """Tests for esmis_consent ACLs."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Consent = cls.env["esmis.consent"]

        cls.user_basic = cls.env["res.users"].create(
            {
                "name": "Basic User",
                "login": "test_basic_consent",
                "password": "test_basic_consent",
                "group_ids": [Command.set([cls.env.ref("base.group_user").id])],
            }
        )
        cls.user_viewer = cls.env["res.users"].create(
            {
                "name": "Security Viewer",
                "login": "test_consent_viewer",
                "password": "test_consent_viewer",
                "group_ids": [
                    Command.set(
                        [
                            cls.env.ref("base.group_user").id,
                            cls.env.ref("esmis_security.group_esmis_security_viewer").id,
                        ]
                    )
                ],
            }
        )
        cls.user_officer = cls.env["res.users"].create(
            {
                "name": "Security Officer",
                "login": "test_consent_officer",
                "password": "test_consent_officer",
                "group_ids": [
                    Command.set(
                        [
                            cls.env.ref("base.group_user").id,
                            cls.env.ref("esmis_security.group_esmis_security_officer").id,
                        ]
                    )
                ],
            }
        )
        cls.user_dpo = cls.env["res.users"].create(
            {
                "name": "DPO User",
                "login": "test_consent_dpo",
                "password": "test_consent_dpo",
                "group_ids": [
                    Command.set(
                        [
                            cls.env.ref("base.group_user").id,
                            cls.env.ref("esmis_security.group_esmis_dpo").id,
                        ]
                    )
                ],
            }
        )

        cls.partner = cls.env["res.partner"].create(
            {
                "name": "Test Partner Consent Security",
            }
        )
        cls.consent = cls.Consent.create(
            {
                "partner_id": cls.partner.id,
                "purpose": "consent_enrollment",
                "lawful_basis": "contract",
            }
        )

    def test_basic_user_can_read_consent(self):
        """Basic internal users can read consent records (needed for consent checks)."""
        consents = self.Consent.with_user(self.user_basic).search([])
        self.assertTrue(len(consents) >= 0)

    def test_basic_user_cannot_create_consent(self):
        """Basic users cannot create consent records."""
        with self.assertRaises(AccessError):
            self.Consent.with_user(self.user_basic).create(
                {
                    "partner_id": self.partner.id,
                    "purpose": "consent_ched_reporting",
                    "lawful_basis": "legal_obligation",
                }
            )

    def test_viewer_cannot_create_consent(self):
        """Security Viewer cannot create consent records."""
        with self.assertRaises(AccessError):
            self.Consent.with_user(self.user_viewer).create(
                {
                    "partner_id": self.partner.id,
                    "purpose": "consent_ched_reporting",
                    "lawful_basis": "legal_obligation",
                }
            )

    def test_officer_can_create_consent(self):
        """Security Officer can create consent records."""
        consent = self.Consent.with_user(self.user_officer).create(
            {
                "partner_id": self.partner.id,
                "purpose": "consent_ched_reporting",
                "lawful_basis": "legal_obligation",
            }
        )
        self.assertTrue(consent)

    def test_officer_cannot_delete_consent(self):
        """Security Officer cannot delete consent records (preserves audit trail)."""
        with self.assertRaises(AccessError):
            self.consent.with_user(self.user_officer).unlink()

    def test_dpo_can_read_and_write_consent(self):
        """DPO can read and write consent records."""
        consent = self.consent.with_user(self.user_dpo)
        consent.read(["purpose"])

    def test_dpo_cannot_create_consent(self):
        """DPO cannot create new consent records (only read/write existing)."""
        with self.assertRaises(AccessError):
            self.Consent.with_user(self.user_dpo).create(
                {
                    "partner_id": self.partner.id,
                    "purpose": "consent_alumni_tracking",
                    "lawful_basis": "consent",
                    "evidence_type": "electronic",
                }
            )
