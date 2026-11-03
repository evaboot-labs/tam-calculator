# Run it in n8n

[`n8n/tam-calculator.json`](../n8n/tam-calculator.json) does the same as `scripts/tam.py`: click to run, get TAM, SAM and SOM. It needs no credential.

## What runs

1. **Run** (Manual trigger).
2. **Your market** (Code): your industries, headcount bands with their ACV, SAM regions, SOM filter and share, and the counts you read in Sales Navigator.
3. **Sales Navigator searches** (Code): one item per search to open, with its `key`, `label` and `url`.
4. **TAM SAM SOM** (Code): the totals, the blended ACV, the SOM, the reachable buyers when you add a sample, the double-counting checks and a Markdown table.

## Set it up

1. **Import** the JSON: *Workflows > Import from file*.
2. **Edit Your market:** replace the example's industries, bands, ACVs and regions with yours. Leave the example counts in place until step 3.
3. **Execute the workflow**, open **Sales Navigator searches** and open each `url` in Sales Navigator, one per minute. Write each "results" number into `counts` in **Your market**, as shown (`27K+`).
4. **Execute again** and open **TAM SAM SOM**.

## Good to know

- To change the example the workflow ships with, edit `examples/software-sales-tool.json` and run `python3 n8n/build_workflow.py`.
- The optional sample (10 leads, 10 credits) runs in your AI Agent with the Evaboot MCP: see the skill, step 5. Copy its three numbers into `sample`.

Back to the [README](../README.md).
