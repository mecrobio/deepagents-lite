"""Lite mode profile management for small language models.

Consolidates "lite mode" logic, providing tailored profiles and toolsets
for IBM Granite 4 Hybrid models (350M, 1B, 3B).
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import TYPE_CHECKING, Any, TypedDict

if TYPE_CHECKING:
    from .model_config import LiteConfig

logger = logging.getLogger(__name__)


class LiteProfile(TypedDict):
    """Configuration for a specific lite model profile."""

    system_prompt_name: str
    enabled_tools: list[str]


# Default profiles for Granite 4 models
GRANITE_PROFILES: dict[str, LiteProfile] = {
    "350m": {
        "system_prompt_name": "lite_prompt_granite4_350m.md",
        "enabled_tools": ["filesystem"],  # Basic file ops only
    },
    "1b": {
        "system_prompt_name": "lite_prompt_granite4_1b.md",
        "enabled_tools": ["filesystem", "search", "shell"],  # + search & execution
    },
    "3b": {
        "system_prompt_name": "lite_prompt_granite4_3b.md",
        "enabled_tools": ["filesystem", "search", "shell"],  # Full dev capability
    },
}


def detect_lite_profile(model_name: str) -> LiteProfile | None:
    """Detect the best lite profile for a given model name.

    Args:
        model_name: The full model identifier (e.g., 'openai:granite4:350m-h').

    Returns:
        The matched `LiteProfile`, or `None` if no match found.
    """
    model_name_lower = model_name.lower()

    # Look for Granite 4 identifiers
    if "granite" in model_name_lower or "ibm" in model_name_lower:
        if "350m" in model_name_lower:
            return GRANITE_PROFILES["350m"]
        if "1b" in model_name_lower:
            return GRANITE_PROFILES["1b"]
        if "3b" in model_name_lower or "8b" in model_name_lower or "7b" in model_name_lower:
            return GRANITE_PROFILES["3b"]

    return None


def get_lite_config(model_name: str, user_lite_config: LiteConfig | None) -> LiteConfig | None:
    """Resolve the final lite configuration by merging user settings with defaults.

    If `lite.enabled` is True but specific fields (like `system_prompt_path` or
    `enabled_tools`/`disabled_tools`) are missing, it attempts to fill them
    with defaults based on the model profile.

    Args:
        model_name: The model identifier to use for auto-detection.
        user_lite_config: The lite configuration from `config.toml`.

    Returns:
        Merged `LiteConfig`, or `None` if lite mode is not enabled.
    """
    if not user_lite_config or not user_lite_config.get("enabled"):
        return None

    # Start with a copy of user config
    config: LiteConfig = user_lite_config.copy()

    # Attempt to detect profile for defaults
    profile = detect_lite_profile(model_name)

    if profile:
        # 1. System Prompt Path (if not specified)
        if not config.get("system_prompt_path"):
            prompt_path = Path(__file__).parent / profile["system_prompt_name"]
            if prompt_path.exists():
                config["system_prompt_path"] = str(prompt_path)
                logger.debug(f"Auto-selected lite prompt: {profile['system_prompt_name']}")

        # 2. Tools (if neither enabled_tools nor disabled_tools is specified)
        if not config.get("enabled_tools") and not config.get("disabled_tools"):
            config["enabled_tools"] = profile["enabled_tools"]
            logger.debug(f"Auto-selected lite tools for {model_name}: {profile['enabled_tools']}")

    return config
