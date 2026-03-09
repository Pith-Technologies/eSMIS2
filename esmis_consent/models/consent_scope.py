import logging

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class ConsentScope(models.Model):
    """Fine-grained scope definition within a consent record.

    A consent record may cover multiple data categories or third-party
    recipients. Each scope line captures one such element, with an
    optional expiry date for time-limited grants.
    """

    _name = "esmis.consent.scope"
    _description = "Consent Scope"
    _order = "consent_id, resource_type"

    consent_id = fields.Many2one(
        comodel_name="esmis.consent",
        string="Consent",
        required=True,
        ondelete="cascade",
        index=True,
        help="The parent consent record this scope belongs to",
    )
    resource_type = fields.Char(
        string="Resource Type",
        required=True,
        help="Type of resource covered (Odoo model name or data category label)",
    )
    purpose = fields.Char(
        string="Sub-Purpose",
        help="Specific sub-purpose within the parent consent",
    )
    third_party_id = fields.Many2one(
        comodel_name="res.partner",
        string="Third Party",
        help="External party authorised to receive data under this scope",
    )
    valid_until = fields.Date(
        string="Valid Until",
        help="Expiry date for this scope. After this date the scope is no longer valid.",
    )

    @api.constrains("valid_until")
    def _check_valid_until(self):
        """Validate that valid_until is not in the past when set."""
        today = fields.Date.today()
        for record in self:
            if record.valid_until and record.valid_until < today:
                raise ValidationError(
                    _("The expiry date for scope '%(resource)s' cannot be in the past.")
                    % {"resource": record.resource_type}
                )
