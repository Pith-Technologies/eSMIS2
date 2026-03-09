import logging

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class Address(models.Model):
    """Structured address linked to a contact.

    Supports multiple typed addresses per partner (permanent, mailing,
    residency, emergency). One address per type per partner is enforced
    via a SQL unique constraint. Only one address can be marked as primary
    at any time — setting a new primary automatically unflags the old one.

    Country-specific modules (e.g. esmis_ph) may extend this model with
    locale-specific geographic fields and override _compute_address_text
    to produce locale-appropriate formatting.
    """

    _name = "esmis.address"
    _description = "Structured address linked to a contact"
    _order = "is_primary desc, id"

    partner_id = fields.Many2one(
        comodel_name="res.partner",
        string="Contact",
        required=True,
        ondelete="cascade",
        index=True,
        help="Contact this address belongs to",
    )
    address_type_id = fields.Many2one(
        comodel_name="esmis.vocabulary.code",
        string="Address Type",
        required=True,
        domain=[("namespace_uri", "=", "urn:esmis:address-type")],
        help="Type of address (permanent, mailing, residency, emergency)",
    )
    is_primary = fields.Boolean(
        string="Primary",
        default=False,
        help="Mark this address as the primary address for the contact",
    )
    address_text = fields.Text(
        string="Address",
        compute="_compute_address_text",
        store=True,
        help="Full formatted address computed from individual components",
    )
    street1 = fields.Char(string="Street Line 1")
    street2 = fields.Char(string="Street Line 2")
    city = fields.Char(string="City / Municipality")
    state_province = fields.Char(string="State / Province")
    postal_code = fields.Char(string="Postal Code")
    country_id = fields.Many2one(
        comodel_name="res.country",
        string="Country",
    )
    notes = fields.Text(string="Notes")

    _unique_type_per_partner = models.Constraint(
        "UNIQUE(partner_id, address_type_id)",
        "Each address type can only appear once per contact.",
    )

    def _raise_if_duplicate_type(self, partner_id, address_type_id, exclude_id=None):
        """Raise ValidationError if a duplicate address type exists for the partner.

        Called from create() and write() before the SQL INSERT/UPDATE to
        give users a friendly error instead of a raw IntegrityError from the
        DB UNIQUE constraint.
        """
        domain = [
            ("partner_id", "=", partner_id),
            ("address_type_id", "=", address_type_id),
        ]
        if exclude_id:
            domain.append(("id", "!=", exclude_id))
        if self.search_count(domain):
            type_rec = self.env["esmis.vocabulary.code"].browse(address_type_id)
            raise ValidationError(
                _(
                    "Address type '%(type)s' already exists for this contact. "
                    "Each address type can only appear once per contact."
                )
                % {"type": type_rec.display}
            )

    @api.depends("street1", "street2", "city", "state_province", "postal_code", "country_id")
    def _compute_address_text(self):
        """Concatenate non-empty address components separated by ', '.

        Country modules may override this method to produce locale-specific
        address formatting.
        """
        for rec in self:
            parts = filter(
                None,
                [
                    rec.street1,
                    rec.street2,
                    rec.city,
                    rec.state_province,
                    rec.postal_code,
                    rec.country_id.name if rec.country_id else None,
                ],
            )
            rec.address_text = ", ".join(parts)

    def _unflag_existing_primary(self, partner_id, exclude_id=None):
        """Remove the primary flag from all existing primary addresses for a partner.

        Called before setting a new primary so that at most one address is
        flagged as primary at any time.
        """
        domain = [("partner_id", "=", partner_id), ("is_primary", "=", True)]
        if exclude_id:
            domain.append(("id", "!=", exclude_id))
        existing = self.search(domain)
        if existing:
            existing.write({"is_primary": False})

    @api.model_create_multi
    def create(self, vals_list):
        """Validate uniqueness and manage primary flag before creation.

        Checks for duplicate address type per partner before the SQL INSERT
        to produce a ValidationError instead of a raw IntegrityError. If
        is_primary=True, any existing primary for the same partner is unflagged.
        """
        for vals in vals_list:
            partner_id = vals.get("partner_id")
            address_type_id = vals.get("address_type_id")
            if partner_id and address_type_id:
                self._raise_if_duplicate_type(partner_id, address_type_id)
            if vals.get("is_primary") and partner_id:
                self._unflag_existing_primary(partner_id)
        return super().create(vals_list)

    def write(self, vals):
        """Validate uniqueness and manage primary flag on update.

        Checks for duplicate address type per partner before the SQL UPDATE
        when partner_id or address_type_id changes. If is_primary is set to
        True, any existing primary for the same partner is unflagged first.
        """
        new_partner_id = vals.get("partner_id")
        new_type_id = vals.get("address_type_id")
        if new_partner_id or new_type_id:
            for rec in self:
                partner_id = new_partner_id or rec.partner_id.id
                address_type_id = new_type_id or rec.address_type_id.id
                self._raise_if_duplicate_type(partner_id, address_type_id, exclude_id=rec.id)
        if vals.get("is_primary"):
            for rec in self:
                partner_id = vals.get("partner_id", rec.partner_id.id)
                self._unflag_existing_primary(partner_id, exclude_id=rec.id)
        return super().write(vals)
