import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    """Extend res.partner with structured addresses."""

    _inherit = "res.partner"

    address_ids = fields.One2many(
        comodel_name="esmis.address",
        inverse_name="partner_id",
        string="Addresses",
        help="Structured addresses linked to this contact",
    )
    primary_address_text = fields.Text(
        string="Primary Address",
        compute="_compute_primary_address_text",
        help="Formatted text of the primary address",
    )

    @api.depends("address_ids", "address_ids.is_primary", "address_ids.address_text")
    def _compute_primary_address_text(self):
        """Return the address_text of the first primary address, or empty string."""
        for partner in self:
            primary = partner.address_ids.filtered("is_primary")[:1]
            partner.primary_address_text = primary.address_text if primary else ""
