#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
from flags import parse_args
from utils import read_csv_data, df_to_format
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib

#指定默认字体
matplotlib.rcParams['font.sans-serif'] = ['SimHei']
matplotlib.rcParams['font.family']='sans-serif'
#解决负号'-'显示为方块的问题
matplotlib.rcParams['axes.unicode_minus'] = False

FLAGS, unparsed = parse_args()
is_log = True
is_plt = True

test_file = os.path.join(FLAGS.data_dir, FLAGS.test_file)

# train, test = read_csv_data(limited=100000)
# # change data format
# train = df_to_format(train, dtype=np.int64, cols=['click','hour','C1','banner_pos','device_type','device_conn_type','C14','C15','C16','C17','C18','C19','C20','C21'])
# train = df_to_format(train, dtype=np.float64, cols=['id'])
# test = df_to_format(test, dtype=np.int64, cols=['hour','C1','banner_pos','device_type','device_conn_type','C14','C15','C16','C17','C18','C19','C20','C21'])
# test = df_to_format(test, dtype=np.float64, cols=['id'])

test = pd.read_csv(test_file)

test['click'] = 0

def log(str):
    if is_log:
        print(str)

def countplot(vals, max=5, title=None, label=None):
    if is_plt:
        fig = plt.figure()
        sns.countplot(vals)
        plt.title(title)
        plt.xlabel(label)
        plt.show()

def feature_engineering(df):
    """
    hour                int64   ===> add feature: hour1 day_hour  day_hour_prev  day_hour_next
    banner_pos          int64

    site_id             object  ===> change value: 0, 1, 2
    site_domain         object
    site_category       object

    app_id              object  ===> change value: 0,1
    app_domain          object
    app_category        object

    device_id           object
    device_ip           object
    device_model        object
    device_type         int64
    device_conn_type    int64
    :param df:
    :return: df
    """
    # add features
    df['day'] = np.round(df.hour % 10000 / 100)  # 日期 day
    df['hour1'] = np.round(df.hour % 100)        # 时间 hour
    df['day_hour'] = (df.day.values - 21) * 24 + df.hour1.values
    df['day_hour_prev'] = df['day_hour'] - 1
    df['day_hour_next'] = df['day_hour'] + 1

    # app_id
    # log(df.app_id.value_counts())
    # app_id top5
    # ecad2386    2530
    # 9c13b419    414
    # 685d1c4c    333
    # febd1138    225
    # d36838b1    178
    df['app_id_ed'] = 0
    df.loc[df.app_id.values == 'ecad2386', 'app_id_ed'] = 1
    df.drop(['app_id'], axis=1)

    # site_id
    log(df.site_id.value_counts())
    # top 5
    # 85f751fd    2470
    # 1fbe01fe    1154
    # 17d1b03f    189
    # df['site_id_ed'] = 0
    # df.loc[df.site_id.values == '85f751fd', 'site_id_ed'] = 2
    # df.loc[df.site_id.values == '1fbe01fe', 'site_id_ed'] = 1
    # df.drop(['site_id'], axis=1)

    df['app_site_id'] = np.add(df.app_id.values, df.site_id.values)
    # log(df.app_site_id.value_counts()[:50])
    df['sources'] = np.add(df.app_id.values, df.site_id.values, df.device_id.values)
    # log(df.sources.value_counts()[:50])

    return df
# log(test.info())
test = feature_engineering(test)

# log(test.hour.value_counts())
# log(test.info())
