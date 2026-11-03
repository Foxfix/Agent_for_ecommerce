"""Amazon Bedrock Guardrails, checked on what the customer types and on what the agent answers.

We call the ApplyGuardrail API ourselves, so it works with any model.
If GUARDRAIL_ID is empty (before the safety lesson), nothing is checked.
"""
import boto3

import config

_client = None


def check(text: str, source: str) -> str | None:
    """Returns a safe replacement message if the guardrail blocks the text, else None.
    source is "INPUT" for the customer's message and "OUTPUT" for the agent's answer."""
    global _client
    if not config.GUARDRAIL_ID or not text.strip():
        return None
    _client = _client or boto3.client("bedrock-runtime", region_name=config.REGION)
    result = _client.apply_guardrail(
        guardrailIdentifier=config.GUARDRAIL_ID,
        guardrailVersion=config.GUARDRAIL_VERSION,
        source=source,
        content=[{"text": {"text": text}}],
    )
    if result["action"] == "GUARDRAIL_INTERVENED":
        outputs = result.get("outputs") or [{"text": "Sorry, I can't help with that."}]
        return outputs[0]["text"]
    return None
