"""One short question to Claude on Amazon Bedrock. Run it to check your access: python check_model.py"""
from strands import Agent

import config
from core.model import make_model

agent = Agent(model=make_model(), callback_handler=None)
reply = agent("Say hello to a new online store owner in one sentence.")
usage = reply.metrics.accumulated_usage

print(f"Model: {config.MODEL_ID}")
print(f"Answer: {str(reply).strip()}")
print(f"Tokens: {usage['inputTokens']} in, {usage['outputTokens']} out")
