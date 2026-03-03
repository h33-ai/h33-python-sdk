# h33 — Post-Quantum Encryption SDK for Python

The official Python SDK for [H33](https://h33.ai), the post-quantum encryption platform delivering 1.6M authentications/sec with lattice-based cryptography.

## Install

```bash
pip install h33
```

## Quick Start

```python
from h33 import H33Client

client = H33Client(api_key="h33_live_...", base_url="https://api.h33.ai")

# Post-quantum storage encryption (Kyber + AES-256-GCM)
result = client.encrypt_blob(b"sensitive data")
ciphertext = result["ciphertext_b64"]
key_id = result["key_id"]

# Decrypt
plaintext = client.decrypt_blob(ciphertext, key_id)
assert plaintext == b"sensitive data"
```

## Storage Encryption

Encrypt data at rest with hybrid post-quantum encryption (ML-KEM/Kyber + AES-256-GCM):

```python
from h33 import StorageClient

storage = StorageClient(api_key="h33_live_...")

# Encrypt with optional authenticated data
result = storage.encrypt(b"patient record", aad=b"user:12345")
print(result["key_id"])  # Kyber key ID for decryption

# Decrypt
plaintext = storage.decrypt(result["ciphertext_b64"], result["key_id"], aad=b"user:12345")

# Field-level encryption with automatic sensitivity classification
fields = storage.encrypt_fields([
    {"name": "ssn", "value": "123-45-6789"},
    {"name": "name", "value": "Jane Doe"},
    {"name": "email", "value": "jane@example.com"},
])
# Each field gets a sensitivity level (Confidential, Internal, etc.)

# Key rotation — re-encrypt under the current active key
rotated = storage.rotate(result["ciphertext_b64"], result["key_id"])
```

## Client-Side FHE (Homomorphic Encryption)

Encrypt biometric embeddings on the client so the server never sees plaintext:

```python
from h33 import FheEncryptor

# Load public key from H33 API
enc = FheEncryptor.from_public_key("public_key.json", embedding_dim=128)

# Encrypt a 128-dimensional face embedding
embedding = [0.1, 0.2, 0.03, ...]  # from your ML model
ciphertext_json = enc.encrypt_embedding(embedding)

# Send ciphertext to H33 for matching — server operates on encrypted data
```

Requires the `h33-fhe-client` native library. Build from source:

```bash
cd h33-fhe-client && cargo build --release
```

## API Reference

### H33Client

| Method | Description |
|--------|-------------|
| `health()` | Check API status |
| `send_code(phone)` | Send SMS OTP for authentication |
| `verify_code(phone, code)` | Verify OTP and get session |
| `create_key(label)` | Create a new API key |
| `list_keys()` | List all API keys |
| `revoke_key(key_id)` | Revoke an API key |
| `encrypt_blob(plaintext, aad)` | PQ-encrypt arbitrary data |
| `decrypt_blob(ciphertext_b64, key_id, aad)` | Decrypt PQ-encrypted data |
| `encrypt_fields(fields)` | Field-level PQ encryption |
| `rotate_encryption(ciphertext_b64, old_key_id, aad)` | Re-encrypt under current key |
| `fhe_schemes()` | List available FHE schemes |
| `noise_estimate(n, t, q_bits, operations)` | Estimate FHE noise budget |

### StorageClient

Convenience wrapper for encryption-only workflows:

| Method | Description |
|--------|-------------|
| `encrypt(plaintext, aad)` | Encrypt bytes |
| `decrypt(ciphertext_b64, key_id, aad)` | Decrypt bytes |
| `encrypt_fields(fields)` | Field-level encryption |
| `rotate(ciphertext_b64, old_key_id, aad)` | Key rotation |

## Platform

H33 is the world's fastest post-quantum authentication platform:

- **1.6M auth/sec** on AWS Graviton4 (96 vCPUs)
- **~42 microseconds** per authentication
- **Kyber + AES-256-GCM** hybrid encryption for data at rest
- **BFV Fully Homomorphic Encryption** for biometric matching on encrypted data
- **Dilithium digital signatures** for attestation
- **Zero-knowledge proofs** for privacy-preserving verification

Learn more at [h33.ai](https://h33.ai)

## Documentation

- [H33 Platform](https://h33.ai)
- [API Documentation](https://h33.ai/docs)
- [FHE Overview](https://h33.ai/fhe)
- [Post-Quantum Cryptography](https://h33.ai/pqc)
- [White Paper](https://h33.ai/white-paper)
- [Benchmarks](https://h33.ai/benchmarks)

## License

MIT — see [LICENSE](LICENSE)
