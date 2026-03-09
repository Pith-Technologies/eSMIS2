from odoo import fields, models


class PsgcProvince(models.Model):
    """Philippine Standard Geographic Code — Province.

    Second level in the PSGC hierarchy, under a region. Highly urbanized
    cities (HUCs) are classified at the province level for PSGC purposes.
    """

    _name = "esmis.psgc.province"
    _description = "PSGC Province"
    _order = "name"

    name = fields.Char(string="Name", required=True)
    psgc_code = fields.Char(string="PSGC Code", required=True, index=True)
    region_id = fields.Many2one(
        comodel_name="esmis.psgc.region",
        string="Region",
        required=True,
        index=True,
        ondelete="restrict",
    )

    _unique_psgc_code = models.Constraint("UNIQUE(psgc_code)", "PSGC code must be unique.")
