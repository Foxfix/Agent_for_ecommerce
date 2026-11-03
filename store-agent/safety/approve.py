"""The store owner's side: python -m safety.approve"""
import sys

from safety.approvals import decide, pending

if len(sys.argv) == 3 and sys.argv[1] in ("yes", "no"):
    item = decide(sys.argv[2], sys.argv[1] == "yes")
    print(item or "No such ticket")
else:
    items = pending()
    if not items:
        print("No returns waiting.")
    for i in items:
        print(f'{i["ticket"]}  order {i["order_id"]}  customer {i["customer_id"]}  reason: {i["reason"]}')
    print("\nTo decide: python -m safety.approve yes R-XXXXXX   (or no)")
