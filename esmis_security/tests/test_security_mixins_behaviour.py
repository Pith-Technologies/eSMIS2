"""Behavioural tests for the esmis_security mixins.

The existing test files assert that these mixins are registered and expose
the expected fields. These run them: legal hold actually refusing an archive
and a delete, PII masking actually masking, field-level access actually
denying, and the access log actually being written.

Legal hold and field-level access are both controls the institution would
have to evidence to the NPC or to CHED. A control that has never been
executed in a test is a claim, not a control.
"""

from unittest.mock import patch

from odoo.exceptions import UserError
from odoo.tests.common import TransactionCase

from .security_test_models import (
    ACCESS_LOG_MODEL,
    AUDIT_MODEL,
    PII_MODEL,
    RETENTION_MODEL,
    build_test_models,
)


class SecurityMixinCase(TransactionCase):
    """Shared fixtures: the models plus an ordinary, unprivileged user."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        build_test_models(cls.env)
        cls.Audit = cls.env[AUDIT_MODEL]
        cls.Retention = cls.env[RETENTION_MODEL]
        cls.Pii = cls.env[PII_MODEL]
        cls.Log = cls.env[ACCESS_LOG_MODEL]

        cls.plain_user = (
            cls.env["res.users"]
            .with_context(no_reset_password=True, tracking_disable=True)
            .create(
                {
                    "name": "Ordinary Staff",
                    "login": "security_mixin_plain",
                    "password": "security_mixin_plain",
                }
            )
        )


class TestAuditMixin(SecurityMixinCase):
    """Archival tracking and legal hold."""

    def _record(self, **values):
        values.setdefault("name", "Auditable record")
        return self.Audit.with_context(tracking_disable=True).create(values)

    def test_archive_records_who_and_when(self):
        """Archiving deactivates the record and leaves an audit trail."""
        record = self._record()

        record.action_archive()

        self.assertFalse(record.active)
        self.assertTrue(record.archived_date)
        self.assertEqual(record.archived_by_id, self.env.user)

    def test_legal_hold_blocks_archive(self):
        """A record under legal hold cannot be archived.

        This is the control that stops premature disposal during an
        investigation or a regulatory audit.
        """
        record = self._record()
        record.action_set_legal_hold("Pending NPC inquiry")

        with self.assertRaises(UserError):
            record.action_archive()

        self.assertTrue(record.active, "The record must survive the refused archive")

    def test_legal_hold_blocks_delete(self):
        """A record under legal hold cannot be deleted either."""
        record = self._record()
        record.action_set_legal_hold("Pending NPC inquiry")

        with self.assertRaises(UserError):
            record.unlink()

        self.assertTrue(record.exists())

    def test_set_legal_hold_records_reason_and_user(self):
        """The hold names why it was placed and who placed it."""
        record = self._record()

        record.action_set_legal_hold("Subject access request under review")

        self.assertTrue(record.legal_hold)
        self.assertEqual(record.legal_hold_reason, "Subject access request under review")
        self.assertEqual(record.legal_hold_set_by, self.env.user)

    def test_set_legal_hold_requires_a_reason(self):
        """A hold with no reason is refused, blank or whitespace."""
        record = self._record()
        for reason in ("", "   \n\t "):
            with self.assertRaises(UserError):
                record.action_set_legal_hold(reason)
        self.assertFalse(record.legal_hold)

    def test_remove_legal_hold_clears_the_hold(self):
        """Lifting the hold clears the reason and the user who set it."""
        record = self._record()
        record.action_set_legal_hold("Pending inquiry")

        record.action_remove_legal_hold("Inquiry closed, no findings")

        self.assertFalse(record.legal_hold)
        self.assertFalse(record.legal_hold_reason)
        self.assertFalse(record.legal_hold_set_by)

    def test_remove_legal_hold_requires_a_resolution(self):
        """A hold cannot be lifted silently."""
        record = self._record()
        record.action_set_legal_hold("Pending inquiry")

        for resolution in ("", "  "):
            with self.assertRaises(UserError):
                record.action_remove_legal_hold(resolution)

        self.assertTrue(record.legal_hold, "The hold must survive a refused removal")

    def test_archive_allowed_once_hold_is_lifted(self):
        """The hold blocks disposal only while it is in force."""
        record = self._record()
        record.action_set_legal_hold("Pending inquiry")
        record.action_remove_legal_hold("Closed")

        record.action_archive()

        self.assertFalse(record.active)

    def test_hold_on_one_record_blocks_the_whole_batch(self):
        """One held record refuses an archive of the set it belongs to."""
        held = self._record(name="Held")
        free = self._record(name="Free")
        held.action_set_legal_hold("Pending inquiry")

        with self.assertRaises(UserError):
            (held | free).action_archive()

        self.assertTrue(free.active, "A refused batch archives nothing")


class TestRetentionAware(SecurityMixinCase):
    """The lightweight legal-hold-only mixin."""

    def _record(self):
        return self.Retention.create({"name": "Retention record"})

    def test_legal_hold_blocks_delete(self):
        """Disposal is refused while the hold is set."""
        record = self._record()
        record.legal_hold = True

        with self.assertRaises(UserError):
            record.unlink()

        self.assertTrue(record.exists())

    def test_delete_allowed_without_hold(self):
        """Without a hold the record disposes normally."""
        record = self._record()
        record.unlink()
        self.assertFalse(record.exists())


class TestPiiAware(SecurityMixinCase):
    """Classification, masking, field-level access and the access log."""

    def _record(self):
        return self.Pii.create(
            {
                # Obviously synthetic, per docs/principles/test-data-pii.md
                "name": "Juan Dela Cruz",
                "national_id": "123456789012",
                "first_name": "Juan",
                "diagnosis": "Condition A",
                "unclassified_note": "Not classified",
            }
        )

    # ------------------------------------------------------- classification

    def test_classification_returned_for_declared_field(self):
        """A declared field reports its tier, pattern and group."""
        classification = self._record()._get_pii_classification("national_id")
        self.assertEqual(classification["tier"], 3)
        self.assertEqual(classification["masking_pattern"], "last4")

    def test_classification_absent_for_undeclared_field(self):
        """An undeclared field has no classification."""
        self.assertIsNone(self._record()._get_pii_classification("unclassified_note"))

    def test_view_pii_fields_lists_declared_fields_sorted(self):
        """The declared PII fields are reported in a stable order."""
        self.assertEqual(
            self._record().action_view_pii_fields(),
            ["diagnosis", "first_name", "national_id"],
        )

    # -------------------------------------------------------------- masking

    def test_last4_keeps_only_the_final_four(self):
        """A government identifier shows its last four digits at most."""
        record = self._record()
        self.assertEqual(record._mask_value("national_id", "123456789012"), "********9012")

    def test_last4_leaves_short_values_alone(self):
        """A value of four characters or fewer cannot be partially masked."""
        record = self._record()
        self.assertEqual(record._mask_value("national_id", "9012"), "9012")

    def test_first_letter_pattern(self):
        """A given name shows its initial only."""
        record = self._record()
        self.assertEqual(record._mask_value("first_name", "Juan"), "J***")

    def test_unrecognised_pattern_masks_completely(self):
        """A classified field with no known pattern is fully masked."""
        record = self._record()
        self.assertEqual(record._mask_value("diagnosis", "Condition A"), "****")

    def test_unclassified_field_is_not_masked(self):
        """Masking applies to declared PII only."""
        record = self._record()
        self.assertEqual(record._mask_value("unclassified_note", "Not classified"), "Not classified")

    def test_empty_value_masks_to_empty_string(self):
        """An absent value yields nothing, not a row of asterisks."""
        record = self._record()
        self.assertEqual(record._mask_value("national_id", False), "")
        self.assertEqual(record._mask_value("national_id", ""), "")

    # ------------------------------------------------------- field access

    def test_restricted_field_denied_to_user_outside_the_group(self):
        """An ordinary user cannot reach a group-restricted Tier 3 field."""
        record = self._record().with_user(self.plain_user)
        with self.assertRaises(UserError):
            record._check_pii_field_access("national_id")

    def test_restricted_field_allowed_for_member_of_the_group(self):
        """A member of the required group passes the check."""
        self._record()._check_pii_field_access("national_id")  # admin is in base.group_system

    def test_unrestricted_classified_field_is_allowed(self):
        """A classified field with no group requirement is open."""
        record = self._record().with_user(self.plain_user)
        record._check_pii_field_access("first_name")  # must not raise

    def test_unclassified_field_is_allowed(self):
        """An undeclared field has nothing to enforce."""
        record = self._record().with_user(self.plain_user)
        record._check_pii_field_access("unclassified_note")  # must not raise

    # ----------------------------------------------------------- access log

    def test_access_is_logged(self):
        """Reading a PII field leaves an entry naming who, what and when."""
        record = self._record()
        before = self.Log.search_count([])

        record._log_pii_access("national_id", "read")

        entries = self.Log.search([("record_id", "=", record.id)])
        self.assertEqual(self.Log.search_count([]), before + 1)
        self.assertEqual(entries.field_name, "national_id")
        self.assertEqual(entries.access_type, "read")
        self.assertEqual(entries.model_name, PII_MODEL)
        self.assertEqual(entries.user_id, self.env.user)

    def test_access_log_holds_no_pii_value(self):
        """The trail records that access happened, never what was read.

        Per docs/principles/data-privacy-and-pii.md an audit log that stored
        the value would turn the control into a second copy of the data.
        """
        record = self._record()
        record._log_pii_access("national_id", "read")

        entry = self.Log.search([("record_id", "=", record.id)], limit=1)
        stored = " ".join(str(v) for v in entry.read()[0].values())

        self.assertNotIn("123456789012", stored)
        self.assertNotIn("Juan Dela Cruz", stored)

    def test_logging_covers_every_record_in_the_set(self):
        """A multi-record access writes one entry per record."""
        records = self._record() | self._record()
        before = self.Log.search_count([])

        records._log_pii_access("first_name", "write")

        self.assertEqual(self.Log.search_count([]), before + 2)

    def test_logging_failure_never_breaks_the_operation(self):
        """A broken audit sink must not block a legitimate read.

        The mixin swallows logging errors deliberately: refusing the primary
        operation because the trail could not be written would take the
        system down rather than degrade it.
        """
        record = self._record()
        before = self.Log.search_count([])

        with patch.object(type(self.Log), "create", side_effect=Exception("audit sink down")):
            record._log_pii_access("national_id", "read")  # must not raise

        self.assertEqual(self.Log.search_count([]), before, "Nothing was logged, as intended")
        record._log_pii_access("national_id", "read")
        self.assertEqual(self.Log.search_count([]), before + 1, "Logging resumes once the sink recovers")
