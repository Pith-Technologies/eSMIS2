import logging

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)

PURPOSE_SELECTION = [
    ("consent_enrollment", "Enrollment Data Processing"),
    ("consent_ched_reporting", "CHED HEMIS/eCAV Submission"),
    ("consent_financial_aid", "Scholarship/Subsidy Eligibility"),
    ("consent_emergency_contact", "Emergency Data Sharing"),
    ("consent_alumni_tracking", "Post-graduation Contact"),
    ("consent_research", "Anonymized Institutional Research"),
    ("consent_lms_sync", "LMS Roster and Grade Sync"),
    ("consent_payment", "Payment Processor Data Sharing"),
    ("consent_philsys", "PhilSys Identity Verification"),
]

LAWFUL_BASIS_SELECTION = [
    ("consent", "Consent"),
    ("contract", "Contract"),
    ("legal_obligation", "Legal Obligation"),
    ("vital_interest", "Vital Interest"),
    ("legitimate_interest", "Legitimate Interest"),
]

EVIDENCE_TYPE_SELECTION = [
    ("electronic", "Electronic"),
    ("written", "Written"),
    ("verbal", "Verbal"),
]


class Consent(models.Model):
    """Per-student, per-purpose consent record under RA 10173.

    Tracks the lawful basis for processing a data subject's personal
    information. Records are never deleted; withdrawal is recorded by
    setting date_withdrawn.
    """

    _name = "esmis.consent"
    _description = "Consent Record"
    _inherit = ["mail.thread"]
    _order = "create_date desc"

    partner_id = fields.Many2one(
        comodel_name="res.partner",
        string="Data Subject",
        required=True,
        index=True,
        ondelete="restrict",
        help="The person whose data is being processed",
    )
    purpose = fields.Selection(
        selection=PURPOSE_SELECTION,
        required=True,
        index=True,
        tracking=True,
        help="The specific purpose for which consent is given",
    )
    lawful_basis = fields.Selection(
        selection=LAWFUL_BASIS_SELECTION,
        required=True,
        tracking=True,
        help="Legal basis under RA 10173 for processing this data",
    )
    date_given = fields.Datetime(
        string="Date Given",
        required=True,
        default=fields.Datetime.now,
        help="When this consent was obtained",
    )
    date_withdrawn = fields.Datetime(
        string="Date Withdrawn",
        tracking=True,
        help="Set when the data subject withdraws consent. Null indicates active consent.",
    )
    evidence_type = fields.Selection(
        selection=EVIDENCE_TYPE_SELECTION,
        string="Evidence Type",
        help="How consent was obtained (required when lawful basis is Consent)",
    )
    evidence_ref = fields.Many2one(
        comodel_name="ir.attachment",
        string="Evidence",
        help="Supporting document or attachment proving consent was obtained",
    )
    captured_by = fields.Many2one(
        comodel_name="res.users",
        string="Captured By",
        default=lambda self: self.env.user,
        help="Staff member who recorded this consent",
    )
    ip_address = fields.Char(
        string="IP Address",
        help="IP address from which electronic consent was submitted",
    )
    form_version = fields.Char(
        string="Form Version",
        help="Version of the consent form used when collecting this consent",
    )
    is_active = fields.Boolean(
        string="Active",
        compute="_compute_is_active",
        store=True,
        help="True when consent has not been withdrawn",
    )
    is_parent_consent = fields.Boolean(
        string="Parent/Guardian Consent",
        default=False,
        help="True when this consent is given by a parent or guardian on behalf of a minor",
    )
    scope_ids = fields.One2many(
        comodel_name="esmis.consent.scope",
        inverse_name="consent_id",
        string="Scopes",
        help="Fine-grained scope definitions within this consent",
    )

    @api.depends("date_withdrawn")
    def _compute_is_active(self):
        """Compute whether consent is currently active.

        Consent is active when date_withdrawn has not been set.
        """
        for record in self:
            record.is_active = not bool(record.date_withdrawn)

    @api.constrains("partner_id", "purpose", "date_withdrawn")
    def _check_active_consent_unique(self):
        """Enforce one active consent per partner per purpose.

        A data subject may not have two simultaneously active consent
        records for the same purpose. Withdrawn consents (date_withdrawn
        is set) are excluded from this check.
        """
        for record in self:
            if record.date_withdrawn:
                # Withdrawn consent does not need to be unique.
                continue
            duplicate = self.search_count(
                [
                    ("partner_id", "=", record.partner_id.id),
                    ("purpose", "=", record.purpose),
                    ("date_withdrawn", "=", False),
                    ("id", "!=", record.id),
                ]
            )
            if duplicate:
                raise ValidationError(
                    _(
                        "An active consent record already exists for this data subject "
                        "and purpose. Withdraw the existing record before creating a new one."
                    )
                )

    @api.constrains("lawful_basis", "evidence_type")
    def _check_evidence_type_required(self):
        """Require evidence_type when lawful_basis is 'consent'.

        When the legal basis is the data subject's explicit consent,
        evidence of how that consent was obtained must be recorded.
        """
        for record in self:
            if record.lawful_basis == "consent" and not record.evidence_type:
                raise ValidationError(
                    _(
                        "Evidence type is required when the lawful basis is 'Consent'. "
                        "Please indicate whether consent was obtained electronically, "
                        "in writing, or verbally."
                    )
                )

    def action_withdraw(self):
        """Withdraw consent for this record.

        Sets date_withdrawn to the current datetime. Consent records are
        never deleted; withdrawal creates an auditable trail.
        """
        self.ensure_one()
        if self.date_withdrawn:
            raise UserError(_("This consent record has already been withdrawn."))
        self.write({"date_withdrawn": fields.Datetime.now()})
        _logger.info(
            "Consent record %s withdrawn by user %s",
            self.id,
            self.env.user.id,
        )
