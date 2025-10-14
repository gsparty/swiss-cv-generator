import json, glob, os, math
import numpy as np
import pandas as pd
from pathlib import Path
files = list(Path('outputs_json').glob('*.json'))
if not files:
    print('No JSON persona files in outputs_json (run generation first).'); raise SystemExit(1)
rows = []
for f in files:
    try:
        d = json.load(open(f,'r',encoding='utf8'))
        rows.append(d)
    except Exception as e:
        print('Failed reading', f, e)
df = pd.DataFrame(rows)
print('Loaded', len(df), 'personas')
# Canton frequency
if 'canton' in df.columns:
    freqs = df['canton'].value_counts(normalize=True).sort_index()
    print('\\nCanton relative frequencies (top 20):')
    print(freqs.head(20).to_string())
else:
    print('No canton column in persona JSONs')

# Age vs experience
if 'age' in df.columns and 'experience_years' in df.columns:
    x = df['age'].dropna().astype(float)
    y = df['experience_years'].dropna().astype(float)
    # linear regression (slope, intercept) and R^2
    A = np.vstack([x, np.ones(len(x))]).T
    m, c = np.linalg.lstsq(A, y, rcond=None)[0]
    yhat = m*x + c
    ss_res = np.sum((y - yhat)**2)
    ss_tot = np.sum((y - np.mean(y))**2)
    r2 = 1 - ss_res/ss_tot if ss_tot>0 else float('nan')
    print(f'Linear fit: experience = {m:.3f}*age + {c:.3f}; R^2 = {r2:.4f}')
else:
    print('age or experience_years not found in persona JSONs; columns:', df.columns.tolist())

# Save summary
summary = {'n': len(df), 'canton_freq': freqs.to_dict() if 'freqs' in globals() else {}, 'r2': float(r2) if 'r2' in globals() else None}
open('debug/stats_summary.json','w',encoding='utf8').write(json.dumps(summary,ensure_ascii=False,indent=2))
print('\\nWrote debug/stats_summary.json')
