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
import datetime
import collections
try:
    import _pickle as Pickle
except:
    import cPickle as Pickle

from sklearn.metrics import log_loss # 评价指标

#指定默认字体
matplotlib.rcParams['font.sans-serif'] = ['SimHei']
matplotlib.rcParams['font.family']='sans-serif'
#解决负号'-'显示为方块的问题
matplotlib.rcParams['axes.unicode_minus'] = False

FLAGS, unparsed = parse_args()

def log(str):
    if is_log:
        print(str)


class ML(object):
	def __init__(self):
		pass

	def ridge_cv(self):
		from sklearn.linear_model import RidgeCV
		# 设置超参数（正则参数）范围
		alphas = [0.001,0.01,0.1,1,10,100]

		# 生成一个RidgeCV实例
		ridge = RidgeCV(alphas=alphas, store_cv_values=True)              # 默认配置初始化 
		ridge.fit(X_train, y_train)             # 训练模型参数

		y_train_pred_ridge = ridge.predict(X_train)  # 预测 训练 数据
		y_test_pred_ridge = ridge.predict(X_test)    # 预测 测试 数据

		# 模型评估
		print('The r2 score of RidgeCV on test is: ', r2_score(y_test, y_test_pred_ridge))
		print('The r2 score of RidgeCV on train is: ', r2_score(y_train, y_train_pred_ridge)) 

		# 查看各特征的权重系数
		columns = ['temp','hum','windspeed','instant'] 
		fs = pd.DataFrame({'columns':list(columns), 'coef':list(ridge.coef_.T)[:4]})
		fs.sort_values(by=['coef'], ascending=False)

		#　找出最佳参数
		mse_mean = np.mean(ridge.cv_values_, axis=0)
		plt.plot(np.log10(alphas), mse_mean.reshape(len(alphas),1))
		plt.plot(np.log10(ridge.alpha_)*np.ones(len(alphas)),list(mse_mean[0]))
		plt.xlabel('log(alpha)')
		plt.ylabel('mse')
		plt.show()
		print('alpha is: ', ridge.alpha_)

    def lasso_cv(self):
    	from sklearn.linear_model import LassoCV
		lasso = LassoCV()  # alphas默认
		# 训练
		lasso.fit(X_train, y_train)
		# 预测
		y_test_pred_lasso = lasso.predict(X_test).reshape(-1,1)
		y_train_pred_lasso = lasso.predict(X_train).reshape(-1,1)
		# 模型评估
		print('The r2 score of LassoCV on test is: ', r2_score(y_test, y_test_pred_lasso)) 
		print('The r2 score of LassoCV on train is: ', r2_score(y_train, y_train_pred_lasso)) 

		# 查看各特征的权重系数
		columns = ['temp','hum','windspeed','instant'] 
		fs = pd.DataFrame({'columns':list(columns), 'coef':list(lasso.coef_.T)[:4]})
		fs.sort_values(by=['coef'], ascending=False)

		#　找出最佳参数
		mses = np.mean(lasso.mse_path_, axis=1)
		plt.plot(np.log10(lasso.alphas_), mses)
		plt.plot(np.log10(lasso.alpha_)*np.ones(len(lasso.alphas_)),list(mses))
		plt.xlabel('log(alpha)')
		plt.ylabel('mse')
		plt.show()
		print('alpha is: ', ridge.alpha_)

	def lr(self):
		from sklearn.linear_model import LogisticRegression
		from sklearn.model_selection import GridSearchCV

		# 初始化 要调优的参数
		penaltys = ['l1','l2']
		C_s = [0.0001,0.001,0.01,0.1,1,10,100,1000]
		tuned_parameters = dict(penalty=penaltys, C=C_s)
		lr_penalty = LogisticRegression()
		grid = GridSearchCV(lr_penalty, tuned_parameters, cv=5, scoring='accuracy')  # CV交叉验证用于评估模型性能和进行参数调优（模型选择）
		grid.fit(X_train, y_train)

		print('***'*3,'Logistic回归 带参数', '***'*3)
		print('Best score: ', -grid.best_score_)
		print('Best params: ', grid.best_params_)
    
    def svm(self,rbf=False):
    	# 线性SVM
		from sklearn.svm import LinearSVC
		from sklearn.metrics import classification_report, confusion_matrix
		SVC1 = LinearSVC().fit(X_train_part,y_train_part)
		# 在校验集上测试，并估计模型性能
		y_predict = SVC1.predict(X_val)
		print('分类结果报告 {}:\n{}\n'.format(SVC1,classification_report(y_val,y_predict)))
