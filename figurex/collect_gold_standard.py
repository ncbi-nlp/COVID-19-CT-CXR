"""
Usage:
    script.py -i SOURCE -o DEST -f FIGURE_DIR -l history

Options:
    -i <file>       Prediction csv file
    -o <file>       Gold standard file
    -f <dir>        figure dir
    -l <file>       history gold standard file
"""

import collections
import os
from pathlib import Path

import docopt
import pandas as pd
import tqdm


def collect_gold_standard(src, dst, gold_dir, previous_gold):
    previous_gold_df = pd.read_csv(previous_gold, dtype=str)
    subfigure_filenames = set(previous_gold_df['subfigure filename'])

    gs = {}
    for label in ['ct', 'cxr']:
        with os.scandir(gold_dir / label) as it:
            for entry in it:
                gs[entry.name] = label

    cnt = collections.Counter()
    df = pd.read_csv(src, dtype=str)
    df = df.drop('prediction', axis=1)

    time = src.name[:src.name.find('.')]
    data = []
    for _, row in tqdm.tqdm(df.iterrows(), total=len(df)):
        subfig = row['subfigure filename']
        if subfig in gs:
            label = gs[subfig]
        else:
            label = 'nature'
            cnt['skip'] += 1

        row['label'] = label
        row['insert_time'] = time

        if subfig in subfigure_filenames:
            cnt['Duplicate'] += 1
        data.append(row)

    df = pd.DataFrame(data)
    df = df.drop_duplicates()
    df = pd.concat([previous_gold_df, df], axis=0)
    df.to_csv(dst, index=False)

    for k, v in cnt.most_common():
        print(k, v)


if __name__ == '__main__':
    args = docopt.docopt(__doc__)
    collect_gold_standard(src=Path(args['-i']),
                          dst=Path(args['-o']),
                          gold_dir=Path(args['-f']),
                          previous_gold=Path(args['-l']))

# if __name__ == '__main__':
#     top = ppathlib.data() / 'covid19/covid'
#     prefix = '05092020.litcovid'
#     gold_dir = top / '05092020.litcovid.subfigures_cxr_ct_gold'
#
#     # top = ppathlib.data() / 'covid19/influenza'
#     # prefix = '04192020.influenza.10000'
#     # gold_dir = top / '04192020.influenza.10000.subfigures_cxr_ct_04212020'
#
#     previous_gold = top / '04202020.litcovid.local_subfigures_gold.csv'
#     src = top / f'{prefix}.local_subfigures_pred.csv'
#     dst = top / f'{prefix}.local_subfigures_gold.csv'
#     collect_gold_standard(src, dst, gold_dir, previous_gold)
