"""Creates the store's guardrail in your AWS account once: python -m safety.create_guardrail"""
import boto3

import config

bedrock = boto3.client("bedrock", region_name=config.REGION)

g = bedrock.create_guardrail(
    name="store-agent-guardrail",
    description="Safety rules for the store support agent",
    contentPolicyConfig={"filtersConfig": [
        {"type": "PROMPT_ATTACK", "inputStrength": "HIGH", "outputStrength": "NONE"},
        {"type": "HATE", "inputStrength": "HIGH", "outputStrength": "HIGH"},
        {"type": "INSULTS", "inputStrength": "MEDIUM", "outputStrength": "HIGH"},
        {"type": "VIOLENCE", "inputStrength": "HIGH", "outputStrength": "HIGH"},
        {"type": "SEXUAL", "inputStrength": "HIGH", "outputStrength": "HIGH"},
        {"type": "MISCONDUCT", "inputStrength": "HIGH", "outputStrength": "HIGH"},
    ]},
    sensitiveInformationPolicyConfig={"piiEntitiesConfig": [
        {"type": "CREDIT_DEBIT_CARD_NUMBER", "action": "BLOCK"},
        {"type": "PASSWORD", "action": "BLOCK"},
    ]},
    topicPolicyConfig={"topicsConfig": [{
        "name": "Financial advice",
        "definition": "Advice about investing money, stocks, crypto or loans.",
        "examples": ["Should I buy Tesla stock?", "Which crypto is best right now?"],
        "type": "DENY",
    }]},
    blockedInputMessaging="Sorry, I can only help with questions about our store and your orders.",
    blockedOutputsMessaging="Sorry, I can't share that. Can I help with something about your order?",
)
v = bedrock.create_guardrail_version(guardrailIdentifier=g["guardrailId"])
print("Guardrail created. Put these two lines into your .env file:")
print(f"GUARDRAIL_ID={g['guardrailId']}")
print(f"GUARDRAIL_VERSION={v['version']}")
