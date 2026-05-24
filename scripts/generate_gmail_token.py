from pathlib import Path
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.modify",
]

credentials_path = "secrets/gmail/credentials.json"
token_path = Path("secrets/gmail/token.json")

token_path.parent.mkdir(parents=True, exist_ok=True)

flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
creds = flow.run_local_server(port=0)

token_path.write_text(creds.to_json(), encoding="utf-8")

print(f"Token saved to: {token_path}")