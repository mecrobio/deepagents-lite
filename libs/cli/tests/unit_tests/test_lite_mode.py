"""Tests for lite mode configuration and tool filtering."""

from pathlib import Path

import pytest

from deepagents_cli.lite_tools import (
    TOOL_CATEGORIES,
    _expand_tool_list,
    get_enabled_backend_type,
    should_disable_tool,
)
from deepagents_cli.model_config import LiteConfig, ModelConfig


class TestToolExpansion:
    """Test tool category expansion."""

    def test_expand_single_tool(self):
        """Test that single tool names pass through unchanged."""
        result = _expand_tool_list(["read_file"])
        assert result == ["read_file"]

    def test_expand_category(self):
        """Test that categories expand to their tools."""
        result = _expand_tool_list(["filesystem"])
        assert result == TOOL_CATEGORIES["filesystem"]

    def test_expand_mixed_list(self):
        """Test mixed tool names and categories."""
        result = _expand_tool_list(["read_file", "shell", "http_request"])
        assert "read_file" in result
        assert "execute" in result  # from shell category
        assert "http_request" in result

    def test_expand_multiple_categories(self):
        """Test multiple categories."""
        result = _expand_tool_list(["filesystem", "web"])
        assert all(tool in result for tool in TOOL_CATEGORIES["filesystem"])
        assert all(tool in result for tool in TOOL_CATEGORIES["web"])


class TestShouldDisableTool:
    """Test tool filtering logic."""

    def test_disabled_when_lite_not_enabled(self):
        """When lite mode is disabled, no tools should be disabled."""
        config: LiteConfig = {"enabled": False, "disabled_tools": ["web_search"]}
        assert not should_disable_tool("web_search", config)
        assert not should_disable_tool("read_file", config)

    def test_disabled_when_config_is_none(self):
        """When lite_config is None, no tools should be disabled."""
        assert not should_disable_tool("web_search", None)
        assert not should_disable_tool("read_file", None)

    def test_blacklist_mode(self):
        """Test blacklist mode (disabled_tools)."""
        config: LiteConfig = {
            "enabled": True,
            "disabled_tools": ["web_search", "fetch_url"],
        }
        assert should_disable_tool("web_search", config)
        assert should_disable_tool("fetch_url", config)
        assert not should_disable_tool("read_file", config)

    def test_whitelist_mode(self):
        """Test whitelist mode (enabled_tools)."""
        config: LiteConfig = {
            "enabled": True,
            "enabled_tools": ["read_file", "write_file"],
        }
        assert not should_disable_tool("read_file", config)
        assert not should_disable_tool("write_file", config)
        assert should_disable_tool("web_search", config)
        assert should_disable_tool("execute", config)

    def test_category_in_blacklist(self):
        """Test category expansion in blacklist."""
        config: LiteConfig = {"enabled": True, "disabled_tools": ["web"]}
        assert should_disable_tool("web_search", config)
        assert should_disable_tool("fetch_url", config)
        assert should_disable_tool("http_request", config)
        assert not should_disable_tool("read_file", config)

    def test_category_in_whitelist(self):
        """Test category expansion in whitelist."""
        config: LiteConfig = {"enabled": True, "enabled_tools": ["filesystem"]}
        assert not should_disable_tool("read_file", config)
        assert not should_disable_tool("write_file", config)
        assert not should_disable_tool("grep", config)
        assert should_disable_tool("execute", config)
        assert should_disable_tool("web_search", config)

    def test_no_filtering_when_neither_specified(self):
        """When neither list is specified, don't disable anything."""
        config: LiteConfig = {"enabled": True}
        assert not should_disable_tool("web_search", config)
        assert not should_disable_tool("read_file", config)


class TestGetEnabledBackendType:
    """Test backend type selection."""

    def test_returns_shell_when_lite_disabled(self):
        """When lite mode is disabled, use shell backend."""
        config: LiteConfig = {"enabled": False}
        assert get_enabled_backend_type(config) == "shell"

    def test_returns_shell_when_config_none(self):
        """When config is None, use shell backend."""
        assert get_enabled_backend_type(None) == "shell"

    def test_returns_filesystem_when_execute_disabled(self):
        """When execute is disabled, use filesystem backend."""
        config: LiteConfig = {"enabled": True, "disabled_tools": ["execute"]}
        assert get_enabled_backend_type(config) == "filesystem"

    def test_returns_filesystem_when_shell_category_disabled(self):
        """When shell category is disabled, use filesystem backend."""
        config: LiteConfig = {"enabled": True, "disabled_tools": ["shell"]}
        assert get_enabled_backend_type(config) == "filesystem"

    def test_returns_shell_when_execute_not_disabled(self):
        """When execute is not disabled, use shell backend."""
        config: LiteConfig = {"enabled": True, "disabled_tools": ["web"]}
        assert get_enabled_backend_type(config) == "shell"

    def test_returns_filesystem_with_whitelist_excluding_execute(self):
        """When whitelist doesn't include execute, use filesystem backend."""
        config: LiteConfig = {"enabled": True, "enabled_tools": ["read_file"]}
        assert get_enabled_backend_type(config) == "filesystem"

    def test_returns_shell_with_whitelist_including_execute(self):
        """When whitelist includes execute, use shell backend."""
        config: LiteConfig = {
            "enabled": True,
            "enabled_tools": ["read_file", "execute"],
        }
        assert get_enabled_backend_type(config) == "shell"


