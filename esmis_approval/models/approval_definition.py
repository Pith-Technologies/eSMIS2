import logging

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class ApprovalDefinition(models.Model):
    """Multi-stage approval chain definition.

    Defines the approval workflow configuration that applies to a specific
    Odoo model. Phase 1 captures the definition; full routing logic and
    stage management are implemented in Phase 2.
    """

    _name = "esmis.approval.definition"
    _description = "Approval Definition"
    _order = "name"

    name = fields.Char(
        required=True,
        help="Descriptive name for this approval definition",
    )
    model_id = fields.Many2one(
        comodel_name="ir.model",
        string="Model",
        required=True,
        ondelete="cascade",
        index=True,
        help="The Odoo model this approval definition applies to",
    )
    active = fields.Boolean(
        default=True,
        help="Set to inactive to disable this approval definition without deleting it",
    )

    _unique_model = models.Constraint(
        "UNIQUE(model_id)",
        "Only one approval definition may be active per model",
    )

    @api.constrains("model_id")
    def _check_model_id(self):
        """Prevent defining approval workflows on transient models.

        Transient models (wizards) are session-scoped and do not persist,
        making approval workflows meaningless for them.
        """
        for record in self:
            if record.model_id and record.model_id.transient:
                raise ValidationError(
                    _(
                        "Approval definitions cannot be applied to transient models "
                        "(wizards). Choose a regular model."
                    )
                )
