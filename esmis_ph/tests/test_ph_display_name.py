from odoo import Command
from odoo.tests.common import TransactionCase


class TestPhDisplayName(TransactionCase):
    """Tests for Philippine name format in _get_student_display_name."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Partner = cls.env["res.partner"].with_context(tracking_disable=True)
        cls.VocabCode = cls.env["esmis.vocabulary.code"]
        cls.suffix_jr = cls.VocabCode.get_code("urn:esmis:name-suffix", "jr")
        cls.suffix_phd = cls.VocabCode.get_code("urn:esmis:name-suffix", "phd")

    def _make_student(self, **kwargs):
        vals = {
            "name": "Fallback Name",
            "is_student": True,
            "birthdate": "2000-01-01",
        }
        vals.update(kwargs)
        return self.Partner.create(vals)

    def test_ph_format_with_middle_initial(self):
        """Display name uses first letter of middle_name as middle initial."""
        student = self._make_student(
            first_name="Juan",
            last_name="Dela Cruz",
            middle_name="Santos",
        )
        student.invalidate_recordset()
        self.assertEqual(student.display_name, "Dela Cruz, Juan S.")

    def test_ph_format_prefers_maiden_name_as_middle_initial(self):
        """middle_name_b4_marriage takes precedence over middle_name for the initial."""
        student = self._make_student(
            first_name="Maria",
            last_name="Reyes",
            middle_name="Santos",
            middle_name_b4_marriage="Gomez",
        )
        student.invalidate_recordset()
        # G. from Gomez, not S. from Santos
        self.assertEqual(student.display_name, "Reyes, Maria G.")

    def test_ph_format_no_middle_name(self):
        """Display name omits middle initial when neither middle_name nor maiden is set."""
        student = self._make_student(
            first_name="Pedro",
            last_name="Lim",
        )
        student.invalidate_recordset()
        self.assertEqual(student.display_name, "Lim, Pedro")

    def test_ph_format_with_single_suffix(self):
        """Display name appends single suffix after middle initial."""
        student = self._make_student(
            first_name="Jose",
            last_name="Santos",
            middle_name="Reyes",
            suffix_ids=[Command.set([self.suffix_jr.id])],
        )
        student.invalidate_recordset()
        self.assertEqual(student.display_name, "Santos, Jose R. Jr.")

    def test_ph_format_with_multiple_suffixes(self):
        """Display name appends comma-separated suffixes when multiple are set."""
        student = self._make_student(
            first_name="Ricardo",
            last_name="Cruz",
            middle_name="Bautista",
            suffix_ids=[Command.set([self.suffix_phd.id, self.suffix_jr.id])],
        )
        student.invalidate_recordset()
        # Suffix order follows vocabulary sequence field
        name = student.display_name
        self.assertIn("Cruz, Ricardo B.", name)
        self.assertIn("PhD", name)
        self.assertIn("Jr.", name)

    def test_ph_format_suffix_only_no_middle(self):
        """Suffix is appended correctly even when no middle name is set."""
        student = self._make_student(
            first_name="Eduardo",
            last_name="Garcia",
            suffix_ids=[Command.set([self.suffix_jr.id])],
        )
        student.invalidate_recordset()
        self.assertEqual(student.display_name, "Garcia, Eduardo Jr.")

    def test_non_student_uses_odoo_default(self):
        """Non-student partners still use the standard Odoo display_name."""
        partner = self.Partner.create(
            {
                "name": "Standard Contact",
                "is_student": False,
            }
        )
        partner.invalidate_recordset()
        self.assertEqual(partner.display_name, "Standard Contact")

    def test_student_without_last_name_falls_back(self):
        """Display name falls back to Odoo default when last_name is not set."""
        student = self._make_student(
            name="One Name Only",
            first_name="One",
        )
        student.invalidate_recordset()
        self.assertEqual(student.display_name, "One Name Only")

    def test_get_student_display_name_hook_returns_string(self):
        """_get_student_display_name returns a non-empty string."""
        student = self._make_student(
            first_name="Test",
            last_name="Hook",
            middle_name="Middle",
        )
        result = student._get_student_display_name()
        self.assertEqual(result, "Hook, Test M.")
