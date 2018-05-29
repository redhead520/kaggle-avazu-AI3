# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
import scipy as sc
import scipy.sparse as sp
from sklearn.utils import check_random_state 
import pylab 
import sys
import time
# sys.path.append('/home/zzhang/Downloads/xgboost/wrapper')
import xgboost as xgb
from joblib import dump, load, Parallel, delayed
import utils
from utils import *


raw_data_path = utils.raw_data_path
tmp_data_path = utils.tmp_data_path


# train_data = pd.read_csv(raw_data_path + "train.csv")
test_data = pd.read_csv(raw_data_path + "test.csv")
train_data = test_data.copy()

# 从训练样本中随机抽取 utils.sample_pct 的样本来训练, 1.0 表示全部,
if utils.sample_pct < 1.0:
    np.random.seed(999)
    r1 = np.random.uniform(0, 1, train_data.shape[0])
    train_data = train_data.ix[r1 < utils.sample_pct, :]
    print("testing with small sample of training data, ", train_data.shape)

# 测试样本比训练样本少了label属性
test_data['click'] = 0
# 合并测试样本和测试样本, 统一进行特征工程处理
all_data = pd.concat([train_data, test_data])
print("finished loading raw data, ", all_data.shape)

print("to add some basic features ...")
# 将hour特征转成hour1, day_hour, day_hour_prev, day_hour_next特征
all_data['day']=np.round(all_data.hour % 10000 / 100)
all_data['hour1'] = np.round(all_data.hour % 100)
all_data['day_hour'] = (all_data.day.values - 21) * 24 + all_data.hour1.values
all_data['day_hour_prev'] = all_data['day_hour'] - 1
all_data['day_hour_next'] = all_data['day_hour'] + 1

all_data['app_or_web'] = 0
all_data.ix[all_data.app_id.values=='ecad2386', 'app_or_web'] = 1

copy_data = all_data

copy_data['app_site_id'] = np.add(copy_data.app_id.values, copy_data.site_id.values)

print("to encode categorical features using mean responses from earlier days -- univariate")
sys.stdout.flush()

calc_exptv(copy_data,  ['app_or_web'])

exptv_vn_list = ['app_site_id', 'as_domain', 'C14','C17', 'C21', 'device_model', 'device_ip', 'device_id', 'dev_ip_aw', 
                'app_site_model', 'site_model','app_model', 'dev_id_ip', 'C14_aw', 'C17_aw', 'C21_aw']

calc_exptv(copy_data, exptv_vn_list)

calc_exptv(copy_data, ['app_site_id'], add_count=True)


print("to encode categorical features using mean responses from earlier days -- multivariate")
vns = ['app_or_web',  'device_ip', 'app_site_id', 'device_model', 'app_site_model', 'C1', 'C14', 'C17', 'C21',
                        'device_type', 'device_conn_type','app_site_model_aw', 'dev_ip_app_site']
dftv = copy_data.ix[np.logical_and(copy_data.day.values >= 21, copy_data.day.values < 32), ['click', 'day', 'id'] + vns].copy()

dftv['app_site_model'] = np.add(dftv.device_model.values, dftv.app_site_id.values)
dftv['app_site_model_aw'] = np.add(dftv.app_site_model.values, dftv.app_or_web.astype('string').values)
dftv['dev_ip_app_site'] = np.add(dftv.device_ip.values, dftv.app_site_id.values)
for vn in vns:
    dftv[vn] = dftv[vn].astype('category')
    print(vn)

n_ks = {'app_or_web': 100, 'app_site_id': 100, 'device_ip': 10, 'C14': 50, 'app_site_model': 50, 'device_model': 100, 'device_id': 50,
        'C17': 100, 'C21': 100, 'C1': 100, 'device_type': 100, 'device_conn_type': 100, 'banner_pos': 100,
        'app_site_model_aw': 100, 'dev_ip_app_site': 10 , 'device_model': 500}

exp2_dict = {}
for vn in vns:
    exp2_dict[vn] = np.zeros(dftv.shape[0])

days_npa = dftv.day.values
    
for day_v in range(22, 32):
    df1 = dftv.ix[np.logical_and(dftv.day.values < day_v, dftv.day.values < 31), :].copy()
    df2 = dftv.ix[dftv.day.values == day_v, :]
    print("Validation day:", day_v, ", train data shape:", df1.shape, ", validation data shape:", df2.shape)
    pred_prev = df1.click.values.mean() * np.ones(df1.shape[0])
    for vn in vns:
        if 'exp2_'+vn in df1.columns:
            df1.drop('exp2_'+vn, inplace=True, axis=1)
    for i in range(3):
        for vn in vns:
            p1 = calcLeaveOneOut2(df1, vn, 'click', n_ks[vn], 0, 0.25, mean0=pred_prev)
            pred = pred_prev * p1
            print(day_v, i, vn, "change = ", ((pred - pred_prev)**2).mean())
            pred_prev = pred    
            
        pred1 = df1.click.values.mean()
        for vn in vns:
            print("="*20, "merge", day_v, vn)
            diff1 = mergeLeaveOneOut2(df1, df2, vn)
            pred1 *= diff1
            exp2_dict[vn][days_npa == day_v] = diff1
        
        pred1 *= df1.click.values.mean() / pred1.mean()
        print("logloss = ", logloss(pred1, df2.click.values))
        #print my_lift(pred1, None, df2.click.values, None, 20, fig_size=(10, 5))
        #plt.show()

for vn in vns:
    copy_data['exp2_'+vn] = exp2_dict[vn]


