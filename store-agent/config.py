"""All settings in one place. Change them here or with environment variables."""
import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / ".env")

ROOT = Path(__file__).parent

# AWS region where we call Claude on Amazon Bedrock.
REGION = os.getenv("AWS_REGION", "us-east-1")

# Claude Sonnet 5.5 runs on Bedrock through the "Mantle" Messages API.
# If your account has no access to it yet, set MODEL_ID=anthropic.claude-sonnet-5
MODEL_ID = os.getenv("MODEL_ID", "anthropic.claude-sonnet-5-5")
MAX_TOKENS = int(os.getenv("MAX_TOKENS", "2000"))

# Which store the agent talks to: demo or shopify.
STORE = os.getenv("STORE", "demo")

# Who is chatting. In a real shop this comes from the login session, never from the chat text.
CUSTOMER_ID = os.getenv("CUSTOMER_ID", "c-7731")

DATA_FILE = ROOT / "data" / "store.json"
POLICY_DIR = ROOT / "data" / "policies"
CHROMA_DIR = ROOT / ".chroma"
APPROVALS_FILE = Path(os.getenv("APPROVALS_FILE", ROOT / "data" / "approvals.json"))
LOG_FILE = Path(os.getenv("LOG_FILE", ROOT / "logs" / "agent.log"))
# "chroma" = the Chroma index from the knowledge lesson; "keyword" = a light search for the cloud.
KNOWLEDGE = os.getenv("KNOWLEDGE", "chroma")

# Shopify (lesson: plug in Shopify)
SHOPIFY_STORE = os.getenv("SHOPIFY_STORE", "")                  # e.g. my-test-shop.myshopify.com
SHOPIFY_CLIENT_ID = os.getenv("SHOPIFY_CLIENT_ID", "")          # Dev Dashboard app > Settings
SHOPIFY_CLIENT_SECRET = os.getenv("SHOPIFY_CLIENT_SECRET", "")  # Dev Dashboard app > Settings
SHOPIFY_API_VERSION = os.getenv("SHOPIFY_API_VERSION", "2026-10")
SHOPIFY_AGENT_PROFILE = os.getenv(
    "SHOPIFY_AGENT_PROFILE",
    "https://shopify.dev/ucp/agent-profiles/examples/2026-08-25/valid-with-capabilities.json",
)

# Bedrock Guardrails (lesson: safety)
GUARDRAIL_ID = os.getenv("GUARDRAIL_ID", "")
GUARDRAIL_VERSION = os.getenv("GUARDRAIL_VERSION", "DRAFT")
