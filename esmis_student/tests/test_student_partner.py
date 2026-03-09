from odoo.tests.common import TransactionCase


class TestStudentPartner(TransactionCase):
    """CRUD tests for student fields on res.partner."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Partner = cls.env["res.partner"].with_context(tracking_disable=True)
        cls.gender_male = cls.env["esmis.vocabulary.code"].get_code("urn:iso:std:iso:5218", "1")
        cls.gender_female = cls.env["esmis.vocabulary.code"].get_code("urn:iso:std:iso:5218", "2")

    def _make_student(self, **kwargs):
        vals = {
            "name": "Test Student",
            "is_student": True,
            "first_name": "Test",
            "last_name": "Student",
            "birthdate": "1999-01-01",
        }
        vals.update(kwargs)
        return self.Partner.create(vals)

    def test_create_student_sets_is_student(self):
        """Creating a partner with is_student=True persists the flag."""
        student = self._make_student()
        self.assertTrue(student.is_student)

    def test_non_student_default(self):
        """is_student defaults to False for ordinary contacts."""
        partner = self.Partner.create({"name": "Ordinary Contact"})
        self.assertFalse(partner.is_student)

    def test_student_number_stored(self):
        """student_number is stored and retrievable."""
        student = self._make_student(student_number="2024-12345")
        self.assertEqual(student.student_number, "2024-12345")

    def test_student_number_not_copied(self):
        """Copying a student partner does not copy the student_number."""
        student = self._make_student(student_number="2024-99999")
        copy = student.copy()
        self.assertFalse(copy.student_number)

    def test_name_components_stored(self):
        """first_name, last_name, and middle_name are stored correctly."""
        student = self._make_student(
            first_name="Juan",
            last_name="Dela Cruz",
            middle_name="Santos",
        )
        self.assertEqual(student.first_name, "Juan")
        self.assertEqual(student.last_name, "Dela Cruz")
        self.assertEqual(student.middle_name, "Santos")

    def test_birthdate_stored(self):
        """birthdate is stored as a date field."""
        import datetime

        student = self._make_student(birthdate="2000-06-15")
        self.assertEqual(student.birthdate, datetime.date(2000, 6, 15))

    def test_age_computed_from_birthdate(self):
        """age is computed from birthdate and is a positive integer."""
        student = self._make_student(birthdate="2000-01-01")
        self.assertGreater(student.age, 0)

    def test_age_zero_when_no_birthdate(self):
        """age is 0 when birthdate is not set."""
        student = self.Partner.create({"name": "No Birthdate", "is_student": True})
        self.assertEqual(student.age, 0)

    def test_gender_vocabulary_link(self):
        """gender_id links to an esmis.vocabulary.code record."""
        student = self._make_student(gender_id=self.gender_male.id)
        self.assertEqual(student.gender_id, self.gender_male)

    def test_nationality_links_to_country(self):
        """nationality_id links to a res.country record."""
        ph = self.env["res.country"].search([("code", "=", "PH")], limit=1)
        student = self._make_student(nationality_id=ph.id)
        self.assertEqual(student.nationality_id, ph)

    def test_is_pwd_default_false(self):
        """is_pwd defaults to False."""
        student = self._make_student()
        self.assertFalse(student.is_pwd)

    def test_is_indigenous_people_default_false(self):
        """is_indigenous_people defaults to False."""
        student = self._make_student()
        self.assertFalse(student.is_indigenous_people)

    def test_student_state_default_applicant(self):
        """student_state defaults to 'applicant'."""
        student = self._make_student()
        self.assertEqual(student.student_state, "applicant")

    def test_write_student_fields(self):
        """Student demographic fields can be updated via write()."""
        student = self._make_student()
        student.write({"birthplace": "Antipolo, Rizal", "is_pwd": True})
        self.assertEqual(student.birthplace, "Antipolo, Rizal")
        self.assertTrue(student.is_pwd)

    def test_unlink_student(self):
        """A student partner can be deleted."""
        student = self._make_student()
        student_id = student.id
        student.unlink()
        self.assertFalse(self.Partner.search([("id", "=", student_id)]))

    def test_identifier_ids_one2many(self):
        """identifier_ids returns an empty recordset by default."""
        student = self._make_student()
        self.assertEqual(len(student.identifier_ids), 0)

    def test_education_history_ids_one2many(self):
        """education_history_ids returns an empty recordset by default."""
        student = self._make_student()
        self.assertEqual(len(student.education_history_ids), 0)

    def test_student_number_unique_per_campus(self):
        """Two students with the same student_number on the same campus raises ValidationError."""
        from odoo.exceptions import ValidationError

        self._make_student(student_number="DUPE-001")
        with self.assertRaises(ValidationError):
            self._make_student(student_number="DUPE-001")

    def test_student_number_unique_different_campus(self):
        """Same student_number on different campuses is allowed."""
        campus_b = self.env["res.company"].create({"name": "Campus B"})
        self._make_student(student_number="SHARED-001")
        student_b = self.Partner.with_context(tracking_disable=True).create(
            {
                "name": "Student B",
                "is_student": True,
                "first_name": "Student",
                "last_name": "B",
                "birthdate": "2000-01-01",
                "student_number": "SHARED-001",
                "company_id": campus_b.id,
            }
        )
        self.assertTrue(student_b.id)
