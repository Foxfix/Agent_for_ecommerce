"""Chat with the store agent in the terminal: python chat.py"""
import config
from core.agent import build_agent, store_tools
from safety.guard import check
from safety.log import log


def main():
    print(f"Harbor Goods support · model {config.MODEL_ID} · store: {config.STORE}")
    print("Type your message. Type quit to leave.\n")
    with store_tools() as mcp:
        agent = build_agent(mcp, callback_handler=None)
        while True:
            text = input("You: ").strip()
            if text.lower() in ("quit", "exit"):
                break
            if not text:
                continue
            log("customer", text=text)
            blocked = check(text, "INPUT")
            if blocked:
                print(f"Agent: {blocked}\n")
                log("guardrail_blocked", side="input")
                continue
            try:
                answer = str(agent(text)).strip()
            except Exception as e:  # e.g. not logged in to AWS, or no access to the model yet
                print(f"Agent error: {e}\n")
                continue
            answer = check(answer, "OUTPUT") or answer
            log("agent", text=answer)
            print(f"Agent: {answer}\n")


if __name__ == "__main__":
    main()
