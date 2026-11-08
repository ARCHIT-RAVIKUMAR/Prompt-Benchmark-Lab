# Prompt Benchmark Lab

A small benchmark comparing three prompting strategies on one task: pulling structured fields out of messy customer complaints.

**Task:** given a complaint, return JSON with `category`, `urgency`, `order_id`, `refund_requested`, `amount_mentioned`.

**Strategies**
| Name | File | Idea |
|---|---|---|
| basic | `prompts/basic.txt` | One sentence of instruction, names the keys |
| few-shot | `prompts/fewshot.txt` | Three worked examples, almost no rules |
| instruction-heavy | `prompts/instruction_heavy.txt` | Explicit definitions, tie-breakers, injection warning, null rules |

**Test set:** 10 complaints in `cases.json` (2 easy, 2 medium, 6 hard). Edge cases include a missing order ID, a phone number and invoice ID that look like order IDs, a prompt injection, sarcasm, Hinglish with a rupee amount, a complaint with two issues, and a near-empty complaint.

## Layout
```
cases.json          test cases with gold labels
prompts/            the three prompts ({complaint} is the placeholder)
run_benchmark.py    calls the model: 3 prompts x 10 cases x 3 runs = 90 calls
score.py            deterministic scoring
SCORING.md          how each dimension is scored and why
outputs/            raw model outputs, one file per run
results/            scores.csv and results.md (tables)
ANALYSIS.md         conclusions
```

## Reproduce
```
pip install -r requirements.txt
export GROQ_API_KEY=your_key
python list_models.py                 # pick a model id from this list
export BENCH_MODEL=<model id>
python run_benchmark.py
python score.py
```
Model ids change over time, so check console.groq.com for the current list. `run_meta.json` in `outputs/` records the model and temperature used. The runner skips files that already exist, so you can resume after an interruption.

## Results
See `results/results.md` and `ANALYSIS.md`.
