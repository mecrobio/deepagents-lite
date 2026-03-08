# Fork Maintenance Strategy

This document describes the maintenance strategy for the `deepagents-lite` fork, which adds Granite 4 small model support to the upstream [langchain-ai/deepagents](https://github.com/langchain-ai/deepagents) project.

## Overview

**Fork Purpose:** Enable DeepAgents CLI to work efficiently with small language models (IBM Granite 4 Hybrid 350M-7B parameters) while maintaining compatibility with upstream.

**Upstream Repository:** `git@github.com:langchain-ai/deepagents.git`
**Fork Repository:** `git@github.com:mecrobio/deepagents-lite.git`

## Branch Structure

### `main` - Upstream Mirror
- **Purpose:** Clean sync with `upstream/main`
- **Policy:** Never commit lite-specific changes here
- **Updates:** Fast-forward only merges from upstream
- **Benefit:** Makes upstream syncing trivial (no conflicts)

### `lite` - Customizations Branch
- **Purpose:** All Granite 4 / lite mode customizations
- **Contains:**
  - Modified files (4): `model_config.py`, `agent.py`, `main.py`, `README.md`
  - New files (7+): `lite_tools.py`, `lite.py`, `lite_prompt_*.md`, `test_lite_mode.py`, etc.
- **Merges:** Receives updates from `main` after upstream syncs

### `upstream-staging` (Optional)
- **Purpose:** Test upstream merges before applying to `lite`
- **Workflow:** `upstream/main` → `upstream-staging` → test → `lite`
- **Use when:** Major upstream refactoring expected

## Remote Configuration

```bash
# Verify remotes are configured correctly
$ git remote -v
origin      git@github.com:mecrobio/deepagents-lite.git (fetch)
origin      git@github.com:mecrobio/deepagents-lite.git (push)
upstream    git@github.com:langchain-ai/deepagents.git (fetch)
upstream    git@github.com:langchain-ai/deepagents.git (push)
```

## Workflows

### Regular Upstream Sync

When a new upstream release is published:

```bash
# 1. Update main branch from upstream (fast-forward only)
git checkout main
git fetch upstream
git merge upstream/main --ff-only
git push origin main

# 2. Merge main into lite
git checkout lite
git merge main

# 3. Resolve conflicts (see Conflict Resolution section)

# 4. Run tests
pytest libs/cli/tests/

# 5. Push lite branch
git push origin lite
```

**Alternative (Rebase):** For cleaner history, replace step 2 with:
```bash
git checkout lite
git rebase main
# After resolving conflicts:
git push origin lite --force-with-lease
```

**Trade-offs:**
- **Merge:** Preserves complete history, easier to understand what changed when
- **Rebase:** Cleaner linear history, but rewrites commits (requires force push)

**Recommendation:** Use merge for regular syncs, rebase only if history becomes too cluttered.

### Creating a Lite Release

After successfully merging upstream changes and testing:

```bash
# Ensure you're on lite branch with latest changes
git checkout lite

# Create annotated tag
git tag -a v0.0.X-lite -m "DeepAgents Lite v0.0.X - Granite 4 optimized

Based on upstream deepagents-cli v0.0.X
- Lite mode features for small models
- Granite 4 Hybrid optimizations (350M-7B)
- Custom tool filtering and prompts
"

# Push tag to origin
git push origin v0.0.X-lite

# (Optional) Create GitHub release from tag
# Visit: https://github.com/mecrobio/deepagents-lite/releases/new
```

**Version Numbering Strategy:**
- Mirror upstream version + `-lite` suffix
- Example: Upstream releases `0.0.29` → Create `v0.0.29-lite`
- Keeps version alignment clear for users

### Emergency Hotfix on Lite

For urgent fixes to lite-specific code only:

```bash
# Make fix directly on lite branch
git checkout lite
# ... make changes ...
git add <files>
git commit -m "fix(lite): description of fix"
git push origin lite

# Tag patch release
git tag -a v0.0.X-lite.1 -m "DeepAgents Lite v0.0.X patch 1"
git push origin v0.0.X-lite.1
```

**Note:** Hotfix versions use `.N` suffix (e.g., `v0.0.29-lite.1`)

## Conflict Resolution Strategy

### Files Most Likely to Conflict

1. **`libs/cli/README.md`** (HIGH)
   - **Reason:** Documentation updates from upstream
   - **Strategy:** Accept upstream changes, manually re-apply lite section at bottom
   - **Location:** Lite section titled "🪶 Lite Mode for Small Language Models"

2. **`libs/cli/deepagents_cli/main.py`** (MEDIUM)
   - **Reason:** Tool loading changes in upstream
   - **Strategy:** Accept upstream tool additions, preserve `should_disable_tool()` filtering
   - **Key lines:** Tool loading section (~538-576)

3. **`libs/cli/deepagents_cli/agent.py`** (LOW)
   - **Reason:** Agent creation signature changes
   - **Strategy:** Accept upstream changes, preserve `lite_config` parameter and backend switching
   - **Key sections:** Function signature, backend selection, prompt loading

4. **`libs/cli/deepagents_cli/model_config.py`** (LOW)
   - **Reason:** Config schema additions
   - **Strategy:** Accept upstream changes, preserve `LiteConfig` TypedDict and loading logic

### Conflict Resolution Process

```bash
# When conflicts occur during merge:
git status  # Shows conflicted files

# For each conflicted file:
# 1. Open in editor, look for conflict markers
# 2. For core functionality: accept upstream changes
# 3. For lite hooks: preserve your additions
# 4. Remove conflict markers

# Mark as resolved
git add <resolved-file>

# Continue merge
git merge --continue  # or git rebase --continue

# Test immediately
pytest libs/cli/tests/
```

### Preserving Lite Hooks

**In `model_config.py`:**
```python
# PRESERVE: LiteConfig definition
class LiteConfig(TypedDict, total=False):
    """Configuration for lite mode optimized for small language models."""
    enabled: bool
    system_prompt_path: str
    disabled_tools: list[str]
    enabled_tools: list[str]

# PRESERVE: lite field in ModelConfig
@dataclass
class ModelConfig:
    # ... other fields ...
    lite: LiteConfig | None = None

# PRESERVE: lite section loading in load() method (lines ~570-585)
# PRESERVE: validation in _validate() (lines ~610-617)
```

**In `agent.py`:**
```python
# PRESERVE: lite_config parameter in create_cli_agent()
def create_cli_agent(
    # ... other params ...
    lite_config: LiteConfig | None = None,
):

# PRESERVE: Backend switching logic (~563-592)
# PRESERVE: System prompt loading with lite support (~607-628)
```

**In `main.py`:**
```python
# PRESERVE: Import
from deepagents_cli.lite_tools import should_disable_tool

# PRESERVE: Tool filtering pattern (~538-576)
if not should_disable_tool("tool_name", lite_config):
    tools.append(tool_name)

# PRESERVE: lite_config passed to create_cli_agent()
```

**In `README.md`:**
```markdown
# PRESERVE: Entire section at bottom of file
## 🪶 Lite Mode for Small Language Models
...
```

## Testing Strategy

### Before Each Release

```bash
# 1. Run full test suite
cd libs/cli
pytest tests/ -v

# Expected: All tests pass (122 existing + 27 lite mode = 149 total)

# 2. Manual testing with small model
# Create test config
cat > /tmp/test_lite_config.toml << 'EOF'
[models]
default = "ollama:granite4:1b-hybrid"

[lite]
enabled = true
system_prompt_path = "~/.deepagents/lite_prompt_granite4_1b.md"
disabled_tools = ["web", "mcp", "task"]

[ollama]
base_url = "http://localhost:11434"
EOF

# Run CLI with test config
DEEPAGENTS_CONFIG=/tmp/test_lite_config.toml deepagents

# Test basic operations:
# - "List files in current directory"
# - "Read the README.md file"
# - "Edit main.py and add a comment"
```

### Continuous Integration

Current CI configuration (if any) should:
- Run on both `main` and `lite` branches
- Execute full test suite
- Fail if lite mode tests don't pass

## File Ownership Map

### Lite-Owned Files (No Upstream Equivalent)

These files are safe from merge conflicts:

```
libs/cli/deepagents_cli/lite_tools.py
libs/cli/deepagents_cli/lite.py
libs/cli/deepagents_cli/lite_prompt_granite4_350m.md
libs/cli/deepagents_cli/lite_prompt_granite4_1b.md
libs/cli/deepagents_cli/lite_prompt_granite4_3b.md
libs/cli/examples/lite_config.toml
libs/cli/tests/unit_tests/test_lite_mode.py
libs/cli/verify_lite_mode.py
FORK_MAINTENANCE.md (this file)
```

### Shared Files (Modified from Upstream)

These files require careful conflict resolution:

```
libs/cli/README.md                      # Lite section added at bottom
libs/cli/deepagents_cli/model_config.py # LiteConfig + loading logic
libs/cli/deepagents_cli/agent.py        # lite_config param + backend switching
libs/cli/deepagents_cli/main.py         # Tool filtering logic
```

### Upstream-Owned Files (No Modifications)

All other files - accept upstream changes unconditionally.

## Documentation Strategy

### Current Approach: Integrated README

**Pros:**
- Single source of truth
- Users see all features in one place
- Lite mode properly integrated into main docs

**Cons:**
- Will conflict on most upstream merges
- Requires manual re-application of lite section

**Mitigation:**
1. Keep lite section at very bottom of README
2. Use distinctive section header: `## 🪶 Lite Mode for Small Language Models`
3. After conflict, search for this header to find where to re-insert

### Alternative: Separate Documentation

If README conflicts become too frequent:

```bash
# Move lite docs to separate file
git mv libs/cli/README.md libs/cli/README.md.tmp
git checkout upstream/main -- libs/cli/README.md
cat >> libs/cli/README.md << 'EOF'

## 🪶 Lite Mode

For comprehensive lite mode documentation, see [LITE_MODE.md](./LITE_MODE.md).
EOF

git mv libs/cli/README.md.tmp libs/cli/LITE_MODE.md
git add libs/cli/README.md libs/cli/LITE_MODE.md
git commit -m "docs: separate lite mode documentation"
```

**Decision Point:** Reevaluate after 2-3 upstream merges. If README conflicts are minimal, keep current approach.

## Upstream Contribution Considerations

### Should You Contribute Lite Mode Back?

**Pros:**
- Eliminates fork maintenance burden
- Benefits broader community
- Potential for upstream improvements/optimizations
- Your implementation is clean and minimal

**Cons:**
- Upstream may have different priorities
- May require additional changes to meet their standards
- Would need to maintain compatibility with other providers

### If Contributing:

1. **Prepare PR:**
   ```bash
   # Create feature branch from main
   git checkout main
   git checkout -b contrib/lite-mode-small-models

   # Cherry-pick lite commits
   git cherry-pick <commit-hash>...

   # Push to your fork
   git push origin contrib/lite-mode-small-models
   ```

2. **PR Description Template:**
   ```markdown
   ## Motivation
   Enable DeepAgents to run efficiently on small language models (350M-7B parameters)

   ## Changes
   - Add configurable tool filtering (whitelist/blacklist/categories)
   - Add custom system prompt support
   - Add 3 example prompts optimized for IBM Granite 4 Hybrid models
   - Add 27 comprehensive tests

   ## Design Principles
   - Minimal changes to core codebase (~100 lines across 3 files)
   - Fully backward compatible (no breaking changes)
   - All features gated behind optional `[lite]` config section

   ## Testing
   - 27 new unit tests (all passing)
   - All existing tests still pass
   - Verified with Granite 4 models (350M, 1B, 3B)
   ```

3. **Timeline:**
   - Let fork stabilize for 2-3 months
   - Gather user feedback
   - Demonstrate real-world usage
   - Then approach upstream

## Maintenance Checklist

### Weekly
- [ ] Check for new upstream releases: https://github.com/langchain-ai/deepagents/releases
- [ ] Review upstream commits: https://github.com/langchain-ai/deepagents/commits/main

### When Upstream Releases
- [ ] Read upstream changelog/release notes
- [ ] Sync `main` branch (fast-forward merge)
- [ ] Merge `main` into `lite`
- [ ] Resolve conflicts (focus on 4 shared files)
- [ ] Run full test suite: `pytest libs/cli/tests/`
- [ ] Manual test with small model
- [ ] Push `lite` branch
- [ ] Create lite release tag
- [ ] Update GitHub release notes

### Monthly
- [ ] Review open upstream issues/PRs for relevant changes
- [ ] Check if any upstream improvements could benefit lite mode
- [ ] Consider whether upstream contribution makes sense

### Per Release
- [ ] Test with all three Granite 4 model sizes (350M, 1B, 3B)
- [ ] Verify all example configs still work
- [ ] Tag release with detailed notes

## Troubleshooting

### Merge Conflicts in README

```bash
# If automatic merge fails:
git checkout --ours libs/cli/README.md    # Start with upstream version
# Manually copy lite section from:
git show lite:libs/cli/README.md
# Append to bottom of README.md
git add libs/cli/README.md
git merge --continue
```

### Upstream Refactored Tool Loading

If upstream significantly changes how tools are loaded:

```bash
# 1. Accept their new implementation
git checkout --theirs libs/cli/deepagents_cli/main.py

# 2. Re-apply tool filtering manually
# Edit main.py and add should_disable_tool() checks around new tool loading

# 3. Test thoroughly
pytest libs/cli/tests/unit_tests/test_lite_mode.py -v
```

### Tests Failing After Merge

```bash
# 1. Check what changed in upstream tests
git diff upstream/main..main libs/cli/tests/

# 2. If test framework changed, update lite tests
# Edit libs/cli/tests/unit_tests/test_lite_mode.py

# 3. If tool interfaces changed, update lite_tools.py
```

## Release History

Track releases here for reference:

| Lite Version | Upstream Version | Date | Notes |
|-------------|------------------|------|-------|
| v0.0.29-lite | v0.0.29 | TBD | Initial lite mode release |

## References

- **Upstream Repository:** https://github.com/langchain-ai/deepagents
- **Lite Fork:** https://github.com/mecrobio/deepagents-lite
- **Upstream Releases:** https://github.com/langchain-ai/deepagents/releases
- **Example Config:** [libs/cli/examples/lite_config.toml](./libs/cli/examples/lite_config.toml)

## Questions or Issues

When encountering maintenance issues:

1. Check this document first
2. Review recent upstream changes for context
3. Test in isolation (create minimal reproduction)
4. Document solution in this file for future reference

## Version

**Document Version:** 1.0
**Last Updated:** 2026-03-08
**Maintained By:** Fork maintainer
