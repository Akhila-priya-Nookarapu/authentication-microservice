import json
import requests

def request_seed(student_id: str, github_repo_url: str, api_url: str):

    # 1. Read student public key
    with open("student_public.pem", "r") as f:
        public_key = f.read()

    # 2. Prepare JSON request body
    payload = {
        "student_id": student_id,
        "github_repo_url": github_repo_url,
        "public_key": public_key
    }

    # 3. Send POST request
    headers = {"Content-Type": "application/json"}
    response = requests.post(api_url, data=json.dumps(payload), headers=headers)

    print("API Response:", response.text)  # DEBUG LINE

    # 4. Parse JSON response
    data = response.json()
    encrypted_seed = data.get("encrypted_seed")

    # 5. Save encrypted seed to file
    with open("encrypted_seed.txt", "w") as f:
        f.write(encrypted_seed)

    print("Saved encrypted_seed.txt successfully!")


# ---- CHANGE ONLY THESE THREE ----
student_id = "Akhila Priya Nookarapu"   # MUST match Partnr student_id
github_repo_url = "https://github.com/Akhila-priya-Nookarapu/authentication-microservice"
api_url = "https://eajeyq4r3zjjoq4rpovy2nthda0vtjqf.lambda-url.ap-south-1.on.aws"

request_seed(student_id, github_repo_url, api_url)
