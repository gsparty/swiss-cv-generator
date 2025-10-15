from collections import Counter
from swisscv.generators.sampler import sample_persona_seeded
c = Counter()
N = 500
for i in range(N):
    p = sample_persona_seeded(seed=10000+i)
    c[p.canton] += 1
print("Top canton counts from", N, "samples:")
print(c.most_common(10))
