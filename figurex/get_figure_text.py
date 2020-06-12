"""
Usage:
    script.py [options] -i SOURCE -o DEST -b BIOC_DIR

Options:
    -i <file>       Gold standard file
    -o <file>       BioC Xml file
    -b <dir>        bioc dir
"""

import json
import re
from pathlib import Path
from typing import Dict, List

import bioc
import docopt
import pandas as pd
import tqdm


class OneFigure:
    def __init__(self):
        self.pmcid = None
        self.url = None
        self.text = []  # type: List[bioc.BioCPassage]

    def to_dict(self) -> Dict:
        return {
            'pmcid': self.pmcid,
            'url': self.url,
            'text': [passage_to_dict(p) for p in self.text],
        }


def df_to_obj(df) -> List[OneFigure]:
    df = df[df['label'].isin(['ct', 'cxr'])]

    objs = []
    for _, row in tqdm.tqdm(df.iterrows()):
        figure = OneFigure()
        figure.pmcid = row['pmcid']
        figure.url = row['figure url']
        objs.append(figure)

    objs = sorted(objs, key=lambda a: a.pmcid)
    return objs


def get_figure_referred_text(doc: bioc.BioCDocument, figure_id):
    p = re.compile(r'(\d)+$')
    m = p.search(figure_id)
    sentences = []
    if m:
        id = int(m.group())
        s = '[F|f]ig(ure)?.?\\s{}'.format(id)
        fig_pattern = re.compile(s)
        for passage in doc.passages:
            m = fig_pattern.search(passage.text)
            if m:
                sentences.append(passage)
    return sentences


def passage_to_dict(passage: bioc.BioCPassage):
    d = {
        'infons': passage.infons,
        'offset': passage.offset,
        'text': passage.text
    }
    return d


def get_figure_caption(figure: OneFigure, doc: bioc.BioCDocument):
    filename = figure.url[figure.url.rfind('/') + 1:]
    for p in doc.passages:
        if len(p.text) == 0:
            continue
        if 'file' in p.infons and p.infons["file"] == filename:
            figure.text.append(p)
            passages = get_figure_referred_text(doc, p.infons['id'])
            figure.text.extend(passages)
            return


def add_text(objs: List[OneFigure], bioc_dir):
    for obj in objs:
        pmcid = obj.pmcid
        with open(bioc_dir / f'{pmcid}.xml', encoding='utf8') as fp:
            collection = bioc.load(fp)
            for doc in collection.documents:
                get_figure_caption(obj, doc)
    return objs


def get_figure_text(src, dest, bioc_dir):
    df = pd.read_csv(src, dtype=str)
    objs = df_to_obj(df)
    objs = add_text(objs, bioc_dir)
    objs = [o.to_dict() for o in objs]
    with open(dest, 'w', encoding='utf8') as fp:
        json.dump(objs, fp, indent=2)


if __name__ == '__main__':
    args = docopt.docopt(__doc__)
    get_figure_text(src=Path(args['-i']),
                    dest=Path(args['-o']),
                    bioc_dir=Path(args['-b']))

