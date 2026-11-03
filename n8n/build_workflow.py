"""Builds n8n/tam-calculator.json. Run: python3 n8n/build_workflow.py

Click to run: "Your market" holds your filters, ACVs and the counts you read in Sales Navigator.
"Sales Navigator searches" lists the account searches to open (one count each).
"TAM SAM SOM" returns the same table as scripts/tam.py calc. No credential needed.
"""
import json
import uuid
from pathlib import Path

HERE = Path(__file__).resolve().parent
MARKET = json.loads((HERE.parent / "examples" / "software-sales-tool.json").read_text())

nodes, connections = [], {}


def node(name, type_, version, params, pos):
    nodes.append({"parameters": params, "id": str(uuid.uuid4()), "name": name, "type": type_,
                  "typeVersion": version, "position": pos})


def link(a, b):
    connections.setdefault(a, {"main": [[]]})["main"][0].append({"node": b, "type": "main", "index": 0})


def code(name, js, pos):
    node(name, "n8n-nodes-base.code", 2, {"jsCode": js}, pos)


MARKET_JS = ("// Edit your market here: industries, headcount bands with their ACV (annual contract value),\n"
             "// SAM regions, the SOM filter and share, then the counts you read in Sales Navigator.\n"
             "return [{ json: " + json.dumps(MARKET, indent=2) + " }];\n")

COMMON_JS = r"""
const BASE = 'https://www.linkedin.com/sales/search/';
const enc = s => encodeURIComponent(s).replace(/%28/g, '(').replace(/%29/g, ')').replace(/%2C/g, ',').replace(/%3A/g, ':');
const flt = (kind, ids) => `(type:${kind},values:List(${ids.map(i => `(id:${i},selectionType:INCLUDED)`).join(',')}))`;
const url = (kind, f) => BASE + kind + '?query=' + enc(`(filters:List(${f.join(',')}))`);
const accountFilters = (m, bands, regions, growth) => {
  const f = [flt('COMPANY_HEADCOUNT', bands), flt('INDUSTRY', m.industries.map(i => i.id))];
  if (regions && regions.length) f.push(flt('REGION', regions.map(r => r.id)));
  if (growth && m.som_filter && m.som_filter.headcount_growth_min)
    f.push(`(type:COMPANY_HEADCOUNT_GROWTH,rangeValue:(min:${m.som_filter.headcount_growth_min}))`);
  return f;
};
// '73K+' -> 73000. Sales Navigator rounds down, so these are floors.
const num = v => {
  if (typeof v === 'number') return v;
  let s = String(v).toUpperCase().replace(/,|\+|RESULTS/g, '').trim(), mult = 1;
  if (s.endsWith('K')) { mult = 1e3; s = s.slice(0, -1); } else if (s.endsWith('M')) { mult = 1e6; s = s.slice(0, -1); }
  return parseFloat(s) * mult;
};
const money = x => x >= 1e9 ? `$${(x / 1e9).toFixed(1)}B` : x >= 1e6 ? `$${(x / 1e6).toFixed(1)}M` : x >= 1e3 ? `$${(x / 1e3).toFixed(1)}K` : `$${Math.round(x)}`;
const m = $('Your market').first().json;
"""

