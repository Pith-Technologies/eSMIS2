import logging

from odoo import _, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class ConsentMixin(models.AbstractModel):
    """Consent enforcement mixin for models that process PII.

    Inherit this mixin on any model whose operations require an active
    RA 10173 consent record before student PII may be processed. The mixin
    provides helpers to check consent status and to block batch exports when
    consent is absent.

    Usage:
        class MyModel(models.Model):
            _name = "my.model"
            _inherit = ["my.model", "esmis.consent.mixin"]

            def export_to_ched(self):
                self._check_consent_for_export()
                # ... proceed

    Per RA 10173, consent must never be bypassed with sudo(). Consent can
    also be withdrawn between requests, so results must never be cached.
    """

    _name = "esmis.consent.mixin"
    _description = "Consent Mixin"

    def _get_consent_partner(self):
        """Return the res.partner to check consent records against.

        The default implementation returns ``self.partner_id``. Override
        this method if the model stores the partner reference under a
        different field name.

        Returns:
            res.partner: The partner record whose consent records are checked.
        """
        self.ensure_one()
        return self.partner_id

    def _has_active_consent(self, purpose):
        """Check whether the record's partner holds active consent for a purpose.

        An active consent record is one where:
        - The purpose matches the given ``purpose`` code.
        - ``date_withdrawn`` is not set (i.e., consent has not been revoked).

        Returns ``False`` when:
        - No ``esmis.consent`` model exists in the registry (e.g., during
          installation before esmis_consent is fully loaded).
        - The partner cannot be resolved.
        - No matching consent record exists.
        - The matching record has ``date_withdrawn`` set.

        Args:
            purpose (str): Purpose code to check (e.g., 'consent_alumni_tracking').

        Returns:
            bool: True if an active consent record exists, False otherwise.
        """
        self.ensure_one()

        if "esmis.consent" not in self.env:
            _logger.debug(
                "esmis.consent model not in registry; consent check for purpose '%s' returns False",
                purpose,
            )
            return False

        partner = self._get_consent_partner()
        if not partner:
            _logger.debug(
                "No partner resolved for record %s (id=%s); consent check for purpose '%s' returns False",
                self._name,
                self.id,
                purpose,
            )
            return False

        consent = self.env["esmis.consent"].search(
            [
                ("partner_id", "=", partner.id),
                ("purpose", "=", purpose),
                ("date_withdrawn", "=", False),
            ],
            limit=1,
        )
        return bool(consent)

    def _check_consent_for_export(self):
        """Raise UserError if any record in self lacks active export consent.

        Iterates over all records in the recordset and verifies that each one
        has an active ``consent_ched_reporting`` consent record. Raises a
        single UserError naming the count of non-consenting records so that
        callers can surface a meaningful message to the user.

        The export purpose ``consent_ched_reporting`` is the default. Override
        this method if a different purpose governs the export in question.

        Raises:
            UserError: When one or more records lack active consent for export.
        """
        missing_count = 0
        for record in self:
            if not record._has_active_consent("consent_ched_reporting"):
                missing_count += 1

        if missing_count:
            raise UserError(
                _(
                    "%(count)s record(s) cannot be exported: active consent for "
                    "CHED reporting is missing or has been withdrawn."
                )
                % {"count": missing_count}
            )
