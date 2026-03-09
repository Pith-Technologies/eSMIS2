from odoo.tests.common import TransactionCase


class TestPiiAware(TransactionCase):
    """Tests for the esmis.pii.aware abstract mixin."""

    def test_mixin_registered(self):
        """The PII aware mixin is registered in the Odoo registry."""
        self.assertIn("esmis.pii.aware", self.env)

    def test_mixin_has_required_methods(self):
        """The mixin provides all expected methods."""
        model = self.env["esmis.pii.aware"]
        expected_methods = [
            "_get_pii_classification",
            "_log_pii_access",
            "_mask_value",
            "_check_pii_field_access",
        ]
        for method_name in expected_methods:
            self.assertTrue(
                hasattr(model, method_name),
                f"Method '{method_name}' missing from esmis.pii.aware",
            )

    def test_get_pii_classification_unclassified(self):
        """_get_pii_classification returns None for unclassified fields."""
        model = self.env["esmis.pii.aware"]
        result = model._get_pii_classification("nonexistent_field")
        self.assertIsNone(result)

    def test_mask_value_last4(self):
        """Masking with 'last4' pattern shows only the last 4 characters."""
        # We need to temporarily set _pii_fields on the model class
        model_cls = type(self.env["esmis.pii.aware"])
        original = model_cls._pii_fields
        try:
            model_cls._pii_fields = {
                "test_id": {"tier": 3, "masking_pattern": "last4", "groups": None},
            }
            model = self.env["esmis.pii.aware"]
            result = model._mask_value("test_id", "123456789012")
            self.assertEqual(result, "********9012")
        finally:
            model_cls._pii_fields = original

    def test_mask_value_first_letter(self):
        """Masking with 'first_letter' shows first character + ***."""
        model_cls = type(self.env["esmis.pii.aware"])
        original = model_cls._pii_fields
        try:
            model_cls._pii_fields = {
                "test_name": {"tier": 2, "masking_pattern": "first_letter", "groups": None},
            }
            model = self.env["esmis.pii.aware"]
            result = model._mask_value("test_name", "Juan")
            self.assertEqual(result, "J***")
        finally:
            model_cls._pii_fields = original

    def test_mask_value_full_mask(self):
        """Masking with no pattern returns full mask '****'."""
        model_cls = type(self.env["esmis.pii.aware"])
        original = model_cls._pii_fields
        try:
            model_cls._pii_fields = {
                "test_field": {"tier": 3, "masking_pattern": None, "groups": None},
            }
            model = self.env["esmis.pii.aware"]
            result = model._mask_value("test_field", "sensitive data")
            self.assertEqual(result, "****")
        finally:
            model_cls._pii_fields = original

    def test_mask_value_empty_returns_empty(self):
        """Masking an empty value returns empty string."""
        model = self.env["esmis.pii.aware"]
        result = model._mask_value("any_field", "")
        self.assertEqual(result, "")

    def test_mask_value_none_returns_empty(self):
        """Masking None returns empty string."""
        model = self.env["esmis.pii.aware"]
        result = model._mask_value("any_field", None)
        self.assertEqual(result, "")

    def test_mask_value_unclassified_returns_value(self):
        """Masking an unclassified field returns the value unchanged."""
        model = self.env["esmis.pii.aware"]
        result = model._mask_value("not_classified", "hello")
        self.assertEqual(result, "hello")

    def test_log_pii_access_without_audit_module(self):
        """_log_pii_access does nothing when esmis.pii.access.log is not installed."""
        model = self.env["esmis.pii.aware"]
        # Should not raise — gracefully handles missing model
        model._log_pii_access("test_field", "read")
