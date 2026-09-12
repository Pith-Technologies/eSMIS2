"""Behavioural tests for the `esmis.approval.mixin` state machine.

The existing tests in `test_approval_mixin.py` assert that the mixin's fields
and methods exist. These run the machine: every transition, every guard that
refuses one, the four-eyes rule, and the hooks an inheriting model overrides.
"""

from odoo.exceptions import UserError, ValidationError
from odoo.tests.common import TransactionCase

from .approval_test_model import build_test_model


class TestApprovalStateMachine(TransactionCase):
    """Drive the mixin through a concrete record."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.model_name = build_test_model(cls.env)
        cls.Record = cls.env[cls.model_name]

        users = cls.env["res.users"].with_context(no_reset_password=True, tracking_disable=True)
        cls.submitter = users.create(
            {"name": "Submitter", "login": "approval_sm_submitter", "password": "approval_sm_submitter"}
        )
        cls.approver = users.create(
            {"name": "Approver", "login": "approval_sm_approver", "password": "approval_sm_approver"}
        )

    def _record(self, **values):
        """A draft record, created as the submitter unless told otherwise."""
        values.setdefault("name", "Test record")
        return self.Record.with_user(self.submitter).create(values)

    def _pending(self):
        """A record already submitted by `self.submitter`."""
        record = self._record()
        record.action_submit_for_approval()
        return record

    # ------------------------------------------------------------------ submit

    def test_submit_from_draft(self):
        """Draft moves to pending and records who submitted it, and when."""
        record = self._record()
        self.assertEqual(record.approval_state, "draft")

        record.action_submit_for_approval()

        self.assertEqual(record.approval_state, "pending")
        self.assertEqual(record.submitted_by_id, self.submitter)
        self.assertTrue(record.submitted_date)

    def test_submit_calls_on_submit_hook_before_state_change(self):
        """_on_submit runs, and runs before the write that changes state."""
        record = self._record()
        record.action_submit_for_approval()
        self.assertEqual(record.hook_calls, "submit;")

    def test_submit_from_revision(self):
        """A record sent back for revision can be resubmitted."""
        record = self._pending()
        record.action_request_revision()
        self.assertEqual(record.approval_state, "revision")

        record.with_user(self.submitter).action_submit_for_approval()

        self.assertEqual(record.approval_state, "pending")

    def test_submit_from_pending_is_refused(self):
        """A pending record cannot be submitted again."""
        record = self._pending()
        with self.assertRaises(UserError):
            record.action_submit_for_approval()

    def test_submit_from_approved_is_refused(self):
        """An approved record cannot be resubmitted."""
        record = self._pending()
        record.with_user(self.approver).action_approve()
        with self.assertRaises(UserError):
            record.action_submit_for_approval()

    # ----------------------------------------------------------------- approve

    def test_approve_by_another_user(self):
        """Pending moves to approved and records the approver, and when."""
        record = self._pending()

        record.with_user(self.approver).action_approve()

        self.assertEqual(record.approval_state, "approved")
        self.assertEqual(record.approved_by_id, self.approver)
        self.assertTrue(record.approved_date)

    def test_approve_calls_on_approve_hook_after_state_change(self):
        """_on_approve runs after submit's hook, in order."""
        record = self._pending()
        record.with_user(self.approver).action_approve()
        self.assertEqual(record.hook_calls, "submit;approve;")

    def test_four_eyes_submitter_cannot_approve_own_record(self):
        """The submitter approving their own record is refused.

        This is the mixin's only substantive business rule, and the reason
        approval exists at all: one person must not be able to move a record
        through the whole chain alone.
        """
        record = self._pending()
        with self.assertRaises(UserError):
            record.with_user(self.submitter).action_approve()
        self.assertEqual(record.approval_state, "pending")

    def test_approve_from_draft_is_refused(self):
        """Only pending records can be approved."""
        record = self._record()
        with self.assertRaises(UserError):
            record.with_user(self.approver).action_approve()

    # ------------------------------------------------------------------ reject

    def test_reject_with_reason(self):
        """Pending moves to rejected, keeping the reason and the rejecter."""
        record = self._pending()

        record.with_user(self.approver).action_reject("Missing supporting document")

        self.assertEqual(record.approval_state, "rejected")
        self.assertEqual(record.rejected_by_id, self.approver)
        self.assertTrue(record.rejected_date)
        self.assertEqual(record.rejection_reason, "Missing supporting document")

    def test_reject_without_reason_is_refused(self):
        """A rejection reason is mandatory."""
        record = self._pending()
        with self.assertRaises(UserError):
            record.with_user(self.approver).action_reject("")
        self.assertEqual(record.approval_state, "pending")

    def test_reject_with_whitespace_reason_is_refused(self):
        """Whitespace is not a reason."""
        record = self._pending()
        with self.assertRaises(UserError):
            record.with_user(self.approver).action_reject("   \n\t ")

    def test_reject_from_draft_is_refused(self):
        """Only pending records can be rejected."""
        record = self._record()
        with self.assertRaises(UserError):
            record.with_user(self.approver).action_reject("Not pending")

    # ------------------------------------------------------------------- reset

    def test_reset_to_draft_clears_every_tracking_field(self):
        """Reset returns the record to a clean draft, losing no field."""
        record = self._pending()
        record.with_user(self.approver).action_reject("Needs work")

        record.action_reset_to_draft()

        self.assertEqual(record.approval_state, "draft")
        self.assertFalse(record.submitted_by_id)
        self.assertFalse(record.submitted_date)
        self.assertFalse(record.approved_by_id)
        self.assertFalse(record.approved_date)
        self.assertFalse(record.rejected_by_id)
        self.assertFalse(record.rejected_date)
        self.assertFalse(record.rejection_reason)

    def test_reset_from_approved_is_refused(self):
        """An approved record cannot be quietly reopened."""
        record = self._pending()
        record.with_user(self.approver).action_approve()
        with self.assertRaises(UserError):
            record.action_reset_to_draft()

    def test_reset_from_pending_is_refused(self):
        """Only rejected records can be reset."""
        record = self._pending()
        with self.assertRaises(UserError):
            record.action_reset_to_draft()

    # ---------------------------------------------------------------- revision

    def test_request_revision_from_pending(self):
        """Pending moves to revision without clearing the submission record."""
        record = self._pending()

        record.with_user(self.approver).action_request_revision()

        self.assertEqual(record.approval_state, "revision")
        self.assertEqual(record.submitted_by_id, self.submitter)

    def test_request_revision_from_draft_is_refused(self):
        """Only pending records can have a revision requested."""
        record = self._record()
        with self.assertRaises(UserError):
            record.with_user(self.approver).action_request_revision()

    # -------------------------------------------------------------- constraint

    def test_known_state_passes_the_constraint(self):
        """Every state the machine can reach satisfies the constraint."""
        record = self._record()
        for action, user in (
            ("action_submit_for_approval", self.submitter),
            ("action_request_revision", self.approver),
            ("action_submit_for_approval", self.submitter),
            ("action_approve", self.approver),
        ):
            getattr(record.with_user(user), action)()
            record._check_approval_state()

    def test_unknown_state_is_rejected(self):
        """A state outside the known set raises.

        Written through SQL because the Selection field refuses an unknown
        value long before the constraint would see it - the constraint exists
        to catch a value that reached the column some other way.
        """
        record = self._record()
        self.env.cr.execute(
            "UPDATE esmis_approval_test_record SET approval_state = 'bogus' WHERE id = %s",
            (record.id,),
        )
        record.invalidate_recordset(["approval_state"])

        with self.assertRaises(ValidationError):
            record._check_approval_state()

    # ------------------------------------------------------------- full cycles

    def test_revision_cycle_ends_approved(self):
        """draft -> pending -> revision -> pending -> approved."""
        record = self._record()
        record.action_submit_for_approval()
        record.with_user(self.approver).action_request_revision()
        record.with_user(self.submitter).action_submit_for_approval()
        record.with_user(self.approver).action_approve()

        self.assertEqual(record.approval_state, "approved")
        self.assertEqual(record.hook_calls, "submit;submit;approve;")

    def test_rejection_cycle_ends_approved(self):
        """draft -> pending -> rejected -> draft -> pending -> approved."""
        record = self._record()
        record.action_submit_for_approval()
        record.with_user(self.approver).action_reject("First attempt incomplete")
        record.action_reset_to_draft()
        record.with_user(self.submitter).action_submit_for_approval()
        record.with_user(self.approver).action_approve()

        self.assertEqual(record.approval_state, "approved")
        self.assertFalse(record.rejection_reason, "Reset must not leave the old reason behind")

    def test_multi_record_submit(self):
        """The actions iterate, so a multi-record set transitions together."""
        records = self._record(name="A") | self._record(name="B")

        records.action_submit_for_approval()

        self.assertEqual(set(records.mapped("approval_state")), {"pending"})
