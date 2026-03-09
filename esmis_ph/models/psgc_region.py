from odoo import fields, models


class PsgcRegion(models.Model):
    """Philippine Standard Geographic Code — Region.

    Top-level geographic unit in the PSGC hierarchy. The PSA assigns each
    region a unique 9-digit code. This model stores the authoritative list
    used for address validation and CHED HEMIS reporting.
    """

    _name = "esmis.psgc.region"
    _description = "PSGC Region"
    _order = "psgc_code"

    name = fields.Char(string="Name", required=True)
    psgc_code = fields.Char(string="PSGC Code", required=True, index=True)
    designation = fields.Char(
        string="Designation",
        help="Full official designation (e.g., 'National Capital Region')",
    )

    _unique_psgc_code = models.Constraint("UNIQUE(psgc_code)", "PSGC code must be unique.")
