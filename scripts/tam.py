#!/usr/bin/env python3
"""TAM, SAM and SOM from LinkedIn Sales Navigator account counts. Standard library only.

  python3 scripts/tam.py urls  <market.json>   the Sales Navigator searches to open, one count each
  python3 scripts/tam.py calc  <market.json>   the TAM, SAM and SOM table (Markdown), from the counts
  python3 scripts/tam.py check <market.json>   the double-counting checks only
  python3 scripts/tam.py sample <export.json>  match and email rates of a small Evaboot export of the buyers search

market.json: see examples/software-sales-tool.json and skills/tam-calculator/SKILL.md.
"""
import json
import re
import sys
from urllib.parse import quote

BASE = "https://www.linkedin.com/sales/search/"


def values(ids):
    return ",".join(f"(id:{i},selectionType:INCLUDED)" for i in ids)


def flt(kind, ids):
    return f"(type:{kind},values:List({values(ids)}))"


def url(kind, filters):
    q = "(filters:List(" + ",".join(filters) + "))"
    return BASE + kind + "?query=" + quote(q, safe="(),:")


def account_filters(m, bands, regions, growth=False):
    f = [flt("COMPANY_HEADCOUNT", bands), flt("INDUSTRY", [i["id"] for i in m["industries"]])]
    if regions:
        f.append(flt("REGION", [r["id"] for r in regions]))
    if growth and m.get("som_filter", {}).get("headcount_growth_min"):
        f.append(f"(type:COMPANY_HEADCOUNT_GROWTH,rangeValue:(min:{m['som_filter']['headcount_growth_min']}))")
    return f


def searches(m):
    """One account search per (level, band). Bands never overlap, so their counts add up."""
    bands = [b["id"] for b in m["bands"]]
    out = []
    for b in m["bands"]:
        out.append((f"tam.{b['id']}", f"TAM accounts, {b['label']} employees",
                    url("company", account_filters(m, [b["id"]], m.get("tam_regions")))))
    for b in m["bands"]:
        out.append((f"sam.{b['id']}", f"SAM accounts, {b['label']} employees",
                    url("company", account_filters(m, [b["id"]], m["sam_regions"]))))
    if m.get("som_filter"):
        out.append(("som_accounts", "SOM accounts: SAM + headcount growth",
                    url("company", account_filters(m, bands, m["sam_regions"], growth=True))))
    if m.get("buyer"):
        # People search: REGION is where the person lives, so filter on the company's headquarters instead.
        f = account_filters(m, bands, None)
        f.append(flt("COMPANY_HEADQUARTERS", [r["id"] for r in m["sam_regions"]]))
        f.append(flt("FUNCTION", [m["buyer"]["function"]]))
        if m["buyer"].get("seniority"):
            f.append(flt("SENIORITY_LEVEL", m["buyer"]["seniority"]))
        out.append(("sam_buyers", "People: buyers in SAM accounts (not for revenue)", url("people", f)))
    return out


def num(v):
    """'73K+' -> 73000, '3.5K+' -> 3500, '1,234' -> 1234. Sales Navigator rounds down: these are floors."""
    if isinstance(v, (int, float)):
        return float(v)
    s = str(v).strip().upper().replace(",", "").replace("+", "").replace("RESULTS", "").strip()
    mult = 1
    if s.endswith("K"):
        mult, s = 1_000, s[:-1]
    elif s.endswith("M"):
        mult, s = 1_000_000, s[:-1]
    return float(s) * mult


def check(m):
    issues = []
    ids = [b["id"] for b in m["bands"]]
    if len(ids) != len(set(ids)):
        issues.append("A headcount band appears twice: each company would be counted twice.")
    for key in ("tam_regions", "sam_regions"):
        r = [x["id"] for x in m.get(key) or []]
        if len(r) != len(set(r)):
            issues.append(f"{key}: a region appears twice.")
    c = m.get("counts", {})
    for b in m["bands"]:
        t, s = c.get("tam", {}).get(b["id"]), c.get("sam", {}).get(b["id"])
        if t is not None and s is not None and num(s) > num(t):
            issues.append(f"SAM {b['label']} ({s}) is above TAM ({t}): the SAM search is not inside the TAM search.")
    sam_total = sum(num(v) for v in c.get("sam", {}).values())
    if c.get("som_accounts") and sam_total and num(c["som_accounts"]) > sam_total:
        issues.append("SOM accounts are above SAM accounts: the SOM search must add filters to the SAM search.")
    return issues


