#!/usr/bin/env python3
"""Diagnostic script to check what prompt is being used."""

from pathlib import Path

from deepagents_cli.model_config import ModelConfig

# Load configuration
config = ModelConfig.load()
lite_config = config.lite

print("=" * 80)
print("📝 System Prompt Check")
print("=" * 80)

if not lite_config or not lite_config.get("enabled"):
    print("\n❌ Lite mode is DISABLED or not configured")
    print("   Using default system prompt (large)")
    print("\n💡 The default prompt is likely causing slow responses.")
else:
    print("\n✅ Lite mode is ENABLED")

    prompt_path_str = lite_config.get("system_prompt_path")
    if prompt_path_str:
        prompt_path = Path(prompt_path_str).expanduser()
        print(f"\n📄 Configured prompt path: {prompt_path}")

        if prompt_path.exists():
            print(f"   ✅ File exists")

            # Read and analyze the prompt
            prompt_content = prompt_path.read_text()

            # Count lines, words, and approximate tokens
            lines = prompt_content.split('\n')
            words = prompt_content.split()

            # Rough token estimate (1 token ≈ 4 characters)
            approx_tokens = len(prompt_content) / 4

            print(f"\n📊 Prompt Statistics:")
            print(f"   • Lines: {len(lines)}")
            print(f"   • Words: {len(words)}")
            print(f"   • Characters: {len(prompt_content)}")
            print(f"   • Approximate tokens: {int(approx_tokens)}")

            # Show first few lines
            print(f"\n📄 First 10 lines of prompt:")
            print("   " + "-" * 76)
            for i, line in enumerate(lines[:10], 1):
                print(f"   {line[:76]}")
            print("   " + "-" * 76)

        else:
            print(f"   ❌ File NOT found!")
            print(f"\n⚠️  The CLI will fall back to default prompt (large)")
            print(f"   This explains the slow responses.")
    else:
        print("\n⚠️  No system_prompt_path configured")
        print("   Using default system prompt (large)")

print("\n" + "=" * 80)
print("🔧 Tool Configuration")
print("=" * 80)

disabled_tools = lite_config.get("disabled_tools") if lite_config else None
enabled_tools = lite_config.get("enabled_tools") if lite_config else None

if disabled_tools:
    print(f"\n🚫 Disabled tools: {disabled_tools}")
elif enabled_tools:
    print(f"\n✅ Enabled tools: {enabled_tools}")
else:
    print("\n⚠️  No tool filtering configured (all tools enabled)")

print("\n" + "=" * 80)
