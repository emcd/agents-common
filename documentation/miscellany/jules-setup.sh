# https://jules.google/docs/environment/

set -eu -o pipefail

uv tool install hatch
uv tool install copier
uv tool install emcd-agents

agentsmgr populate project github:emcd/agents-common@master#defaults

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

go install github.com/isaacphi/mcp-language-server@latest

npm install -g pyright
npm install -g @fission-ai/openspec@latest
