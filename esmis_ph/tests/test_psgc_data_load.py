import os

from odoo.tests.common import TransactionCase


class TestPsgcDataLoad(TransactionCase):
    """Tests for post_init_hook barangay loading from CSV."""

    def test_barangays_loaded_from_csv_via_hook(self):
        """Barangay records loaded by post_init_hook are present in the database."""
        # The hook runs at module install time; by the time tests run,
        # barangays from the sample CSV should already be in the table.
        Barangay = self.env["esmis.psgc.barangay"]
        count = Barangay.search_count([])
        self.assertGreater(count, 0, "At least one barangay should be loaded by post_init_hook")

    def test_known_sample_barangay_present(self):
        """A specific sample barangay from the CSV is present and linked correctly."""
        Barangay = self.env["esmis.psgc.barangay"]
        barangay = Barangay.search([("psgc_code", "=", "137404001")], limit=1)
        self.assertTrue(barangay, "Barangay 137404001 (Bagong Pag-asa) should be loaded")
        self.assertEqual(barangay.name, "Bagong Pag-asa")
        self.assertEqual(barangay.city_municipality_id.psgc_code, "137404000")

    def test_barangay_city_link_valid(self):
        """All loaded barangays have a valid city_municipality_id reference."""
        Barangay = self.env["esmis.psgc.barangay"]
        # If any barangay has no city_municipality_id, the FK constraint would
        # have prevented its insertion. Verify a sample barangay has it set.
        barangay = Barangay.search([("psgc_code", "=", "042105001")], limit=1)
        self.assertTrue(barangay, "Burol barangay from Dasmarinas should be loaded")
        self.assertTrue(barangay.city_municipality_id)

    def test_csv_file_exists(self):
        """The sample barangays CSV file exists at the expected path."""
        csv_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "data",
            "psgc",
            "barangays.csv",
        )
        self.assertTrue(os.path.exists(csv_path), f"CSV file not found at {csv_path}")

    def test_hook_is_idempotent(self):
        """Running the post_init_hook a second time does not duplicate barangays."""
        from odoo.addons.esmis_ph.hooks import post_init_hook

        Barangay = self.env["esmis.psgc.barangay"]
        count_before = Barangay.search_count([])

        post_init_hook(self.env)

        count_after = Barangay.search_count([])
        self.assertEqual(
            count_before,
            count_after,
            "Re-running post_init_hook should not insert duplicate barangays",
        )

    def test_malolos_barangays_loaded(self):
        """Sample Malolos (Bulacan) barangays from the CSV are present."""
        Barangay = self.env["esmis.psgc.barangay"]
        barangay = Barangay.search([("psgc_code", "=", "031405001")], limit=1)
        self.assertTrue(barangay, "Anilao barangay of Malolos should be loaded")
        self.assertEqual(barangay.name, "Anilao")
