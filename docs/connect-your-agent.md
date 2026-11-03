# Connect your AI Agent

The counts need only Sales Navigator. The Evaboot MCP server builds searches and runs the optional 10-lead sample.

## 1. Accounts

- An [Evaboot account](https://dash.evaboot.com/accounts/signup/?last_click_origin=tam-calculator-repo) with credits.
- A LinkedIn Sales Navigator seat, connected to Evaboot: open any search in Chrome and click **Export with Evaboot** once.

## 2. Get the repo

```bash
git clone https://github.com/evaboot-labs/tam-calculator
cd tam-calculator
cp .env.example .env
```

Write your key from [dash.evaboot.com/dash/api/](https://dash.evaboot.com/dash/api/) into `.env` as `EVABOOT_API_KEY`. `.mcp.json` reads the variable from your shell, so load it before you start Claude Code: `set -a; source .env; set +a; claude`.

## 3. Connect the MCP server

- **Claude Code:** start it from this folder, with the key loaded as above. `.mcp.json` connects `https://mcp.evaboot.com/mcp`. A 401 from the evaboot server means the variable is not set.
- **Claude (web and desktop app):** *Settings > Connectors > Add custom connector*, name `Evaboot`, URL `https://mcp.evaboot.com/mcp`, then sign in to Evaboot.
- **Codex, Cursor:** add `https://mcp.evaboot.com/mcp` as an HTTP MCP server with the header `Authorization: Bearer <your key>`.

## 4. Check

Run `python3 scripts/tam.py calc examples/software-sales-tool.json`, then ask your AI Agent: "Check my Evaboot quota and whether my Sales Navigator is connected." A quota and `has_valid_salesnav: true` mean you are ready.

Back to the [README](../README.md).
