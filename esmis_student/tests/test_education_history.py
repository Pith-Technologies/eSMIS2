from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestEducationHistory(TransactionCase):
    """Tests for esmis.education.history — CRUD, computed fields, constraints."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Partner = cls.env["res.partner"].with_context(tracking_disable=True)
        cls.EducationHistory = cls.env["esmis.education.history"]
        cls.VocabCode = cls.env["esmis.vocabulary.code"]

        cls.student = cls.Partner.create(
            {
                "name": "Education History Student",
                "is_student": True,
                "first_name": "Education",
                "last_name": "Student",
                "birthdate": "1998-01-01",
            }
        )

        cls.level_elementary = cls.VocabCode.get_code("urn:esmis:education-level", "elementary")
        cls.level_jhs = cls.VocabCode.get_code("urn:esmis:education-level", "junior_high_school")
        cls.level_shs = cls.VocabCode.get_code("urn:esmis:education-level", "senior_high_school")
        cls.level_tertiary = cls.VocabCode.get_code("urn:esmis:education-level", "tertiary")

    def test_vocabulary_seeds_loaded(self):
        """Education level vocabulary codes are loaded by seed data."""
        self.assertTrue(self.level_elementary, "elementary code must exist")
        self.assertTrue(self.level_jhs, "junior_high_school code must exist")
        self.assertTrue(self.level_shs, "senior_high_school code must exist")
        self.assertTrue(self.level_tertiary, "tertiary code must exist")
        pre_school = self.VocabCode.get_code("urn:esmis:education-level", "pre_school")
        graduate = self.VocabCode.get_code("urn:esmis:education-level", "graduate")
        post_graduate = self.VocabCode.get_code("urn:esmis:education-level", "post_graduate")
        self.assertTrue(pre_school, "pre_school code must exist")
        self.assertTrue(graduate, "graduate code must exist")
        self.assertTrue(post_graduate, "post_graduate code must exist")

    def test_create_education_history(self):
        """An education history record can be created with required fields."""
        record = self.EducationHistory.create(
            {
                "partner_id": self.student.id,
                "education_level_id": self.level_elementary.id,
                "school_name": "Test Elementary School",
            }
        )
        self.assertEqual(record.partner_id, self.student)
        self.assertEqual(record.education_level_id, self.level_elementary)
        self.assertEqual(record.school_name, "Test Elementary School")
        self.assertFalse(record.is_graduated)

    def test_education_level_sequence_related(self):
        """education_level_sequence is populated from the code's sequence."""
        record = self.EducationHistory.create(
            {
                "partner_id": self.student.id,
                "education_level_id": self.level_elementary.id,
                "school_name": "Sequence Test School",
            }
        )
        self.assertEqual(record.education_level_sequence, self.level_elementary.sequence)

    def test_year_range_valid(self):
        """A record with year_graduated >= year_started is accepted."""
        record = self.EducationHistory.create(
            {
                "partner_id": self.student.id,
                "education_level_id": self.level_jhs.id,
                "school_name": "Valid Year School",
                "year_started": 2012,
                "year_graduated": 2016,
                "is_graduated": True,
            }
        )
        self.assertEqual(record.year_started, 2012)
        self.assertEqual(record.year_graduated, 2016)

    def test_year_range_invalid_raises_validation_error(self):
        """year_graduated < year_started raises ValidationError."""
        with self.assertRaises(ValidationError):
            self.EducationHistory.create(
                {
                    "partner_id": self.student.id,
                    "education_level_id": self.level_shs.id,
                    "school_name": "Bad Year School",
                    "year_started": 2018,
                    "year_graduated": 2015,
                }
            )

    def test_year_range_equal_is_valid(self):
        """year_graduated == year_started is accepted."""
        record = self.EducationHistory.create(
            {
                "partner_id": self.student.id,
                "education_level_id": self.level_shs.id,
                "school_name": "Same Year School",
                "year_started": 2018,
                "year_graduated": 2018,
            }
        )
        self.assertEqual(record.year_started, record.year_graduated)

    def test_no_year_fields_no_constraint_error(self):
        """Records without year fields are accepted without constraint errors."""
        record = self.EducationHistory.create(
            {
                "partner_id": self.student.id,
                "education_level_id": self.level_tertiary.id,
                "school_name": "No Year School",
            }
        )
        self.assertFalse(record.year_started)
        self.assertFalse(record.year_graduated)

    def test_honors_received_stored(self):
        """honors_received is stored as a Char field."""
        record = self.EducationHistory.create(
            {
                "partner_id": self.student.id,
                "education_level_id": self.level_elementary.id,
                "school_name": "Honor School",
                "honors_received": "Valedictorian",
                "is_graduated": True,
            }
        )
        self.assertEqual(record.honors_received, "Valedictorian")

    def test_ordering_by_level_sequence(self):
        """Records are ordered by education_level_sequence (lowest first)."""
        self.EducationHistory.create(
            {
                "partner_id": self.student.id,
                "education_level_id": self.level_tertiary.id,
                "school_name": "University A",
            }
        )
        self.EducationHistory.create(
            {
                "partner_id": self.student.id,
                "education_level_id": self.level_elementary.id,
                "school_name": "Elementary B",
            }
        )
        records = self.EducationHistory.search([("partner_id", "=", self.student.id)])
        sequences = [r.education_level_sequence for r in records]
        self.assertEqual(sequences, sorted(sequences))

    def test_cascade_delete_with_partner(self):
        """Education history records are deleted when the student partner is deleted."""
        partner = self.Partner.create(
            {
                "name": "Cascade Partner",
                "is_student": True,
                "first_name": "C",
                "last_name": "P",
                "birthdate": "2000-01-01",
            }
        )
        record = self.EducationHistory.create(
            {
                "partner_id": partner.id,
                "education_level_id": self.level_elementary.id,
                "school_name": "Cascade School",
            }
        )
        record_id = record.id
        partner.unlink()
        self.assertFalse(self.EducationHistory.search([("id", "=", record_id)]))

    def test_write_year_invalid_raises_validation_error(self):
        """Updating year_graduated to be before year_started raises ValidationError."""
        record = self.EducationHistory.create(
            {
                "partner_id": self.student.id,
                "education_level_id": self.level_jhs.id,
                "school_name": "Write Year School",
                "year_started": 2014,
                "year_graduated": 2018,
            }
        )
        with self.assertRaises(ValidationError):
            record.write({"year_graduated": 2010})

    def test_student_education_history_ids(self):
        """partner.education_history_ids includes created records."""
        record = self.EducationHistory.create(
            {
                "partner_id": self.student.id,
                "education_level_id": self.level_tertiary.id,
                "school_name": "One2many School",
            }
        )
        self.assertIn(record, self.student.education_history_ids)
