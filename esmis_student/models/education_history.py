import logging

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class EducationHistory(models.Model):
    """Educational background record for a student.

    Tracks the institutions a student attended at each education level
    (pre-school through post-graduate). Ordered by education level
    sequence so the list always shows from lowest to highest level.

    Country modules (e.g. esmis_ph) may extend this model to add
    locale-specific fields such as school classification or LRN.
    """

    _name = "esmis.education.history"
    _description = "Educational background record"
    _order = "education_level_sequence, id"

    partner_id = fields.Many2one(
        comodel_name="res.partner",
        string="Student",
        required=True,
        ondelete="cascade",
        index=True,
    )
    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Campus",
        related="partner_id.company_id",
        store=True,
        index=True,
    )
    education_level_id = fields.Many2one(
        comodel_name="esmis.vocabulary.code",
        string="Education Level",
        required=True,
        domain=[("namespace_uri", "=", "urn:esmis:education-level")],
    )
    education_level_sequence = fields.Integer(
        string="Level Sequence",
        related="education_level_id.sequence",
        store=True,
        help="Sequence value from the education level code, used for ordering",
    )
    school_name = fields.Char(
        string="School / Institution",
        required=True,
    )
    school_address = fields.Char(string="School Address")
    year_started = fields.Integer(string="Year Started")
    year_graduated = fields.Integer(string="Year Completed")
    honors_received = fields.Char(string="Honors / Awards")
    is_graduated = fields.Boolean(
        string="Completed",
        default=False,
        help="Whether the student completed or graduated from this level",
    )

    @api.constrains("year_started", "year_graduated")
    def _check_year_range(self):
        """Require year_graduated >= year_started when both are provided."""
        for rec in self:
            if rec.year_started and rec.year_graduated and rec.year_graduated < rec.year_started:
                raise ValidationError(
                    _("Year completed (%(graduated)s) cannot be earlier than year started (%(started)s).")
                    % {
                        "graduated": rec.year_graduated,
                        "started": rec.year_started,
                    }
                )
