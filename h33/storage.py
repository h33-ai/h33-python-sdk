"""Standalone Storage Encryption Client.

Thin wrapper around H33Client's storage methods for users who only need
data-at-rest encryption without the full SDK.
"""

from .client import H33Client
from typing import Optional, Dict, Any, List


class StorageClient:
    """Post-quantum storage encryption client.

    Usage::

        from h33 import StorageClient

        storage = StorageClient(api_key="h33_live_...")

        # Encrypt
        result = storage.encrypt(b"sensitive data")
        ciphertext = result["ciphertext_b64"]
        key_id = result["key_id"]

        # Decrypt
        plaintext = storage.decrypt(ciphertext, key_id)
        assert plaintext == b"sensitive data"
    """

    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.h33.ai",
    ):
        self._client = H33Client(api_key=api_key, base_url=base_url)

    def encrypt(self, plaintext: bytes, aad: Optional[bytes] = None) -> Dict[str, Any]:
        """Encrypt data with Kyber+AES-256-GCM."""
        return self._client.encrypt_blob(plaintext, aad)

    def decrypt(self, ciphertext_b64: str, key_id: str, aad: Optional[bytes] = None) -> bytes:
        """Decrypt PQ-encrypted data."""
        return self._client.decrypt_blob(ciphertext_b64, key_id, aad)

    def encrypt_fields(self, fields: List[Dict[str, str]]) -> Dict[str, Any]:
        """Encrypt fields with sensitivity classification."""
        return self._client.encrypt_fields(fields)

    def rotate(self, ciphertext_b64: str, old_key_id: str, aad: Optional[bytes] = None) -> Dict[str, Any]:
        """Re-encrypt under current active key."""
        return self._client.rotate_encryption(ciphertext_b64, old_key_id, aad)
