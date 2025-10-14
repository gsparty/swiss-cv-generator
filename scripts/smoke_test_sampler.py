from swiss_cv.sampler import load_canton_populations, sample_cantons, smoke_test_sample
import json

print("Loaded", len(load_canton_populations()), "cantons.")
print("Sample 10 (seed=123):", sample_cantons(10, seed=123))
dist = smoke_test_sample(1000, seed=123)
top = sorted(dist.items(), key=lambda x:-x[1])[:8]
print("Top 8 sample distribution (percent):")
for k,v in top:
    print(f"  {k}: {v:.1f}%")
