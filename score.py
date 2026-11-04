"""Score the saved outputs. Deterministic, no model involved.

Usage: python score.py
Writes results/scores.csv and results/results.md
"""
import csv
import json
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).parent
PROMPTS = ["basic", "fewshot", "instruction_heavy"]
KEYS = ["category", "urgency", "order_id", "refund_requested", "amount_mentioned"]
CATEGORIES = {"billing", "delivery", "product_defect", "service", "account_access", "other"}
URGENCIES = {"low", "medium", "high"}
WEIGHTS = {"correctness": 0.40, "format": 0.20, "hallucination": 0.25, "consistency": 0.15}


def norm_id(v):
    return None if v is None else re.sub(r"[#\s]", "", str(v)).upper()


def to_float(v):
    if isinstance(v, bool):
        return None
    try:
        return float(str(v).replace(",", ""))
    except (TypeError, ValueError):
        return None


def lenient_parse(raw):
    """Pull a JSON object out of the text even if the model wrapped it in prose/fences."""
    m = re.search(r"\{.*\}", raw, re.S)
    if not m:
        return None
    try:
        obj = json.loads(m.group(0))
        return obj if isinstance(obj, dict) else None
    except json.JSONDecodeError:
        return None


def score_correctness(obj, gold):
    if obj is None:
        return 0.0
    hits = 0
    hits += obj.get("category") == gold["category"]
    hits += obj.get("urgency") == gold["urgency"]
    hits += norm_id(obj.get("order_id")) == norm_id(gold["order_id"])
    hits += obj.get("refund_requested") is gold["refund_requested"]
    a, g = to_float(obj.get("amount_mentioned")), gold["amount_mentioned"]
    hits += (a is None and g is None) or (a is not None and g is not None and abs(a - g) < 0.01)
    return hits / 5


def score_format(raw):
    """Three checks, 1/3 each: strict JSON only, exact key set, valid enums and types."""
    checks = 0
    try:
        obj = json.loads(raw.strip())
        strict = isinstance(obj, dict)
    except json.JSONDecodeError:
        obj, strict = None, False
    checks += strict
    if strict:
        checks += set(obj.keys()) == set(KEYS)
        types_ok = (
            obj.get("category") in CATEGORIES
            and obj.get("urgency") in URGENCIES
            and isinstance(obj.get("refund_requested"), bool)
            and (obj.get("order_id") is None or isinstance(obj.get("order_id"), str))
            and (obj.get("amount_mentioned") is None
                 or (isinstance(obj.get("amount_mentioned"), (int, float))
                     and not isinstance(obj.get("amount_mentioned"), bool)))
        )
        checks += types_ok
    return checks / 3


def score_hallucination(obj, case):
    """1.0 if nothing was invented, 0.0 otherwise.
    Flags: an order_id that is not in the text, an order_id when the gold has none,
    or an amount that is not written in the text. An unparseable output is not
    counted as a hallucination here (it is already punished under format)."""
    if obj is None:
        return 1.0
    text, gold = case["text"], case["gold"]
    oid = norm_id(obj.get("order_id"))
    if oid is not None:
        if oid not in re.sub(r"[#\s]", "", text.upper()):
            return 0.0
        if gold["order_id"] is None:
            return 0.0
    amt = to_float(obj.get("amount_mentioned"))
    if amt is not None:
        numbers = {float(n) for n in re.findall(r"\d+(?:\.\d+)?", text.replace(",", ""))}
        if not any(abs(amt - n) < 0.01 for n in numbers):
            return 0.0
    return 1.0


def score_consistency(objs):
    keys = [json.dumps(o, sort_keys=True) if o is not None else "UNPARSEABLE" for o in objs]
    return Counter(keys).most_common(1)[0][1] / len(keys)


def main():
    cases = json.loads((ROOT / "cases.json").read_text(encoding="utf-8"))
    rows = []
    for name in PROMPTS:
        for case in cases:
            files = sorted((ROOT / "outputs" / name).glob(f"{case['id']}_run*.txt"))
            if not files:
                raise SystemExit(f"No outputs for {name}/{case['id']}. Run run_benchmark.py first.")
            raws = [f.read_text(encoding="utf-8") for f in files]
            objs = [lenient_parse(r) for r in raws]
            n = len(raws)
            row = {
                "prompt": name,
                "case": case["id"],
                "correctness": sum(score_correctness(o, case["gold"]) for o in objs) / n,
                "format": sum(score_format(r) for r in raws) / n,
                "hallucination": sum(score_hallucination(o, case) for o in objs) / n,
                "consistency": score_consistency(objs),
            }
            row["composite"] = sum(row[k] * w for k, w in WEIGHTS.items())
            rows.append(row)

    out = ROOT / "results"
    out.mkdir(exist_ok=True)
    fields = ["prompt", "case", "correctness", "format", "hallucination", "consistency", "composite"]
    with open(out / "scores.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for r in rows:
            w.writerow({k: (round(v, 3) if isinstance(v, float) else v) for k, v in r.items()})

    def get(p, c, k):
        return next(r[k] for r in rows if r["prompt"] == p and r["case"] == c)

    lines = ["# Results", "", "## Composite score per case (0 to 1)", "",
             "| Case | Difficulty | Edge case | basic | few-shot | instruction-heavy |",
             "|---|---|---|---|---|---|"]
    for c in cases:
        vals = [f"{get(p, c['id'], 'composite'):.2f}" for p in PROMPTS]
        lines.append(f"| {c['id']} | {c['difficulty']} | {c['tag']} | " + " | ".join(vals) + " |")

    lines += ["", "## Average per dimension", "",
              "| Dimension | Weight | basic | few-shot | instruction-heavy |", "|---|---|---|---|---|"]
    for k in list(WEIGHTS) + ["composite"]:
        w = f"{WEIGHTS[k]:.0%}" if k in WEIGHTS else "-"
        avgs = [sum(r[k] for r in rows if r["prompt"] == p) / len(cases) for p in PROMPTS]
        lines.append(f"| {k} | {w} | " + " | ".join(f"{a:.2f}" for a in avgs) + " |")

    for k in ["correctness", "format", "hallucination", "consistency"]:
        lines += ["", f"## {k} per case", "", "| Case | basic | few-shot | instruction-heavy |", "|---|---|---|---|"]
        for c in cases:
            lines.append(f"| {c['id']} | " + " | ".join(f"{get(p, c['id'], k):.2f}" for p in PROMPTS) + " |")

    (out / "results.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines[:lines.index('## correctness per case') - 1]))


if __name__ == "__main__":
    main()
