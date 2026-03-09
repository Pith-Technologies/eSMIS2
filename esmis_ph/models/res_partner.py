from odoo import api, fields, models


class ResPartner(models.Model):
    """Philippine-specific extensions to res.partner.

    Adds fields required for Philippine HEI student records:
    - Maiden surname (used as middle name after marriage per PH convention)
    - Name suffixes (Jr., Sr., PhD, etc.)
    - Ethnicity and religion from PH vocabulary codes
    - Solo Parent status (RA 8972/11861 scholarship eligibility)
    - 4Ps beneficiary flag (Pantawid Pamilyang Pilipino Program)

    Also overrides _get_student_display_name() to produce the standard
    Philippine name format: LAST NAME, FIRST NAME M. SUFFIX
    where M. is the middle initial derived from middle_name_b4_marriage
    (if set) or middle_name.
    """

    _inherit = "res.partner"

    middle_name_b4_marriage = fields.Char(
        string="Middle Name (Before Marriage)",
        help="Woman's maiden surname, which becomes the middle name after marriage per Philippine naming convention.",
    )
    suffix_ids = fields.Many2many(
        comodel_name="esmis.vocabulary.code",
        relation="res_partner_suffix_rel",
        column1="partner_id",
        column2="suffix_id",
        string="Name Suffixes",
        domain="[('namespace_uri', '=', 'urn:esmis:name-suffix')]",
    )
    ethnicity_id = fields.Many2one(
        comodel_name="esmis.vocabulary.code",
        string="Ethnicity",
        domain="[('namespace_uri', '=', 'urn:esmis:ethnicity-ph')]",
    )
    religion_id = fields.Many2one(
        comodel_name="esmis.vocabulary.code",
        string="Religion",
        domain="[('namespace_uri', '=', 'urn:esmis:religion-ph')]",
    )
    is_solo_parent = fields.Boolean(
        string="Solo Parent",
        default=False,
        help="Solo Parent per RA 8972/11861. Eligible for scholarship programs.",
    )
    is_4ps_beneficiary = fields.Boolean(
        string="4Ps Beneficiary",
        default=False,
        help="Pantawid Pamilyang Pilipino Program (4Ps) beneficiary.",
    )

    # --- PII field classification ---
    # Ethnicity and religion are SPI per RA 10173 Section 3(l).
    _pii_fields = {
        "ethnicity_id": {"tier": 3, "masking_pattern": None, "groups": "esmis_student.group_esmis_registrar_officer"},
        "religion_id": {"tier": 3, "masking_pattern": None, "groups": "esmis_student.group_esmis_registrar_officer"},
        "middle_name_b4_marriage": {"tier": 1, "masking_pattern": None, "groups": None},
    }

    def _get_student_display_name(self):
        """Return student display name in Philippine name format.

        Format: "LAST_NAME, FIRST_NAME M. SUFFIX"
        - M. is the first letter of middle_name_b4_marriage (if set) or middle_name
        - SUFFIX is the comma-joined list of suffix_ids display labels

        Falls back to the base implementation when PH-specific fields are not set.
        """
        self.ensure_one()
        parts = [self.last_name + ",", self.first_name]
        mi_source = self.middle_name_b4_marriage or self.middle_name
        if mi_source:
            parts.append(mi_source[0] + ".")
        if self.suffix_ids:
            parts.append(", ".join(self.suffix_ids.mapped("display")))
        return " ".join(filter(None, parts))

    @api.depends(
        "first_name",
        "last_name",
        "middle_name",
        "middle_name_b4_marriage",
        "suffix_ids",
        "is_student",
    )
    def _compute_display_name(self):
        """Override to include PH-specific fields in display name dependency tracking."""
        super()._compute_display_name()
