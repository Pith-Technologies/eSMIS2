from odoo import api, fields, models


class EsmisAddress(models.Model):
    """Philippine address extensions on esmis.address.

    Adds PSGC geographic hierarchy fields (region → province →
    city/municipality → barangay) with cascading onchange methods that
    clear child selections when a parent changes.

    When region_id is set, _compute_address_text produces a Philippine
    address string instead of the generic base format. The zip_code field
    is derived from the selected city/municipality.
    """

    _inherit = "esmis.address"

    region_id = fields.Many2one(
        comodel_name="esmis.psgc.region",
        string="Region",
        index=True,
    )
    province_id = fields.Many2one(
        comodel_name="esmis.psgc.province",
        string="Province",
        index=True,
        domain="[('region_id', '=', region_id)]",
    )
    city_municipality_id = fields.Many2one(
        comodel_name="esmis.psgc.city.municipality",
        string="City / Municipality",
        index=True,
        domain="[('province_id', '=', province_id)]",
    )
    barangay_id = fields.Many2one(
        comodel_name="esmis.psgc.barangay",
        string="Barangay",
        index=True,
        domain="[('city_municipality_id', '=', city_municipality_id)]",
    )
    zip_code = fields.Char(
        string="ZIP Code",
        related="city_municipality_id.zip_code",
        store=True,
    )

    @api.depends(
        "street1",
        "street2",
        "city",
        "state_province",
        "postal_code",
        "country_id",
        "region_id",
        "province_id",
        "city_municipality_id",
        "barangay_id",
        "zip_code",
    )
    def _compute_address_text(self):
        """Produce a Philippine address string when region_id is set.

        PH format: street1, street2, barangay, city/municipality, province,
        region, zip_code — joined by ', ', skipping blank components.

        Falls back to the base implementation when region_id is not set
        so that non-PH addresses continue to work correctly.
        """
        for rec in self:
            if rec.region_id:
                parts = filter(
                    None,
                    [
                        rec.street1,
                        rec.street2,
                        rec.barangay_id.name,
                        rec.city_municipality_id.name,
                        rec.province_id.name,
                        rec.region_id.name,
                        rec.zip_code,
                    ],
                )
                rec.address_text = ", ".join(parts)
            else:
                super(EsmisAddress, rec)._compute_address_text()

    @api.onchange("region_id")
    def _onchange_region_id(self):
        """Clear province and all dependent fields when region changes."""
        self.province_id = False
        self.city_municipality_id = False
        self.barangay_id = False

    @api.onchange("province_id")
    def _onchange_province_id(self):
        """Clear city/municipality and barangay when province changes."""
        self.city_municipality_id = False
        self.barangay_id = False

    @api.onchange("city_municipality_id")
    def _onchange_city_municipality_id(self):
        """Clear barangay when city/municipality changes."""
        self.barangay_id = False
