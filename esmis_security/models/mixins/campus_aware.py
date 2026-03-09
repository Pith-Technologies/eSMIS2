import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)


class CampusAware(models.AbstractModel):
    """Campus isolation mixin using Odoo's multi-company mechanism.

    Inherit this mixin on any model that should be scoped to a single campus.
    Each campus is represented by a ``res.company`` record. The mixin adds a
    ``company_id`` field with a sensible default and index.

    The consuming module is responsible for defining the corresponding record
    rule in its own ``security/record_rules.xml``. The standard pattern is::

        <record id="rule_{model}_campus" model="ir.rule">
            <field name="name">{Model}: Campus Isolation</field>
            <field name="model_id" ref="model_{model}"/>
            <field name="domain_force">
                ['|', ('company_id', '=', False), ('company_id', 'in', company_ids)]
            </field>
            <field name="groups" eval="[Command.link(ref('base.group_user'))]"/>
        </record>
    """

    _name = "esmis.campus.aware"
    _description = "Campus Aware Mixin"

    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Campus",
        required=True,
        default=lambda self: self.env.company,
        index=True,
        help="Campus this record belongs to. Used for multi-campus record isolation.",
    )
