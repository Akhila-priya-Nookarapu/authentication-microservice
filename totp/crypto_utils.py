# totp/crypto_utils.py
import base64
import re
from typing import Union

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.backends import default_backend


_HEX64_RE = re.compile(r"^[0-9a-f]{64}$")


def load_private_key_from_pem(pem_bytes: bytes) -> rsa.RSAPrivateKey:
    """
    Load an RSA private key from PEM bytes (unencrypted key).
    """
    return serialization.load_pem_private_key(
        pem_bytes,
        password=None,
        backend=default_backend()
    )


def decrypt_seed(encrypted_seed_b64: str, private_key: Union[rsa.RSAPrivateKey, bytes, str]) -> str:
    """
    Decrypt base64-encoded encrypted seed using RSA/OAEP (SHA-256).
    Args:
        encrypted_seed_b64: base64 encoded ciphertext (string)
        private_key: either an RSA private key object (cryptography) or
                     PEM bytes or path to PEM file (str).
    Returns:
        Decrypted hex seed as a 64-character lowercase string.
    Raises:
        ValueError on invalid input or decryption/validation failure.
    """
    # Accept private_key as loaded key, bytes, or file path
    if isinstance(private_key, (bytes, bytearray)):
        priv = load_private_key_from_pem(bytes(private_key))
    elif isinstance(private_key, str):
        # treat as a file path
        with open(private_key, "rb") as f:
            pem = f.read()
        priv = load_private_key_from_pem(pem)
    else:
        # assume it's already an RSAPrivateKey instance
        priv = private_key

    # 1) Base64 decode
    try:
        ciphertext = base64.b64decode(encrypted_seed_b64, validate=True)
    except Exception as e:
        raise ValueError(f"invalid base64 encrypted_seed: {e}")

    # 2) RSA/OAEP decrypt with SHA-256
    try:
        plaintext_bytes = priv.decrypt(
            ciphertext,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
    except Exception as e:
        # Do not leak sensitive info — raise generic error
        raise ValueError(f"decryption failed: {e}")

    # 3) Decode bytes to UTF-8 string
    try:
        seed_str = plaintext_bytes.decode("utf-8").strip()
    except Exception as e:
        raise ValueError(f"failed to decode plaintext as utf-8: {e}")

    # 4) Validate: must be 64-character lowercase hex
    # (task says 64-character hexadecimal string; examples use lowercase)
    if not _HEX64_RE.match(seed_str):
        raise ValueError("decrypted seed is not a 64-character lowercase hex string")

    return seed_str
