# Scoring method

Everything is scored by `score.py`, with no model-as-judge, so rerunning it on the same outputs always gives the same numbers.

Each (prompt, test case) pair is run 3 times at temperature 0.7. Scores below are computed per run and averaged, except consistency, which is computed across the 3 runs.

## Correctness (weight 40%)
Compare the output to the gold answer in `cases.json`, field by field. Five fields, 0.2 each:
`category`, `urgency`, `order_id`, `refund_requested`, `amount_mentioned`.
- `order_id`: compared after removing `#` and spaces, case-insensitive.
- `amount_mentioned`: numeric, tolerance 0.01. Both null counts as a match.
- JSON is pulled out leniently (prose or code fences around it are ignored here) so that a formatting slip does not also zero out correctness. If no JSON object can be found at all, correctness is 0.

## Format compliance (weight 20%)
Three checks, 1/3 each, applied to the raw text:
1. The entire output parses as a JSON object (no prose, no code fences).
2. The keys are exactly the five required keys.
3. Values are valid: `category` and `urgency` from the allowed lists, `refund_requested` is a real boolean, `order_id` is a string or null, `amount_mentioned` is a number or null.

## Hallucination (weight 25%)
Binary per run: 1 if nothing was invented, 0 if any of these happen:
- `order_id` is not present in the complaint text
- `order_id` is filled in when the gold answer says there is none (e.g. an invoice number or phone number treated as an order ID)
- `amount_mentioned` is a number that does not appear in the complaint (e.g. a computed difference)

Unparseable output is not counted as a hallucination, since it is already penalised under format.

## Consistency (weight 15%)
Across the 3 runs for one case, take the most common parsed output (exact match on all five fields). Score = share of runs that agree with it: 1.0, 0.67 or 0.33. Unparseable runs count as their own value.

## Composite
`0.40 * correctness + 0.20 * format + 0.25 * hallucination + 0.15 * consistency`

I weighted correctness and hallucination highest because in a support pipeline a wrong or made-up field does more damage than an extra line of prose, which a parser could strip.

## Task definition (same for all three prompts)
Extract five fields from a customer complaint: category, urgency, order_id, refund_requested, amount_mentioned. The gold labels follow these rules, which only the instruction-heavy prompt states explicitly:
- category = the issue the customer wants resolved
- urgency = high only for a safety hazard, 3+ repeated failures, or a threat of legal/regulatory/bank-dispute action
- order_id = only something the customer calls an order number
- amount_mentioned = the amount wrongly charged / to be refunded, as written in the text

This is deliberate: the basic and few-shot prompts have to guess some of these conventions, which is exactly what the benchmark is meant to expose.
