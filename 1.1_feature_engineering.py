#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
from flags import parse_args
from utils import read_csv_data, df_to_format,generator_data
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib
import datetime
import collections
import csv
try:
    import _pickle as Pickle
except:
    import cPickle as Pickle
import gc
#指定默认字体
matplotlib.rcParams['font.sans-serif'] = ['SimHei']
matplotlib.rcParams['font.family']='sans-serif'
#解决负号'-'显示为方块的问题
matplotlib.rcParams['axes.unicode_minus'] = False

FLAGS, unparsed = parse_args()


# ##### 定义特征, 特征处理方案
# - 'hour', ===> weeks, hours
# - 'device_ip', ==-> ip段(ip_address) ===> 特征值截断
# - 'device_id',  ===> 特征值截断
# - 'site_id',  'site_domain' ===> 特征联合 ===> 特征值截断
# - 'app_id', 'app_domain' ===> 特征联合 ===> 特征值截断
# - 'site_id', 'app_id', ===> 特征联合 ===> 特征值截断
# - 'C17',  'C14', 'C20',  'device_model' ===> 特征值截断
# 
# 特征提取 xgboost


class FE(object):

    def __init__(self):
        self.train_path = os.path.join(FLAGS.data_dir, FLAGS.train_file)
        self.test_path = os.path.join(FLAGS.data_dir, FLAGS.test_file)
        self.fe_path = os.path.join(FLAGS.output_dir, FLAGS.fe_data_file)
        self.all_data = None
        self.batch_size = 500
        self.is_log = True       
        self.param = FLAGS
        self.less_than_num = 10        # 出现次数少于10次的特征值合并到新特征值 'merged-N' 中
        # 丢弃的特征
        self.drop_features = ['id', 'hour', 'Date']
        # 可以直接one_hot的特征
        self.one_hot_features = ['C1', 'banner_pos', 'site_category','app_category', 'device_type', 'device_conn_type',  'C15', 'C16','C18', 'C19', 'C21']
        # 特征值出现次数
        self.counts = {}
        self.n_sample = 40428967   # 样本数  默认是train.csv样本数
        self.columns = ['id', 'click', 'hour', 'C1', 'banner_pos', 'site_id','site_domain', 'site_category', 'app_id', 'app_domain','app_category', 'device_id', 'device_ip', 'device_model',
       'device_type', 'device_conn_type', 'C14', 'C15', 'C16', 'C17', 'C18', 'C19', 'C20', 'C21']
        

    def run(self):
        self.step_1()       
        self.step_2()        
        self.step_3()
        self.step_4()

    def step_1(self):
        """
        特征工程第1步
        """
        train_data = pd.read_csv(self.train_path, nrows=1e3)
        test_data = pd.read_csv(self.test_path, nrows=1e2)
        test_data['click'] = 0
        # 合并测试样本和测试样本, 统一进行特征工程处理
        self.all_data = pd.concat([train_data, test_data], axis=0, sort=False)

        fe_path01 = self.fe_path.format('01')
        if os.path.exists(fe_path01):
            os.remove(fe_path01)    

        # 处理时间特征 'hour', ===> 7week, 24hour
        self.all_data['Date'] = pd.to_datetime(self.all_data['hour'], format='%y%m%d%H')
        self.all_data['Day'] = self.all_data['Date'].dt.day
        self.all_data['Week'] = self.all_data['Date'].dt.dayofweek
        # self.all_data['Yday'] = self.all_data['Date'].dt.dayofyear
        self.all_data['Hour'] = self.all_data['Date'].dt.hour
        self.all_data.drop(['Date', 'hour'], axis=1, inplace=True)

        # 'device_ip', ==-> ip段(ip_address)
        # self.all_data['Ip_address'] = self.all_data['device_ip'][:4]
        self.all_data['Ip_address'] = self.all_data['device_ip'].apply(lambda ip: ip[:4])

        # 特征联合
        union_value_fn = lambda feature1, feature2: np.add(self.all_data[feature1].astype(str).values, self.all_data[feature2].astype(str).values)
        self.all_data['Site_id_site_domain'] = union_value_fn('site_id',  'site_domain')
        self.all_data['App_id_app_domain'] = union_value_fn('app_id', 'app_domain')
        self.all_data['Site_id_app_id'] = union_value_fn('site_id', 'app_id')

        # 新特征
        self.all_data['web_or_app'] = 0
        self.all_data.ix[self.all_data.app_id.values=='ecad2386', 'web_or_app'] = 1

        # 丢弃不要的特征
        self.all_data = self.all_data.drop(['id'], axis=1)

        # 样本写入csv文件
        # self.all_data.to_csv(fe_path01)
        print('*****************FE step1 progress: 特征工程第1步****************') 

    def step_2(self):
        """
        特征值截断: 合并稀疏特征值 
        特征值数量大于30个, 出现次数小于10个的,合并值为 merged-01 
        """
        less_than_num = 10
        print('-------------'*10)

        features = list(set(self.all_data.columns.values) - set(['C1', 'click','banner_pos', 'site_category', 'app_category', 'device_type', 'device_conn_type','C18']))

        for col in features:
            count_arr = self.all_data[col].value_counts()
            merge_values = [v for v in count_arr.index.values if count_arr[v] < less_than_num and len(count_arr.index.values) > 10]
            if merge_values:
                self.all_data[col] = self.all_data[col].replace(merge_values, '-11' if self.all_data[col].dtype == object else -11)
        print('*****************FE step2 progress: 合并稀疏特征值*****************')        

    
    def step_3(self): 
        """
        one hot function
        skip_cols: list type, all columns of feature not not not to be one_hot_encoder
        """
        # LabelEncoder
        from sklearn.preprocessing import LabelEncoder, OneHotEncoder
        features = list(self.all_data.columns.values)
        features.remove('click')
        print(features)
        self.all_data[features] = self.all_data[features].apply(LabelEncoder().fit_transform)

        # OneHotEncoder
        _fn = lambda col_name: pd.get_dummies(self.all_data[col_name],prefix=col_name)
        self.x_data = pd.concat(map(_fn, features), axis=1)
        
        # self.x_data = OneHotEncoder().fit_transform(self.all_data[features])
        print('*****************FE step3 progress: LabelEncoder +  OneHotEncoder*****************')

    def step_4(self): 
        """
        split dataset, save dataset
        """
        print(self.x_data.shape)
        print(self.all_data.shape)

        self.fianl_data = pd.concat([self.x_data, self.all_data[['click']]], axis=1)
        print(self.fianl_data.shape)
        print(self.fianl_data.head(10))
        self.fianl_data.to_csv(os.path.join(FLAGS.output_dir, 'train_fe.csv'), index_label=False)

if __name__ == '__main__':
    fe = FE()
    fe.run()
