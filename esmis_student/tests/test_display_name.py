from odoo.tests.common import TransactionCase


class TestDisplayName(TransactionCase):
    """Tests for display_name computation on student and non-student partners."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Partner = cls.env["res.partner"].with_context(tracking_disable=True)

    def _make_student(self, **kwargs):
        base = {
            "name": "Fallback Name",
            "is_student": True,
            "birthdate": "2000-01-01",
        }
        base.update(kwargs)
        return self.Partner.create(base)

    def test_student_with_all_name_parts(self):
        """Student display_name is 'LAST, FIRST MIDDLE' when all parts are set."""
        student = self._make_student(
            first_name="Juan",
            last_name="Dela Cruz",
            middle_name="Santos",
        )
        student.invalidate_recordset()
        self.assertEqual(student.display_name, "Dela Cruz, Juan Santos")

    def test_student_without_middle_name(self):
        """Student display_name is 'LAST, FIRST' when middle_name is not set."""
        student = self._make_student(
            first_name="Maria",
            last_name="Reyes",
        )
        student.invalidate_recordset()
        self.assertEqual(student.display_name, "Reyes, Maria")

    def test_student_without_last_name_falls_back(self):
        """display_name falls back to Odoo default when last_name is not set."""
        student = self._make_student(
            name="Only One Name",
            first_name="OneFirst",
        )
        student.invalidate_recordset()
        # Falls back to partner.name because last_name is not set.
        self.assertEqual(student.display_name, "Only One Name")

    def test_non_student_uses_odoo_default(self):
        """Non-student partners use the standard Odoo display_name logic."""
        partner = self.Partner.create(
            {
                "name": "Standard Contact",
                "is_student": False,
            }
        )
        partner.invalidate_recordset()
        self.assertEqual(partner.display_name, "Standard Contact")

    def test_student_flag_toggle_updates_display_name(self):
        """Setting is_student=False on a student reverts to Odoo default name."""
        student = self._make_student(
            name="Normal Name",
            first_name="Juan",
            last_name="Cruz",
        )
        student.invalidate_recordset()
        self.assertEqual(student.display_name, "Cruz, Juan")

        student.write({"is_student": False})
        student.invalidate_recordset()
        self.assertEqual(student.display_name, "Normal Name")

    def test_last_name_only(self):
        """Student with only last_name has 'LAST, ' in display_name."""
        student = self._make_student(last_name="Lopez")
        student.invalidate_recordset()
        # first_name is None, filter(None, ...) removes it, but comma is part of last_name+','
        self.assertIn("Lopez,", student.display_name)

    def test_get_student_display_name_hook(self):
        """_get_student_display_name returns the formatted name directly."""
        student = self._make_student(
            first_name="Test",
            last_name="Hook",
            middle_name="Middle",
        )
        result = student._get_student_display_name()
        self.assertEqual(result, "Hook, Test Middle")
