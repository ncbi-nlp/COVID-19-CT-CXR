"""
Usage:
    script.py [options] -i SOURCE -o DEST -f FIGURE_DIR -s SUBFIGURE_DIR -m MODEL_FILE

Options:
    -i <file>       Figure csv file
    -o <file>       Subfigure csv file
    -f <dir>        figure dir
    -s <dir>        subfigure dir
    -m <file>       model path
"""

import collections
import copy
import json
import shutil
from pathlib import Path

import docopt
import pandas as pd
import tensorflow as tf
import tqdm
from PIL import Image

from figurex.figure_separator import FigureSeparator
from figurex.utils import is_file_empty


def split_figure(src, subfigures, dest_dir, min_width=214, min_height=214):
    filenames = []

    if len(subfigures) > 1:
        im = Image.open(src)
        for subfigure in subfigures:
            if subfigure['w'] < min_width or subfigure['h'] < min_height:
                continue
            left = subfigure['x']
            top = subfigure['y']
            right = left + subfigure['w']
            bottom = top + subfigure['h']
            dst = dest_dir / f'{src.stem}_{left}x{top}_{right}x{bottom}{src.suffix}'
            if not dst.exists():
                subim = im.crop((left, top, right, bottom))
                subim.save(dst)
            filenames.append(dst)

    return filenames


def split_figure_f(src, dest, src_image_dir, dest_image_dir, dest_json_dir, model_pathname, batch_size=64):
    figure_df = pd.read_csv(src)
    data = []
    cnt = collections.Counter()

    tf.compat.v1.disable_eager_execution()
    separator = FigureSeparator(str(model_pathname))

    with tf.compat.v1.Session(graph=separator.graph) as sess:
        needs_to_split = []

        def split_and_save():
            results = separator.extract_batch(sess, needs_to_split)
            assert len(results) == len(needs_to_split)
            for src, result in zip(needs_to_split, results):
                subfigures = result['sub_figures']
                json_dst = dest_json_dir / f'{src.stem}.json'
                with open(json_dst, 'w') as fp:
                    json.dump(subfigures, fp)

        for filename in tqdm.tqdm(figure_df['figure filename'], total=len(figure_df), desc='Check subfigures'):
            src = src_image_dir / filename
            if is_file_empty(src):
                cnt['empty figure'] += 1
                continue
            json_dst = dest_json_dir / f'{src.stem}.json'
            if not json_dst.exists():
                needs_to_split.append(src)

            if len(needs_to_split) >= batch_size:
                split_and_save()
                needs_to_split = []
        if len(needs_to_split) > 0:
            split_and_save()

    for _, row in tqdm.tqdm(figure_df.iterrows(), total=len(figure_df), desc='Write sub figures'):
        src = src_image_dir / row['figure filename']
        json_dst = dest_json_dir / f'{src.stem}.json'
        if not json_dst.exists():
            continue

        with open(json_dst) as fp:
            subfigures = json.load(fp)

        pathnames = split_figure(src, subfigures, dest_image_dir, 214, 214)
        # subfigure
        for pathname in pathnames:
            x = copy.deepcopy(row)
            x['subfigure filename'] = pathname.name
            cnt['subfig'] += len(pathnames)
            cnt['figure'] += 1
            data.append(x)

        # whole figure
        pathname = dest_image_dir / src.name
        if not pathname.exists():
            shutil.copy(src, pathname)
        x = copy.deepcopy(row)
        x['subfigure filename'] = pathname.name
        cnt['figure'] += 1
        data.append(x)

    df = pd.DataFrame(data)
    df.to_csv(dest, index=False)

    for k, v in cnt.most_common():
        print(k, ':', v)


if __name__ == '__main__':
    args = docopt.docopt(__doc__)
    split_figure_f(src=Path(args['-i']),
                   dest=Path(args['-o']),
                   src_image_dir=Path(args['-f']),
                   dest_image_dir=Path(args['-f']),
                   dest_json_dir=Path(args['-s']),
                   model_pathname=Path(args['-m']))

