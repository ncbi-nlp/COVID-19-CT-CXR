"""
Usage:
    script.py [options] -i SOURCE -o DEST -f FIGURE_DIR -l history

Options:
    -i <file>       Prediction csv file
    -o <dir>        Output dir
    -f <dir>        figure dir
    -l <file>       history csv file
"""

import collections
import shutil
from pathlib import Path

import docopt
import pandas as pd
import tqdm


def collect_cxr_ct(src, src_image_dir, dst_image_dir, gold_file=None, skip_gold=True):
    df = pd.read_csv(src)
    subdf = df[df['prediction'].isin(('cxr', 'ct'))].reset_index(drop=True)
    # subdf.to_csv(dst, index=None)
    print(len(df), len(subdf))
    cnt = collections.Counter()

    if not dst_image_dir.exists():
        dst_image_dir.mkdir()

    for label in ['ct', 'cxr', 'nature']:
        sub_dst_image_dir = dst_image_dir / label
        if not sub_dst_image_dir.exists():
            sub_dst_image_dir.mkdir()

    gs = {}
    if gold_file is not None:
        gold_df = pd.read_csv(gold_file)
        for i, row in gold_df.iterrows():
            gs[row['subfigure filename']] = row['label']

    for _, row in tqdm.tqdm(df.iterrows(), total=len(df)):
        subfig = row['subfigure filename']
        src_img = src_image_dir / subfig
        if subfig in gs:
            if skip_gold:
                continue
            prediction = gs[subfig]
        else:
            prediction = row['prediction']

        if prediction in ['cxr', 'ct']:
            dst_img = dst_image_dir / prediction / subfig
            if dst_img.exists():
                cnt['skip'] += 1
                continue
            try:
                shutil.copy(src_img, dst_img)
                cnt['copy'] += 1
            except:
                cnt['Cannot found'] += 1
                print('Cannot find', src_img)
                exit(1)

    # # whole figure
    # src_image_dir = top / 'figures'
    # for _, row in tqdm.tqdm(subdf.iterrows()):
    #     src_img = src_image_dir / row['figure filename']
    #     if row['figure filename'] in gs:
    #         prediction = gs[row['figure filename']]
    #     else:
    #         prediction = row['prediction']
    #     dst_img = dst_image_dir / prediction / row['figure filename']
    #     if dst_img.exists():
    #         continue
    #     shutil.copy(src_img, dst_img)

    for k, v in cnt.most_common():
        print(k, ':', v)


if __name__ == '__main__':
    args = docopt.docopt(__doc__)
    collect_cxr_ct(src=Path(args['-i']),
                   dst_image_dir=Path(args['-o']),
                   src_image_dir=Path(args['-f']),
                   gold_file=Path(args['-l']))


