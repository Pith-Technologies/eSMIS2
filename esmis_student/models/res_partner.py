import logging

from dateutil.relativedelta import relativedelta

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)

STUDENT_STATES = [
    ("applicant", "Applicant"),
    ("admitted", "Admitted"),
    ("enrolled", "Enrolled"),
    ("active", "Active"),
    ("loa", "Leave of Absence"),
    ("graduated", "Graduated"),
    ("alumni", "Alumni"),
    ("dismissed", "Dismissed"),
    ("transferred_out", "Transferred Out"),
    ("denied", "Denied"),
]

# Maps each state to the set of states it may transition into.
VALID_TRANSITIONS = {
    "applicant": {"admitted", "denied"},
    "admitted": {"enrolled", "denied"},
    "enrolled": {"active"},
    "active": {"enrolled", "loa", "graduated", "dismissed", "transferred_out"},
    "loa": {"enrolled", "dismissed"},
    "graduated": {"alumni"},
    "alumni": set(),
    "dismissed": set(),
    "transferred_out": set(),
    "denied": set(),
}


class ResPartner(models.Model):
    """Extends res.partner with student demographics and lifecycle state.

    Adds all student-specific fields (name components, demographics, guardian,
    identifiers, education history) and enforces the student state machine.
    Campus isolation is handled via record rules on company_id (already present
    on res.partner from Odoo core).

    Only partners with is_student=True are affected by the student-specific
    display name logic; all other partners use Odoo's default computation.
    """

    _inherit = "res.partner"

    # --- Identity flags ---
    is_student = fields.Boolean(
        string="Is Student",
        default=False,
        index=True,
        help="Mark this contact as a student. Activates student-specific fields and workflows.",
    )
    student_number = fields.Char(
        string="Student Number",
        copy=False,
        index=True,
        help="Institution-assigned student number. Must be unique across the campus.",
    )

    # --- Name components ---
    first_name = fields.Char(string="First Name")
    last_name = fields.Char(string="Last Name")
    middle_name = fields.Char(string="Middle Name")

    # --- Demographics ---
    birthdate = fields.Date(string="Date of Birth")
    birthplace = fields.Char(string="Place of Birth")
    age = fields.Integer(
        string="Age",
        compute="_compute_age",
        store=True,
        help="Age in years, computed from birthdate. Recomputed daily via cron.",
    )
    gender_id = fields.Many2one(
        comodel_name="esmis.vocabulary.code",
        string="Gender",
        domain=[("namespace_uri", "=", "urn:iso:std:iso:5218")],
        help="Gender code per ISO 5218",
    )
    civil_status_id = fields.Many2one(
        comodel_name="esmis.vocabulary.code",
        string="Civil Status",
        domain=[("namespace_uri", "=", "urn:un:unsd:pop-census:marital-status")],
    )
    nationality_id = fields.Many2one(
        comodel_name="res.country",
        string="Nationality",
    )
    blood_type_id = fields.Many2one(
        comodel_name="esmis.vocabulary.code",
        string="Blood Type",
        domain=[("namespace_uri", "=", "urn:tpl:vocab:blood-type")],
    )
    disability_type_id = fields.Many2one(
        comodel_name="esmis.vocabulary.code",
        string="Disability Type",
        domain=[("namespace_uri", "=", "urn:esmis:vocabulary:disability-type")],
        help="PWD classification per RA 7277/10754",
    )
    is_pwd = fields.Boolean(
        string="Person with Disability",
        default=False,
        help="Flag for Person with Disability (PWD) status per RA 7277/10754",
    )
    is_indigenous_people = fields.Boolean(
        string="Indigenous Peoples Member",
        default=False,
        help="Flag for Indigenous Peoples affiliation per IPRA RA 8371",
    )

    # --- Guardian (required for minors) ---
    guardian_id = fields.Many2one(
        comodel_name="res.partner",
        string="Parent / Guardian",
        help="Parent or guardian for students under 18 years of age",
    )
    guardian_relationship_id = fields.Many2one(
        comodel_name="esmis.vocabulary.code",
        string="Relationship to Guardian",
        domain=[("namespace_uri", "=", "urn:esmis:vocabulary:relationship-type")],
    )

    # --- Lifecycle state ---
    student_state = fields.Selection(
        selection=STUDENT_STATES,
        string="Student Status",
        default="applicant",
        tracking=True,
        help="Current stage in the student lifecycle.",
    )

    # --- Related records ---
    identifier_ids = fields.One2many(
        comodel_name="esmis.identifier",
        inverse_name="partner_id",
        string="Identifiers",
    )
    education_history_ids = fields.One2many(
        comodel_name="esmis.education.history",
        inverse_name="partner_id",
        string="Education History",
    )

    # --- PII field classification (used by esmis.pii.aware mixin consumers) ---
    _pii_fields = {
        "first_name": {"tier": 1, "masking_pattern": None, "groups": None},
        "last_name": {"tier": 1, "masking_pattern": None, "groups": None},
        "middle_name": {"tier": 1, "masking_pattern": None, "groups": None},
        "birthdate": {
            "tier": 2,
            "masking_pattern": "****-**-##",
            "groups": "esmis_security.group_esmis_security_officer",
        },
        "birthplace": {"tier": 1, "masking_pattern": None, "groups": None},
        "guardian_id": {
            "tier": 2,
            "masking_pattern": None,
            "groups": "esmis_security.group_esmis_security_officer",
        },
    }

    # --- Computed fields ---

    @api.depends("birthdate")
    def _compute_age(self):
        """Compute age in whole years from birthdate. Returns 0 when not set."""
        today = fields.Date.today()
        for partner in self:
            partner.age = 0
            if partner.birthdate:
                partner.age = relativedelta(today, partner.birthdate).years

    def _compute_display_name(self):
        """Override display name for student partners.

        When is_student=True and last_name is set, formats as:
            LAST_NAME, FIRST_NAME MIDDLE_NAME
        Otherwise delegates to the standard Odoo display name computation.

        Country modules may extend this method by overriding
        _get_student_display_name to inject locale-specific formatting.
        """
        for partner in self:
            if partner.is_student and partner.last_name:
                partner.display_name = partner._get_student_display_name()
            else:
                super(ResPartner, partner)._compute_display_name()

    def _get_student_display_name(self):
        """Return the formatted student display name.

        Default format: "LAST_NAME, FIRST_NAME MIDDLE_NAME"
        Override in country modules (e.g. esmis_ph) to add suffixes or
        locale-specific formatting.
        """
        self.ensure_one()
        parts = [self.last_name + ",", self.first_name]
        if self.middle_name:
            parts.append(self.middle_name)
        return " ".join(filter(None, parts))

    # --- Constraints ---

    @api.constrains("birthdate", "guardian_id", "is_student")
    def _check_guardian_required_for_minors(self):
        """Require guardian_id when a student is under 18 years of age."""
        today = fields.Date.today()
        for partner in self:
            if not partner.is_student or not partner.birthdate:
                continue
            delta = relativedelta(today, partner.birthdate)
            if delta.years < 18 and not partner.guardian_id:
                raise ValidationError(
                    _(
                        "A parent or guardian is required for students under 18 years of age. "
                        "Please set the 'Parent / Guardian' field."
                    )
                )

    @api.constrains("student_number", "company_id", "is_student")
    def _check_student_number_unique(self):
        """Enforce campus-scoped uniqueness of the student number."""
        for partner in self:
            if not partner.is_student or not partner.student_number:
                continue
            duplicate = self.search_count(
                [
                    ("student_number", "=", partner.student_number),
                    ("company_id", "=", partner.company_id.id),
                    ("id", "!=", partner.id),
                    ("is_student", "=", True),
                ]
            )
            if duplicate:
                raise ValidationError(
                    _("Student number '%(number)s' is already assigned to another student at this campus.")
                    % {"number": partner.student_number}
                )

    # --- State machine ---

    def write(self, vals):
        """Enforce valid state transitions before persisting changes."""
        new_state = vals.get("student_state")
        if new_state:
            for partner in self:
                if not partner.is_student and not vals.get("is_student"):
                    continue
                old_state = partner.student_state
                if old_state and old_state != new_state:
                    allowed = VALID_TRANSITIONS.get(old_state, set())
                    if new_state not in allowed:
                        raise UserError(
                            _(
                                "Cannot change student status from '%(from_state)s' to '%(to_state)s'. "
                                "Allowed transitions: %(allowed)s."
                            )
                            % {
                                "from_state": dict(STUDENT_STATES).get(old_state, old_state),
                                "to_state": dict(STUDENT_STATES).get(new_state, new_state),
                                "allowed": ", ".join(dict(STUDENT_STATES).get(s, s) for s in sorted(allowed))
                                or _("none"),
                            }
                        )
        return super().write(vals)
