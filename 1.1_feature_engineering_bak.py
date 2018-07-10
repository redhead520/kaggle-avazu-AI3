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

#指定默认字体
matplotlib.rcParams['font.sans-serif'] = ['SimHei']
matplotlib.rcParams['font.family']='sans-serif'
#解决负号'-'显示为方块的问题
matplotlib.rcParams['axes.unicode_minus'] = False

FLAGS, unparsed = parse_args()

def log(str):
    if is_log:
        print(str)

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
        self.fe_train_path = os.path.join(FLAGS.output_dir, FLAGS.fe_prefix + FLAGS.train_file)
        self.fe_test_path = os.path.join(FLAGS.output_dir,  FLAGS.fe_prefix + FLAGS.test_file)
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
        self.counts_path = os.path.join(FLAGS.output_dir,  FLAGS.fe_prefix + 'counts.bin')
        self.n_sample = 0   # 样本数
        self.columns = ['id', 'click', 'hour', 'C1', 'banner_pos', 'site_id','site_domain', 'site_category', 'app_id', 'app_domain','app_category', 'device_id', 'device_ip', 'device_model',
       'device_type', 'device_conn_type', 'C14', 'C15', 'C16', 'C17', 'C18', 'C19', 'C20', 'C21']
        

    def run(self):
        self.n_sample = 0
        self.counts = {}       
        # self.step_1(False) # test dataset
        # self.step_1(True)  # train dataset
        # self.run_counts('01')

        # self.get_counts('01')
        # self.step_2(False)  #  test dataset
        # self.step_2(True)   #  train dataset
        print('=============>')
        # self.run_counts('02')

        self.get_counts('02')
        self.step_3(False)  #  test dataset
        self.step_3(True)   #  train dataset

    def step_0_generate_data(self, n=10):
        """
        generate train_data,val_data
        split train.csv to 10 dataset, pick 1 for train, 1 for val
        """   
        if utils.sample_pct < 1.0:
            np.random.seed(999)
            r1 = np.random.uniform(0, 1, train_data.shape[0])
            train_data = train_data.ix[r1 < utils.sample_pct, :]     
                    

    def step_1(self, is_train=True):
        """
        特征工程第1步
        """   
        data_path = self.train_path if is_train else self.test_path
        fe_path = self.fe_train_path if is_train else self.fe_test_path
        fe_path01 = fe_path.format('01')        
        if os.path.exists(fe_path01):
            os.remove(fe_path01)
        headers = False     
        with open(fe_path01,'w') as csv_file:  
            csv_writer = csv.writer(csv_file)
            for batch_data in generator_data(data_path, self.batch_size)
                columns = batch_data.columns.values

                # 处理时间特征 'hour', ===> 7week, 24hour 
                batch_data['Date'] = pd.to_datetime(batch_data['hour'], format='%y%m%d%H')  
                batch_data['Day'] = batch_data['Date'].dt.day
                batch_data['Week'] = batch_data['Date'].dt.dayofweek
                # batch_data['Yday'] = batch_data['Date'].dt.dayofyear
                batch_data['Hour'] = batch_data['Date'].dt.hour
                batch_data.drop(['Date','hour'], axis=1,inplace = True)  

                    
                # 'device_ip', ==-> ip段(ip_address)
                batch_data['Ip_address'] = data['device_ip'][:4]
                    
                # 特征联合
                union_value_fn = lambda feature1,feature2:np.add(batch_data[feature1].astype(str).values, batch_data[feature2].astype(str).values)
                batch_data['Site_id_site_domain'] = union_value_fn('site_id',  'site_domain')
                batch_data['App_id_app_domain'] = union_value_fn('app_id', 'app_domain')
                batch_data['Site_id_app_id'] = union_value_fn('site_id', 'app_id')

                # 新特征
                batch_data['web_or_app'] = 0  
                batch_data.ix[batch_data.app_id.values=='ecad2386', 'app_or_web'] = 1
                    
                # 丢弃不要的特征                
                batch_data.drop(self.drop_features, axis=1)

                # 样本写入csv文件
                if not headers:                                       
                    headers = list(batch_data.columns.values)
                    csv_writer.writerow(headers)
                
                csv_writer.writerows(batch_data.values.tolist())
                self.n_sample +=batch_data.shape[0]
                if self.n_sample % 1e5 == 0 and self.is_log:
                    print('*****************FE step1 progress: {} w numbers sample*****************'.format(self.n_sample/1e4)) 
        
        

    def get_counts(self, nick_name='01'):
        self.counts_path = self.counts_path.format(nick_name)
        if os.path.exists(self.counts_path):
            self.counts = Pickle.load(open(self.counts_path,'rb'))  
    
    def save_counts(self):
        if os.path.exists(self.counts_path):
            os.remove(self.counts_path)
        Pickle.dump(self.counts, open(self.counts_path,'wb'), -1)
    
    def run_counts(self, nick_name='01'):
        train_path = self.fe_train_path.format(nick_name)
        test_path = self.fe_test_path.format(nick_name)
        self.counts_path = self.counts_path.format(nick_name)

        counts = self.counts_values(train_path)
        self.counts = self.counts_values(test_path, counts)        
        self.save_counts()
        print('======== save counts:{}========\n {}'.format(nick_name,self.counts_path))

    def counts_values(self, path, counts={}):        
        with open(path,'r') as f:   
            columns = f.readline().strip().split(',')
            for line in f:
                data = zip(columns, line.strip().split(",")) 
                # 计算特征值出现次数
                for k,v in data:
                    if k in counts:                            
                        if v in counts[k]:
                            counts[k][v] +=1
                        else:
                            counts[k][v] =1
                    else:
                        counts[k] = {v: 1}
        return counts
    def counts_sampale_num(self, path=self.train_path):
        count = 0        
        with open(path,'r') as f:   
            columns = f.readline().strip().split(',')
            for line in f:
                count += 1
        return counts  


    def step_2(self, is_train=True):
        """
        特征值截断: 合并稀疏特征值 
        特征值数量大于30个, 出现次数小于10个的,合并值为 merged-01 
        """   
        fe_path = self.fe_train_path if is_train else self.fe_test_path
        fe_path01 = fe_path.format('01') 
        fe_path02 = fe_path.format('02') 
        strat_index = 0
        cols_counts = {k:len(v.keys()) for k,v in self.counts.items()}
        header = False

        with open(fe_path02, 'w') as fe02_f:
            with open(fe_path01, 'r') as fe01_f:
                columns = fe01_f.readline().strip().split(',')
                for line in fe01_f:
                    data = collections.OrderedDict(zip(columns, line.strip().split(",")))    
                    for k, v in data.items():                        
                        if cols_counts[k] > 30 and self.counts[k][v] < 10:
                            data[k] = 'merged-01'

                    strat_index +=1
                    # 样本写入csv文件
                    if not header:
                        fe02_f.write(','.join(data.keys()))                       
                        header = True
                    fe02_f.write('\n')
                    fe02_f.write(','.join(map(str, data.values())))
                    if strat_index % 1e5 == 0 and self.is_log:
                        print('*****************FE step2 progress: {} w numbers {} sample*****************'.format(strat_index/1e4, 'Train' if is_train else 'Test')) 

       

    
    def step_3(self, is_train=True, skip_cols=['click','web_or_app']): 
        """
        one hot function
        skip_cols: list type, all columns of feature not not not to be one_hot_encoder
        """
        # _fn = lambda col_name: pd.get_dummies(df[col_name],prefix=col_name)
        
        fe_path = self.fe_train_path if is_train else self.fe_test_path
        fe_path02 = fe_path.format('02') 
        fe_path03 = fe_path.format('03') 
        strat_index = 0
        cols_counts = {k:len(v.keys()) for k,v in self.counts.items()}
        header = False        
        one_hot_keys = [ label + '_' + value  for label,values in self.counts.items() if label not in skip_cols for value in values.keys()]
        one_hot_default = dict.fromkeys(one_hot_keys, 0) 
        with open(fe_path03, 'w') as fe03_f:            
            with open(fe_path02, 'r') as fe02_f:
                columns = fe02_f.readline().strip().split(',')
                merge_cols = list(set(columns) - set(skip_cols))
                for line in fe02_f:
                    data = collections.OrderedDict(zip(columns, line.strip().split(",")))                      
                    for (k, v) in data.items():                        
                        if k not in skip_cols:
                            one_hot_default[k + '_' + v] = 1
                            del data[k]
                    data.update(one_hot_default)
                    strat_index +=1
                    # 样本写入csv文件
                    if not header:
                        fe_path03.write(','.join(data.keys()))                       
                        header = True
                    fe_path03.write('\n')
                    fe_path03.write(','.join(data.values()))
                    if strat_index % 1e4 == 0 and self.is_log:
                        print('*****************FE step3 progress: {} w numbers sample*****************'.format(strat_index/1e4)) 



if __name__ == '__main__':
    fe = FE()
    # fe.run()
    print(fe.counts_sampale_num())