class TestLiteConfigLoading:
    """Test loading lite config from TOML."""

    def test_load_lite_config_disabled(self, tmp_path: Path):
        """Test loading config with lite mode disabled."""
        config_path = tmp_path / "config.toml"
        config_path.write_text("""
[lite]
enabled = false
""")
        config = ModelConfig.load(config_path)
        assert config.lite is not None
        assert config.lite.get("enabled") is False

    def test_load_lite_config_with_prompt_path(self, tmp_path: Path):
        """Test loading config with custom prompt path."""
        config_path = tmp_path / "config.toml"
        config_path.write_text("""
[lite]
enabled = true
system_prompt_path = "~/.deepagents/custom_prompt.md"
""")
        config = ModelConfig.load(config_path)
        assert config.lite is not None
        assert config.lite.get("enabled") is True
        assert config.lite.get("system_prompt_path") == "~/.deepagents/custom_prompt.md"

    def test_load_lite_config_with_disabled_tools(self, tmp_path: Path):
        """Test loading config with disabled tools."""
        config_path = tmp_path / "config.toml"
        config_path.write_text("""
[lite]
enabled = true
disabled_tools = ["web_search", "mcp"]
""")
        config = ModelConfig.load(config_path)
        assert config.lite is not None
        assert config.lite.get("disabled_tools") == ["web_search", "mcp"]

    def test_load_lite_config_with_enabled_tools(self, tmp_path: Path):
        """Test loading config with enabled tools (whitelist)."""
        config_path = tmp_path / "config.toml"
        config_path.write_text("""
[lite]
enabled = true
enabled_tools = ["read_file", "write_file"]
""")
        config = ModelConfig.load(config_path)
        assert config.lite is not None
        assert config.lite.get("enabled_tools") == ["read_file", "write_file"]

    def test_mutual_exclusivity_warning(self, tmp_path: Path, caplog):
        """Test that using both lists triggers a warning."""
        config_path = tmp_path / "config.toml"
        config_path.write_text("""
[lite]
enabled = true
disabled_tools = ["web_search"]
enabled_tools = ["read_file"]
""")
        config = ModelConfig.load(config_path)
        # Should have loaded but logged a warning
        assert config.lite is not None
        # Check that warning was logged
        assert any(
            "Cannot use both 'disabled_tools' and 'enabled_tools'" in record.message
            for record in caplog.records
        )

    def test_load_config_without_lite_section(self, tmp_path: Path):
        """Test loading config without lite section."""
        config_path = tmp_path / "config.toml"
        config_path.write_text("""
[models]
default = "anthropic:claude-sonnet-4-5"
""")
        config = ModelConfig.load(config_path)
        # lite should be None when section is missing
        assert config.lite is None

    def test_load_empty_lite_section(self, tmp_path: Path):
        """Test loading config with empty lite section."""
        config_path = tmp_path / "config.toml"
        config_path.write_text("""
[lite]
""")
        config = ModelConfig.load(config_path)
        # Should have created a lite config with defaults
        assert config.lite is not None
        assert config.lite.get("enabled", False) is False


class TestLiteConfigValidation:
    """Test validation of lite configuration."""

    def test_validate_accepts_valid_blacklist(self, tmp_path: Path):
        """Test that valid blacklist config passes validation."""
        config_path = tmp_path / "config.toml"
        config_path.write_text("""
[lite]
enabled = true
disabled_tools = ["web_search"]
""")
        # Should not raise
        config = ModelConfig.load(config_path)
        assert config.lite is not None

    def test_validate_accepts_valid_whitelist(self, tmp_path: Path):
        """Test that valid whitelist config passes validation."""
        config_path = tmp_path / "config.toml"
        config_path.write_text("""
[lite]
enabled = true
enabled_tools = ["read_file", "write_file"]
""")
        # Should not raise
        config = ModelConfig.load(config_path)
        assert config.lite is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
