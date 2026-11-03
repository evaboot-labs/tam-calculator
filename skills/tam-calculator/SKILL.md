---
name: tam-calculator
description: Calculate TAM, SAM and SOM bottom-up from LinkedIn Sales Navigator account counts - one account search per company-size band (bands never overlap, so counts add up), the same searches inside the countries you sell to for SAM, an in-market filter for SOM, each count multiplied by an annual contract value (ACV) per band, plus an optional 10-lead Evaboot sample to measure how many buyers are reachable. Use when the user asks to calculate or size their TAM, SAM, SOM, total addressable market or market size from LinkedIn or Sales Navigator data.
---

# TAM calculator

This skill runs inside a clone of https://github.com/evaboot-labs/tam-calculator. If `scripts/tam.py` is not in the working directory, clone the repo and work from there.

## Rules

- Count accounts (companies), never people, for revenue. A people count says how many buyers you can reach, not how many companies can pay.
- Bands and regions must not overlap. `python3 scripts/tam.py check <market.json>` must print OK before you report a number.
- Never invent a count. Every count comes from a Sales Navigator results header the user or you read, written as shown (`73K+`).
- ACVs and the SOM share are the user's assumptions. Ask for them and label them as assumptions in the report.
- Print every Sales Navigator URL as a Markdown link with the URL in angle brackets: `[Open in Sales Navigator](<url>)`.
- Reading counts spends no credits. Only the optional sample in step 5 does: confirm it first (1 Evaboot credit per lead, 10 leads).

## Step 1: the market

Ask, in the user's words: what they sell, the industries they sell to, the company sizes, the countries they can serve today, and one ACV per company-size band (from their own deals or price list). Copy `examples/software-sales-tool.json` to `data/<name>.json` and fill `industries`, `bands` (Sales Navigator headcount ids: B 1-10, C 11-50, D 51-200, E 201-500, F 501-1,000, G 1,001-5,000, H 5,001-10,000, I 10,001+), `sam_regions` and `buyer`. Leave `tam_regions` empty for worldwide. Find industry and region ids with `build_sn_search_from_prompt` (Evaboot MCP): its `filters_used` lists them.

## Step 2: the searches

Run `python3 scripts/tam.py urls data/<name>.json`. It prints one account search per band for TAM, the same per band for SAM, one SOM search (SAM plus headcount growth), and one people search for the buyers.

## Step 3: the counts

Open each search in Sales Navigator and read the number next to "results". With a browser tool, wait 60 seconds between two searches: LinkedIn rate-limits fast page loads. Without one, give the user the links and ask for the numbers. Write them into `counts` as shown.

## Step 4: the calculation

Run `python3 scripts/tam.py calc data/<name>.json`. Show the table, the blended ACV, the SOM line and the double-counting check. A warning means a search is not inside the one above it: fix the filters and recount that search only.

## Step 5: optional sample (10 credits)

To know how many buyers are reachable, export 10 leads of the `sam_buyers` search with `export_sn_search_or_list` (`max_results: 10`), poll `get_export` until `EXECUTED`, save the result to `data/<name>-sample.json`, run `python3 scripts/tam.py sample data/<name>-sample.json` and copy `exported`, `matched` and `safe` into `sample`. Rerun step 4.

## Step 6: report

Give TAM, SAM and SOM in one table with the counts, the ACVs (marked as assumptions), the date, and the Sales Navigator links. Say that `K+` counts are floors.

If the user wants n8n instead, follow `docs/n8n.md` with them one step at a time.
