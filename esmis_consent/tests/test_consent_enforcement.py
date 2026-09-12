"""Behavioural tests for consent enforcement (RA 10173).

`test_consent_mixin.py` asserts the mixin's methods exist. These run them:
whether consent is found, what happens when it has been withdrawn, and that
an export of non-consenting records is refused rather than silently allowed.

Withdrawal is the case that matters most. Consent under RA 10173 can be
revoked at any time, so a withdrawn record must read as absent immediately -
a stale "yes" is an unlawful disclosure, not a caching bug.
"""

from datetime import timedelta

from odoo import fields
from odoo.exceptions import UserError, ValidationError
from odoo.tests.common import TransactionCase

from .consent_test_model import build_test_model

EXPORT_PURPOSE = "consent_ched_reporting"


class TestConsentEnforcement(TransactionCase):
    """Drive the consent mixin through a concrete record."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.model_name = build_test_model(cls.env)
        cls.Record = cls.env[cls.model_name]
        cls.Consent = cls.env["esmis.consent"]
        # Synthetic, obviously-fake names per docs/principles/test-data-pii.md
        cls.partner = cls.env["res.partner"].create({"name": "Juan Dela Cruz"})
        cls.other_partner = cls.env["res.partner"].create({"name": "Maria Clara Santos"})

    def _consent(self, partner, purpose=EXPORT_PURPOSE, withdrawn=False):
        record = self.Consent.create(
            {
                "partner_id": partner.id,
                "purpose": purpose,
                "lawful_basis": "consent",
                # Required by _check_evidence_type_required whenever the
                # lawful basis is consent: RA 10173 consent must be evidenced.
                "evidence_type": "electronic",
                "date_given": fields.Datetime.now(),
            }
        )
        if withdrawn:
            record.date_withdrawn = fields.Datetime.now()
        return record

    def _record(self, partner=None, name="Test record"):
        return self.Record.create({"name": name, "partner_id": partner.id if partner else False})

    # ------------------------------------------------------- partner resolution

    def test_get_consent_partner_returns_partner_id(self):
        """The default implementation reads partner_id."""
        record = self._record(self.partner)
        self.assertEqual(record._get_consent_partner(), self.partner)

    # ----------------------------------------------------------- consent lookup

    def test_active_consent_is_found(self):
        """A consent record with no withdrawal date counts as active."""
        self._consent(self.partner)
        record = self._record(self.partner)
        self.assertTrue(record._has_active_consent(EXPORT_PURPOSE))

    def test_withdrawn_consent_is_not_active(self):
        """Withdrawal takes effect immediately, with no cached 'yes'."""
        consent = self._consent(self.partner)
        record = self._record(self.partner)
        self.assertTrue(record._has_active_consent(EXPORT_PURPOSE))

        consent.date_withdrawn = fields.Datetime.now()

        self.assertFalse(
            record._has_active_consent(EXPORT_PURPOSE),
            "Withdrawn consent must read as absent on the very next check",
        )

    def test_consent_is_per_purpose(self):
        """Enrollment consent does not authorise a CHED submission."""
        self._consent(self.partner, purpose="consent_enrollment")
        record = self._record(self.partner)

        self.assertTrue(record._has_active_consent("consent_enrollment"))
        self.assertFalse(record._has_active_consent(EXPORT_PURPOSE))

    def test_consent_is_per_partner(self):
        """One student's consent says nothing about another's."""
        self._consent(self.other_partner)
        record = self._record(self.partner)
        self.assertFalse(record._has_active_consent(EXPORT_PURPOSE))

    def test_no_partner_means_no_consent(self):
        """A record with no partner cannot have consent, and must not error."""
        record = self._record(partner=None)
        self.assertFalse(record._has_active_consent(EXPORT_PURPOSE))

    def test_no_consent_record_at_all(self):
        """Absence of any consent record reads as False, not as permission."""
        record = self._record(self.partner)
        self.assertFalse(record._has_active_consent(EXPORT_PURPOSE))

    # ------------------------------------------------------------------ export

    def test_export_allowed_when_every_record_consents(self):
        """A fully consenting recordset exports without complaint."""
        self._consent(self.partner)
        self._consent(self.other_partner)
        records = self._record(self.partner, "A") | self._record(self.other_partner, "B")

        records._check_consent_for_export()  # must not raise

    def test_export_refused_when_consent_missing(self):
        """One non-consenting record blocks the whole export."""
        self._consent(self.partner)
        records = self._record(self.partner, "A") | self._record(self.other_partner, "B")

        with self.assertRaises(UserError):
            records._check_consent_for_export()

    def test_export_refused_when_consent_withdrawn(self):
        """Withdrawal blocks an export that was permitted a moment earlier."""
        consent = self._consent(self.partner)
        record = self._record(self.partner)
        record._check_consent_for_export()

        consent.date_withdrawn = fields.Datetime.now()

        with self.assertRaises(UserError):
            record._check_consent_for_export()

    def test_export_error_names_no_personal_information(self):
        """The refusal counts records; it never names the data subject.

        Per docs/principles/data-privacy-and-pii.md an exception message may
        reach logs and users who are not authorised to see who the subject is.
        """
        record = self._record(self.partner)
        with self.assertRaises(UserError) as caught:
            record._check_consent_for_export()

        message = str(caught.exception)
        self.assertNotIn(self.partner.name, message)
        self.assertIn("1", message)

    def test_export_on_empty_recordset_is_allowed(self):
        """Nothing to export is not a consent failure."""
        self.Record.browse()._check_consent_for_export()  # must not raise

    # ------------------------------------------------------------- scope expiry

    def test_scope_expiry_in_the_past_is_refused(self):
        """A scope cannot be created already expired."""
        consent = self._consent(self.partner)
        with self.assertRaises(ValidationError):
            self.env["esmis.consent.scope"].create(
                {
                    "consent_id": consent.id,
                    "resource_type": "transcript",
                    "valid_until": fields.Date.today() - timedelta(days=1),
                }
            )

    def test_scope_expiry_today_or_later_is_allowed(self):
        """Today is still valid; the constraint rejects only the past."""
        consent = self._consent(self.partner)
        scope = self.env["esmis.consent.scope"].create(
            {
                "consent_id": consent.id,
                "resource_type": "transcript",
                "valid_until": fields.Date.today(),
            }
        )
        self.assertTrue(scope.exists())

    def test_scope_without_expiry_is_allowed(self):
        """valid_until is optional; an unset date is not an expired one."""
        consent = self._consent(self.partner)
        scope = self.env["esmis.consent.scope"].create({"consent_id": consent.id, "resource_type": "transcript"})
        self.assertFalse(scope.valid_until)
