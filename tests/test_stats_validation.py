import json, glob
import numpy as np
import pandas as pd
from pathlib import Path

def load_personas(path='outputs_json'):
    p = Path(path)
    files = list(p.glob('*.json'))
    rows = []
    for f in files[:1000]:
        try:
            rows.append(json.load(open(f,'r',encoding='utf8')))
        except Exception:
            pass
    return pd.DataFrame(rows)

def test_canton_non_empty():
    df = load_personas()
    assert not df.empty, 'No personas found in outputs_json'
    assert 'canton' in df.columns, 'canton not present in persona schema'
    # at least 2 different cantons present
    assert df['canton'].nunique() >= 2

def test_age_experience_correlation():
    df = load_personas()
    # accept either years_experience or experience_years
    if 'years_experience' in df.columns:
        y = pd.to_numeric(df['years_experience'], errors='coerce').dropna()
    elif 'experience_years' in df.columns:
        y = pd.to_numeric(df['experience_years'], errors='coerce').dropna()
    else:
        assert False, 'No experience column detected'

    x = pd.to_numeric(df['age'], errors='coerce').dropna()
    common = pd.concat([x, y], axis=1, join='inner').dropna()
    if len(common) < 10:
        # skip if not enough samples
        return
    xs = common.iloc[:,0].values
    ys = common.iloc[:,1].values
    A = np.vstack([xs, np.ones(len(xs))]).T
    m, c = np.linalg.lstsq(A, ys, rcond=None)[0]
    yhat = m*xs + c
    ss_res = ((ys - yhat)**2).sum()
    ss_tot = ((ys - ys.mean())**2).sum()
    r2 = 1 - ss_res/ss_tot if ss_tot>0 else 0.0
    print('age/experience R2=', r2)
    assert r2 >= 0.6
