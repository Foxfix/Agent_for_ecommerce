# Store Agent

A customer support agent you can plug into any online store.
Claude on Amazon Bedrock thinks, Strands Agents runs the loop, and our own MCP server gives it four store tools.

```
chat.py / api/app.py / deploy/main.py      how customers reach the agent
core/                                      the agent: model, prompt, tools
mcp_server/server.py                       our MCP server: 4 store tools
connectors/                                one contract, two stores: demo, shopify
knowledge/                                 store policies in Chroma
safety/                                    guardrail, approval queue, log
evals/                                     test conversations
tests/                                     contract and offline tests (no AWS needed)
deploy/                                    put it online with AgentCore
```

## Start
Nothing is installed globally: Python packages go into `.venv` inside this folder, and the AgentCore CLI is installed into this folder (`npm install --save-dev --save-exact @aws/agentcore@1.0.0`) and run with `npx agentcore`.
```
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
pytest                     # everything offline, no AWS
python check_model.py      # one question to Claude
python chat.py             # chat with the agent
```


## Commands by lesson
All commands, step by step, including the model check and the full clean-up: **PLAYBOOK.md**.

| Lesson | Commands |
|---|---|
| Demo store and tools | `pytest tests/test_contract.py -v` |
| The agent | `python check_model.py`, `python chat.py` |
| Our MCP server | `python -m mcp_server.try_it` |
| Knowledge | `python -m knowledge.build`, `python -m knowledge.search can I return worn shoes` |
| Safety | `python -m safety.create_guardrail`, `python -m safety.approve` |
| Shopify | `STORE=shopify python chat.py` |
| Test everything | `pytest`, `python -m evals.run` |
| Online | `uvicorn api.app:app`, `npx agentcore create --name StoreAgentLive --skip-git`, `npx agentcore add runtime --name StoreAgentLive --language python` (inside `StoreAgentLive/`), `python deploy/prepare.py StoreAgentLive`, `npx agentcore deploy` |

## Clean up
`npx agentcore remove all --yes` + `npx agentcore deploy --yes` inside `StoreAgentLive/`, then `python -m safety.delete_guardrail`.
