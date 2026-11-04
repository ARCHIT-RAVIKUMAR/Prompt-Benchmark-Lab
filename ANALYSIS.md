# Analysis

> Write this after you run the benchmark. Delete this note when done.
> Suggested things to look at, using `results/results.md` and the files in `outputs/`:
> - Which prompt had the highest composite, and was the gap large or small?
> - Format: did the basic prompt wrap JSON in prose or code fences? How often? Did it change keys or enum values?
> - Hallucination: open c03 and c07 for every prompt. Did anyone invent or reuse an ID?
> - c06 (injection): which prompts followed the injected instruction?
> - c04 and c09 (judgment calls): do the failures look like prompt problems or ambiguity in my gold labels?
> - Consistency: were disagreements between runs concentrated in specific cases?
> - Did few-shot beat instruction-heavy anywhere? Why might that be?
> - Limitations: 10 cases, 3 runs, one model, my own gold labels.
> Quote at least two raw outputs by filename (e.g. `outputs/basic/c03_run2.txt`).
