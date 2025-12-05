#!/usr/bin/env python3
"""
Generate commit proof:
1. Read latest commit hash (git log -1 --format=%H)
2. Sign the ASCII commit hash using RSA-PSS SHA256 with student_private.pem
   - message bytes = commit_hash.encode('utf-8')
3. Encrypt the signature bytes with instructor_public.pem using RSA-OAEP SHA256
4. Base64-encode the encrypted ciphertext and print:
   Commit Hash: <40-char hex>
   Encrypted Signature: <base64 single line>
"""

import subprocess
import sys
import base64
from pathlib import Path

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.backends import default_backend

# Adjust paths if your PEMs are elsewhere
STUDENT_PRIV_PATH = Path("data/student_private.pem")
INSTRUCTOR_PUB_PATH = Path("data/instructor_public.pem")

def get_latest_commit_hash():
    try:
        out = subprocess.check_output(["git", "log", "-1", "--format=%H"], stderr=subprocess.DEVNULL)
        return out.decode("utf-8").strip()
    except subprocess.CalledProcessError as e:
        sys.exit("ERROR: cannot get git commit hash. Make sure this is a git repo and commits exist.")

def load_private_key(path: Path):
    b = path.read_bytes()
    return serialization.load_pem_private_key(b, password=None, backend=default_backend())

def load_public_key(path: Path):
    b = path.read_bytes()
    return serialization.load_pem_public_key(b, backend=default_backend())

def sign_commit_hash(private_key, commit_hash: str) -> bytes:
    message = commit_hash.encode("utf-8")  # ASCII/UTF-8 bytes of commit hash
    signature = private_key.sign(
        message,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )
    return signature

def encrypt_signature(pub_key, signature: bytes) -> bytes:
    ciphertext = pub_key.encrypt(
        signature,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return ciphertext

def main():
    if not STUDENT_PRIV_PATH.exists():
        sys.exit(f"ERROR: student private key not found at {STUDENT_PRIV_PATH}")
    if not INSTRUCTOR_PUB_PATH.exists():
        sys.exit(f"ERROR: instructor public key not found at {INSTRUCTOR_PUB_PATH}")

    commit_hash = get_latest_commit_hash()
    if len(commit_hash) < 40:
        # Git normally produces 40-character SHA1; warn but continue if shortened
        print("WARNING: commit hash shorter than 40 characters:", commit_hash, file=sys.stderr)

    priv = load_private_key(STUDENT_PRIV_PATH)
    pub = load_public_key(INSTRUCTOR_PUB_PATH)

    signature = sign_commit_hash(priv, commit_hash)
    ciphertext = encrypt_signature(pub, signature)
    b64 = base64.b64encode(ciphertext).decode("ascii")

    # Print exactly what the grader expects: commit hash and single-line base64 ciphertext
    print(commit_hash)
    print(b64)

if __name__ == "__main__":
    main()
