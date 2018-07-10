
# coding: utf-8

# In[1]:


# _*_ coding: utf-8 _*_
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import OneHotEncoder
import os
import matplotlib
get_ipython().run_line_magic('matplotlib', 'inline')
matplotlib.rcParams['font.sans-serif'] = ['SimHei']   
matplotlib.rcParams['font.family']='sans-serif' 
matplotlib.rcParams['axes.unicode_minus'] = False 


# 1、读取训练数据集

# In[2]:


train_data_path = r"./data/train.csv"
data = pd.read_csv(train_data_path,nrows=1e5)
data.head()


# In[3]:


##### 定义特征, 特征处理方案
all_columns = data.columns.values
# 丢弃的特征
drop_feature_1 = ['id']
# 可以直接one_hot的特征
one_hot_feature_1 = ['click', 'C1', 'banner_pos', 'site_category','app_category', 'device_type', 'device_conn_type',  'C15', 'C16', 
       'C18', 'C19', 'C21']
# 剩下要单独处理的特征
other_feature = list(set(all_columns) - set(drop_feature_1) - set(one_hot_feature_1) - set(drop_feature_1))


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

# In[4]:


# one hot function
def one_hot(cols,pre_data=data): 
    """
    cols: list type, all columns of feature to be one_hot_encoder
    """
    _fn = lambda col_name: pd.get_dummies(pre_data[col_name],prefix=col_name)
    return pd.concat(map(_fn,cols), axis=1)


# In[5]:


one_hot(one_hot_feature_1).head()


# In[6]:


# 'hour', ===> 7week, 24hour
def preprocessing_date(time_data, time_format='%y%m%d%H'):
    pre_data = pd.DataFrame(pd.to_datetime(time_data, format=time_format),columns=['Date'])
#     pre_data['Year'] = pre_data['Date'].dt.year
#     pre_data['Month'] = pre_data['Date'].dt.month
    pre_data['Day'] = pre_data['Date'].dt.day
    pre_data['Week'] = pre_data['Date'].dt.dayofweek
#     pre_data['Yday'] = pre_data['Date'].dt.dayofyear
    pre_data['Hour'] = pre_data['Date'].dt.hour
    pre_data.drop(['Date'], axis=1,inplace = True)
    return pre_data


# In[7]:


new_hours=preprocessing_date(data['hour'].values)
new_hours.head()


# In[8]:


# new_data 是后面需要特征值截断 的特征
# 'device_ip', ==-> ip段(ip_address)
new_device_ip = pd.DataFrame(data['device_ip'].apply(lambda ip_str: ip_str[:4]).values,columns=['Device_ip'])
# new_data['Device_ip'] = data['device_ip'].apply(lambda ip_str: ip_str[:4])
new_device_ip.head()


# In[9]:


# 特征联合
def union_feature(feature1, feature2):
    new_data = np.add(data[feature1].astype(str).values, data[feature2].astype(str).values)
    new_data = pd.DataFrame(new_data,columns=[feature1 + '_' + feature2])
    return new_data

new_feature1 = union_feature('site_id',  'site_domain')
new_feature2 = union_feature('app_id', 'app_domain')
new_feature3 = union_feature('site_id', 'app_id')
pd.concat([new_feature1, new_feature2, new_feature3], axis=1).head()


# In[10]:


new_feature4 = data[['app_id']]
new_feature4.loc['app_or_web'] = 0
new_feature4.loc[new_feature4.app_id.values=='ecad2386', 'app_or_web'] = 1
new_feature4.drop('app_id',inplace=True, axis=1)
new_feature4.head()


# In[11]:


# 特征值截断: 合并稀少的特征值
original_cols = ['C14', 'app_id', 'C17', 'site_id', 'device_id', 'app_domain', 'site_domain', 'device_model', 'C20']
original_df = pd.concat([new_device_ip,new_feature1,new_feature2,new_feature3,data[original_cols]], axis=1)


# In[12]:


# 
merge_dic = {} # key:稀少的特征, value:需要合并稀少的特征值
less_than_num = 10  # 出现次数少于5的特征值合并到新特征值 'merged-values' 中
for col in original_df.columns.values:
    count_arr = original_df[col].value_counts()       
    merge_values = list(filter(lambda value:count_arr[value] < less_than_num, count_arr.index.values))
#     print(len(merge_values))
#     original_df[original_df[col].isin(merge_values)].apply(lambda d: d[col]='merged-1')
#     original_df[col] = original_df[col].apply(lambda x: 'merged-1' if x in merge_values else x)
    original_df[col] = original_df[col].replace(merge_values,'merged-1')

original_df.head(5)


# 特征处理结果存为文件

# In[ ]:


train.to_csv('02_FE_train.csv', index=False)

