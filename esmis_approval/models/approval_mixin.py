import logging

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class ApprovalMixin(models.AbstractModel):
    """Standardized approval workflow for eSMIS models.

    Inherit this mixin to add a consistent approval state machine to any
    model. Provides four-eyes enforcement (submitter cannot self-approve),
    a full audit trail of who acted and when, and hook methods for
    customizing validation and post-approval logic.

    State machine:
        draft → pending → approved
                  ↓             (terminal)
               rejected → draft (reset)
                  ↓
               revision → pending (resubmit)
    """

    _name = "esmis.approval.mixin"
    _description = "Approval Mixin"

    approval_state = fields.Selection(
        selection=[
            ("draft", "Draft"),
            ("pending", "Pending"),
            ("approved", "Approved"),
            ("rejected", "Rejected"),
            ("revision", "Revision Requested"),
        ],
        default="draft",
        tracking=True,
        help="Current state in the approval workflow.",
    )
    submitted_by_id = fields.Many2one(
        comodel_name="res.users",
        string="Submitted By",
        readonly=True,
        help="User who submitted this record for approval.",
    )
    submitted_date = fields.Datetime(
        string="Submitted On",
        readonly=True,
        help="Date and time when this record was submitted for approval.",
    )
    approved_by_id = fields.Many2one(
        comodel_name="res.users",
        string="Approved By",
        readonly=True,
        help="User who approved this record.",
    )
    approved_date = fields.Datetime(
        string="Approved On",
        readonly=True,
        help="Date and time when this record was approved.",
    )
    rejected_by_id = fields.Many2one(
        comodel_name="res.users",
        string="Rejected By",
        readonly=True,
        help="User who rejected this record.",
    )
    rejected_date = fields.Datetime(
        string="Rejected On",
        readonly=True,
        help="Date and time when this record was rejected.",
    )
    rejection_reason = fields.Text(
        string="Rejection Reason",
        readonly=True,
        help="Reason provided by the reviewer when rejecting this record.",
    )

    def action_submit_for_approval(self):
        """Submit this record for approval.

        Transitions from 'draft' or 'revision' to 'pending'. Records the
        submitting user and timestamp, then calls _on_submit() so inheriting
        models can add custom validation before the state changes.

        Raises:
            UserError: If the record is not in a submittable state.
        """
        for record in self:
            if record.approval_state not in ("draft", "revision"):
                raise UserError(
                    _("Only records in Draft or Revision Requested state can be submitted. (ID: %(id)s)")
                    % {"id": record.id}
                )
            record._on_submit()
            record.write(
                {
                    "approval_state": "pending",
                    "submitted_by_id": self.env.uid,
                    "submitted_date": fields.Datetime.now(),
                }
            )
            _logger.info(
                "Record %s (id=%s) submitted for approval by uid=%s",
                record._name,
                record.id,
                self.env.uid,
            )

    def action_approve(self):
        """Approve this record.

        Transitions from 'pending' to 'approved'. Enforces the four-eyes
        principle: the approver must not be the same user who submitted.
        Records the approving user and timestamp, then calls _on_approve().

        Raises:
            UserError: If the record is not pending, or if the approver is
                       the same user who submitted (four-eyes violation).
        """
        for record in self:
            if record.approval_state != "pending":
                raise UserError(
                    _("Only records in Pending state can be approved. (ID: %(id)s)") % {"id": record.id}
                )
            if record.submitted_by_id and record.submitted_by_id.id == self.env.uid:
                raise UserError(
                    _(
                        "The approver cannot be the same user who submitted this record. "
                        "A different user must approve (four-eyes principle)."
                    )
                )
            record.write(
                {
                    "approval_state": "approved",
                    "approved_by_id": self.env.uid,
                    "approved_date": fields.Datetime.now(),
                }
            )
            record._on_approve()
            _logger.info(
                "Record %s (id=%s) approved by user id=%s",
                record._name,
                record.id,
                self.env.uid,
            )

    def action_reject(self, reason):
        """Reject this record with a mandatory reason.

        Transitions from 'pending' to 'rejected'. Records the rejecting user,
        timestamp, and the reason.

        Args:
            reason (str): Human-readable explanation for the rejection.

        Raises:
            UserError: If the record is not pending, or if no reason is given.
        """
        if not reason or not reason.strip():
            raise UserError(_("A rejection reason is required."))
        for record in self:
            if record.approval_state != "pending":
                raise UserError(
                    _("Only records in Pending state can be rejected. (ID: %(id)s)") % {"id": record.id}
                )
            record.write(
                {
                    "approval_state": "rejected",
                    "rejected_by_id": self.env.uid,
                    "rejected_date": fields.Datetime.now(),
                    "rejection_reason": reason,
                }
            )
            _logger.info(
                "Record %s (id=%s) rejected by user id=%s",
                record._name,
                record.id,
                self.env.uid,
            )

    def action_reset_to_draft(self):
        """Reset a rejected record back to draft.

        Clears all approval tracking fields so the record can be corrected
        and resubmitted. Only records in 'rejected' state may be reset.

        Raises:
            UserError: If the record is not in 'rejected' state.
        """
        for record in self:
            if record.approval_state != "rejected":
                raise UserError(
                    _("Only rejected records can be reset to draft. (ID: %(id)s)") % {"id": record.id}
                )
            record.write(
                {
                    "approval_state": "draft",
                    "submitted_by_id": False,
                    "submitted_date": False,
                    "approved_by_id": False,
                    "approved_date": False,
                    "rejected_by_id": False,
                    "rejected_date": False,
                    "rejection_reason": False,
                }
            )
            _logger.info(
                "Record %s (id=%s) reset to draft by user id=%s",
                record._name,
                record.id,
                self.env.uid,
            )

    def action_request_revision(self):
        """Request a revision from the submitter.

        Transitions from 'pending' to 'revision'. The submitter can then
        update the record and call action_submit_for_approval() again.

        Raises:
            UserError: If the record is not pending.
        """
        for record in self:
            if record.approval_state != "pending":
                raise UserError(
                    _("Only records in Pending state can have a revision requested. (ID: %(id)s)")
                    % {"id": record.id}
                )
            record.write({"approval_state": "revision"})
            _logger.info(
                "Revision requested for record %s (id=%s) by user id=%s",
                record._name,
                record.id,
                self.env.uid,
            )

    def _on_submit(self):
        """Hook called before the approval state changes to 'pending'.

        Override in inheriting models to add custom validation. Raise
        ValidationError to block submission. The default implementation
        does nothing.
        """

    def _on_approve(self):
        """Hook called after the approval state changes to 'approved'.

        Override in inheriting models to trigger post-approval logic
        (e.g., sending notifications, updating related records). The
        default implementation does nothing.
        """

    @api.constrains("approval_state")
    def _check_approval_state(self):
        """Validate that approval_state holds a known value."""
        valid = {"draft", "pending", "approved", "rejected", "revision"}
        for record in self:
            if record.approval_state not in valid:
                raise ValidationError(
                    _("Unknown approval state '%(state)s'.") % {"state": record.approval_state}
                )
