# Jules Session Setup

**Instructions for Jules instances**: Execute the following setup steps at the beginning of each Jules session to ensure all required tools are available.

## Required Setup Steps

### 1. Install Core Python Tools

Check if `hatch`, `copier`, and `agentsmgr` are already installed. If not, install them:

```bash
if ! command -v hatch &> /dev/null; then
    uv tool install hatch
fi
if ! command -v copier &> /dev/null; then
    uv tool install copier
fi
if ! command -v agentsmgr &> /dev/null; then
    uv tool install emcd-agents
fi
```

### 2. Populate Project Agents

```bash
agentsmgr populate project github:emcd/agents-common@master#defaults
```

### 3. Configure Environment

Set up XDG-compliant Go paths. Append to `~/.profile` (or your preferred environment file):

```bash
cat >> ~/.profile << 'EOF'

# Add Go bin to PATH (XDG compliant)
export GOPATH="${HOME}/.local/share/go"
case ":${PATH}:" in
    *:"${GOPATH}/bin":*)
        ;;
    *)
        export PATH="${GOPATH}/bin:${PATH}"
        ;;
esac
EOF
```

Source the updated environment:

```bash
source ~/.profile
```

### 4. Install Language Servers

Install `mcp-language-server` (proxies language servers for MCP):

```bash
go install github.com/isaacphi/mcp-language-server@latest
```

Install Pyright (Python language server) if not already present:

```bash
if ! command -v pyright &> /dev/null; then
    npm install -g pyright
fi
```

Install Ruff (Python linter/formatter) if not already present:

```bash
if ! command -v ruff &> /dev/null; then
    uv tool install ruff
fi
```
