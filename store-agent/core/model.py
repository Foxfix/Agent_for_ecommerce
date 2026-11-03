"""Claude on Amazon Bedrock.

Bedrock serves Claude two ways, and the model ID tells us which one:
- New models (Claude Sonnet 5.5, Sonnet 5...) have short IDs like "anthropic.claude-sonnet-5-5".
  They run on the Mantle Messages API, so Strands' AnthropicModel gets a Bedrock Mantle client.
- Older models (Claude Sonnet 4.5 and earlier) have IDs with a version at the end, like
  "us.anthropic.claude-sonnet-4-5-20250929-v1:0". They run on the Converse API: BedrockModel.
Both sign requests with your AWS login. The rest of the code doesn't care which one we pick.
"""
import anthropic
from strands.models.anthropic import AnthropicModel
from strands.models.bedrock import BedrockModel

import config


def uses_mantle(model_id: str) -> bool:
    return ":" not in model_id  # old-style IDs end with a version like "-v1:0"


def make_model(**client_kwargs):
    if uses_mantle(config.MODEL_ID):
        model = AnthropicModel(model_id=config.MODEL_ID, max_tokens=config.MAX_TOKENS)
        model.client = anthropic.AsyncAnthropicBedrockMantle(aws_region=config.REGION, **client_kwargs)
        return model
    return BedrockModel(model_id=config.MODEL_ID, region_name=config.REGION, max_tokens=config.MAX_TOKENS)
