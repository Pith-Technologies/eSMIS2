from odoo.tests.common import TransactionCase


class TestPhAddress(TransactionCase):
    """Tests for PH address extensions: PSGC cascading and address_text override."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Address = cls.env["esmis.address"].with_context(tracking_disable=True)
        cls.VocabCode = cls.env["esmis.vocabulary.code"]

        # Locate sample PSGC data loaded via XML
        cls.region_ncr = cls.env["esmis.psgc.region"].search([("psgc_code", "=", "130000000")], limit=1)
        cls.province_ncr = cls.env["esmis.psgc.province"].search([("psgc_code", "=", "133900000")], limit=1)
        cls.city_qc = cls.env["esmis.psgc.city.municipality"].search([("psgc_code", "=", "137404000")], limit=1)
        cls.barangay_bagong = cls.env["esmis.psgc.barangay"].search([("psgc_code", "=", "137404001")], limit=1)

        # Address type vocabulary code needed for esmis.address
        cls.addr_type = cls.VocabCode.search([("namespace_uri", "=", "urn:esmis:address-type")], limit=1)
        cls.partner = (
            cls.env["res.partner"].with_context(tracking_disable=True).create({"name": "Test Partner PH Address"})
        )

    def _make_address(self, **kwargs):
        vals = {
            "partner_id": self.partner.id,
            "address_type_id": self.addr_type.id,
        }
        vals.update(kwargs)
        return self.Address.create(vals)

    def test_region_id_stored(self):
        """region_id can be set and retrieved on an esmis.address."""
        addr = self._make_address(region_id=self.region_ncr.id)
        self.assertEqual(addr.region_id, self.region_ncr)

    def test_province_id_stored(self):
        """province_id can be set and retrieved on an esmis.address."""
        addr = self._make_address(
            region_id=self.region_ncr.id,
            province_id=self.province_ncr.id,
        )
        self.assertEqual(addr.province_id, self.province_ncr)

    def test_city_municipality_id_stored(self):
        """city_municipality_id can be set on an esmis.address."""
        addr = self._make_address(
            region_id=self.region_ncr.id,
            province_id=self.province_ncr.id,
            city_municipality_id=self.city_qc.id,
        )
        self.assertEqual(addr.city_municipality_id, self.city_qc)

    def test_barangay_id_stored(self):
        """barangay_id can be set on an esmis.address."""
        addr = self._make_address(
            region_id=self.region_ncr.id,
            province_id=self.province_ncr.id,
            city_municipality_id=self.city_qc.id,
            barangay_id=self.barangay_bagong.id,
        )
        self.assertEqual(addr.barangay_id, self.barangay_bagong)

    def test_zip_code_derived_from_city(self):
        """zip_code is computed from city_municipality_id.zip_code."""
        addr = self._make_address(
            region_id=self.region_ncr.id,
            province_id=self.province_ncr.id,
            city_municipality_id=self.city_qc.id,
        )
        # Quezon City has zip_code 1100 in sample data
        self.assertEqual(addr.zip_code, "1100")

    def test_address_text_ph_format(self):
        """address_text uses PH format when region_id is set."""
        addr = self._make_address(
            street1="123 Sample Street",
            region_id=self.region_ncr.id,
            province_id=self.province_ncr.id,
            city_municipality_id=self.city_qc.id,
            barangay_id=self.barangay_bagong.id,
        )
        text = addr.address_text
        self.assertIn("123 Sample Street", text)
        self.assertIn("Quezon City", text)
        self.assertIn("NCR", text)

    def test_address_text_generic_format_without_region(self):
        """address_text falls back to generic format when region_id is not set."""
        addr = self._make_address(
            street1="456 Generic St",
            city="Manila",
            state_province="Metro Manila",
            postal_code="1000",
        )
        text = addr.address_text
        self.assertIn("456 Generic St", text)
        self.assertIn("Manila", text)
        self.assertIn("1000", text)

    def test_address_text_ph_includes_all_levels(self):
        """PH address_text includes all non-empty PSGC components."""
        addr = self._make_address(
            street1="Main St",
            street2="Block 5",
            region_id=self.region_ncr.id,
            province_id=self.province_ncr.id,
            city_municipality_id=self.city_qc.id,
            barangay_id=self.barangay_bagong.id,
        )
        text = addr.address_text
        self.assertIn("Main St", text)
        self.assertIn("Block 5", text)
        self.assertIn(self.barangay_bagong.name, text)
        self.assertIn("Quezon City", text)
        self.assertIn("Metro Manila (NCR)", text)
        self.assertIn("NCR", text)

    def test_clear_region_resets_address_text_to_generic(self):
        """Clearing region_id causes address_text to revert to generic format."""
        addr = self._make_address(
            street1="Test St",
            city="Quezon City",
            region_id=self.region_ncr.id,
        )
        self.assertIn("NCR", addr.address_text)

        addr.write({"region_id": False, "province_id": False})
        addr.invalidate_recordset()
        self.assertNotIn("NCR", addr.address_text)
