import re
from pathlib import Path
import json
import pandas as pd

files = Path().glob(pattern='../data/raw/*')
OUTPUT_DIR = Path('../data/texts')
REGEX = re.compile(r'articles_(.+)\.jsonl')

sstrs = ['klima', 'klimawandel', 'klimaschutz']

log = []

for file in files:
    fname = str(file)
    ministry = REGEX.findall(fname)[0].upper()
    with open(file) as f:
        (OUTPUT_DIR / ministry).mkdir(exist_ok=True, parents=True)
        for li, line in enumerate(f):
            obj = json.loads(line)
            out_file = OUTPUT_DIR / ministry / f'{li:04}.txt'
            log.append({
                'ministry': ministry,
                'li': li,
                'date': obj['date'],
                'title': obj['title'],
                'file': str(out_file),
                'src': fname,
                **{
                    f'contains_{ss}': 'x' if ss in (obj.get('text') or '').lower()
                                             or ss in (obj.get('teaser') or '').lower()
                                             or ss in (obj.get('title') or '').lower() else ''
                    for ss in sstrs
                }
            })

            with open(out_file, 'w') as fout:
                fout.write((obj.get('link') or '[link missing]') + '\n')
                fout.write((obj.get('descriptor') or '[descriptor missing]') + '\n')
                fout.write(', '.join((obj.get('tags') or ['[tags missing]'])) + '\n')
                fout.write((obj.get('date') or '[date missing]') + '\n')
                fout.write((obj.get('title') or '[title missing]') + '\n')
                fout.write((obj.get('teaser') or '[teaser missing]') + '\n')
                fout.write('----------------\n')
                fout.write((obj.get('text') or '[text missing]'))

df = pd.DataFrame(log)
df.to_excel(OUTPUT_DIR / 'pressemeldungen.xlsx')
