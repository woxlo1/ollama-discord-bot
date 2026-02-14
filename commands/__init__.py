"""Commands module."""
from commands.slash_commands import setup_slash_commands
from commands.events import setup_events

__all__ = ["setup_slash_commands", "setup_events"]
