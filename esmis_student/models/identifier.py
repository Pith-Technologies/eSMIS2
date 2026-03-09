import base64
import hashlib
import hmac
import logging
import os

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)

# Environment variable name for the encryption key (base64-encoded 32-byte key).
_ENCRYPTION_KEY_ENV = "ESMIS_ENCRYPTION_KEY"
# ir.config_parameter key used as fallback when the env var is not set.
_ENCRYPTION_KEY_PARAM = "esmis.encryption_key"


def _get_encryption_key():
    """Return the 32-byte AES-256 key from the environment variable, or None.

    Resolution order for callers:
    1. ESMIS_ENCRYPTION_KEY environment variable (base64-encoded 32 bytes).
    2. esmis.encryption_key ir.config_parameter (base64-encoded 32 bytes).
    3. Generate a new random key and store it in ir.config_parameter.

    The key is NOT cached here — callers access it fresh per operation so that
    key rotation takes effect without a server restart.
    """
    env_val = os.environ.get(_ENCRYPTION_KEY_ENV)
    if not env_val:
        return None
    try:
        key = base64.b64decode(env_val)
        if len(key) == 32:
            return key
        _logger.warning(
            "ESMIS_ENCRYPTION_KEY env var is set but does not decode to 32 bytes; "
            "falling back to ir.config_parameter"
        )
    except (ValueError, base64.binascii.Error):
        _logger.warning(
            "ESMIS_ENCRYPTION_KEY env var is set but cannot be base64-decoded; "
            "falling back to ir.config_parameter"
        )
    return None


def _decode_stored_key(stored):
    """Decode a base64-encoded key from ir.config_parameter. Returns 32 bytes or None."""
    try:
        key = base64.b64decode(stored)
        return key if len(key) == 32 else None
    except (ValueError, base64.binascii.Error):
        return None


