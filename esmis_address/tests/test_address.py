from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestAddress(TransactionCase):
    """Tests for the esmis.address model — CRUD, computed fields, constraints."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Address = cls.env["esmis.address"]
        cls.Partner = cls.env["res.partner"]

        cls.partner = cls.Partner.create({"name": "Test Contact"})

        # Fetch address type codes seeded by vocabulary_address_type.xml
        VocabCode = cls.env["esmis.vocabulary.code"]
        cls.type_permanent = VocabCode.get_code("urn:esmis:address-type", "permanent")
        cls.type_mailing = VocabCode.get_code("urn:esmis:address-type", "mailing")
        cls.type_residency = VocabCode.get_code("urn:esmis:address-type", "residency")
        cls.type_emergency = VocabCode.get_code("urn:esmis:address-type", "emergency")

    def test_create_address(self):
        """An address can be created with required fields."""
        addr = self.Address.create(
            {
                "partner_id": self.partner.id,
                "address_type_id": self.type_permanent.id,
                "street1": "123 Main Street",
                "city": "Quezon City",
            }
        )
        self.assertEqual(addr.partner_id, self.partner)
        self.assertEqual(addr.address_type_id, self.type_permanent)
        self.assertEqual(addr.street1, "123 Main Street")
        self.assertFalse(addr.is_primary)

    def test_address_text_full(self):
        """address_text concatenates all non-empty components with ', '."""
        country = self.env["res.country"].search([("code", "=", "PH")], limit=1)
        addr = self.Address.create(
            {
                "partner_id": self.partner.id,
                "address_type_id": self.type_mailing.id,
                "street1": "456 Rizal Ave",
                "street2": "Brgy. Sample",
                "city": "Manila",
                "state_province": "Metro Manila",
                "postal_code": "1000",
                "country_id": country.id,
            }
        )
        expected_parts = ["456 Rizal Ave", "Brgy. Sample", "Manila", "Metro Manila", "1000", country.name]
        self.assertEqual(addr.address_text, ", ".join(expected_parts))

    def test_address_text_partial(self):
        """address_text skips empty components."""
        addr = self.Address.create(
            {
                "partner_id": self.partner.id,
                "address_type_id": self.type_residency.id,
                "city": "Cebu City",
                "postal_code": "6000",
            }
        )
        self.assertEqual(addr.address_text, "Cebu City, 6000")

    def test_address_text_empty_when_no_components(self):
        """address_text is empty when all components are blank."""
        addr = self.Address.create(
            {
                "partner_id": self.partner.id,
                "address_type_id": self.type_emergency.id,
            }
        )
        self.assertEqual(addr.address_text, "")

    def test_address_text_recomputes_on_write(self):
        """address_text is recomputed when a component changes."""
        addr = self.Address.create(
            {
                "partner_id": self.partner.id,
                "address_type_id": self.type_permanent.id,
                "city": "Davao",
            }
        )
        self.assertEqual(addr.address_text, "Davao")

        addr.write({"street1": "789 Bonifacio St"})
        self.assertEqual(addr.address_text, "789 Bonifacio St, Davao")

    def test_unique_type_per_partner_constraint(self):
        """Cannot create two addresses of the same type for the same partner."""
        self.Address.create(
            {
                "partner_id": self.partner.id,
                "address_type_id": self.type_permanent.id,
            }
        )
        with self.assertRaises(ValidationError):
            self.Address.create(
                {
                    "partner_id": self.partner.id,
                    "address_type_id": self.type_permanent.id,
                }
            )

    def test_different_type_same_partner_allowed(self):
        """Two addresses of different types for the same partner are allowed."""
        addr1 = self.Address.create(
            {
                "partner_id": self.partner.id,
                "address_type_id": self.type_permanent.id,
            }
        )
        addr2 = self.Address.create(
            {
                "partner_id": self.partner.id,
                "address_type_id": self.type_mailing.id,
            }
        )
        self.assertTrue(addr1.id)
        self.assertTrue(addr2.id)

    def test_same_type_different_partner_allowed(self):
        """Two addresses of the same type for different partners are allowed."""
        other_partner = self.Partner.create({"name": "Another Contact"})
        addr1 = self.Address.create(
            {
                "partner_id": self.partner.id,
                "address_type_id": self.type_permanent.id,
            }
        )
        addr2 = self.Address.create(
            {
                "partner_id": other_partner.id,
                "address_type_id": self.type_permanent.id,
            }
        )
        self.assertTrue(addr1.id)
        self.assertTrue(addr2.id)

    def test_cascade_delete_with_partner(self):
        """Addresses are deleted when the partner is deleted (ondelete cascade)."""
        partner = self.Partner.create({"name": "To Be Deleted"})
        addr = self.Address.create(
            {
                "partner_id": partner.id,
                "address_type_id": self.type_permanent.id,
            }
        )
        addr_id = addr.id
        partner.unlink()
        self.assertFalse(self.Address.search([("id", "=", addr_id)]))

    def test_seed_address_type_vocabulary_exists(self):
        """Address type vocabulary codes are loaded by seed data."""
        self.assertTrue(self.type_permanent, "permanent code should exist")
        self.assertTrue(self.type_mailing, "mailing code should exist")
        self.assertTrue(self.type_residency, "residency code should exist")
        self.assertTrue(self.type_emergency, "emergency code should exist")

    def test_seed_address_type_display_values(self):
        """Address type codes have the correct display labels."""
        self.assertEqual(self.type_permanent.display, "Permanent Address")
        self.assertEqual(self.type_mailing.display, "Mailing Address")
        self.assertEqual(self.type_residency.display, "Current Residence")
        self.assertEqual(self.type_emergency.display, "Emergency Contact Address")

    def test_partner_address_ids_one2many(self):
        """partner.address_ids returns all addresses linked to the partner."""
        self.Address.create(
            {
                "partner_id": self.partner.id,
                "address_type_id": self.type_permanent.id,
                "city": "Makati",
            }
        )
        self.Address.create(
            {
                "partner_id": self.partner.id,
                "address_type_id": self.type_mailing.id,
                "city": "Pasig",
            }
        )
        self.assertEqual(len(self.partner.address_ids), 2)

    def test_primary_address_text_on_partner(self):
        """partner.primary_address_text returns the address_text of the primary address."""
        addr = self.Address.create(
            {
                "partner_id": self.partner.id,
                "address_type_id": self.type_permanent.id,
                "city": "Iloilo City",
                "is_primary": True,
            }
        )
        self.partner.invalidate_recordset()
        self.assertEqual(self.partner.primary_address_text, addr.address_text)

    def test_primary_address_text_empty_when_no_primary(self):
        """partner.primary_address_text is empty when no address is primary."""
        self.Address.create(
            {
                "partner_id": self.partner.id,
                "address_type_id": self.type_mailing.id,
                "city": "Baguio",
                "is_primary": False,
            }
        )
        self.partner.invalidate_recordset()
        self.assertEqual(self.partner.primary_address_text, "")
