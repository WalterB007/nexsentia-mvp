import requests
from typing import List, Dict
from ..config import M365_TENANT_ID, M365_CLIENT_ID, M365_CLIENT_SECRET, M365_MAILBOX


class OutlookClient:
    BASE_URL = "https://graph.microsoft.com/v1.0"

    def __init__(self):
        self.tenant_id = M365_TENANT_ID
        self.client_id = M365_CLIENT_ID
        self.client_secret = M365_CLIENT_SECRET
        self.mailbox = M365_MAILBOX
        self.token = self._get_token()

    def _get_token(self) -> str:
        token_url = f"https://login.microsoftonline.com/{self.tenant_id}/oauth2/v2.0/token"
        payload = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "scope": "https://graph.microsoft.com/.default",
            "grant_type": "client_credentials",
        }
        resp = requests.post(token_url, data=payload, timeout=30)
        resp.raise_for_status()
        return resp.json()["access_token"]

    def fetch_messages(self, top: int = 50) -> List[Dict]:
        url = f"{self.BASE_URL}/users/{self.mailbox}/messages"
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/json",
        }
        params = {
            "$top": top,
            "$orderby": "receivedDateTime desc",
        }
        resp = requests.get(url, headers=headers, params=params, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        return data.get("value", [])
