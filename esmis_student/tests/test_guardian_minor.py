import datetime

from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestGuardianMinor(TransactionCase):
    """Tests for the guardian requirement when a student is under 18."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Partner = cls.env["res.partner"].with_context(tracking_disable=True)

        cls.guardian = cls.Partner.create({"name": "Guardian Parent"})

        today = datetime.date.today()
        # Minor: 16 years old
        cls.minor_birthdate = (today - datetime.timedelta(days=365 * 16)).strftime("%Y-%m-%d")
        # Adult: 20 years old
        cls.adult_birthdate = (today - datetime.timedelta(days=365 * 20)).strftime("%Y-%m-%d")

    def _make_student(self, **kwargs):
        base = {
            "name": "Test Student",
            "is_student": True,
            "first_name": "Test",
            "last_name": "Student",
        }
        base.update(kwargs)
        return self.Partner.create(base)

    def test_minor_without_guardian_raises(self):
        """Creating a minor student without guardian_id raises ValidationError."""
        with self.assertRaises(ValidationError):
            self._make_student(birthdate=self.minor_birthdate)

    def test_minor_with_guardian_succeeds(self):
        """Creating a minor student with guardian_id is allowed."""
        student = self._make_student(
            birthdate=self.minor_birthdate,
            guardian_id=self.guardian.id,
        )
        self.assertEqual(student.guardian_id, self.guardian)

    def test_adult_without_guardian_succeeds(self):
        """Creating an adult student without guardian_id is allowed."""
        student = self._make_student(birthdate=self.adult_birthdate)
        self.assertFalse(student.guardian_id)

    def test_adult_with_guardian_succeeds(self):
        """An adult student may optionally have a guardian (e.g. for emergency contact)."""
        student = self._make_student(
            birthdate=self.adult_birthdate,
            guardian_id=self.guardian.id,
        )
        self.assertEqual(student.guardian_id, self.guardian)

    def test_minor_write_remove_guardian_raises(self):
        """Removing guardian_id from a minor student raises ValidationError."""
        student = self._make_student(
            birthdate=self.minor_birthdate,
            guardian_id=self.guardian.id,
        )
        with self.assertRaises(ValidationError):
            student.write({"guardian_id": False})

    def test_no_birthdate_no_guardian_required(self):
        """Without birthdate, guardian is not required (age cannot be determined)."""
        student = self._make_student()
        self.assertFalse(student.guardian_id)

    def test_non_student_minor_no_guardian_required(self):
        """Guardian constraint does not apply to non-student partners."""
        partner = self.Partner.create(
            {
                "name": "Minor Non-Student",
                "is_student": False,
                "birthdate": self.minor_birthdate,
            }
        )
        self.assertFalse(partner.guardian_id)

    def test_exactly_18_not_minor(self):
        """A student who is exactly 18 years old today is not treated as a minor."""
        today = datetime.date.today()
        birthdate_18 = today.replace(year=today.year - 18)
        student = self._make_student(birthdate=birthdate_18.strftime("%Y-%m-%d"))
        self.assertFalse(student.guardian_id)
