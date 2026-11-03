# Agent instructions

This repo calculates a market size bottom-up from LinkedIn Sales Navigator: one account search per company-size band for TAM, the same searches in the countries the user sells to for SAM, an in-market filter for SOM, then each count times an annual contract value (ACV). Reading counts costs no Evaboot credit; an optional 10-lead sample measures how many buyers are reachable.

1. Follow the skill in `skills/tam-calculator/SKILL.md` step by step.
2. `scripts/tam.py` builds the searches (`urls`), checks for double counting (`check`), reads a sample export (`sample`) and calculates (`calc`). Standard library only.
3. `examples/software-sales-tool.json` is a filled example with real counts from 2026-11-03.
4. The counting rules are in `docs/counting-rules.md`.
5. If the Evaboot connector or key is missing, follow `docs/connect-your-agent.md`.
6. If the user wants n8n instead, follow `docs/n8n.md` with them one step at a time.

Confirm with the user before any call that spends credits (the sample export: 1 Evaboot credit per lead). Never ask for or handle an API key: the user writes it into `.env` or connects Evaboot in their AI Agent. Never commit `.env` or `data/`: they hold secrets and real people's data. Wait 60 seconds between two Sales Navigator page loads.
