"""Run every test case through every prompt N times and save the raw model output.

Usage:
    export GROQ_API_KEY=...
    export BENCH_MODEL=llama-3.3-70b-versatile    # any model id from console.groq.com
    python run_benchmark.py
"""
import json
import os
import sys
import time
from pathlib import Path

from groq import Groq, RateLimitError, APIConnectionError, InternalServerError

ROOT = Path(__file__).parent
RUNS = 3            # repeats per (prompt, case), needed for the consistency score
TEMPERATURE = 0.7   # same for all prompts so the comparison is fair
MODEL = os.environ.get("BENCH_MODEL")
if not MODEL:
    raise SystemExit("Set BENCH_MODEL first. Run python list_models.py to see valid ids.")
PROMPTS = ["basic", "fewshot", "instruction_heavy"]
PAUSE = 20         # seconds between calls, keeps us under free-tier per-minute limits


def call_model(client, prompt, tries=6):
    for attempt in range(tries):
        try:
            resp = client.chat.completions.create(
                model=MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=TEMPERATURE,
                max_tokens=2000,
            )
            return resp.choices[0].message.content or ""
        except (RateLimitError, APIConnectionError, InternalServerError) as e:  # only transient errors are retried
            wait = 10 * (attempt + 1)
            print(f"  {type(e).__name__}, retrying in {wait}s", file=sys.stderr)
            time.sleep(wait)
    raise RuntimeError("Gave up after repeated API errors; rerun to resume.")


def main():
    client = Groq()  # reads GROQ_API_KEY from the environment
    cases = json.loads((ROOT / "cases.json").read_text(encoding="utf-8"))
    (ROOT / "outputs").mkdir(exist_ok=True)
    meta = {"provider": "groq", "model": MODEL, "temperature": TEMPERATURE, "runs": RUNS}
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
                path.write_text(call_model(client, prompt), encoding="utf-8")
                print(f"{name:18} {case['id']} run{run} done", file=sys.stderr)
                time.sleep(PAUSE)


if __name__ == "__main__":
    main()
