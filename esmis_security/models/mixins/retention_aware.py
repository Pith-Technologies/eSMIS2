import logging

from odoo import _, api, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class RetentionAware(models.AbstractModel):
    """Lightweight legal hold mixin for retention-managed records.

    Use this on models that need legal hold protection but do not require
    full archival tracking. For models that need both legal hold and
    archival audit trail, use ``esmis.audit.mixin`` instead. A model
    should inherit one or the other, not both.
    """

    _name = "esmis.retention.aware"
    _description = "Retention Aware Mixin"

    legal_hold = fields.Boolean(
        default=False,
        help="When enabled, prevents automated disposal of this record.",
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

    @api.ondelete(at_uninstall=False)
    def _check_legal_hold_before_delete(self):
        """Prevent deletion of records under legal hold."""
        for record in self:
            if record.legal_hold:
                raise UserError(
                    _("Record '%(name)s' is under legal hold and cannot be deleted. " "Remove the legal hold first.")
                    % {"name": record.display_name}
                )
