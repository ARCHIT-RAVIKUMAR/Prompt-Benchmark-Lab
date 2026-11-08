# Results

## Composite score per case (0 to 1)

| Case | Difficulty | Edge case | basic | few-shot | instruction-heavy |
|---|---|---|---|---|---|
| c01 | easy | clean defect report | 0.59 | 1.00 | 0.93 |
| c02 | easy | clean billing | 0.64 | 0.92 | 0.93 |
| c03 | medium | no order id (hallucination trap) | 0.57 | 0.92 | 1.00 |
| c04 | hard | two issues, pick the one the customer wants resolved | 0.64 | 0.85 | 1.00 |
| c05 | hard | sarcasm + repeated failure | 0.57 | 0.80 | 1.00 |
| c06 | hard | prompt injection inside the complaint | 0.59 | 0.84 | 1.00 |
| c07 | hard | phone number + invoice id, no order id | 0.23 | 0.63 | 1.00 |
| c08 | hard | Hinglish + rupee amount with comma | 0.57 | 0.92 | 0.93 |
| c09 | hard | almost no information | 0.59 | 0.92 | 1.00 |
| c10 | medium | safety issue | 0.59 | 1.00 | 1.00 |

## Average per dimension

| Dimension | Weight | basic | few-shot | instruction-heavy |
|---|---|---|---|---|
| correctness | 40% | 0.65 | 0.81 | 1.00 |
| format | 20% | 0.02 | 0.96 | 0.97 |
| hallucination | 25% | 0.90 | 0.93 | 1.00 |
| consistency | 15% | 0.47 | 0.87 | 0.90 |
| composite | - | 0.56 | 0.88 | 0.98 |

## correctness per case

| Case | basic | few-shot | instruction-heavy |
|---|---|---|---|
| c01 | 0.73 | 1.00 | 1.00 |
| c02 | 0.73 | 0.80 | 1.00 |
| c03 | 0.67 | 0.80 | 1.00 |
| c04 | 0.73 | 0.80 | 1.00 |
| c05 | 0.67 | 0.80 | 1.00 |
| c06 | 0.60 | 0.60 | 1.00 |
| c07 | 0.33 | 0.73 | 1.00 |
| c08 | 0.67 | 0.80 | 1.00 |
| c09 | 0.60 | 0.80 | 1.00 |
| c10 | 0.73 | 1.00 | 1.00 |

## format per case

| Case | basic | few-shot | instruction-heavy |
|---|---|---|---|
| c01 | 0.00 | 1.00 | 0.89 |
| c02 | 0.00 | 1.00 | 0.89 |
| c03 | 0.00 | 1.00 | 1.00 |
| c04 | 0.00 | 0.89 | 1.00 |
| c05 | 0.00 | 0.67 | 1.00 |
| c06 | 0.00 | 1.00 | 1.00 |
| c07 | 0.22 | 1.00 | 1.00 |
| c08 | 0.00 | 1.00 | 0.89 |
| c09 | 0.00 | 1.00 | 1.00 |
| c10 | 0.00 | 1.00 | 1.00 |

## hallucination per case

| Case | basic | few-shot | instruction-heavy |
|---|---|---|---|
| c01 | 1.00 | 1.00 | 1.00 |
| c02 | 1.00 | 1.00 | 1.00 |
| c03 | 1.00 | 1.00 | 1.00 |
| c04 | 1.00 | 1.00 | 1.00 |
| c05 | 1.00 | 1.00 | 1.00 |
| c06 | 1.00 | 1.00 | 1.00 |
| c07 | 0.00 | 0.33 | 1.00 |
| c08 | 1.00 | 1.00 | 1.00 |
| c09 | 1.00 | 1.00 | 1.00 |
| c10 | 1.00 | 1.00 | 1.00 |

## consistency per case

| Case | basic | few-shot | instruction-heavy |
|---|---|---|---|
| c01 | 0.33 | 1.00 | 0.67 |
| c02 | 0.67 | 1.00 | 0.67 |
| c03 | 0.33 | 1.00 | 1.00 |
| c04 | 0.67 | 0.67 | 1.00 |
| c05 | 0.33 | 0.67 | 1.00 |
| c06 | 0.67 | 1.00 | 1.00 |
| c07 | 0.33 | 0.33 | 1.00 |
| c08 | 0.33 | 1.00 | 0.67 |
| c09 | 0.67 | 1.00 | 1.00 |
| c10 | 0.33 | 1.00 | 1.00 |
