"""Deletes the guardrail at the end of the course: python -m safety.delete_guardrail"""
import boto3

import config

bedrock = boto3.client("bedrock", region_name=config.REGION)
for g in bedrock.list_guardrails()["guardrails"]:
    if g["name"] == "store-agent-guardrail":
        bedrock.delete_guardrail(guardrailIdentifier=g["id"])
        print("Deleted", g["name"])
