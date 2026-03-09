from odoo.tests.common import TransactionCase


class TestAddressPrimary(TransactionCase):
    """Tests for the primary address flag auto-management on esmis.address."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Address = cls.env["esmis.address"]
        cls.Partner = cls.env["res.partner"]

        cls.partner = cls.Partner.create({"name": "Primary Flag Test Contact"})
        cls.other_partner = cls.Partner.create({"name": "Other Contact"})

        VocabCode = cls.env["esmis.vocabulary.code"]
        cls.type_permanent = VocabCode.get_code("urn:esmis:address-type", "permanent")
        cls.type_mailing = VocabCode.get_code("urn:esmis:address-type", "mailing")
        cls.type_residency = VocabCode.get_code("urn:esmis:address-type", "residency")

    def test_create_first_primary(self):
        """Creating an address with is_primary=True marks it as primary."""
        addr = self.Address.create(
            {
                "partner_id": self.partner.id,
                "address_type_id": self.type_permanent.id,
                "is_primary": True,
            }
        )
        self.assertTrue(addr.is_primary)

    def test_create_second_primary_unflags_first(self):
        """Creating a second primary address auto-unflags the first."""
        addr1 = self.Address.create(
            {
                "partner_id": self.partner.id,
                "address_type_id": self.type_permanent.id,
                "is_primary": True,
            }
        )
        addr2 = self.Address.create(
            {
                "partner_id": self.partner.id,
                "address_type_id": self.type_mailing.id,
                "is_primary": True,
            }
        )
        addr1.invalidate_recordset()
        self.assertFalse(addr1.is_primary, "First address should no longer be primary")
        self.assertTrue(addr2.is_primary, "Second address should be primary")

    def test_write_sets_primary_unflags_others(self):
        """Setting is_primary=True via write() auto-unflags the existing primary."""
        addr1 = self.Address.create(
            {
                "partner_id": self.partner.id,
                "address_type_id": self.type_permanent.id,
                "is_primary": True,
            }
        )
        addr2 = self.Address.create(
            {
                "partner_id": self.partner.id,
                "address_type_id": self.type_mailing.id,
                "is_primary": False,
            }
        )
        addr2.write({"is_primary": True})
        addr1.invalidate_recordset()
        self.assertFalse(addr1.is_primary, "Original primary should be unflagged")
        self.assertTrue(addr2.is_primary, "Updated address should now be primary")

    def test_write_primary_false_does_not_unflag_others(self):
        """Setting is_primary=False does not affect other addresses."""
        addr1 = self.Address.create(
            {
                "partner_id": self.partner.id,
                "address_type_id": self.type_permanent.id,
                "is_primary": True,
            }
        )
        addr2 = self.Address.create(
            {
                "partner_id": self.partner.id,
                "address_type_id": self.type_mailing.id,
                "is_primary": False,
            }
        )
        addr2.write({"is_primary": False})
        addr1.invalidate_recordset()
        self.assertTrue(addr1.is_primary, "Existing primary should remain unchanged")

    def test_primary_flag_isolated_per_partner(self):
        """Primary flag management does not cross partner boundaries."""
        addr_own = self.Address.create(
            {
                "partner_id": self.partner.id,
                "address_type_id": self.type_permanent.id,
                "is_primary": True,
            }
        )
        addr_other = self.Address.create(
            {
                "partner_id": self.other_partner.id,
                "address_type_id": self.type_permanent.id,
                "is_primary": True,
            }
        )
        # Create a second primary for self.partner — should NOT affect other_partner's address
        self.Address.create(
            {
                "partner_id": self.partner.id,
                "address_type_id": self.type_mailing.id,
                "is_primary": True,
            }
        )
        addr_own.invalidate_recordset()
        addr_other.invalidate_recordset()
        self.assertFalse(addr_own.is_primary, "own partner's old primary should be unflagged")
        self.assertTrue(addr_other.is_primary, "other partner's primary should be untouched")

    def test_only_one_primary_allowed_at_a_time(self):
        """At most one address per partner has is_primary=True at any time."""
        self.Address.create(
            {
                "partner_id": self.partner.id,
                "address_type_id": self.type_permanent.id,
                "is_primary": True,
            }
        )
        self.Address.create(
            {
                "partner_id": self.partner.id,
                "address_type_id": self.type_mailing.id,
                "is_primary": True,
            }
        )
        self.Address.create(
            {
                "partner_id": self.partner.id,
                "address_type_id": self.type_residency.id,
                "is_primary": True,
            }
        )
        primaries = self.Address.search([("partner_id", "=", self.partner.id), ("is_primary", "=", True)])
        self.assertEqual(len(primaries), 1, "Only one address should be primary")

    def test_partner_primary_address_text_updates_after_flag_change(self):
        """partner.primary_address_text reflects the current primary address."""
        addr1 = self.Address.create(
            {
                "partner_id": self.partner.id,
                "address_type_id": self.type_permanent.id,
                "city": "Zamboanga",
                "is_primary": True,
            }
        )
        addr2 = self.Address.create(
            {
                "partner_id": self.partner.id,
                "address_type_id": self.type_mailing.id,
                "city": "General Santos",
                "is_primary": False,
            }
        )
        self.partner.invalidate_recordset()
        self.assertEqual(self.partner.primary_address_text, addr1.address_text)

        addr2.write({"is_primary": True})
        self.partner.invalidate_recordset()
        self.assertEqual(self.partner.primary_address_text, addr2.address_text)
