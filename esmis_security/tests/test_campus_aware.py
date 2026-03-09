from odoo.tests.common import TransactionCase


class TestCampusAware(TransactionCase):
    """Tests for the esmis.campus.aware abstract mixin."""

    def test_mixin_registered(self):
        """The campus aware mixin is registered in the Odoo registry."""
        self.assertIn("esmis.campus.aware", self.env)

    def test_mixin_has_company_id_field(self):
        """The mixin provides a company_id field."""
        model = self.env["esmis.campus.aware"]
        self.assertIn("company_id", model._fields)

    def test_company_id_is_required(self):
        """The company_id field is marked as required."""
        field = self.env["esmis.campus.aware"]._fields["company_id"]
        self.assertTrue(field.required)

    def test_company_id_has_index(self):
        """The company_id field is indexed for query performance."""
        field = self.env["esmis.campus.aware"]._fields["company_id"]
        self.assertTrue(field.index)

    def test_company_id_string_is_campus(self):
        """The company_id field uses 'Campus' as its user-facing label."""
        field = self.env["esmis.campus.aware"]._fields["company_id"]
        self.assertEqual(field.string, "Campus")
