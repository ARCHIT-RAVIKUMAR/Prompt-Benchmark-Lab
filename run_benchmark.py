"""Run every test case through every prompt N times and save the raw model output.

Usage:
    export ANTHROPIC_API_KEY=...
    export BENCH_MODEL=claude-sonnet-5-5     # any model you want to test
    python run_benchmark.py
"""
import json
import os
import sys
from pathlib import Path

import anthropic

ROOT = Path(__file__).parent
RUNS = 3            # repeats per (prompt, case), needed for the consistency score
TEMPERATURE = 0.7   # same for all prompts so the comparison is fair
MODEL = os.environ.get("BENCH_MODEL", "claude-sonnet-5-5")
PROMPTS = ["basic", "fewshot", "instruction_heavy"]


def main():
    client = anthropic.Anthropic()
    cases = json.loads((ROOT / "cases.json").read_text(encoding="utf-8"))
    meta = {"model": MODEL, "temperature": TEMPERATURE, "runs": RUNS}
    (ROOT / "outputs").mkdir(exist_ok=True)
    (ROOT / "outputs" / "run_meta.json").write_text(json.dumps(meta, indent=2))

    for name in PROMPTS:
        template = (ROOT / "prompts" / f"{name}.txt").read_text(encoding="utf-8")
        out_dir = ROOT / "outputs" / name
        out_dir.mkdir(parents=True, exist_ok=True)
        for case in cases:
            # str.replace instead of .format because the prompts contain literal braces
            prompt = template.replace("{complaint}", case["text"])
            for run in range(1, RUNS + 1):
                path = out_dir / f"{case['id']}_run{run}.txt"
                if path.exists():
                    continue  # lets you resume after an interruption
                resp = client.messages.create(
                    model=MODEL,
                    max_tokens=300,
                    temperature=TEMPERATURE,
                    messages=[{"role": "user", "content": prompt}],
                )
                path.write_text(resp.content[0].text, encoding="utf-8")
                print(f"{name:18} {case['id']} run{run} done", file=sys.stderr)


if __name__ == "__main__":
    main()