def money(x):
    for unit, d in (("B", 1e9), ("M", 1e6), ("K", 1e3)):
        if x >= d:
            return f"${x / d:,.1f}{unit}"
    return f"${x:,.0f}"


def calc(m):
    c = m["counts"]
    rows, tam, sam, tam_n, sam_n = [], 0.0, 0.0, 0.0, 0.0
    for b in m["bands"]:
        t, s = num(c["tam"][b["id"]]), num(c["sam"][b["id"]])
        tam, sam, tam_n, sam_n = tam + t * b["acv"], sam + s * b["acv"], tam_n + t, sam_n + s
        rows.append((b["label"], c["tam"][b["id"]], c["sam"][b["id"]], b["acv"], t * b["acv"], s * b["acv"]))
    blended = sam / sam_n if sam_n else 0
    som_n = num(c["som_accounts"]) if c.get("som_accounts") else sam_n
    share = m.get("som_share", 0.05)
    som = som_n * blended * share
    out = [f"# {m['name']} ({m.get('date', '')})", "",
           "| Band | TAM accounts | SAM accounts | ACV | TAM | SAM |", "|---|---|---|---|---|---|"]
    for label, t, s, acv, tv, sv in rows:
        out.append(f"| {label} | {t} | {s} | ${acv:,} | {money(tv)} | {money(sv)} |")
    out.append(f"| **Total** | {tam_n:,.0f} | {sam_n:,.0f} | | **{money(tam)}** | **{money(sam)}** |")
    out += ["", f"- Blended SAM ACV: {money(blended)} ({money(sam)} / {sam_n:,.0f} accounts)",
            f"- SOM: {som_n:,.0f} in-market accounts x {money(blended)} x {share:.1%} = **{money(som)}** "
            f"(about {som_n * share:,.0f} customers)"]
    if c.get("sam_buyers"):
        out.append(f"- Buyers in SAM accounts: {c['sam_buyers']} people. Use them for outreach capacity, never for revenue.")
        smp = m.get("sample")
        if smp and smp.get("exported"):
            match, safe = smp["matched"] / smp["exported"], smp["safe"] / smp["exported"]
            out.append(f"- Sample export: {smp['matched']}/{smp['exported']} match your filters, {smp['safe']}/{smp['exported']} "
                       f"match with a safe email. Reachable buyers: about {num(c['sam_buyers']) * safe:,.0f}.")
    out.append("- Counts ending in K+ are Sales Navigator floors: the real market is at least this big.")
    issues = check(m)
    out += [""] + ([f"WARNING: {i}" for i in issues] or ["Double-counting checks: OK"])
    return "\n".join(out), {"tam": tam, "sam": sam, "som": som, "tam_accounts": tam_n,
                            "sam_accounts": sam_n, "som_accounts": som_n, "blended_acv": blended}


def sample(path):
    """Evaboot export (get_export result or a list of prospects) -> exported, matched, safe."""
    d = json.load(open(path))
    rows = d.get("result", d).get("prospects", []) if isinstance(d, dict) else d
    matched = [r for r in rows if r.get("Matches Filters") == "YES"]
    safe = [r for r in matched if r.get("Email Status") == "safe"]
    reasons = {}
    for r in rows:
        if r.get("Matches Filters") != "YES":
            k = r.get("No Match Reasons") or "unknown"
            reasons[k] = reasons.get(k, 0) + 1
    return {"exported": len(rows), "matched": len(matched), "safe": len(safe), "no_match_reasons": reasons}


def main():
    if len(sys.argv) != 3 or sys.argv[1] not in ("urls", "calc", "check", "sample"):
        sys.exit(__doc__)
    if sys.argv[1] == "sample":
        print(json.dumps(sample(sys.argv[2]), indent=1))
        return
    m = json.load(open(sys.argv[2]))
    if sys.argv[1] == "urls":
        for key, label, u in searches(m):
            print(f"{key}\t{label}\n{u}\n")
    elif sys.argv[1] == "check":
        issues = check(m)
        print("\n".join(issues) or "OK")
        sys.exit(1 if issues else 0)
    else:
        text, totals = calc(m)
        print(text)
        print("\n" + json.dumps({k: round(v) for k, v in totals.items()}))


if __name__ == "__main__":
    main()
