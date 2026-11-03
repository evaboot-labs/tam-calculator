<picture>
  <source media="(prefers-color-scheme: dark)" srcset=".github/assets/banner-dark.png">
  <img src=".github/assets/banner-light.png" alt="TAM calculator: TAM, SAM and SOM from real Sales Navigator account counts" width="1280">
</picture>

# TAM calculator

Size your market bottom-up from LinkedIn Sales Navigator: one account search per company-size band, the same searches in the countries you sell to, one in-market filter, then each count times your annual contract value (ACV). No double counting, no analyst report.

[![Works with Claude Code · Codex · Cursor](https://img.shields.io/badge/works%20with-Claude%20Code%20%C2%B7%20Codex%20%C2%B7%20Cursor-5719D9)](AGENTS.md)
[![MCP server](https://img.shields.io/badge/MCP-mcp.evaboot.com-5719D9)](https://evaboot.com/mcp)
[![License: MIT](https://img.shields.io/badge/license-MIT-5719D9)](LICENSE)

## Set it up in one prompt

Paste this into Claude Code, Codex or Cursor:

```text
Clone https://github.com/evaboot-labs/tam-calculator, read AGENTS.md and follow the skill. Calculate the TAM, SAM and SOM of my product: we sell to software companies with 11 to 500 employees in the US and the UK.
```

<details>
<summary>Or install the skill</summary>

Claude Code:

```text
/plugin marketplace add evaboot-labs/tam-calculator
/plugin install tam-calculator@evaboot-labs-tam-calculator
```

Codex, Cursor and other agents:

```bash
npx skills add evaboot-labs/tam-calculator
```

</details>

## How it works

**1. One account search per band.** Company-size bands never overlap, so their counts add up. The SAM searches add your countries; the SOM search adds an in-market filter.

<img src=".github/assets/screenshots/1-account-count.png" alt="Sales Navigator account search: Software Development, 11-50 employees, headquarters in the US, UK, France and Germany, 27K+ results" width="800">

**2. Script or n8n.** `scripts/tam.py` and the n8n workflow build the same searches and run the same math.

<img src=".github/assets/screenshots/2-n8n.png" alt="n8n workflow: Run, Your market, Sales Navigator searches, TAM SAM SOM" width="800">

**3. One table.** Counts times ACV per band, a blended ACV, the SOM, and a double-counting check.

<img src=".github/assets/screenshots/3-tam-table.png" alt="tam.py output: TAM $201.6M, SAM $90.0M, SOM $1.2M for a sales tool sold to software companies" width="800">

## What you need

- A Sales Navigator seat to read the counts.
- Python 3 (standard library only), or n8n.
- Your ACV per company-size band, from your own deals or price list.
- Cost: reading counts is free. The optional reachability sample costs 10 [Evaboot](https://dash.evaboot.com/accounts/signup/?last_click_origin=tam-calculator-repo) credits.

## Go further

| Page | For |
|---|---|
| [docs/counting-rules.md](docs/counting-rules.md) | The four rules that stop double counting |
| [docs/connect-your-agent.md](docs/connect-your-agent.md) | The Evaboot connector or key, by hand, for each agent |
| [docs/n8n.md](docs/n8n.md) | The same calculator in n8n |

---

Agents: start at [AGENTS.md](AGENTS.md) · Built by [Evaboot](https://evaboot.com) · More workflows at [github.com/evaboot-labs](https://github.com/evaboot-labs) · [MIT license](LICENSE)
