from pathlib import Path
import json
import pandas as pd

files = Path().glob(pattern='../data/raw/*')
sstrs = ['klima', 'klimawandel', 'klimaschutz']
res = {}
for file in files:
    res[file] = {s: 0 for s in sstrs}
    res[file]['all'] = 0
    with open(file) as f:
        for line in f:
            obj = json.loads(line)
            if obj['text'] is not None:
                res[file]['all'] += 1
                txt = obj['text'].lower()
                for s in sstrs:
                    if s in txt:
                        res[file][s] += 1

df = pd.DataFrame(res).transpose()
df.to_csv('../data/counts.csv')
