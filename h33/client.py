"""H33 API Client — HTTP client for the H33 post-quantum platform."""

import requests
from typing import Optional, Dict, Any


class H33Client:
    """Main client for the H33 API.

    Usage::

        from h33 import H33Client

        client = H33Client(api_key="h33_live_...", base_url="https://api.h33.ai")
        result = client.health()
    """

    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.h33.ai",
        timeout: int = 30,
    ):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json",
            "X-API-Key": api_key,
        })

    def _request(self, method: str, path: str, **kwargs) -> Dict[str, Any]:
        url = f"{self.base_url}{path}"
        kwargs.setdefault("timeout", self.timeout)
        resp = self.session.request(method, url, **kwargs)
        resp.raise_for_status()
        return resp.json()

    def health(self) -> Dict[str, Any]:
        """Check API health."""
        return self._request("GET", "/health")

    # ── Auth (Onboarding) ─────────────────────────────────────────────────

    def send_code(self, phone: str, country_code: str = "+1") -> Dict[str, Any]:
        """Send SMS OTP verification code."""
        return self._request("POST", "/api/auth/send-code", json={
            "phone": phone,
            "country_code": country_code,
        })

    def verify_code(self, phone: str, code: str) -> Dict[str, Any]:
        """Verify OTP code and get auth cookies."""
        return self._request("POST", "/api/auth/verify-code", json={
            "phone": phone,
            "code": code,
        })

    # ── Keys ──────────────────────────────────────────────────────────────

    def create_key(self, label: str = "default") -> Dict[str, Any]:
        """Create a new API key."""
        return self._request("POST", "/api/keys/create", json={"label": label})

    def list_keys(self) -> Dict[str, Any]:
        """List all API keys."""
        return self._request("GET", "/api/keys/list")

    def revoke_key(self, key_id: str) -> Dict[str, Any]:
        """Revoke an API key."""
        return self._request("POST", "/api/keys/revoke", json={"key_id": key_id})

    # ── Customer ──────────────────────────────────────────────────────────

    def get_me(self) -> Dict[str, Any]:
        """Get current customer profile."""
        return self._request("GET", "/api/customer/me")

    def get_usage(self) -> Dict[str, Any]:
        """Get usage statistics."""
        return self._request("GET", "/api/customer/usage")

    # ── FHE ───────────────────────────────────────────────────────────────

    def fhe_schemes(self) -> Dict[str, Any]:
        """List available FHE schemes and parameters."""
        return self._request("GET", "/api/fhe/schemes")

    def noise_estimate(
        self,
        n: int,
        t: int,
        q_bits: list,
        operations: list,
    ) -> Dict[str, Any]:
        """Estimate noise budget for a circuit.

        Args:
            n: Polynomial degree (e.g., 2048, 4096)
            t: Plaintext modulus (e.g., 65537)
            q_bits: Coefficient modulus bit sizes (e.g., [40, 40])
            operations: List of operation names ("add", "multiply", "relinearize", etc.)
        """
        return self._request("POST", "/api/fhe/noise-estimate", json={
            "n": n,
            "t": t,
            "q_bits": q_bits,
            "operations": operations,
        })

    # ── Storage Encryption ────────────────────────────────────────────────

    def encrypt_blob(
        self,
        plaintext: bytes,
        aad: Optional[bytes] = None,
    ) -> Dict[str, Any]:
        """Encrypt data with post-quantum hybrid encryption (Kyber+AES-256-GCM).

        Args:
            plaintext: Raw bytes to encrypt
            aad: Optional additional authenticated data

        Returns:
            {"ciphertext_b64": "...", "key_id": "..."}
        """
        import base64
        body = {"plaintext_b64": base64.b64encode(plaintext).decode()}
        if aad is not None:
            body["aad"] = base64.b64encode(aad).decode()
        return self._request("POST", "/api/storage/encrypt", json=body)

    def decrypt_blob(
        self,
        ciphertext_b64: str,
        key_id: str,
        aad: Optional[bytes] = None,
    ) -> bytes:
        """Decrypt a PQ-encrypted blob.

        Returns:
            Decrypted plaintext bytes
        """
        import base64
        body = {"ciphertext_b64": ciphertext_b64, "key_id": key_id}
        if aad is not None:
            body["aad"] = base64.b64encode(aad).decode()
        result = self._request("POST", "/api/storage/decrypt", json=body)
        return base64.b64decode(result["plaintext_b64"])

    def encrypt_fields(
        self,
        fields: list,
    ) -> Dict[str, Any]:
        """Encrypt fields with automatic sensitivity classification.

        Args:
            fields: List of {"name": "ssn", "value": "123-45-6789"}

        Returns:
            {"fields": [{"name", "sensitivity", "ciphertext_b64"}], "key_id": "..."}
        """
        return self._request("POST", "/api/storage/encrypt-fields", json={
            "fields": fields,
        })

    def rotate_encryption(
        self,
        ciphertext_b64: str,
        old_key_id: str,
        aad: Optional[bytes] = None,
    ) -> Dict[str, Any]:
        """Re-encrypt data under the current active key.

        Returns:
            {"ciphertext_b64": "...", "new_key_id": "..."}
        """
        import base64
        body = {"ciphertext_b64": ciphertext_b64, "old_key_id": old_key_id}
        if aad is not None:
            body["aad"] = base64.b64encode(aad).decode()
        return self._request("POST", "/api/storage/rotate", json=body)
