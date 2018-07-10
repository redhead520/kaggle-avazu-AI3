#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
from flags import parse_args
import pandas as pd
import numpy as np
import gc

FLAGS, unparsed = parse_args()

train_file = os.path.join(FLAGS.data_dir, FLAGS.train_file)
test_file = os.path.join(FLAGS.data_dir, FLAGS.test_file)
def csv2df(file, limited=0):
    with open(file, 'r') as f:
        columns = f.readline().strip().split(',')
        strat_index = 0
        data = []
        for line in f:
            strat_index += 1
            data.append(line.strip().split(","))
            if limited and strat_index >= limited:
                break
        return pd.DataFrame(data, columns=columns)


def generator_data(file_path=train_file, batch_size=0):    
    batch_size = batch_size if batch_size else FLAGS.batch_size
    with open(file_path, 'r') as f:
        columns = f.readline().strip().split(',')
        strat_index = 0
        data = []
        for line in f:
            if not line:
                break
            strat_index += 1
            data.append(line.strip().split(","))
            if strat_index % 1e5 == 0:
                gc.collect() 
            if strat_index % batch_size == 0:
                yield pd.DataFrame(data, columns=columns)
                data=[]
        if data:
            yield pd.DataFrame(data, columns=columns)



def read_csv_data(test=True, limited=0):
    if not limited:
        train_data = pd.read_csv(train_file)
        columns = train_data.colums()
        if test:
            test_data = pd.read_csv(test_file)
            return train_data, test_data, columns
        return train_data, columns
    else:
        train = csv2df(train_file, limited)
        if test:
            test = csv2df(test_file, limited)
            return train, test
        return train

def df_to_format(df, dtype, cols=None):
    for col in cols:
        df[col] = np.asarray(df[col], dtype=dtype)
    return df
