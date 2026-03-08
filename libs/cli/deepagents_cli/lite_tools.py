"""Tool filtering utilities for lite mode.

Provides functions to filter tools based on lite mode configuration,
enabling reduced context usage for small language models.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from deepagents_cli.model_config import LiteConfig

# Tool categories for convenient filtering
TOOL_CATEGORIES = {
    "filesystem": ["list_files", "read_file", "write_file", "edit_file", "glob", "grep"],
    "shell": ["execute"],
    "web": ["web_search", "fetch_url", "http_request"],
    "mcp": [],  # Handled separately in main.py
    "advanced": ["task", "compact_conversation"],
}
"""Mapping of tool categories to their constituent tool names.

Categories allow users to enable/disable groups of related tools:
- filesystem: File operations (read, write, edit, list, glob, grep)
- shell: Command execution (execute)
- web: Network operations (web_search, fetch_url, http_request)
- mcp: Model Context Protocol tools (all MCP servers)
- advanced: Complex features (task/subagents, compact_conversation)
"""


def _expand_tool_list(tools: list[str]) -> list[str]:
    """Expand category names into individual tool names.

    Args:
        tools: List that may contain tool names and/or category names.

    Returns:
        Expanded list with all category names replaced by their tool names.

    Examples:
        >>> _expand_tool_list(["read_file", "web"])
        ['read_file', 'web_search', 'fetch_url', 'http_request']
        >>> _expand_tool_list(["all"])
        ['list_files', 'read_file', ..., 'mcp', 'task', 'compact_conversation']
    """
    expanded = []
    for item in tools:
        # Special case: "all" expands to all categories AND special tools
        if item == "all":
            for category_tools in TOOL_CATEGORIES.values():
                expanded.extend(category_tools)
            # Add special tools that don't have tools in their category
            expanded.append("mcp")  # MCP is handled specially
        elif item in TOOL_CATEGORIES:
            # It's a category - expand it
            if item == "mcp":
                # MCP category is empty, so add the literal "mcp" tool name
                expanded.append("mcp")
            else:
                expanded.extend(TOOL_CATEGORIES[item])
        else:
            # It's a tool name
            expanded.append(item)
    return expanded


def should_disable_tool(tool_name: str, lite_config: LiteConfig | None) -> bool:
    """Check if a tool should be disabled based on lite configuration.

    Args:
        tool_name: Name of the tool to check (e.g., "web_search", "execute").
        lite_config: Lite mode configuration, or None if lite mode disabled.

    Returns:
        True if the tool should be disabled, False otherwise.

    Examples:
        >>> config = {"enabled": True, "disabled_tools": ["web_search"]}
        >>> should_disable_tool("web_search", config)
        True
        >>> should_disable_tool("read_file", config)
        False
    """
    # If lite mode not enabled, don't disable anything
    if not lite_config or not lite_config.get("enabled"):
        return False

    disabled_tools = lite_config.get("disabled_tools")
    enabled_tools = lite_config.get("enabled_tools")

    # Whitelist mode (enabled_tools specified)
    if enabled_tools:
        expanded_enabled = _expand_tool_list(enabled_tools)
        # Tool is disabled if it's NOT in the enabled list
        return tool_name not in expanded_enabled

    # Blacklist mode (disabled_tools specified)
    if disabled_tools:
        expanded_disabled = _expand_tool_list(disabled_tools)
        # Tool is disabled if it's in the disabled list
        return tool_name in expanded_disabled

    # No filtering specified - don't disable anything
    return False


def get_enabled_backend_type(lite_config: LiteConfig | None) -> str:
    """Determine which backend type should be used based on lite config.

    The CLI can use either LocalShellBackend (with execute tool) or
    FilesystemBackend (without execute). This function determines which
    should be used based on whether the execute tool is disabled.

    Args:
        lite_config: Lite mode configuration, or None if lite mode disabled.

    Returns:
        "shell" if LocalShellBackend should be used (execute enabled),
        "filesystem" if FilesystemBackend should be used (execute disabled).

    Examples:
        >>> config = {"enabled": True, "disabled_tools": ["shell"]}
        >>> get_enabled_backend_type(config)
        'filesystem'
        >>> config = {"enabled": True, "disabled_tools": ["web"]}
        >>> get_enabled_backend_type(config)
        'shell'
    """
    # If lite mode not enabled, use shell backend by default
    if not lite_config or not lite_config.get("enabled"):
        return "shell"

    # Check if execute tool is disabled
    if should_disable_tool("execute", lite_config):
        return "filesystem"

    return "shell"
