"""MCP server exposing The 11/11 Portal to any MCP client (Claude Desktop, Claude Code, IDEs).

Run:  PORTAL_DATA=path/to/backup.json portal-mcp     (stdio transport)"""
from __future__ import annotations
import json

from mcp.server.mcpserver import MCPServer
from mcp.types import ToolAnnotations

from .store import AREAS
from .tools import Toolbox

box = Toolbox()
server = MCPServer(
    name="the-11-11-portal",
    instructions=("Personal life and training tracker. Use search_journal to ground answers in the user's own entries and cite ids. "
                  "Write tools return a preview first; only call them with confirm=true after the user explicitly approves."),
)
RO = ToolAnnotations(readOnlyHint=True, destructiveHint=False, idempotentHint=True, openWorldHint=False)
RW = ToolAnnotations(readOnlyHint=False, destructiveHint=False, idempotentHint=True, openWorldHint=False)


@server.tool(annotations=RO)
def get_plan(day: str) -> dict:
    """Planned run and workout for a date (YYYY-MM-DD)."""
    return box.get_plan(day)


@server.tool(annotations=RO)
def search_journal(query: str, k: int = 5) -> list[dict]:
    """Search the user's runs, notes, life-area plans and life vision. Returns ids to cite."""
    return box.search_journal(query, k)


@server.tool(annotations=RO)
def week_summary(day: str) -> dict:
    """Miles, sessions and life-area check-ins for the week containing the date."""
    return box.week_summary(day)


@server.tool(annotations=RO)
def life_area_status() -> list[dict]:
    """Rating and plan completeness for each of the 12 life areas."""
    return box.life_area_status()


@server.tool(annotations=RW)
def log_run(day: str, miles: float, minutes: float, mode: str = "run", confirm: bool = False) -> dict:
    """Log a run or ride. Without confirm=true this only previews the change."""
    return box.log_run(day, miles, minutes, mode, confirm)


@server.tool(annotations=RW)
def check_in_area(day: str, area: str, confirm: bool = False) -> dict:
    """Mark a life area as worked on for a date. Preview unless confirm=true."""
    return box.check_in_area(day, area, confirm)


@server.resource("portal://areas", name="life-areas", mime_type="application/json")
def areas_resource() -> str:
    """The 12 life areas and their ids."""
    return json.dumps([{"id": a, "name": n} for a, n in AREAS])


def main() -> None:
    server.run("stdio")


if __name__ == "__main__":
    main()
