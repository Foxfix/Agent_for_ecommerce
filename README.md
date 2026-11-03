<div align="center">

# 🛒 Store Agent

### Build & Deploy an Enterprise AI Agent for E-commerce in 3 Hours

**A production-style support agent for online stores: Claude on Amazon Bedrock, Strands Agents, your own MCP server, AWS Guardrails, and one-command cloud deployment.**

<br>

[![Get the workshop](https://img.shields.io/badge/🚀_GET_THE_FULL_WORKSHOP-$25_(was_$85)-FF9900?style=for-the-badge&labelColor=232F3E)](https://codeaiflow.cloud/agents)

<br>

![Python](https://img.shields.io/badge/Python-3.12+-3776AB?style=flat-square&logo=python&logoColor=white)
![AWS Bedrock](https://img.shields.io/badge/AWS-Bedrock-FF9900?style=flat-square&logo=icloud&logoColor=white)
![MCP](https://img.shields.io/badge/MCP-Server-6E56CF?style=flat-square)
![Strands Agents](https://img.shields.io/badge/Strands-Agents-232F3E?style=flat-square)
![Shopify](https://img.shields.io/badge/Shopify-Dev_Store-7AB55C?style=flat-square&logo=shopify&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat-square&logo=fastapi&logoColor=white)
![Free Tier](https://img.shields.io/badge/AWS-Free_Tier_Ready-2EA44F?style=flat-square)

</div>

---

## 📣 Follow along

<div align="center">

<a href="https://www.youtube.com/@Code_AI_Lab"><img src="https://img.shields.io/badge/YouTube-Code_AI_Lab-FF0000?style=for-the-badge&logo=youtube&logoColor=white" alt="YouTube"></a>
&nbsp;
<a href="https://builder.aws.com/profile?tab=articles"><img src="https://img.shields.io/badge/AWS_Builder-Articles-FF9900?style=for-the-badge&logoColor=white&labelColor=232F3E" alt="AWS Builder Center"></a>
&nbsp;
<a href="https://dev.to/helga_code"><img src="https://img.shields.io/badge/DEV.to-helga__code-0A0A0A?style=for-the-badge&logo=devdotto&logoColor=white" alt="DEV Community"></a>

<sub>Video walkthroughs · AWS deep dives · Written tutorials</sub>

</div>

---

## 💡 What is this?

This repository is the **complete source code** behind the paid workshop **"Build & Deploy an Enterprise AI Agent for E-commerce in 3 Hours."**

It is not a toy demo. It's a customer support agent that **does real work** in a store: looks up live order status, checks stock, searches products, answers policy questions, and opens return requests that wait for human approval. It plugs into any shop through a single connector contract.

[![Watch Playlist](https://img.youtube.com/vi/WNfaRno07Ho/maxresdefault.jpg)](https://youtu.be/WNfaRno07Ho)

▶️ [What we will be working on](https://youtu.be/WNfaRno07Ho)



| | |
|---|---|
| 🧠 **Think** | Claude on Amazon Bedrock, with the loop run by Strands Agents |
| 🔧 **Act** | Your own MCP server exposing four store tools |
| 🔌 **Connect** | One contract, two stores: a demo store and Shopify |
| 📚 **Know** | Store policies in a Chroma knowledge base |
| 🛡️ **Protect** | AWS Guardrails, a human-approval queue, and an audit log |
| ☁️ **Ship** | Deployed to AWS with AgentCore, then torn down to $0 |

## 🗺️ Project map

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


## 🧹 Zero-risk clean-up

Pay $0 for idle resources. Inside `StoreAgentLive/`:

```bash
npx agentcore remove all --yes
npx agentcore deploy --yes
python -m safety.delete_guardrail
```

---

## 🎯 Want the full walkthrough?

The code here is the finished result. The workshop shows **how to build it, why each decision was made, and how to attack your own agent and watch the guardrails block it.**

<div align="center">

| ✅ What you get |
|---|
| 3 hours of hands-on, step-by-step video |
| Agent architecture teardown, line by line |
| Live prompt-injection defense checks |
| Deployment to AWS AgentCore, then full tear-down |
| Free Tier friendly: live testing under $0.50 |

<br>

[![Join the workshop](https://img.shields.io/badge/🚀_JOIN_THE_WORKSHOP-$25_one--time_payment-FF9900?style=for-the-badge&labelColor=232F3E)](https://codeaiflow.cloud/agents)


</div>

<br><br>

⭐ **If this repo helps you, give it a star. It helps other developers find it.**

</div>
