from fastapi import FastAPI, Body
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding
import base64, time, os

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# ✅ Allow all origins for Swagger testing
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


from totp.totp_utils import generate_totp_code, verify_totp_code

app = FastAPI()

class DecryptRequest(BaseModel):
    encrypted_seed: str

@app.post("/decrypt-seed")
async def decrypt_seed(request: DecryptRequest):
    try:
        key_path = os.path.join("data", "student_private.pem")
        with open(key_path, "rb") as key_file:
            private_key = serialization.load_pem_private_key(
                key_file.read(),
                password=None
            )
        cipher_bytes = base64.b64decode(request.encrypted_seed)
        plaintext = private_key.decrypt(
            cipher_bytes,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        seed = plaintext.decode('utf-8').strip()
        if len(seed) != 64 or not all(c in '0123456789abcdef' for c in seed.lower()):
            raise ValueError("Invalid seed format")
        seed_path = os.path.join("data", "seed.txt")
        with open(seed_path, "w") as f:
            f.write(seed)
    except Exception:
        return JSONResponse(status_code=500, content={"error": "Decryption failed"})
    return {"status": "ok"}

@app.get("/generate-2fa")
async def generate_2fa():
    seed_path = os.path.join("data", "seed.txt")
    try:
        with open(seed_path, "r") as f:
            seed = f.read().strip()
        if len(seed) != 64 or not all(c in '0123456789abcdef' for c in seed.lower()):
            raise FileNotFoundError
    except Exception:
        return JSONResponse(status_code=500, content={"error": "Seed not decrypted yet"})
    code = generate_totp_code(seed)
    now = int(time.time())
    valid_for = 30 - (now % 30)
    return {"code": code, "valid_for": valid_for}

@app.post("/verify-2fa")
async def verify_2fa(payload: dict = Body(...)):
    try:
        code = payload.get("code")
        if code is None:
            return JSONResponse(status_code=400, content={"error": "Missing code"})

        seed_path = os.path.join("data", "seed.txt")
        with open(seed_path, "r") as f:
            seed = f.read().strip()
        if len(seed) != 64 or not all(c in '0123456789abcdef' for c in seed.lower()):
            raise ValueError("Invalid seed format")

        valid = verify_totp_code(seed, code, valid_window=1)
        return {"valid": valid}

    except Exception as e:
        print("🚨 ERROR in /verify-2fa:", str(e))  # 🧪 This will show in your terminal
        return JSONResponse(status_code=500, content={"error": "Internal server error"})

