#!/usr/bin/env python3
"""Diagnostic script to verify lite mode configuration."""

from pathlib import Path

from deepagents_cli.lite_tools import should_disable_tool
from deepagents_cli.model_config import ModelConfig

# Load configuration
config = ModelConfig.load()

print("=" * 60)
print("LITE MODE DIAGNOSTIC")
print("=" * 60)

# Check if lite config exists
if config.lite is None:
    print("\n❌ Lite mode section NOT FOUND in config.toml")
    print("\nCreate ~/.deepagents/config.toml with:")
    print("""
[lite]
enabled = true
system_prompt_path = "~/.deepagents/lite_prompt_granite4_1b.md"
disabled_tools = ["web", "mcp", "advanced"]
""")
    exit(1)

print("\n✅ Lite config found!")
print(f"   Enabled: {config.lite.get('enabled')}")
print(f"   System Prompt: {config.lite.get('system_prompt_path')}")
print(f"   Disabled Tools: {config.lite.get('disabled_tools')}")
print(f"   Enabled Tools: {config.lite.get('enabled_tools')}")

# Check if enabled
if not config.lite.get("enabled"):
    print("\n⚠️  Lite mode is DISABLED")
    print("   Set 'enabled = true' in [lite] section")
    exit(0)

print("\n✅ Lite mode is ENABLED")

# Check prompt file
prompt_path = config.lite.get("system_prompt_path")
if prompt_path:
    prompt_path_expanded = Path(prompt_path).expanduser()
    if prompt_path_expanded.exists():
        print(f"\n✅ Custom prompt found: {prompt_path_expanded}")
        # Show first few lines
        lines = prompt_path_expanded.read_text().split("\n")[:5]
        print("\n   Preview:")
        for line in lines:
            print(f"   {line}")
    else:
        print(f"\n❌ Prompt file NOT FOUND: {prompt_path_expanded}")
else:
    print("\n⚠️  No custom prompt path specified")

# Test tool filtering
print("\n" + "=" * 60)
print("TOOL FILTERING TEST")
print("=" * 60)

all_tools = [
    "read_file",
    "write_file",
    "edit_file",
    "list_files",
    "glob",
    "grep",
    "execute",
    "http_request",
    "fetch_url",
    "web_search",
    "mcp",
    "task",
    "compact_conversation",
]

enabled_tools = []
disabled_tools = []

for tool in all_tools:
    if should_disable_tool(tool, config.lite):
        disabled_tools.append(tool)
    else:
        enabled_tools.append(tool)

print(f"\n✅ ENABLED tools ({len(enabled_tools)}):")
for tool in enabled_tools:
    print(f"   • {tool}")

print(f"\n❌ DISABLED tools ({len(disabled_tools)}):")
for tool in disabled_tools:
    print(f"   • {tool}")

# Summary
print("\n" + "=" * 60)
print("SUMMARY")
print("=" * 60)

if config.lite.get("enabled"):
    print("\n✅ Lite mode is ACTIVE")
    print(f"   {len(enabled_tools)}/{len(all_tools)} tools enabled")
    print(f"   {len(disabled_tools)}/{len(all_tools)} tools disabled")

    # Specific checks
    if should_disable_tool("mcp", config.lite):
        print("\n✅ MCP tools will be DISABLED (expected)")
    else:
        print("\n⚠️  MCP tools will be ENABLED (check your config)")

    if should_disable_tool("web_search", config.lite):
        print("✅ Web search will be DISABLED (expected)")
    else:
        print("⚠️  Web search will be ENABLED (check your config)")

    if should_disable_tool("task", config.lite):
        print("✅ Task (subagents) will be DISABLED (expected)")
    else:
        print("⚠️  Task (subagents) will be ENABLED (check your config)")
else:
    print("\n❌ Lite mode is DISABLED")

print("\n" + "=" * 60)
