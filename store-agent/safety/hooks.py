"""Writes every tool call the agent makes into the log, with its inputs and result."""
from strands.hooks import AfterToolCallEvent, BeforeToolCallEvent, HookProvider, HookRegistry

from safety.log import log


class AuditHooks(HookProvider):
    def register_hooks(self, registry: HookRegistry, **kwargs) -> None:
        registry.add_callback(BeforeToolCallEvent, self.before)
        registry.add_callback(AfterToolCallEvent, self.after)

    def before(self, event: BeforeToolCallEvent) -> None:
        log("agent_calls_tool", tool=event.tool_use["name"], input=event.tool_use["input"])

    def after(self, event: AfterToolCallEvent) -> None:
        log("tool_result", tool=event.tool_use["name"], status=event.result.get("status"))
