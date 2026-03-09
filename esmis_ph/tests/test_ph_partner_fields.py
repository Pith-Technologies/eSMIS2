from odoo import Command
from odoo.tests.common import TransactionCase


class TestPhPartnerFields(TransactionCase):
    """Tests for Philippine-specific fields on res.partner."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Partner = cls.env["res.partner"].with_context(tracking_disable=True)
        cls.VocabCode = cls.env["esmis.vocabulary.code"]

    def _make_student(self, **kwargs):
        vals = {
            "name": "Test Student",
            "is_student": True,
            "first_name": "Maria",
            "last_name": "Santos",
            "birthdate": "2000-01-01",
        }
        vals.update(kwargs)
        return self.Partner.create(vals)

    def test_middle_name_b4_marriage_stored(self):
        """middle_name_b4_marriage is stored and retrievable."""
        student = self._make_student(middle_name_b4_marriage="Reyes")
        self.assertEqual(student.middle_name_b4_marriage, "Reyes")

    def test_middle_name_b4_marriage_default_empty(self):
        """middle_name_b4_marriage defaults to empty."""
        student = self._make_student()
        self.assertFalse(student.middle_name_b4_marriage)

    def test_suffix_ids_many2many_stores(self):
        """suffix_ids accepts and retrieves multiple vocabulary codes."""
        suffix_jr = self.VocabCode.get_code("urn:esmis:name-suffix", "jr")
        suffix_phd = self.VocabCode.get_code("urn:esmis:name-suffix", "phd")
        student = self._make_student(suffix_ids=[Command.set([suffix_jr.id, suffix_phd.id])])
        self.assertIn(suffix_jr, student.suffix_ids)
        self.assertIn(suffix_phd, student.suffix_ids)

    def test_suffix_ids_default_empty(self):
        """suffix_ids defaults to an empty recordset."""
        student = self._make_student()
        self.assertEqual(len(student.suffix_ids), 0)

    def test_ethnicity_id_stores(self):
        """ethnicity_id links to an esmis.vocabulary.code from the PH ethnicity namespace."""
        ethnicity = self.VocabCode.get_code("urn:esmis:ethnicity-ph", "tagalog")
        student = self._make_student(ethnicity_id=ethnicity.id)
        self.assertEqual(student.ethnicity_id, ethnicity)

    def test_religion_id_stores(self):
        """religion_id links to an esmis.vocabulary.code from the PH religion namespace."""
        religion = self.VocabCode.get_code("urn:esmis:religion-ph", "roman_catholic")
        student = self._make_student(religion_id=religion.id)
        self.assertEqual(student.religion_id, religion)

    def test_is_solo_parent_default_false(self):
        """is_solo_parent defaults to False."""
        student = self._make_student()
        self.assertFalse(student.is_solo_parent)

    def test_is_solo_parent_can_be_set(self):
        """is_solo_parent can be set to True."""
        student = self._make_student(is_solo_parent=True)
        self.assertTrue(student.is_solo_parent)

    def test_is_4ps_beneficiary_default_false(self):
        """is_4ps_beneficiary defaults to False."""
        student = self._make_student()
        self.assertFalse(student.is_4ps_beneficiary)

    def test_is_4ps_beneficiary_can_be_set(self):
        """is_4ps_beneficiary can be set to True."""
        student = self._make_student(is_4ps_beneficiary=True)
        self.assertTrue(student.is_4ps_beneficiary)

    def test_write_ph_fields(self):
        """PH-specific fields can be updated via write()."""
        suffix_sr = self.VocabCode.get_code("urn:esmis:name-suffix", "sr")
        student = self._make_student()
        student.write(
            {
                "middle_name_b4_marriage": "Dela Cruz",
                "is_solo_parent": True,
                "is_4ps_beneficiary": False,
                "suffix_ids": [Command.set([suffix_sr.id])],
            }
        )
        self.assertEqual(student.middle_name_b4_marriage, "Dela Cruz")
        self.assertTrue(student.is_solo_parent)
        self.assertIn(suffix_sr, student.suffix_ids)

    def test_ph_fields_on_non_student(self):
        """PH-specific fields are available on non-student partners too."""
        partner = self.Partner.create(
            {
                "name": "Faculty Member",
                "is_student": False,
                "middle_name_b4_marriage": "Gomez",
            }
        )
        self.assertEqual(partner.middle_name_b4_marriage, "Gomez")
