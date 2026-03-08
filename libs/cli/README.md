# 🧠🤖 Deep Agents CLI

[![PyPI - Version](https://img.shields.io/pypi/v/deepagents-cli?label=%20)](https://pypi.org/project/deepagents-cli/#history)
[![PyPI - License](https://img.shields.io/pypi/l/deepagents-cli)](https://opensource.org/licenses/MIT)
[![PyPI - Downloads](https://img.shields.io/pepy/dt/deepagents-cli)](https://pypistats.org/packages/deepagents-cli)
[![Twitter](https://img.shields.io/twitter/url/https/twitter.com/langchain.svg?style=social&label=Follow%20%40LangChain)](https://x.com/langchain)

<p align="center">
  <img src="https://raw.githubusercontent.com/langchain-ai/deepagents/main/libs/cli/images/cli.png" alt="Deep Agents CLI" width="600"/>
</p>

## Quick Install

```bash
curl -LsSf https://raw.githubusercontent.com/langchain-ai/deepagents/main/scripts/install.sh | bash
```

```bash
# With model provider extras (OpenAI is included by default)
DEEPAGENTS_EXTRAS="anthropic,groq" curl -LsSf https://raw.githubusercontent.com/langchain-ai/deepagents/main/scripts/install.sh | bash
```

Or install directly with `uv`:

```bash
# Install with chosen model providers (OpenAI is included by default)
uv tool install 'deepagents-cli[anthropic,groq]'
```

Run the CLI:

```bash
deepagents
```

## 🤔 What is this?

Using an LLM to call tools in a loop is the simplest form of an agent. This architecture, however, can yield agents that are "shallow" and fail to plan and act over longer, more complex tasks.

Applications like "Deep Research", "Manus", and "Claude Code" have gotten around this limitation by implementing a combination of four things: a **planning tool**, **sub agents**, access to a **file system**, and a **detailed prompt**.

`deepagents` is a Python package that implements these in a general purpose way so that you can easily create a Deep Agent for your application. For a full overview and quickstart of Deep Agents, the best resource is our [docs](https://docs.langchain.com/oss/python/deepagents/overview).

**Acknowledgements: This project was primarily inspired by Claude Code, and initially was largely an attempt to see what made Claude Code general purpose, and make it even more so.**

## 🪶 Lite Mode for Small Language Models

Deep Agents CLI includes "lite mode" optimized for smaller models, particularly IBM Granite 4 Hybrid models (350M-7B parameters).

### Quick Start

1. **Choose a distilled prompt** based on your model size (examples provided):
   - `lite_prompt_granite4_350m.md` - For 350M-700M parameter models
   - `lite_prompt_granite4_1b.md` - For 1B-2B parameter models
   - `lite_prompt_granite4_3b.md` - For 3B-7B parameter models

2. **Copy the prompt** to your config directory:
   ```bash
   mkdir -p ~/.deepagents
   cp libs/cli/deepagents_cli/lite_prompt_granite4_1b.md ~/.deepagents/
   ```

3. **Configure** `~/.deepagents/config.toml`:
   ```toml
   [lite]
   enabled = true
   system_prompt_path = "~/.deepagents/lite_prompt_granite4_1b.md"
   disabled_tools = ["web_search", "mcp"]
   ```

### Configuration Options

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
| **glob** | filesystem | Find files by glob pattern | Medium | ✓ |
| **grep** | filesystem | Search text across files | Medium | ✓ |
| **execute** | shell | Execute shell commands | High | ✓ |
| **http_request** | web | Make HTTP API requests | Medium | ✓ |
| **fetch_url** | web | Fetch and parse web pages | High | ✓ |
| **web_search** | web | Tavily web search | Very High | ✓* |
| **mcp** | mcp | Model Context Protocol tools | Varies | ✓* |
| **task** | advanced | Delegate to subagents | Very High | ✓ |
| **compact_conversation** | advanced | Compress conversation history | High | ✓ |

\* Requires API key or configuration

### Tool Categories

**filesystem** (6 tools)
- `read_file`, `write_file`, `edit_file`, `list_files`, `glob`, `grep`
- Essential file operations with low context overhead

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

#### Ultra-Minimal (350M parameters - Granite 4 Hybrid 350M)
```toml
[lite]
enabled = true
system_prompt_path = "~/.deepagents/lite_prompt_granite4_350m.md"
enabled_tools = ["read_file", "write_file", "edit_file", "list_files"]
```

#### Development Assistant (1B-2B parameters - Granite 4 Hybrid 1B)
```toml
[lite]
enabled = true
system_prompt_path = "~/.deepagents/lite_prompt_granite4_1b.md"
disabled_tools = ["web_search", "fetch_url", "mcp", "task"]
```

#### Code Review Only (Read-Only - Granite 4 Hybrid 3B)
```toml
[lite]
enabled = true
system_prompt_path = "~/.deepagents/lite_prompt_granite4_3b.md"
enabled_tools = ["read_file", "list_files", "glob", "grep"]
```

#### Local Development (No External APIs)
```toml
[lite]
enabled = true
system_prompt_path = "~/.deepagents/lite_prompt_granite4_1b.md"
disabled_tools = ["web", "mcp"]  # Disables all web and MCP tools
```

### Recommended Configurations for IBM Granite 4 Hybrid

| Model | Parameters | Prompt | Disabled Tools |
|-------|-----------|--------|----------------|
| Granite 4 Hybrid | 350M | `lite_prompt_granite4_350m.md` | web, mcp, advanced |
| Granite 4 Hybrid | 1B | `lite_prompt_granite4_1b.md` | web, mcp, task |
| Granite 4 Hybrid | 3B | `lite_prompt_granite4_3b.md` | web_search, mcp |

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

## 📖 Resources

- **[CLI Documentation](https://docs.langchain.com/oss/python/deepagents/cli/overview)** — Full documentation
- **[CLI Source](https://github.com/langchain-ai/deepagents/tree/main/libs/cli)** — Full source code
- **[Deep Agents SDK](https://github.com/langchain-ai/deepagents)** — The underlying agent harness
- **[Chat LangChain](https://chat.langchain.com)** - Chat interactively with the docs

## 📕 Releases & Versioning

See our [Releases](https://docs.langchain.com/oss/python/release-policy) and [Versioning](https://docs.langchain.com/oss/python/versioning) policies.

## 💁 Contributing

As an open-source project in a rapidly developing field, we are extremely open to contributions, whether it be in the form of a new feature, improved infrastructure, or better documentation.

For detailed information on how to contribute, see the [Contributing Guide](https://docs.langchain.com/oss/python/contributing/overview).
