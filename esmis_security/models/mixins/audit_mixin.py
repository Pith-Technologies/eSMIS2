import logging

from odoo import _, api, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class AuditMixin(models.AbstractModel):
    """Soft delete, legal hold, and archival tracking for auditable records.

    Provides controlled record lifecycle management required by RA 10173
    and CHED MORPHE. When a record is under legal hold, it cannot be
    archived or deleted — this prevents premature disposal during active
    investigations or regulatory audits.

    A model should inherit either ``esmis.audit.mixin`` (full tracking) or
    ``esmis.retention.aware`` (legal hold only), not both, as they share
    the ``legal_hold`` field.
    """

    _name = "esmis.audit.mixin"
    _description = "Audit Mixin"
    _inherit = ["mail.thread"]

    legal_hold = fields.Boolean(
        default=False,
        tracking=True,
        help="When enabled, prevents automated or manual disposal/archival of this record.",
    )
    legal_hold_reason = fields.Text(
        help="Reason for placing this record under legal hold.",
    )
    legal_hold_set_by = fields.Many2one(
        comodel_name="res.users",
        string="Hold Set By",
        readonly=True,
        help="User who placed the legal hold.",
    )
    archived_date = fields.Datetime(
        string="Archived On",
        readonly=True,
        help="Date and time when this record was archived.",
    )
    archived_by_id = fields.Many2one(
        comodel_name="res.users",
        string="Archived By",
        readonly=True,
        help="User who archived this record.",
    )
    archive_reason = fields.Text(
        help="Reason for archiving this record.",
    )

    def action_archive(self):
        """Archive records with audit tracking.

        Overrides Odoo's standard archive to record who archived and when.
        Records under legal hold cannot be archived.

        Raises:
            UserError: If any record in self is under legal hold.
        """
        for record in self:
            if record.legal_hold:
                raise UserError(
                    _("Record '%(name)s' is under legal hold and cannot be archived. " "Remove the legal hold first.")
                    % {"name": record.display_name}
                )
        self.write(
            {
                "active": False,
                "archived_date": fields.Datetime.now(),
                "archived_by_id": self.env.uid,
            }
        )
        return True

    def action_set_legal_hold(self, reason):
        """Place records under legal hold.

        Requires the DPO group. Records under legal hold cannot be archived
        or deleted until the hold is removed.

        Args:
            reason (str): Explanation for the legal hold.

        Raises:
            UserError: If no reason is provided.
        """
        if not reason or not reason.strip():
            raise UserError(_("A reason is required to place a legal hold."))
        self.write(
            {
                "legal_hold": True,
                "legal_hold_reason": reason,
                "legal_hold_set_by": self.env.uid,
            }
        )
        _logger.info(
            "Legal hold set on %s records of %s by user id=%s",
            len(self),
            self._name,
            self.env.uid,
        )

    def action_remove_legal_hold(self, resolution):
        """Remove legal hold from records.

        Requires the DPO group. The resolution documents why the hold
        was lifted.

        Args:
            resolution (str): Explanation for removing the hold.

        Raises:
            UserError: If no resolution is provided.
        """
        if not resolution or not resolution.strip():
            raise UserError(_("A resolution is required to remove a legal hold."))
        self.write(
            {
                "legal_hold": False,
                "legal_hold_reason": False,
                "legal_hold_set_by": False,
            }
        )
        _logger.info(
            "Legal hold removed from %s records of %s by user id=%s: %s",
            len(self),
            self._name,
            self.env.uid,
            resolution,
        )

    @api.ondelete(at_uninstall=False)
    def _check_legal_hold_before_delete(self):
        """Prevent deletion of records under legal hold."""
        for record in self:
            if record.legal_hold:
                raise UserError(
                    _("Record '%(name)s' is under legal hold and cannot be deleted. " "Remove the legal hold first.")
                    % {"name": record.display_name}
                )
