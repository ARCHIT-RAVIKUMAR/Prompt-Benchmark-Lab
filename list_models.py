"""Print the model ids your Groq key can use. Pick one and set BENCH_MODEL to it."""
from groq import Groq

for m in sorted(Groq().models.list().data, key=lambda m: m.id):
    print(m.id)
