import re
from pathlib import Path
import json
import pandas as pd

p = re.compile(r'klima(\w+)')
REGEX = re.compile(r'articles_(.+)\.jsonl')

files = Path().glob(pattern='../data/raw/*')

res = []

for file in files:
    fname = str(file)
    print(fname)
    ministry = REGEX.findall(fname)[0].upper()
    with open(file) as f:
        for li, line in enumerate(f):
            obj = json.loads(line)
            if obj['text'] is not None:
                txt = obj['text'].lower()
                if 'klima' in txt:
                    tokens = set(p.findall(txt))
                    for t in tokens:
                        res.append({'ministry': ministry, 'compound': t, 'dummy': 1})

df = pd.DataFrame(res)
g1 = df.groupby(['compound']).count()
g2 = df.groupby(['ministry', 'compound']).count()

g1['dummy'].sort_values().to_csv('../data/compounds.csv')
g2.sort_values(['ministry', 'dummy']).to_csv('../data/compounds_grouped.csv')
