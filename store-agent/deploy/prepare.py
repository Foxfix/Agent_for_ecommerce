"""Copies our agent into the AgentCore project made by `agentcore create`.

    python deploy/prepare.py StoreAgentLive
"""
import json
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import config  # noqa: E402

name = sys.argv[1] if len(sys.argv) > 1 else "StoreAgentLive"
project = config.ROOT / name
app_dir = project / "app" / name
if not app_dir.exists():
    sys.exit(f"Run `agentcore create` first: {app_dir} not found")

# 1. Our code replaces the example agent.
for folder in ["core", "connectors", "mcp_server", "knowledge", "safety", "data"]:
    shutil.rmtree(app_dir / folder, ignore_errors=True)
    shutil.copytree(config.ROOT / folder, app_dir / folder,
                    ignore=shutil.ignore_patterns("__pycache__", "approvals.json"))
for folder in ["model", "mcp_client", "skills"]:
    shutil.rmtree(app_dir / folder, ignore_errors=True)
shutil.copy(config.ROOT / "config.py", app_dir / "config.py")
shutil.copy(config.ROOT / "deploy" / "main.py", app_dir / "main.py")

# 2. The libraries the cloud needs.
pyproject = app_dir / "pyproject.toml"
if not pyproject.exists():  # `agentcore add runtime` (CLI 1.x) leaves the folder empty
    pyproject.write_text(
        '[build-system]\nrequires = ["hatchling ~= 1.27.0"]\nbuild-backend = "hatchling.build"\n\n'
        f'[project]\nname = "{name.lower()}"\nversion = "1.0.0"\nrequires-python = ">=3.12"\n'
        'dependencies = [\n]\n\n[tool.hatch.build.targets.wheel]\npackages = ["."]\n')
text = pyproject.read_text()
start = text.index("dependencies = [")
end = text.index("\n]", start) + 2  # the list ends with "]" on its own line
deps = [
    "bedrock-agentcore >= 1.18.1", "strands-agents >= 1.61.0", "mcp >= 2.1.0",
    "anthropic[bedrock] >= 1.15.0", "boto3", "botocore[crt]", "requests", "python-dotenv",
    "aws-opentelemetry-distro ~= 0.21.0",  # AgentCore CLI 1.x starts main.py through opentelemetry-instrument
]
pyproject.write_text(text[:start] + "dependencies = [\n" + "".join(f'    "{d}",\n' for d in deps) + "]" + text[end:])
(app_dir / "uv.lock").unlink(missing_ok=True)  # old lock file from the example agent

# 3. Permission to call Claude through Bedrock Mantle and to use our guardrail.
policy = {"Version": "2012-10-17", "Statement": [
    {"Effect": "Allow", "Action": "bedrock-mantle:CreateInference",
     "Resource": f"arn:aws:bedrock-mantle:{config.REGION}:*:project/default"},
    {"Effect": "Allow", "Action": "bedrock:ApplyGuardrail", "Resource": "*"},
]}
(app_dir / "store-agent-policy.json").write_text(json.dumps(policy, indent=2))

# 4. Settings for the cloud copy.
spec_file = project / "agentcore" / "agentcore.json"
spec = json.loads(spec_file.read_text())
runtime = next(r for r in spec["runtimes"] if r["name"] == name)
runtime["additionalPolicies"] = ["store-agent-policy.json"]
env = {
    "MODEL_ID": config.MODEL_ID, "STORE": "demo", "KNOWLEDGE": "keyword",
    "LOG_FILE": "/dev/stdout", "APPROVALS_FILE": "/tmp/approvals.json",  # stdout = CloudWatch logs
    "GUARDRAIL_ID": config.GUARDRAIL_ID, "GUARDRAIL_VERSION": config.GUARDRAIL_VERSION,
}
runtime["envVars"] = [{"name": k, "value": v} for k, v in env.items() if v]
spec_file.write_text(json.dumps(spec, indent=2) + "\n")

print(f"Ready. Now: cd {name} && npx agentcore deploy")