print("to count prev/current/next hour by ip ...")
cntDualKey(copy_data, 'device_ip', None, 'day_hour', 'day_hour_prev', fill_na=0)
cntDualKey(copy_data, 'device_ip', None, 'day_hour', 'day_hour', fill_na=0)
cntDualKey(copy_data, 'device_ip', None, 'day_hour', 'day_hour_next', fill_na=0)

print("to create day diffs")
copy_data['pday'] = copy_data.day - 1
calcDualKey(copy_data, 'device_ip', None, 'day', 'pday', 'click', 10, None, True, True)
copy_data['cnt_diff_device_ip_day_pday'] = copy_data.cnt_device_ip_day.values  - copy_data.cnt_device_ip_pday.values
copy_data['hour1_web'] = copy_data.hour1.values
copy_data.ix[copy_data.app_or_web.values==0, 'hour1_web'] = -1
copy_data['app_cnt_by_dev_ip'] = my_grp_cnt(copy_data.device_ip.values.astype('string'), copy_data.app_id.values.astype('string'))


copy_data['hour1'] = np.round(copy_data.hour.values % 100)
copy_data['cnt_diff_device_ip_day_pday'] = copy_data.cnt_device_ip_day.values  - copy_data.cnt_device_ip_pday.values

copy_data['rank_dev_ip'] = my_grp_idx(copy_data.device_ip.values.astype('string'), copy_data.id.values.astype('string'))
copy_data['rank_day_dev_ip'] = my_grp_idx(np.add(copy_data.device_ip.values, copy_data.day.astype('string').values).astype('string'), copy_data.id.values.astype('string'))
copy_data['rank_app_dev_ip'] = my_grp_idx(np.add(copy_data.device_ip.values, copy_data.app_id.values).astype('string'), copy_data.id.values.astype('string'))


copy_data['cnt_dev_ip'] = get_agg(copy_data.device_ip.values, copy_data.id, np.size)
copy_data['cnt_dev_id'] = get_agg(copy_data.device_id.values, copy_data.id, np.size)

copy_data['dev_id_cnt2'] = np.minimum(copy_data.cnt_dev_id.astype('int32').values, 300)
copy_data['dev_ip_cnt2'] = np.minimum(copy_data.cnt_dev_ip.astype('int32').values, 300)

copy_data['dev_id2plus'] = copy_data.device_id.values
copy_data.ix[copy_data.cnt_dev_id.values == 1, 'dev_id2plus'] = '___only1'
copy_data['dev_ip2plus'] = copy_data.device_ip.values
copy_data.ix[copy_data.cnt_dev_ip.values == 1, 'dev_ip2plus'] = '___only1'

copy_data['diff_cnt_dev_ip_hour_phour_aw2_prev'] = (copy_data.cnt_device_ip_day_hour.values - copy_data.cnt_device_ip_day_hour_prev.values) * ((copy_data.app_or_web * 2 - 1)) 
copy_data['diff_cnt_dev_ip_hour_phour_aw2_next'] = (copy_data.cnt_device_ip_day_hour.values - copy_data.cnt_device_ip_day_hour_next.values) * ((copy_data.app_or_web * 2 - 1)) 


print("to save copy_data ...")

dump(copy_data, tmp_data_path + 'copy_data.joblib_dat')


print("to generate copy_datatv_mx .. ")
app_or_web = None
_start_day = 22
list_param = ['C1', 'C14', 'C15', 'C16', 'C17', 'C18', 'C19', 'C20', 'C21', 'banner_pos', 'device_type', 'device_conn_type']
feature_list_dict = {}

feature_list_name = 'tvexp3'
feature_list_dict[feature_list_name] = list_param + \
                            ['exptv_' + vn for vn in ['app_site_id', 'as_domain', 
                             'C14','C17', 'C21', 'device_model', 'device_ip', 'device_id', 'dev_ip_aw', 
                             'dev_id_ip', 'C14_aw', 'C17_aw', 'C21_aw']] + \
                            ['cnt_diff_device_ip_day_pday', 
                             'app_cnt_by_dev_ip', 'cnt_device_ip_day_hour', 'app_or_web',
                             'rank_dev_ip', 'rank_day_dev_ip', 'rank_app_dev_ip',
                             'diff_cnt_dev_ip_hour_phour_aw2_prev', 'diff_cnt_dev_ip_hour_phour_aw2_next',
                             'exp2_device_ip', 'exp2_app_site_id', 'exp2_device_model', 'exp2_app_site_model',
                             'exp2_app_site_model_aw', 'exp2_dev_ip_app_site',
                             'cnt_dev_ip', 'cnt_dev_id', 'hour1_web']

filter_tv = np.logical_and(copy_data.day.values >= _start_day, copy_data.day.values < 31)
filter_t1 = np.logical_and(copy_data.day.values < 30, filter_tv)
filter_v1 = np.logical_and(~filter_t1, filter_tv)    
    
print(filter_tv.sum())


for vn in feature_list_dict[feature_list_name] :
    if vn not in copy_data.columns:
        print("="*60 + vn)
        
yv = copy_data.click.values[filter_v1]

copy_datatv_mx = copy_data.as_matrix(feature_list_dict[feature_list_name])

print(copy_datatv_mx.shape)


print("to save copy_datatv_mx ...")

copy_datatv_mx_save = {}
copy_datatv_mx_save['copy_datatv_mx'] = copy_datatv_mx
copy_datatv_mx_save['click'] = copy_data.click.values
copy_datatv_mx_save['day'] = copy_data.day.values
copy_datatv_mx_save['site_id'] = copy_data.site_id.values
dump(copy_datatv_mx_save, tmp_data_path + 'copy_datatv_mx.joblib_dat')



