"""Refunds wait here until a person says yes."""
import json
import uuid
from datetime import datetime, timezone

import config


def _load():
    f = config.APPROVALS_FILE
    return json.loads(f.read_text()) if f.exists() else []


def _save(items):
    config.APPROVALS_FILE.write_text(json.dumps(items, indent=2))


def add_request(store, order_id, customer_id, reason):
    item = {
        "ticket": "R-" + uuid.uuid4().hex[:6].upper(),
        "store": store, "order_id": order_id, "customer_id": customer_id,
        "reason": reason, "status": "pending approval",
        "created": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }
    items = _load()
    items.append(item)
    _save(items)
    return {"ticket": item["ticket"], "status": item["status"],
            "message": "A team member will review this return within 2 business days."}


def pending():
    return [i for i in _load() if i["status"] == "pending approval"]


def decide(ticket, approve: bool):
    items = _load()
    for i in items:
        if i["ticket"] == ticket:
            i["status"] = "approved" if approve else "rejected"
            _save(items)
            return i
    return None
