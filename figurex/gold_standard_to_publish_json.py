"""
Usage:
    script.py -i SOURCE -o DEST

Options:
    -i <file>       gold standard file
    -o <file>       released file
"""
import json
import re
from pathlib import Path

import docopt
import pandas as pd
import tqdm
from PIL import Image


def gold_to_publish(src, dst, drop_nature=True):
    df = pd.read_csv(src, dtype={'insert_time': str})
    if drop_nature:
        df = df[df['label'] != 'nature']

    figures = {}
    for _, row in tqdm.tqdm(df.iterrows(), total=len(df)):
        pmc = row['pmcid']
        figure_url = row['figure url']
        url = f'https://www.ncbi.nlm.nih.gov/pmc/articles/{pmc}/bin/{figure_url}'
        if url not in figures:
            figures[url] = {
                'pmcid': pmc,
                'url': url,
                'insert_time': row['insert_time']
            }
        figure = figures[url]

        subfigure_filename = row['subfigure filename']
        m = re.search(r'(\d+)x(\d+)_(\d+)x(\d+)', subfigure_filename)
        if m:
            if 'box' not in figure:
                figure['box'] = []
            figure['box'].append({
                'xtl': int(m.group(1)),
                'ytl': int(m.group(2)),
                'xbr': int(m.group(3)),
                'ybr': int(m.group(4)),
                'label': row['label']
            })
        else:
            if 'box' not in figure:
                figure['label'] = row['label']

    figures = sorted(figures.values(), key=lambda x: (x['pmcid'], x['url']))
    with open(dst, 'w') as fp:
        json.dump(figures, fp, indent=2)


if __name__ == '__main__':
    args = docopt.docopt(__doc__)
    gold_to_publish(src=Path(args['-i']),
                    dst=Path(args['-o']))

