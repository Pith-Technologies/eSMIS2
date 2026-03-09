from odoo import fields, models


class PsgcCityMunicipality(models.Model):
    """Philippine Standard Geographic Code — City or Municipality.

    Third level in the PSGC hierarchy, under a province. Cities and
    municipalities share the same level in PSGC. The is_city flag
    distinguishes them for reporting and display purposes.
    """

    _name = "esmis.psgc.city.municipality"
    _description = "PSGC City / Municipality"
    _order = "name"

    name = fields.Char(string="Name", required=True)
    psgc_code = fields.Char(string="PSGC Code", required=True, index=True)
    province_id = fields.Many2one(
        comodel_name="esmis.psgc.province",
        string="Province",
        required=True,
        index=True,
        ondelete="restrict",
    )
    is_city = fields.Boolean(
        string="Is City",
        default=False,
        help="True for cities (component, independent, or highly urbanized), False for municipalities.",
    )
    zip_code = fields.Char(string="ZIP Code")

    _unique_psgc_code = models.Constraint("UNIQUE(psgc_code)", "PSGC code must be unique.")
