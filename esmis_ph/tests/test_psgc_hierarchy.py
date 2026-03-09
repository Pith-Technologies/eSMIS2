import psycopg2.errors

from odoo.tests.common import TransactionCase


class TestPsgcHierarchy(TransactionCase):
    """Tests for PSGC geographic model CRUD, constraints, and hierarchy."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Region = cls.env["esmis.psgc.region"]
        cls.Province = cls.env["esmis.psgc.province"]
        cls.CityMunicipality = cls.env["esmis.psgc.city.municipality"]
        cls.Barangay = cls.env["esmis.psgc.barangay"]

    def _make_region(self, name="Test Region", psgc_code="990000000", **kwargs):
        return self.Region.create({"name": name, "psgc_code": psgc_code, **kwargs})

    def _make_province(self, region, name="Test Province", psgc_code="990100000", **kwargs):
        return self.Province.create({"name": name, "psgc_code": psgc_code, "region_id": region.id, **kwargs})

    def _make_city(self, province, name="Test City", psgc_code="990101000", **kwargs):
        return self.CityMunicipality.create(
            {"name": name, "psgc_code": psgc_code, "province_id": province.id, **kwargs}
        )

    def _make_barangay(self, city, name="Test Barangay", psgc_code="990101001", **kwargs):
        return self.Barangay.create({"name": name, "psgc_code": psgc_code, "city_municipality_id": city.id, **kwargs})

    # --- Region tests ---

    def test_region_create_and_read(self):
        """A region can be created and its fields retrieved."""
        region = self._make_region(name="Test NCR", psgc_code="990000001", designation="Test Capital Region")
        self.assertEqual(region.name, "Test NCR")
        self.assertEqual(region.psgc_code, "990000001")
        self.assertEqual(region.designation, "Test Capital Region")

    def test_region_psgc_code_unique_constraint(self):
        """Creating two regions with the same PSGC code raises ValidationError."""
        self._make_region(psgc_code="991000000")
        with self.assertRaises(psycopg2.errors.UniqueViolation):
            self._make_region(psgc_code="991000000")

    def test_region_unlink(self):
        """A region with no provinces can be deleted."""
        region = self._make_region(psgc_code="999000000")
        region_id = region.id
        region.unlink()
        self.assertFalse(self.Region.search([("id", "=", region_id)]))

    # --- Province tests ---

    def test_province_create_and_read(self):
        """A province can be created under a region."""
        region = self._make_region(psgc_code="990000002")
        province = self._make_province(region, name="Test Province A", psgc_code="990200000")
        self.assertEqual(province.name, "Test Province A")
        self.assertEqual(province.region_id, region)

    def test_province_psgc_code_unique_constraint(self):
        """Creating two provinces with the same PSGC code raises ValidationError."""
        region = self._make_region(psgc_code="990000003")
        self._make_province(region, psgc_code="990300000")
        with self.assertRaises(psycopg2.errors.UniqueViolation):
            self._make_province(region, psgc_code="990300000")

    # --- City / Municipality tests ---

    def test_city_municipality_create(self):
        """A city can be created under a province with is_city=True."""
        region = self._make_region(psgc_code="990000004")
        province = self._make_province(region, psgc_code="990400000")
        city = self._make_city(province, name="Test City A", psgc_code="990401000", is_city=True)
        self.assertTrue(city.is_city)
        self.assertEqual(city.province_id, province)

    def test_municipality_create(self):
        """A municipality can be created with is_city=False (default)."""
        region = self._make_region(psgc_code="990000005")
        province = self._make_province(region, psgc_code="990500000")
        muni = self._make_city(province, name="Test Municipality", psgc_code="990501000")
        self.assertFalse(muni.is_city)

    def test_city_municipality_zip_code(self):
        """zip_code is stored and retrievable on a city/municipality."""
        region = self._make_region(psgc_code="990000006")
        province = self._make_province(region, psgc_code="990600000")
        city = self._make_city(province, psgc_code="990601000", zip_code="1234")
        self.assertEqual(city.zip_code, "1234")

    def test_city_psgc_code_unique_constraint(self):
        """Creating two cities with the same PSGC code raises ValidationError."""
        region = self._make_region(psgc_code="990000007")
        province = self._make_province(region, psgc_code="990700000")
        self._make_city(province, psgc_code="990701000")
        with self.assertRaises(psycopg2.errors.UniqueViolation):
            self._make_city(province, psgc_code="990701000")

    # --- Barangay tests ---

    def test_barangay_create_and_read(self):
        """A barangay can be created under a city/municipality."""
        region = self._make_region(psgc_code="990000008")
        province = self._make_province(region, psgc_code="990800000")
        city = self._make_city(province, psgc_code="990801000")
        barangay = self._make_barangay(city, name="Barangay Test A", psgc_code="990801001")
        self.assertEqual(barangay.name, "Barangay Test A")
        self.assertEqual(barangay.city_municipality_id, city)

    def test_barangay_psgc_code_unique_constraint(self):
        """Creating two barangays with the same PSGC code raises ValidationError."""
        region = self._make_region(psgc_code="990000009")
        province = self._make_province(region, psgc_code="990900000")
        city = self._make_city(province, psgc_code="990901000")
        self._make_barangay(city, psgc_code="990901001")
        with self.assertRaises(psycopg2.errors.UniqueViolation):
            self._make_barangay(city, psgc_code="990901001")

    # --- Hierarchy traversal ---

    def test_full_hierarchy_traversal(self):
        """Records at each PSGC level correctly reference their parent."""
        region = self._make_region(psgc_code="990000010")
        province = self._make_province(region, psgc_code="991000000")
        city = self._make_city(province, psgc_code="991001000")
        barangay = self._make_barangay(city, psgc_code="991001001")

        self.assertEqual(barangay.city_municipality_id, city)
        self.assertEqual(barangay.city_municipality_id.province_id, province)
        self.assertEqual(barangay.city_municipality_id.province_id.region_id, region)

    def test_sample_region_data_loaded(self):
        """The NCR sample region from psgc_regions.xml is present."""
        ncr = self.Region.search([("psgc_code", "=", "130000000")], limit=1)
        self.assertTrue(ncr, "NCR region should be loaded from sample data")
        self.assertEqual(ncr.name, "NCR")

    def test_sample_city_data_loaded(self):
        """Quezon City sample record from psgc_cities_municipalities.xml is present."""
        qc = self.CityMunicipality.search([("psgc_code", "=", "137404000")], limit=1)
        self.assertTrue(qc, "Quezon City should be loaded from sample data")
        self.assertTrue(qc.is_city)
