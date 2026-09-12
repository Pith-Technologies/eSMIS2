import base64
import os

from psycopg2 import IntegrityError

from odoo.tests.common import TransactionCase


class TestIdentifierEncryption(TransactionCase):
    """Tests for AES-256-GCM encryption and HMAC-SHA256 blind index on esmis.identifier."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Partner = cls.env["res.partner"].with_context(tracking_disable=True)
        cls.Identifier = cls.env["esmis.identifier"]

        # Create a test encryption key (32 random bytes) and store it in
        # ir.config_parameter so all tests in this class use a consistent key.
        cls.test_key = os.urandom(32)
        cls.env["ir.config_parameter"].sudo().set_param(
            "esmis.encryption_key",
            base64.b64encode(cls.test_key).decode(),
        )

        # Create a vocabulary type for the identifier — we need any code that
        # can serve as type_id. Use gender male as a stand-in since no
        # identifier-type vocabulary is seeded in the base module.
        cls.identifier_type = cls.env["esmis.vocabulary.code"].get_code("urn:iso:std:iso:5218", "1")

        cls.student = cls.Partner.create(
            {
                "name": "Encrypted ID Student",
                "is_student": True,
                "first_name": "Encrypted",
                "last_name": "Student",
                "birthdate": "2000-01-01",
            }
        )

    def _make_identifier(self, value, student=None):
        partner = student or self.student
        return self.Identifier.create(
            {
                "partner_id": partner.id,
                "type_id": self.identifier_type.id,
                "value": value,
            }
        )

    def test_value_not_stored_in_plaintext(self):
        """The plaintext value is not persisted in the value column."""
        identifier = self._make_identifier("1234-5678-9012")
        # After create(), the value field should not hold the plaintext.
        # The ORM clears it because we pop it in create() before super().
        self.assertFalse(identifier.value)

    def test_ciphertext_stored(self):
        """value_ciphertext is populated after creation."""
        identifier = self._make_identifier("1234-5678-9012")
        self.assertTrue(identifier.value_ciphertext)

    def test_blind_index_stored(self):
        """value_blind_index is populated after creation."""
        identifier = self._make_identifier("1234-5678-9012")
        self.assertTrue(identifier.value_blind_index)

    def test_encrypt_decrypt_round_trip(self):
        """Decrypting the stored ciphertext returns the original plaintext."""
        plaintext = "9876-5432-1098"
        identifier = self._make_identifier(plaintext)
        decrypted = identifier.get_decrypted_value()
        self.assertEqual(decrypted, plaintext)

    def test_different_values_have_different_ciphertexts(self):
        """Two identifiers with different values produce different ciphertexts."""
        partner_a = self.Partner.create(
            {"name": "Partner A", "is_student": True, "first_name": "A", "last_name": "X", "birthdate": "2000-01-01"}
        )
        partner_b = self.Partner.create(
            {"name": "Partner B", "is_student": True, "first_name": "B", "last_name": "Y", "birthdate": "2000-01-01"}
        )
        id_a = self._make_identifier("AAAA-1111-0001", student=partner_a)
        id_b = self._make_identifier("BBBB-2222-0002", student=partner_b)
        self.assertNotEqual(id_a.value_ciphertext, id_b.value_ciphertext)

    def test_same_value_different_ciphertexts_due_to_nonce(self):
        """Two identifiers with the same value have different ciphertexts (unique nonces)."""
        partner_a = self.Partner.create(
            {"name": "Nonce A", "is_student": True, "first_name": "NA", "last_name": "X", "birthdate": "2000-01-01"}
        )
        partner_b = self.Partner.create(
            {"name": "Nonce B", "is_student": True, "first_name": "NB", "last_name": "Y", "birthdate": "2000-01-01"}
        )
        id_a = self._make_identifier("SAME-VALUE-0001", student=partner_a)
        id_b = self._make_identifier("SAME-VALUE-0001", student=partner_b)
        # Nonces differ, so ciphertexts should differ.
        self.assertNotEqual(id_a.value_ciphertext, id_b.value_ciphertext)

    def test_same_value_same_blind_index(self):
        """Two identifiers with the same value produce the same blind index (HMAC is deterministic)."""
        partner_a = self.Partner.create(
            {"name": "Blind A", "is_student": True, "first_name": "BA", "last_name": "X", "birthdate": "2000-01-01"}
        )
        partner_b = self.Partner.create(
            {"name": "Blind B", "is_student": True, "first_name": "BB", "last_name": "Y", "birthdate": "2000-01-01"}
        )
        id_a = self._make_identifier("BLIND-MATCH-0001", student=partner_a)
        id_b = self._make_identifier("BLIND-MATCH-0001", student=partner_b)
        self.assertEqual(id_a.value_blind_index, id_b.value_blind_index)

    def test_different_values_different_blind_indexes(self):
        """Different plaintext values produce different blind indexes."""
        partner_a = self.Partner.create(
            {"name": "Diff A", "is_student": True, "first_name": "DA", "last_name": "X", "birthdate": "2000-01-01"}
        )
        partner_b = self.Partner.create(
            {"name": "Diff B", "is_student": True, "first_name": "DB", "last_name": "Y", "birthdate": "2000-01-01"}
        )
        id_a = self._make_identifier("VALUE-ONE-0001", student=partner_a)
        id_b = self._make_identifier("VALUE-TWO-0002", student=partner_b)
        self.assertNotEqual(id_a.value_blind_index, id_b.value_blind_index)

    def test_search_by_value_finds_record(self):
        """search_by_value returns the matching identifier via blind index."""
        partner = self.Partner.create(
            {
                "name": "Search Target",
                "is_student": True,
                "first_name": "S",
                "last_name": "T",
                "birthdate": "2000-01-01",
            }
        )
        target_value = "SEARCH-TARGET-9999"
        identifier = self._make_identifier(target_value, student=partner)
        results = self.Identifier.search_by_value(target_value)
        self.assertIn(identifier, results)

    def test_search_by_value_no_false_positives(self):
        """search_by_value does not return identifiers with different values."""
        partner = self.Partner.create(
            {"name": "No Match", "is_student": True, "first_name": "NM", "last_name": "X", "birthdate": "2000-01-01"}
        )
        self._make_identifier("NO-MATCH-VALUE-001", student=partner)
        results = self.Identifier.search_by_value("COMPLETELY-DIFFERENT-VALUE")
        self.assertFalse(results)

    def test_write_updates_encryption(self):
        """Writing a new value to an existing identifier re-encrypts."""
        identifier = self._make_identifier("INITIAL-VALUE-001")
        old_blind = identifier.value_blind_index
        identifier.write({"value": "UPDATED-VALUE-001"})
        new_blind = identifier.value_blind_index
        self.assertNotEqual(old_blind, new_blind)
        self.assertEqual(identifier.get_decrypted_value(), "UPDATED-VALUE-001")

    def test_unique_type_per_partner_constraint(self):
        """Cannot create two identifiers of the same type for the same partner.

        The SQL UNIQUE constraint fires before @api.constrains, so we need
        a savepoint to catch the IntegrityError without corrupting the
        transaction for subsequent tests.
        """
        self._make_identifier("FIRST-ID-001")
        with self.assertRaises(IntegrityError), self.cr.savepoint():
            self._make_identifier("SECOND-ID-001")

    def test_cascade_delete_with_partner(self):
        """Identifiers are deleted when the student partner is deleted."""
        partner = self.Partner.create(
            {
                "name": "Cascade Delete",
                "is_student": True,
                "first_name": "C",
                "last_name": "D",
                "birthdate": "2000-01-01",
            }
        )
        identifier = self._make_identifier("CASCADE-0001", student=partner)
        identifier_id = identifier.id
        partner.unlink()
        self.assertFalse(self.Identifier.search([("id", "=", identifier_id)]))
