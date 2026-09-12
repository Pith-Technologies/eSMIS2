import logging

from odoo import _, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class PiiAware(models.AbstractModel):
    """Field-level PII classification and masking for eSMIS models.

    Inherit this mixin to declare which fields on a model carry PII, at what
    sensitivity tier, and how those values should be masked when displayed to
    users who lack the required group membership.

    Declare PII fields by overriding ``_pii_fields`` on the inheriting model:

        _pii_fields = {
            "philsys_number": {
                "tier": 3,
                "masking_pattern": "last4",
                "groups": "esmis_security.group_registrar_officer",
            },
            "name": {
                "tier": 2,
                "masking_pattern": "first_letter",
                "groups": None,
            },
        }

    Tier values align with ADR-005:
        1 — Public
        2 — Confidential
        3 — Sensitive Personal Information (SPI)

    Masking patterns:
        "last4"        — show only the last 4 characters (e.g., national IDs)
        "first_letter" — show first letter then *** (e.g., names)
        None / any     — full mask: ****
    """

    _name = "esmis.pii.aware"
    _description = "PII Aware Mixin"

    # Subclasses override this dict to register their PII fields.
    _pii_fields = {}

    def _get_pii_classification(self, field_name):
        """Return the PII classification dict for a field, or None.

        Args:
            field_name (str): Name of the field to look up.

        Returns:
            dict | None: Classification dict with keys 'tier', 'masking_pattern',
                         and 'groups', or None if the field is not classified.
        """
        return self._pii_fields.get(field_name)

    def _log_pii_access(self, field_name, access_type):
        """Create an audit log entry for PII field access.

        Writes a record to ``esmis.pii.access.log`` if that model is present
        in the registry (it lives in the optional esmis_audit module). When
        the model is absent this method silently does nothing — it must never
        raise an exception, as doing so would block normal reads and writes.

        No PII values are written to the log. Only the field name, model name,
        record ID, user ID, and action type are recorded.

        Args:
            field_name (str): The model field being accessed.
            access_type (str): One of 'read' or 'write'.
        """
        if "esmis.pii.access.log" not in self.env:
            return

        for record in self:
            try:
                # sudo: the PII access trail must be written whatever rights the
                # acting user holds on the log model. A user who could suppress
                # their own access record would defeat the audit requirement in
                # RA 10173; the create below writes only this access event.
                # nosemgrep: odoo-sudo-without-context
                self.env["esmis.pii.access.log"].sudo().create(
                    {
                        "model_name": record._name,
                        "record_id": record.id,
                        "field_name": field_name,
                        "access_type": access_type,
                        "user_id": self.env.uid,
                    }
                )
            except Exception:
                # Audit logging must never break the primary operation.
                _logger.exception(
                    "Failed to write PII access log for model=%s field=%s access_type=%s",
                    record._name,
                    field_name,
                    access_type,
                )

    def _mask_value(self, field_name, value):
        """Return a masked representation of a field value.

        Applies the masking pattern declared in ``_pii_fields`` for the given
        field. If the field is not classified, returns the value unchanged.
        If the value is falsy (None, empty string), returns an empty string.

        Masking patterns:
            "last4"        — keeps the last 4 characters, masks the rest with *.
                             e.g., "123456789012" → "********9012"
            "first_letter" — keeps the first character, replaces the rest with ***.
                             e.g., "Juan" → "J***"
            other / None   — full mask: "****"

        Args:
            field_name (str): The field whose value is being masked.
            value: The raw field value to mask.

        Returns:
            str: A masked string representation of the value.
        """
        if not value:
            return ""

        classification = self._get_pii_classification(field_name)
        if not classification:
            # Field is not classified — return the value as-is (as a string).
            return str(value)

        pattern = classification.get("masking_pattern")
        value_str = str(value)

        if pattern == "last4":
            if len(value_str) <= 4:
                return value_str
            return "*" * (len(value_str) - 4) + value_str[-4:]

        if pattern == "first_letter":
            if not value_str:
                return ""
            return value_str[0] + "***"

        # Default: full mask
        return "****"

    def action_view_pii_fields(self):
        """Return a list of PII field names declared on this model.

        Convenience method for inspection and UI generation. Returns the list
        of field names that have PII classifications.

        Returns:
            list[str]: Sorted list of field names with PII classifications.
        """
        return sorted(self._pii_fields.keys())

    def _check_pii_field_access(self, field_name):
        """Raise UserError if the current user lacks access to a PII field.

        Checks the ``groups`` entry in the field's classification. If a group
        is required and the current user is not a member, raises UserError.
        If no group is required, access is granted to all users.

        Args:
            field_name (str): The field to check access for.

        Raises:
            UserError: If the user is not a member of the required group.
        """
        classification = self._get_pii_classification(field_name)
        if not classification:
            return

        required_group = classification.get("groups")
        if not required_group:
            return

        if not self.env.user.has_group(required_group):
            raise UserError(_("You do not have permission to access the '%(field)s' field.") % {"field": field_name})
