import os
from dotenv import load_dotenv

# Load environment variables from .env if present
load_dotenv()

M365_TENANT_ID = os.getenv("M365_TENANT_ID", "")
M365_CLIENT_ID = os.getenv("M365_CLIENT_ID", "")
M365_CLIENT_SECRET = os.getenv("M365_CLIENT_SECRET", "")
M365_MAILBOX = os.getenv("M365_MAILBOX", "signals@nexsentia.fr")
