from odoo.tests.common import TransactionCase


class TestConsentIntegration(TransactionCase):
    """Tests for consent mixin integration with student partners.

    Verifies that esmis.consent records can be checked against student
    partners and that the consent mixin helpers work as expected.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Partner = cls.env["res.partner"].with_context(tracking_disable=True)
        cls.Consent = cls.env.get("esmis.consent")

        cls.student = cls.Partner.create(
            {
                "name": "Consent Test Student",
                "is_student": True,
                "first_name": "Consent",
                "last_name": "Student",
                "birthdate": "2000-01-01",
            }
        )

    def test_no_consent_record_returns_false(self):
        """_has_active_consent returns False when no consent record exists.

        Uses the esmis.consent.mixin helper attached to any model with partner_id.
        Since res.partner does not directly inherit the mixin, we test via
        an esmis.education.history record which is linked to the partner.
        """
        if not self.Consent:
            self.skipTest("esmis.consent not installed")

        history = self.env["esmis.education.history"].create(
            {
                "partner_id": self.student.id,
                "education_level_id": self.env["esmis.vocabulary.code"]
                .get_code("urn:esmis:education-level", "tertiary")
                .id,
                "school_name": "Consent Check School",
            }
        )
        result = history._has_active_consent("consent_ched_reporting")
        self.assertFalse(result)

    def test_active_consent_returns_true(self):
        """_has_active_consent returns True when an active consent record exists."""
        if not self.Consent:
            self.skipTest("esmis.consent not installed")

        # Create an active consent record for the student.
        self.Consent.sudo().create(
            {
                "partner_id": self.student.id,
                "purpose": "consent_ched_reporting",
            }
        )

        history = self.env["esmis.education.history"].create(
            {
                "partner_id": self.student.id,
                "education_level_id": self.env["esmis.vocabulary.code"]
                .get_code("urn:esmis:education-level", "elementary")
                .id,
                "school_name": "Consent Active School",
            }
        )
        result = history._has_active_consent("consent_ched_reporting")
        self.assertTrue(result)

    def test_withdrawn_consent_returns_false(self):
        """_has_active_consent returns False when consent has been withdrawn."""
        if not self.Consent:
            self.skipTest("esmis.consent not installed")

        import datetime

        consent = self.Consent.sudo().create(
            {
                "partner_id": self.student.id,
                "purpose": "consent_ched_reporting",
            }
        )
        consent.sudo().write({"date_withdrawn": datetime.date.today()})

        history = self.env["esmis.education.history"].create(
            {
                "partner_id": self.student.id,
                "education_level_id": self.env["esmis.vocabulary.code"]
                .get_code("urn:esmis:education-level", "junior_high_school")
                .id,
                "school_name": "Withdrawn Consent School",
            }
        )
        result = history._has_active_consent("consent_ched_reporting")
        self.assertFalse(result)
