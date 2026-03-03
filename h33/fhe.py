"""FHE Client — ctypes FFI to h33-fhe-client Rust cdylib.

Provides client-side BFV encryption for biometric embeddings and
other FHE operations without exposing plaintext to the server.

Requires the compiled cdylib (libh33_fhe_client.so / .dylib / .dll).
Build with: cd h33-fhe-client && cargo build --release

Usage::

    from h33.fhe import FheEncryptor

    enc = FheEncryptor.from_public_key("path/to/public_key.json")
    ciphertext_json = enc.encrypt_embedding([0.1, 0.2, ...])  # 128-dim float vector
"""

import ctypes
import json
import os
import sys
from typing import List, Optional


def _find_lib() -> Optional[str]:
    """Search for the h33-fhe-client cdylib."""
    names = {
        "linux": "libh33_fhe_client.so",
        "darwin": "libh33_fhe_client.dylib",
        "win32": "h33_fhe_client.dll",
    }
    libname = names.get(sys.platform, "libh33_fhe_client.so")

    # Check common locations
    search_paths = [
        os.path.join(os.path.dirname(__file__), "..", "..", "h33-fhe-client", "target", "release"),
        os.path.join(os.path.dirname(__file__), ".."),
        "/usr/local/lib",
        "/usr/lib",
    ]

    for path in search_paths:
        full = os.path.join(path, libname)
        if os.path.exists(full):
            return full
    return None


class FheEncryptor:
    """Client-side FHE encryptor using h33-fhe-client Rust cdylib via ctypes.

    This encrypts data locally so the server never sees plaintext.
    The server operates on encrypted data using homomorphic operations.
    """

    def __init__(self, handle, lib):
        self._handle = handle
        self._lib = lib

    @classmethod
    def from_public_key(cls, pk_json_path: str, embedding_dim: int = 128) -> "FheEncryptor":
        """Load from a public key JSON file.

        Args:
            pk_json_path: Path to public key JSON (from /api/fhe/init)
            embedding_dim: Embedding dimension (default 128)
        """
        lib_path = _find_lib()
        if lib_path is None:
            raise FileNotFoundError(
                "h33-fhe-client cdylib not found. "
                "Build it with: cd h33-fhe-client && cargo build --release"
            )

        lib = ctypes.CDLL(lib_path)

        # Set up function signatures
        lib.h33_encryptor_new.argtypes = [
            ctypes.c_char_p,  # public_key_json
            ctypes.c_size_t,  # json_len
            ctypes.c_size_t,  # embedding_dim
            ctypes.POINTER(ctypes.c_void_p),  # out_handle
        ]
        lib.h33_encryptor_new.restype = ctypes.c_int

        lib.h33_encrypt_embedding.argtypes = [
            ctypes.c_void_p,  # handle
            ctypes.POINTER(ctypes.c_float),  # embedding
            ctypes.c_size_t,  # dim
            ctypes.POINTER(ctypes.c_char_p),  # out_json
            ctypes.POINTER(ctypes.c_size_t),  # out_len
        ]
        lib.h33_encrypt_embedding.restype = ctypes.c_int

        lib.h33_encryptor_free.argtypes = [ctypes.c_void_p]
        lib.h33_encryptor_free.restype = None

        lib.h33_free_bytes.argtypes = [ctypes.c_char_p, ctypes.c_size_t]
        lib.h33_free_bytes.restype = None

        with open(pk_json_path, "rb") as f:
            pk_json = f.read()

        handle = ctypes.c_void_p()
        rc = lib.h33_encryptor_new(pk_json, len(pk_json), embedding_dim, ctypes.byref(handle))
        if rc != 0:
            raise RuntimeError(f"h33_encryptor_new failed with code {rc}")

        return cls(handle, lib)

    def encrypt_embedding(self, embedding: List[float]) -> str:
        """Encrypt a float embedding vector.

        Args:
            embedding: List of floats (must match embedding_dim)

        Returns:
            JSON string containing the encrypted ciphertext
        """
        arr = (ctypes.c_float * len(embedding))(*embedding)
        out_json = ctypes.c_char_p()
        out_len = ctypes.c_size_t()

        rc = self._lib.h33_encrypt_embedding(
            self._handle, arr, len(embedding),
            ctypes.byref(out_json), ctypes.byref(out_len),
        )
        if rc != 0:
            raise RuntimeError(f"h33_encrypt_embedding failed with code {rc}")

        result = out_json.value[:out_len.value].decode("utf-8")

        # Free the Rust-allocated buffer
        self._lib.h33_free_bytes(out_json, out_len)

        return result

    def __del__(self):
        if hasattr(self, "_handle") and self._handle:
            self._lib.h33_encryptor_free(self._handle)
            self._handle = None
