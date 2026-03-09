# 🧠🤖 Deep Agents CLI

[![PyPI - Version](https://img.shields.io/pypi/v/deepagents-lite?label=%20)](https://pypi.org/project/deepagents-lite/#history)
[![PyPI - License](https://img.shields.io/pypi/l/deepagents-lite)](https://opensource.org/licenses/MIT)
[![PyPI - Downloads](https://img.shields.io/pepy/dt/deepagents-lite)](https://pypistats.org/packages/deepagents-lite)
[![Twitter](https://img.shields.io/twitter/url/https/twitter.com/langchain.svg?style=social&label=Follow%20%40LangChain)](https://x.com/langchain)

<p align="center">
  <img src="https://raw.githubusercontent.com/langchain-ai/deepagents/main/libs/cli/images/cli.png" alt="Deep Agents CLI" width="600"/>
</p>

## Quick Install

```bash
curl -LsSf https://raw.githubusercontent.com/mecrobio/deepagents-lite/lite/scripts/install.sh | bash
```

```bash
# With model provider extras (OpenAI is included by default)
DEEPAGENTS_EXTRAS="anthropic,groq" curl -LsSf https://raw.githubusercontent.com/mecrobio/deepagents-lite/lite/scripts/install.sh | bash
```

Or install directly with `uv`:

```bash
# Install with chosen model providers (OpenAI is included by default)
uv tool install 'deepagents-lite[anthropic,groq]'
```

Run the CLI:

```bash
deepagents-lite
```

## 🤔 What is this?

Using an LLM to call tools in a loop is the simplest form of an agent. This architecture, however, can yield agents that are "shallow" and fail to plan and act over longer, more complex tasks.

Applications like "Deep Research", "Manus", and "Claude Code" have gotten around this limitation by implementing a combination of four things: a **planning tool**, **sub agents**, access to a **file system**, and a **detailed prompt**.

`deepagents` is a Python package that implements these in a general purpose way so that you can easily create a Deep Agent for your application. For a full overview and quickstart of Deep Agents, the best resource is our [docs](https://docs.langchain.com/oss/python/deepagents/overview).

**Acknowledgements: This project was primarily inspired by Claude Code, and initially was largely an attempt to see what made Claude Code general purpose, and make it even more so.**

## 🪶 Lite Mode for Small Language Models

Deep Agents CLI includes "lite mode" optimized for smaller models, particularly IBM Granite 4 Hybrid models (350M-7B parameters). This feature enables efficient operation with reduced context usage and simplified tool sets.

> **Note:** This is a fork-specific feature. For fork maintenance information, see [FORK_MAINTENANCE.md](../../FORK_MAINTENANCE.md).

### Quick Start

1. **Configure** `~/.deepagents/config.toml`:
   ```toml
   [models]
   default = "openai:ibm/granite-4-350m-instruct"

   [lite]
   enabled = true
   ```
   *Deep Agents will automatically detect the best system prompt and toolset based on your model.*

2. **Set API key** (use any dummy value for local servers):
   ```bash
   export OPENAI_API_KEY="local"
   ```

3. **Run DeepAgents**:
   ```bash
   deepagents-lite
   ```

For detailed configuration and model-specific profiles, see [LITE_MODE.md](LITE_MODE.md).

### Configuration Options

#### Model and Provider Setup

**Using OpenAI-compatible endpoints (ramalama, vLLM, llama.cpp):**

```toml
[models]
default = "openai:granite4:350m-h"

[models.providers.openai]
base_url = "http://localhost:8080/v1"  # Your local server endpoint
models = ["granite4:350m-h"]           # Available models from this provider

# Optional: Model-specific parameters
# [models.providers.openai.params]
# temperature = 0.7    # Sampling temperature
# max_tokens = 4096    # Maximum response length
```

**Note on Chat Templates:** Most OpenAI-compatible servers (ramalama, vLLM, llama.cpp) automatically apply the correct chat template based on the model. 
You typically don't need to configure this manually. 
If your server requires specific template configuration, refer to its documentation.

#### System Prompt

Specify the path to your distilled prompt:
```toml
system_prompt_path = "~/.deepagents/lite_prompt_granite4_1b.md"
```

The CLI includes three example prompts optimized for IBM Granite 4 Hybrid models:
- **`lite_prompt_granite4_350m.md`** - Ultra-minimal (~800 tokens) for 350M param models
- **`lite_prompt_granite4_1b.md`** - Balanced (~1500 tokens) for 1B-2B param models
- **`lite_prompt_granite4_3b.md`** - Comprehensive (~2200 tokens) for 3B-7B param models

You can also create your own custom distilled prompt tailored to your specific model.

#### Tool Control

**Disable specific tools (blacklist):**
```toml
disabled_tools = ["web_search", "fetch_url", "mcp", "task"]
```

**Or enable only specific tools (whitelist):**
```toml
enabled_tools = ["read_file", "write_file", "edit_file", "list_files"]
```

**Use categories for convenience:**
```toml
disabled_tools = ["web", "mcp", "advanced"]  # Disables all tools in these categories
```

### Complete Tool Reference

| Tool | Category | Description | Context Cost | Default |
|------|----------|-------------|--------------|---------|
| **read_file** | filesystem | Read files with pagination support | Low | ✓ |
| **write_file** | filesystem | Create new files | Low | ✓ |
| **edit_file** | filesystem | String replacement in existing files | Low | ✓ |
| **list_files** | filesystem | List directory contents | Low | ✓ |
| **glob** | search | Find files by glob pattern | Medium | ✓ |
| **grep** | search | Search text across files | Medium | ✓ |
| **execute** | shell | Execute shell commands | High | ✓ |
| **http_request** | web | Make HTTP API requests | Medium | ✓ |
| **fetch_url** | web | Fetch and parse web pages | High | ✓ |
| **web_search** | web | Tavily web search | Very High | ✓* |
| **mcp** | mcp | Model Context Protocol tools | Varies | ✓* |
| **task** | advanced | Delegate to subagents | Very High | ✓ |
| **compact_conversation** | advanced | Compress conversation history | High | ✓ |

\* Requires API key or configuration

### Tool Categories

**filesystem** (4 tools)
- `read_file`, `write_file`, `edit_file`, `list_files`
- Essential file operations with low context overhead

**search** (2 tools)
- `glob`, `grep`
- Codebase exploration and text search

**shell** (1 tool)
- `execute`
- Command execution (can increase prompt complexity)

**web** (3 tools)
- `http_request`, `fetch_url`, `web_search`
- Network access (high context cost for results)

**mcp** (variable)
- All Model Context Protocol server tools
- Depends on configured MCP servers

**advanced** (2 tools)
- `task` (subagents), `compact_conversation`
- High complexity and context cost

### Example Configurations

#### Ultra-Minimal (350M Granite 4 Hybrid)
```toml
[models]
default = "openai:ibm/granite-4-350m-instruct"

[models.providers.openai]
base_url = "http://localhost:8080/v1"
models = ["ibm/granite-4-350m-instruct"]

[lite]
enabled = true
# Deep Agents auto-detects 350M profile: filesystem tools only.
```

#### Development Assistant (1B Granite 4 Hybrid)
```toml
[models]
default = "openai:ibm/granite-4-1b-instruct"

[models.providers.openai]
base_url = "http://localhost:8080/v1"
models = ["ibm/granite-4-1b-instruct"]

[lite]
enabled = true
# Auto-detects 1B profile: filesystem + search + shell tools.
```

#### Code Assistant (3B Granite 4 Hybrid)
```toml
[models]
default = "openai:ibm/granite-4-3b-instruct"

[models.providers.openai]
base_url = "http://localhost:8080/v1"
models = ["ibm/granite-4-3b-instruct"]

[lite]
enabled = true
# Auto-detects 3B profile: full filesystem + search + shell capabilities.
# Explicitly disable heavy tools to keep context usage low:
disabled_tools = ["web", "mcp", "advanced"]
```

#### Using ramalama
```bash
# Start ramalama server
ramalama serve --port 8080 ibm/granite-4-350m-instruct
export OPENAI_API_KEY="local"
```

```toml
[models]
default = "openai:ibm/granite-4-350m-instruct"

[models.providers.openai]
base_url = "http://localhost:8080/v1"
models = ["ibm/granite-4-350m-instruct"]

[lite]
enabled = true
# Auto-detects 350M profile: filesystem tools only.
```

### Recommended Configurations for IBM Granite 4 Hybrid

| Model | Parameters | Profile | Tools Enabled |
|-------|-----------|---------|---------------|
| Granite 4 Hybrid | 350M | `350m` | `filesystem` |
| Granite 4 Hybrid | 1B | `1b` | `filesystem`, `search`, `shell` |
| Granite 4 Hybrid | 3B | `3b` | `filesystem`, `search`, `shell` |

### Benefits

- **Reduced Context Usage:** Distilled prompts use 50-75% less tokens than default
- **Faster Responses:** Fewer tools = clearer decision space for small models
- **Lower Resource Requirements:** Works on CPU-only systems
- **Improved Reliability:** Simpler prompts = more consistent behavior
- **Cost Savings:** Smaller models = lower inference costs
- **Optimized for Granite 4 Hybrid:** Example prompts specifically tuned for IBM's hybrid models

### Tips for Small Models

1. **Start minimal:** Begin with 350m prompt and essential tools only
2. **Iterate:** Gradually enable more tools as needed
3. **Monitor quality:** Some tasks may require larger models
4. **Use explicit instructions:** Small models benefit from specific, clear requests
5. **Leverage strengths:** Focus on code editing and file operations
6. **Customize prompts:** The provided examples are starting points - adapt for your model
7. **Use ramalama for easy setup:** `ramalama serve --port 8080 <model-name>` handles chat templates automatically
8. **Set dummy API key:** Local servers don't need real keys: `export OPENAI_API_KEY="local"`

### Additional Resources

- **[Complete Example Config](./examples/lite_config.toml)** - Fully documented configuration file
- **[Unit Tests](./tests/unit_tests/test_lite_mode.py)** - 27 comprehensive tests for lite mode
- **[Fork Maintenance](../../FORK_MAINTENANCE.md)** - Strategy for keeping fork in sync with upstream

## 📖 Resources

- **[Fork Repository](https://github.com/mecrobio/deepagents-lite)** — This fork's repository
- **[CLI Source](https://github.com/mecrobio/deepagents-lite/tree/lite/libs/cli)** — Full source code
- **[Upstream Deep Agents](https://github.com/langchain-ai/deepagents)** — Original upstream project
- **[Upstream Documentation](https://docs.langchain.com/oss/python/deepagents/cli/overview)** — Upstream docs (most features apply)

## 📕 Releases & Versioning

See our [Releases](https://docs.langchain.com/oss/python/release-policy) and [Versioning](https://docs.langchain.com/oss/python/versioning) policies.

## 💁 Contributing

As an open-source project in a rapidly developing field, we are extremely open to contributions, whether it be in the form of a new feature, improved infrastructure, or better documentation.

For detailed information on how to contribute, see the [Contributing Guide](https://docs.langchain.com/oss/python/contributing/overview).
