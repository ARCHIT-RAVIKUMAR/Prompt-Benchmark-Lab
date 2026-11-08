# Analysis

Model: `openai/gpt-oss-20b` on Groq, temperature 0.7, 3 runs per case (see `outputs/run_meta.json`). Task: extract five fields from customer complaints. Full tables are in `results/results.md`.

## Overall

| | basic | few-shot | instruction-heavy |
|---|---|---|---|
| correctness | 0.65 | 0.81 | 1.00 |
| format | 0.02 | 0.96 | 0.97 |
| hallucination | 0.90 | 0.93 | 1.00 |
| consistency | 0.47 | 0.87 | 0.90 |
| **composite** | **0.56** | **0.88** | **0.98** |

Instruction-heavy came first on every dimension. The ranking does not depend on the format score. Format is only 20% of the composite, so even a perfect format score would only lift basic to about 0.76, still well behind.

## Format

Basic scored about 0 on format because almost every output was wrapped in a code fence (for example `outputs/basic/c01_run1.txt`). It also made up its own labels, using `"product defect"`, `"Billing"` and `"normal"` where the schema needed `product_defect`, `billing` and `low/medium/high`, and in `outputs/basic/c06_run1.txt` it returned `order_id` as a number. The basic prompt never said "JSON only" or listed the allowed values, so some of this is a consequence of how the prompt was written. Few-shot copied the format of its examples and scored 0.96.

## Hallucination (c07)

Hallucination was only a problem in c07, where the complaint contains a phone number, an invoice number (`INV-2290`) and two euro amounts. All three basic runs put `INV-2290` in `order_id`, and run 1 returned an amount of `18`, which I never wrote in the complaint and is just the difference between the two prices (`outputs/basic/c07_run1.txt`). Few-shot was right once (`order_id: null` in run 1) and wrong twice (`INV-2290` in runs 2 and 3), so it knew the format but not the rule. Instruction-heavy returned `null` all three times. The explicit rule that only something the customer calls an order number counts as an order ID seems to be what fixed this.

## Injection (c06)

Basic and few-shot both followed the instruction hidden in the complaint and returned `billing` / `high` for a broken blender (`outputs/basic/c06_run1.txt`, `outputs/fewshot/c06_run1.txt`). Both scored 0.60 on correctness for that case. Instruction-heavy, which tells the model to treat the complaint as data, got it right. My hallucination metric did not count this as a hallucination, since nothing was invented, so the cost shows up only in correctness.

## Consistency

Basic was the least consistent (0.47). Its answers changed between runs even on the same complaint, for example three different amounts in c07. Few-shot was stable on easy cases but had 0.33 on c07 and 0.67 on c04 and c05. Instruction-heavy was fully consistent on 7 of 10 cases.

## Where instruction-heavy slipped

It never lost points on correctness, but c01, c02 and c08 each had one run that differed. In `outputs/instruction_heavy/c01_run2.txt` the amount came back as the string `"249.99"` instead of the number `249.99`. The content is right, but it breaks the strict format check and counts as a different answer for consistency. c02 and c08 show the same score pattern.

## Limitations

- The instruction-heavy prompt states the same rules my gold labels follow, so part of its lead is expected. What the results show is that explicit rules remove guesswork, not that the prompt is universally better.
- Part of basic's correctness gap comes from label spelling (`"product defect"` vs `product_defect`), not misunderstanding.
- My scorer treats amounts written like `"€120"` as missing, which penalises basic slightly more than the others.
- One model, 10 cases, 3 runs, and gold labels written by me. Cases c04 and c09 involve judgment calls where another annotator might disagree.