class EsmisIdentifier(models.Model):
    """Multi-type identifier store with AES-256-GCM field-level encryption.

    Stores government and institutional identifiers (PhilSys, LRN, TIN, etc.)
    for a student partner. The plaintext value is never written to the database
    — only the encrypted ciphertext and a HMAC-SHA256 blind index for search.

    Encryption key resolution: ESMIS_ENCRYPTION_KEY env var → esmis.encryption_key
    ir.config_parameter → auto-generated key stored in ir.config_parameter.

    The blind index allows equality searches on the encrypted value without
    decrypting all rows. It uses HMAC-SHA256 with a separate key derived from
    the main key.
    """

    _name = "esmis.identifier"
    _description = "Multi-type identifier store with encryption"
    _inherit = ["esmis.pii.aware"]
    _order = "partner_id, type_id"
    _rec_name = "type_id"

    partner_id = fields.Many2one(
        comodel_name="res.partner",
        string="Student",
        required=True,
        ondelete="cascade",
        index=True,
    )
    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Campus",
        related="partner_id.company_id",
        store=True,
        index=True,
    )
    type_id = fields.Many2one(
        comodel_name="esmis.vocabulary.code",
        string="Identifier Type",
        required=True,
        help="Type of identifier (e.g. PhilSys, LRN, TIN). Seeded by country modules.",
    )
    system_uri = fields.Char(
        string="System URI",
        related="type_id.namespace_uri",
        store=True,
        help="Namespace URI of the identifier type vocabulary",
    )
    # The plaintext value field is write-only at the model level: writing it
    # encrypts and stores value_ciphertext + value_blind_index, then clears
    # itself. Reading returns an empty string for security.
    value = fields.Char(
        string="Identifier Value",
        groups="esmis_student.group_esmis_registrar_officer",
        help="Plain-text identifier value. Write-only: stored as encrypted ciphertext.",
    )
    value_ciphertext = fields.Binary(
        string="Encrypted Value",
        attachment=False,
        help="AES-256-GCM encrypted identifier value",
    )
    value_blind_index = fields.Char(
        string="Search Index",
        index=True,
        help="HMAC-SHA256 blind index for equality search without decryption",
    )

    _unique_identifier_per_type = models.Constraint(
        "UNIQUE(partner_id, type_id)",
        "Each identifier type may only appear once per student.",
    )

    # PII classification for the identifier value
    _pii_fields = {
        "value": {
            "tier": 3,
            "masking_pattern": "last4",
            "groups": "esmis_student.group_esmis_registrar_officer",
        },
    }

    # --- Encryption helpers ---

    def _resolve_encryption_key(self):
        """Return (encrypt_key, index_key) as 32-byte bytes objects.

        The index key is derived from the main key by appending '-index' before
        hashing so the two keys are distinct without requiring separate storage.
        """
        key_bytes = _get_encryption_key()
        if key_bytes is None:
            # Attempt to read from ir.config_parameter (sudo because the
            # parameter is system-level and should not be ACL-gated per user).
            ICP = self.env["ir.config_parameter"].sudo()
            stored = ICP.get_param(_ENCRYPTION_KEY_PARAM)
            if stored:
                key_bytes = _decode_stored_key(stored)

            if key_bytes is None:
                # Generate a new key and persist it.
                key_bytes = os.urandom(32)
                ICP.set_param(_ENCRYPTION_KEY_PARAM, base64.b64encode(key_bytes).decode())
                _logger.info(
                    "Generated new esmis encryption key and stored in ir.config_parameter. "
                    "For production, set the ESMIS_ENCRYPTION_KEY environment variable."
                )

        index_key = hashlib.sha256(key_bytes + b"-index").digest()
        return key_bytes, index_key

    def _encrypt_value(self, plaintext):
        """Encrypt plaintext with AES-256-GCM. Returns ciphertext bytes.

        The nonce is prepended to the ciphertext so it can be recovered on
        decryption. Format: 12-byte nonce || ciphertext+tag.
        """
        try:
            from cryptography.hazmat.primitives.ciphers.aead import AESGCM
        except ImportError as exc:
            raise UserError(
                _(
                    "The 'cryptography' Python package is required for identifier encryption. "
                    "Install it with: uv add cryptography"
                )
            ) from exc

        enc_key, _idx_key = self._resolve_encryption_key()
        aesgcm = AESGCM(enc_key)
        nonce = os.urandom(12)
        ciphertext = aesgcm.encrypt(nonce, plaintext.encode("utf-8"), None)
        return nonce + ciphertext

    def _decrypt_value(self, ciphertext_bytes):
        """Decrypt AES-256-GCM ciphertext. Returns plaintext string or None.

        Returns None (rather than raising) when decryption fails so callers
        can distinguish between 'no value stored' and 'decryption error'.
        """
        if not ciphertext_bytes:
            return None
        try:
            from cryptography.exceptions import InvalidKey, InvalidTag
            from cryptography.hazmat.primitives.ciphers.aead import AESGCM
        except ImportError:
            _logger.error("cryptography package not installed; cannot decrypt identifier value")
            return None

        try:
            dec_key, _idx_key = self._resolve_encryption_key()
            raw = bytes(ciphertext_bytes)
            nonce = raw[:12]
            ct = raw[12:]
            aesgcm = AESGCM(dec_key)
            return aesgcm.decrypt(nonce, ct, None).decode("utf-8")
        except (ValueError, UnicodeDecodeError, InvalidTag, InvalidKey, base64.binascii.Error):
            _logger.error(
                "Failed to decrypt identifier value for record id=%s (model=%s)",
                self.id,
                self._name,
            )
            return None

    def _compute_blind_index(self, plaintext):
        """Return HMAC-SHA256 hex digest for blind index search."""
        _enc_key, index_key = self._resolve_encryption_key()
        return hmac.new(index_key, plaintext.encode("utf-8"), hashlib.sha256).hexdigest()

    # --- ORM overrides ---

    @api.model_create_multi
    def create(self, vals_list):
        """Encrypt the value field before inserting into the database."""
        for vals in vals_list:
            plaintext = vals.pop("value", None)
            if plaintext:
                self._encrypt_and_index(vals, plaintext)
        return super().create(vals_list)

    def write(self, vals):
        """Encrypt the value field before updating the database."""
        plaintext = vals.pop("value", None)
        if plaintext:
            self._encrypt_and_index(vals, plaintext)
        return super().write(vals)

    def _encrypt_and_index(self, vals, plaintext):
        """Populate value_ciphertext and value_blind_index from plaintext.

        Mutates vals in-place. Does not return anything.
        """
        if not plaintext:
            return
        ciphertext = self._encrypt_value(plaintext)
        vals["value_ciphertext"] = base64.b64encode(ciphertext).decode()
        vals["value_blind_index"] = self._compute_blind_index(plaintext)

    def get_decrypted_value(self):
        """Return the decrypted plaintext value for this record.

        Access is restricted to registrar officers. Raises UserError for
        unauthorized callers and returns None when decryption fails.
        """
        self.ensure_one()
        if not self.env.user.has_group("esmis_student.group_esmis_registrar_officer"):
            raise UserError(_("You do not have permission to view decrypted identifier values."))
        if not self.value_ciphertext:
            return None
        raw = base64.b64decode(self.value_ciphertext)
        return self._decrypt_value(raw)

    @api.model
    def search_by_value(self, plaintext):
        """Search for identifiers matching plaintext using the blind index.

        This is the correct way to search by identifier value without
        decrypting all rows. Returns a recordset.
        """
        blind_index = self._compute_blind_index_for_search(plaintext)
        return self.search([("value_blind_index", "=", blind_index)])

    @api.model
    def _compute_blind_index_for_search(self, plaintext):
        """Compute HMAC-SHA256 blind index without requiring a record instance."""
        key_bytes = _get_encryption_key()
        if key_bytes is None:
            stored = self.env["ir.config_parameter"].sudo().get_param(_ENCRYPTION_KEY_PARAM)
            if stored:
                key_bytes = _decode_stored_key(stored)
        if key_bytes is None:
            raise UserError(_("No encryption key configured. Cannot search by identifier value."))
        index_key = hashlib.sha256(key_bytes + b"-index").digest()
        return hmac.new(index_key, plaintext.encode("utf-8"), hashlib.sha256).hexdigest()

    @api.constrains("type_id", "partner_id")
    def _check_unique_type_per_partner(self):
        """Raise user-friendly error on duplicate identifier type per partner."""
        for rec in self:
            duplicate = self.search_count(
                [
                    ("partner_id", "=", rec.partner_id.id),
                    ("type_id", "=", rec.type_id.id),
                    ("id", "!=", rec.id),
                ]
            )
            if duplicate:
                raise ValidationError(
                    _("An identifier of type '%(type)s' already exists for this student.")
                    % {"type": rec.type_id.display}
                )
