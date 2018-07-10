#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse
import datetime

import pytz


tz = pytz.timezone('Asia/Shanghai')
current_time = datetime.datetime.now(tz)


def parse_args(check=True):
    parser = argparse.ArgumentParser()
    parser.add_argument('--output_dir', type=str, default='/home/hhf/code/AI/12.projects/02.CTR/kaggle-avazu-AI3/output',
                        help='path to save log and checkpoint.')

    parser.add_argument('--data_dir',  type=str, default='/home/hhf/code/AI/12.projects/02.CTR/kaggle-avazu-AI3/data/',
                        help='the path of raw data(contain test dataset and train dataset)')

    parser.add_argument('--train_file',  type=str, default='train.csv',
                        help='the name of train dataset')

    parser.add_argument('--test_file',  type=str, default='test.csv',
                        help='the name of test dataset')

    parser.add_argument('--fe_data_file',  type=str, default='FE_data_{}',
                        help='the prefix of the data when feature engineering finished!')

    parser.add_argument('--batch_size', type=int, default=500,
                        help='batch size to use.')

    parser.add_argument('--learning_rate', type=float, default=0.001,
                        help='learning rate')

    parser.add_argument('--keep_prob', type=float, default=0.5,
                        help='keep_prob')

    parser.add_argument('--iterations', type=int, default=30,
                        help='iterations')


    FLAGS, unparsed = parser.parse_known_args()

    return FLAGS, unparsed


if __name__ == '__main__':
    FLAGS, unparsed = parse_args()

    for x in dir(FLAGS):
        print(getattr(FLAGS, x))
