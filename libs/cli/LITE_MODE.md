# Deep Agents Lite Mode

Lite mode is a specialized configuration for Deep Agents CLI optimized for small language models (SLMs), particularly the **IBM Granite 4 Hybrid** models (350M, 1B, and 3B parameters).

It provides distilled system prompts and filtered toolsets to ensure high performance and reliability even with limited model capacity.

## Key Features

- **Consolidated Profiles**: Optimized settings for 350M, 1B, and 3B Granite 4 models.
- **Auto-detection**: Automatically selects the best prompt and toolset based on the model name.
- **Minimum Toolsets**: Enables only the essential tools for each model size to reduce context usage and prevent tool-calling errors.
- **Tailored Prompts**: Ultra-concise system instructions designed specifically for the capabilities of each model size.

## Model Profiles

### Granite 4 350M
The smallest model, highly optimized for basic file operations.
- **Toolset**: `filesystem` only (`read_file`, `write_file`, `edit_file`, `list_files`).
- **Prompt**: Focuses on ultra-concise responses and strict tool following.

### Granite 4 1B
A balanced model capable of codebase exploration and basic execution.
- **Toolset**: `filesystem` + `search` + `shell` (`read_file`, `write_file`, `edit_file`, `list_files`, `grep`, `glob`, `execute`).
- **Prompt**: Adds guidance for direct action and mimicking project style.

### Granite 4 3B
A capable model for complex development tasks.
- **Toolset**: `filesystem` + `search` + `shell` (full capabilities).
- **Prompt**: Emphasizes thorough investigation, iterative improvement, and verification.

## Real-World Use Cases

### Granite 4 350M (Ultra-Minimal)
**Focus**: Fast, reliable, single-file operations.
- **Documentation Maintenance**: Fixing typos, updating README files, and adding docstrings.
- **Code Formatting**: Applying simple style fixes or renaming variables in a single file.
- **Contextual Search**: Using `read_file` to find specific information in known locations.
- **Tools used**: `read_file`, `write_file`, `edit_file`, `list_files`.

### Granite 4 1B (Balanced)
**Focus**: Codebase exploration and basic development tasks.
- **Bug Fixing**: Investigating simple issues and applying targeted fixes across 1-2 files.
- **Refactoring**: Breaking down small functions or updating function signatures.
- **Exploration**: Using `glob` and `grep` to understand project structure and usage patterns.
- **Testing**: Running unit tests via `execute` to verify simple changes.
- **Tools used**: `filesystem` + `shell` (`execute`, `grep`, `glob`, etc.).

### Granite 4 3B (Advanced)
**Focus**: Comprehensive development and complex logic.
- **Feature Implementation**: Adding new functionality that requires coordination between multiple files.
- **Large Refactors**: Moving logic between modules or restructuring parts of the codebase.
- **Complex Debugging**: Analyzing stack traces, running multi-step test suites, and identifying root causes.
- **Verification**: Iteratively building and testing changes until they meet quality standards.
- **Tools used**: Full `filesystem` and `shell` (`execute`) capabilities.

## Configuration

To enable lite mode, add the `[lite]` section to your `~/.deepagents/config.toml`:

```toml
[lite]
enabled = true
```

With `enabled = true`, Deep Agents will automatically detect your model and apply the appropriate profile.

### Customizing Tools

You can explicitly enable or disable tools/categories:

```toml
[lite]
enabled = true
# Only enable basic file operations
enabled_tools = ["filesystem"] 
# OR disable specific heavy tools
# disabled_tools = ["web", "mcp", "task"]
```

### Custom System Prompt

If you want to use your own distilled prompt:

```toml
[lite]
enabled = true
system_prompt_path = "~/my_prompts/custom_lite.md"
```

## Recommended Models

For the best experience in lite mode, we recommend the following IBM Granite 4 Hybrid models via OpenRouter or WatsonX:

- `ibm/granite-4-350m-instruct`
- `ibm/granite-4-1b-instruct`
- `ibm/granite-4-3b-instruct`

Check the `recommended_configs/` directory in the project root for starter configuration files for each of these models.

## Examples

### Using Granite 4 350M (Minimum Tools)

**Command:**
```bash
deepagents --model openai:ibm/granite-4-350m-instruct
```

**Config (`config.toml`):**
```toml
[lite]
enabled = true
enabled_tools = ["filesystem"]
```

### Using Granite 4 1B (Balanced)

**Command:**
```bash
deepagents --model openai:ibm/granite-4-1b-instruct
```

**Config (`config.toml`):**
```toml
[lite]
enabled = true
enabled_tools = ["filesystem", "search", "shell"]
```
