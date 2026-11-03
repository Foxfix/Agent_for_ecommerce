"""Every step goes to logs/agent.log, one JSON line each."""
import json
from datetime import datetime, timezone

import config


def log(kind, **fields):
    config.LOG_FILE.parent.mkdir(exist_ok=True)
    line = {"time": datetime.now(timezone.utc).isoformat(timespec="seconds"), "kind": kind, **fields}
    with config.LOG_FILE.open("a") as f:
        f.write(json.dumps(line, default=str) + "\n")
