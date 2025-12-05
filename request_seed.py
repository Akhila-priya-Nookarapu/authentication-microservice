import requests
import json

API_URL = "https://eajeyq4r3zjloqa4rpovy2nthda0vtjaf.lambda-url.ap-south-1.on.aws/"
STUDENT_ID = "23P31A05N6"
GITHUB_REPO_URL = "https://github.com/Akhila-priya-Nookarapu/authentication-microservice"
PUBLIC_KEY_FILE = "data/student_public.pem"

def request_seed(student_id, github_repo_url):
    with open(PUBLIC_KEY_FILE, "r") as f:
        public_key = f.read().strip().replace("\r", "").replace("\n", "\\n")

    payload = {
        "student_id": student_id,
        "github_repo_url": github_repo_url,
        "public_key": public_key,
    }

    print("\n===== PAYLOAD SENT TO API =====")
    print(payload)
    print("================================\n")

    response = requests.post(API_URL, json=payload)

    if response.status_code != 200:
        print("❌ API Error:", response.status_code, response.text)
        return

    data = response.json()
    encrypted_seed = data.get("encrypted_seed")

    if not encrypted_seed:
        print("❌ No encrypted seed received!")
        print("Response:", data)
        return

    with open("encrypted_seed.txt", "w") as f:
        f.write(encrypted_seed)

    print("✅ Encrypted seed saved to encrypted_seed.txt!")

if __name__ == "__main__":
    request_seed(STUDENT_ID, GITHUB_REPO_URL)
