#!/usr/bin/env python3
import os
import sys
import datetime
import base64
import pyotp

SEED_PATH = "data/seed.txt"   # path to your seed file

def read_hex_seed():
    try:
        with open(SEED_PATH, "r") as f:
            return f.read().strip()
    except FileNotFoundError:
        sys.stderr.write("seed.txt not found\n")
        return None

def hex_to_base32(hex_seed):
    raw = bytes.fromhex(hex_seed)
    return base64.b32encode(raw).decode("utf-8").replace("=", "")

def main():
    hex_seed = read_hex_seed()
    if not hex_seed:
        return

    base32_seed = hex_to_base32(hex_seed)
    totp = pyotp.TOTP(base32_seed)
    code = totp.now()

    timestamp = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    print(f"{timestamp} - 2FA Code: {code}")

if __name__ == "__main__":
    main()
