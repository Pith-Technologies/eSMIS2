from odoo import fields, models


class PsgcBarangay(models.Model):
    """Philippine Standard Geographic Code — Barangay.

    Lowest level in the PSGC hierarchy, under a city or municipality.
    The full dataset (~42,000 records) is loaded via post_init_hook
    using bulk SQL rather than ORM to keep install time reasonable.
    """

    _name = "esmis.psgc.barangay"
    _description = "PSGC Barangay"
    _order = "name"

    name = fields.Char(string="Name", required=True)
    psgc_code = fields.Char(string="PSGC Code", required=True, index=True)
    city_municipality_id = fields.Many2one(
        comodel_name="esmis.psgc.city.municipality",
        string="City / Municipality",
        required=True,
        index=True,
        ondelete="restrict",
    )

    _unique_psgc_code = models.Constraint("UNIQUE(psgc_code)", "PSGC code must be unique.")
