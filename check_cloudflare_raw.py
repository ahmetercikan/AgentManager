import requests
import os
import json
from dotenv import load_dotenv

load_dotenv()

account_id = os.getenv("CLOUDFLARE_ACCOUNT_ID")
api_token = os.getenv("CLOUDFLARE_API_TOKEN")
model_id = os.getenv("CLOUDFLARE_MODEL_ID")

url = f"https://api.cloudflare.com/client/v4/accounts/{account_id}/ai/v1/chat/completions"
headers = {
    "Authorization": f"Bearer {api_token}",
    "Content-Type": "application/json"
}
data = {
    "model": model_id,
    "messages": [{"role": "user", "content": "Hello"}]
}

print(f"Calling Cloudflare: {url}")
response = requests.post(url, headers=headers, json=data)
print(f"Status: {response.status_code}")
try:
    print("Response JSON:")
    print(json.dumps(response.json(), indent=2))
except:
    print("Response Text:")
    print(response.text)
