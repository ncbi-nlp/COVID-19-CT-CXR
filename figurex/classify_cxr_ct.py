"""
Usage:
    script.py [options] -i SOURCE -o DEST -f FIGURE_DIR -m MODEL_FILE -l history

Options:
    -i <file>       Subfigure csv file
    -o <file>       Prediction csv file
    -f <dir>        figure dir
    -m <file>       model path
    -l <file>       history csv file
"""

import os
from pathlib import Path

import docopt
import numpy as np
import pandas as pd
from keras.applications import densenet
from keras.models import load_model
from keras.preprocessing.image import ImageDataGenerator


def detect_normal_cxr_ct(model_pathname, src, dest, image_dir, x_col='filename', history=None, include_history=False):
    if history is not None:
        history_df = pd.read_csv(history)
    else:
        history_df = pd.DataFrame()

    total_df = pd.read_csv(src)
    df = total_df.merge(history_df, how='outer', indicator=True).loc[lambda x: x['_merge'] == 'left_only']
    print('total figures', len(total_df))
    print('history figures', len(history_df))
    print('new figures', len(df))

    df = df.reset_index(drop=True)
    df = df.assign(full_path=df[x_col].apply(lambda x: os.path.join(image_dir, x)))
    datagen = ImageDataGenerator(preprocessing_function=densenet.preprocess_input)
    generator = datagen.flow_from_dataframe(
        dataframe=df,
        target_size=(214, 214),
        x_col='full_path',
        class_mode=None,
        batch_size=32,
        shuffle=False
    )

    print('Load from %s', model_pathname)
    model = load_model(model_pathname)
    y_score = model.predict_generator(generator, verbose=1)

    columns = ['ct', 'cxr', 'nature']
    y_pred = np.argmax(y_score, axis=1)
    predictions = [columns[x] for x in y_pred]
    assert len(predictions) == len(df), '{} vs {}'.format(len(predictions), len(df))

    df = df.drop(['full_path', '_merge'], axis=1)
    df = df.assign(prediction=predictions)
    # print(history_df.columns, df.columns)
    if include_history:
        result = pd.concat([history_df, df], axis=0)
    else:
        result = df
    result.to_csv(dest, index=False)


if __name__ == '__main__':
    args = docopt.docopt(__doc__)
    detect_normal_cxr_ct(src=Path(args['-i']),
                         dest=Path(args['-o']),
                         image_dir=Path(args['-f']),
                         x_col='subfigure filename',
                         history=Path(args['-l']),
                         model_pathname=Path(args['-m']))
