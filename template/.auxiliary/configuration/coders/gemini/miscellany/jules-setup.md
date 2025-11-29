# Jules Session Setup

**Instructions for Jules instances**: Execute the following setup steps at the beginning of each Jules session to ensure all required tools are available.

## Required Setup Steps

### 1. Install Core Python Tools

```bash
uv tool install hatch
uv tool install copier
uv tool install emcd-agents
```

### 2. Populate Project Agents

```bash
agentsmgr populate project github:emcd/agents-common@master#defaults
```

### 3. Configure Environment

Add Go bin to PATH for persistent access. Append to `~/.bashrc`:

```bash
echo 'export PATH="$HOME/go/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

### 4. Install Language Servers

Install `mcp-language-server` (proxies language servers for MCP):

```bash
go install github.com/isaacphi/mcp-language-server@latest
```

Install Pyright (Python language server):

```bash
npm install -g pyright
```

Install Ruff (Python linter/formatter):

```bash
uv tool install ruff
```

## Notes

- The `.mcp.json` configuration expects these tools to be in PATH