SEARCHES_JS = COMMON_JS + r"""
// One account search per level and band. Bands never overlap, so their counts add up.
const bands = m.bands.map(b => b.id), out = [];
for (const b of m.bands) out.push({ key: `tam.${b.id}`, label: `TAM accounts, ${b.label} employees`, url: url('company', accountFilters(m, [b.id], m.tam_regions)) });
for (const b of m.bands) out.push({ key: `sam.${b.id}`, label: `SAM accounts, ${b.label} employees`, url: url('company', accountFilters(m, [b.id], m.sam_regions)) });
if (m.som_filter) out.push({ key: 'som_accounts', label: 'SOM accounts: SAM + headcount growth', url: url('company', accountFilters(m, bands, m.sam_regions, true)) });
if (m.buyer) {
  // People search: REGION is where the person lives, so filter on the company's headquarters instead.
  const f = accountFilters(m, bands, null);
  f.push(flt('COMPANY_HEADQUARTERS', m.sam_regions.map(r => r.id)));
  f.push(flt('FUNCTION', [m.buyer.function]));
  if (m.buyer.seniority) f.push(flt('SENIORITY_LEVEL', m.buyer.seniority));
  out.push({ key: 'sam_buyers', label: 'People: buyers in SAM accounts (not for revenue)', url: url('people', f) });
}
return out.map(json => ({ json }));
"""

CALC_JS = COMMON_JS + r"""
const c = m.counts, warnings = [];
let tam = 0, sam = 0, tamN = 0, samN = 0;
const rows = m.bands.map(b => {
  const t = num(c.tam[b.id]), s = num(c.sam[b.id]);
  if (s > t) warnings.push(`SAM ${b.label} (${c.sam[b.id]}) is above TAM (${c.tam[b.id]}): the SAM search is not inside the TAM search.`);
  tam += t * b.acv; sam += s * b.acv; tamN += t; samN += s;
  return { band: b.label, tam_accounts: c.tam[b.id], sam_accounts: c.sam[b.id], acv: b.acv, tam: money(t * b.acv), sam: money(s * b.acv) };
});
if (new Set(m.bands.map(b => b.id)).size !== m.bands.length) warnings.push('A headcount band appears twice: each company would be counted twice.');
for (const key of ['tam_regions', 'sam_regions']) {
  const r = (m[key] || []).map(x => x.id);
  if (new Set(r).size !== r.length) warnings.push(`${key}: a region appears twice.`);
}
const blended = samN ? sam / samN : 0;
const somN = c.som_accounts ? num(c.som_accounts) : samN;
if (somN > samN) warnings.push('SOM accounts are above SAM accounts: the SOM search must add filters to the SAM search.');
const share = m.som_share ?? 0.05, som = somN * blended * share;
const table = ['| Band | TAM accounts | SAM accounts | ACV | TAM | SAM |', '|---|---|---|---|---|---|',
  ...rows.map(r => `| ${r.band} | ${r.tam_accounts} | ${r.sam_accounts} | $${r.acv.toLocaleString('en-US')} | ${r.tam} | ${r.sam} |`),
  `| Total | ${tamN.toLocaleString('en-US')} | ${samN.toLocaleString('en-US')} | | ${money(tam)} | ${money(sam)} |`].join('\n');
let reachable = null;
if (c.sam_buyers && m.sample && m.sample.exported) reachable = Math.round(num(c.sam_buyers) * m.sample.safe / m.sample.exported);
return [{ json: {
  market: m.name, tam: money(tam), sam: money(sam), som: money(som),
  tam_accounts: tamN, sam_accounts: samN, som_accounts: somN, blended_acv: money(blended), som_share: share,
  som_customers: Math.round(somN * share), reachable_buyers: reachable,
  checks: warnings.length ? warnings : ['Double-counting checks: OK'], table,
} }];
"""

node("Run", "n8n-nodes-base.manualTrigger", 1, {}, [0, 0])
code("Your market", MARKET_JS, [220, 0])
code("Sales Navigator searches", SEARCHES_JS, [460, -120])
code("TAM SAM SOM", CALC_JS, [460, 120])
link("Run", "Your market")
link("Your market", "Sales Navigator searches")
link("Your market", "TAM SAM SOM")

wf = {"name": "TAM calculator (Sales Navigator counts)", "nodes": nodes, "connections": connections,
      "settings": {"executionOrder": "v1"}, "pinData": {}}
(HERE / "tam-calculator.json").write_text(json.dumps(wf, indent=2) + "\n")
print("wrote n8n/tam-calculator.json")
