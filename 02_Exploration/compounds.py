import re
from pathlib import Path
import json
import pandas as pd

p = re.compile(r'klima(\w+)')


files = Path().glob(pattern='../data/raw/*')

res = []

for file in files:
    with open(file) as f:
        for line in f:
            obj = json.loads(line)
            if obj['text'] is not None:
                txt = obj['text'].lower()
                if 'klima' in txt:
                    tokens = set(p.findall(txt))
                    for t in tokens:
                        res.append({'file': file, 'compound': t, 'dummy': 1})

df = pd.DataFrame(res)
g1 = df.groupby(['compound']).count()
g2 = df.groupby(['file', 'compound']).count()

g1['dummy'].sort_values().to_csv('../data/compounds.csv')
g2.to_csv('../data/compounds_grouped.csv')
