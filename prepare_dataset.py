# Generate adult dataset

import os
import json
import numpy as np
import pandas as pd
from dataset_utils import CATEGORICAL, CONTINUOUS, ORDINAL, verify


output_dir = 'data'
name = "adult"

def project_table(data, meta):
    values = np.zeros(shape=data.shape, dtype='float32')

    for id_, info in enumerate(meta):
        if info['type'] == CONTINUOUS:
            values[:, id_] = data.iloc[:, id_].values.astype('float32')
        else:
            mapper = dict([(item, id) for id, item in enumerate(info['i2s'])])
            mapped = data.iloc[:, id_].apply(lambda x: mapper[x]).values
            values[:, id_] = mapped
            mapped = data.iloc[:, id_].apply(lambda x: mapper[x]).values
    return values


def main():
    try:
        os.mkdir(output_dir) 
    except:
        pass

    try:
        os.mkdir(temp_dir)
    except:
        pass

    df = pd.read_csv("utils/raw/binary/adult.csv".format(name), dtype='str', delimiter=',', header=None)
    df = pd.DataFrame(df)
    print(df.shape)

    col_type = [
        ('Age', CONTINUOUS),
        ('workclass', CATEGORICAL),
        ('fnlwgt', CONTINUOUS),
        ('education', CATEGORICAL),
        ('education-num', CONTINUOUS),
        ('marital-status', CATEGORICAL),
        ('occupation', CATEGORICAL),
        ('relationship', CATEGORICAL),
        ('race', CATEGORICAL),
        ('sex', CATEGORICAL),
        ('capital-gain', CONTINUOUS),
        ('capital-loss', CONTINUOUS),
        ('hours-per-week', CONTINUOUS),
        ('native-country', CATEGORICAL),
        ('label', CATEGORICAL)
    ]
    print(len(col_type))
    for id_ in range(len(col_type)):
        df = df[df.iloc[:,id_].values != ' ?']
    df=df.replace(' >50K.', ' >50K')
    df=df.replace(' <=50K.', ' <=50K') 
    print(df.shape)
    # print(df.columns)
    meta = []
    for id_, info in enumerate(col_type):
        if info[1] == CONTINUOUS:
            meta.append({
                "name": info[0],
                "type": info[1],
                "min": np.min(df.iloc[:, id_].values.astype('float')),
                "max": np.max(df.iloc[:, id_].values.astype('float'))
            })
        else:
            if info[1] == CATEGORICAL:
                value_count = list(dict(df.iloc[:, id_].value_counts()).items())
                value_count = sorted(value_count, key=lambda x: -x[1])
                mapper = list(map(lambda x: x[0], value_count))
            else:
                mapper = info[2]

            meta.append({
                "name": info[0],
                "type": info[1],
                "size": len(mapper),
                "i2s": mapper
            })

    tdata = project_table(df, meta)

    config = {
                'columns':meta, 
                'problem_type':'binary_classification'
            }

    np.random.seed(0)
    np.random.shuffle(tdata)

    train_ratio = int(tdata.shape[0]*0.2)
    t_train = tdata[:-train_ratio]
    t_test = tdata[-train_ratio:]

    
    with open("{}/{}.json".format(output_dir, name), 'w') as f:
        json.dump(config, f, sort_keys=True, indent=4, separators=(',', ': '))
    np.savez("{}/{}.npz".format(output_dir, name), train=t_train, test=t_test)

    verify("{}/{}.npz".format(output_dir, name),
            "{}/{}.json".format(output_dir, name))

main()
