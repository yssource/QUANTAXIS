# coding:utf-8
#
# The MIT License (MIT)
#
# Copyright (c) 2016-2018 yutiansut/QUANTAXIS
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import json
import os
import configparser
from QUANTAXIS.QASU.user import QA_user_sign_in
from QUANTAXIS.QAUtil.QALocalize import qa_path, setting_path
from QUANTAXIS.QAUtil.QASql import QA_util_sql_mongo_setting
from QUANTAXIS.QASU.save_local import qa_path


# quantaxis有一个配置目录存放在 ~/.quantaxis
# 如果配置目录不存在就创建，主要配置都保存在config.json里面
# 貌似yutian已经进行了，文件的创建步骤，他还会创建一个setting的dir
# 需要与yutian讨论具体配置文件的放置位置 author:Will 2018.5.19

DEFAULT_DB_URI = 'mongodb://localhost:27017/quantaxis'
CONFIGFILE_PATH = '{}{}{}'.format(setting_path, os.sep, 'config.ini')


class QA_Setting():
    def __init__(self, uri=None):
        self.mongo_uri = uri or self.get_config() or self.env_config() or DEFAULT_DB_URI
        self.username = None
        self.password = None

        # 加入配置文件地址

    def get_config(self):
        config = configparser.ConfigParser()
        if os.path.exists(CONFIGFILE_PATH):
            config.read(CONFIGFILE_PATH)
            try:
                return config.get('MONGODB', 'uri')
            except configparser.NoSectionError:
                config.add_section('MONGODB')
                config.set('MONGODB', 'uri', DEFAULT_DB_URI)
                return DEFAULT_DB_URI
            except configparser.NoOptionError:
                config.set('MONGODB', 'uri', DEFAULT_DB_URI)
                return DEFAULT_DB_URI
            finally:

                with open(CONFIGFILE_PATH, 'w') as f:
                    config.write(f)

        else:
            f=open(CONFIGFILE_PATH, 'w')
            config.add_section('MONGODB')
            config.set('MONGODB', 'uri', DEFAULT_DB_URI)
            config.write(f)
            f.close()
            return DEFAULT_DB_URI

    def env_config(self):
        return os.environ.get("MONGOURI", None)

    @property
    def client(self):
        return QA_util_sql_mongo_setting(self.mongo_uri)

    def change(self, ip, port):
        self.ip = ip
        self.port = port
        global DATABASE
        DATABASE = self.client
        return self

    def login(self, user_name, password):
        user = QA_user_sign_in(user_name, password, self.client)
        if user is not None:
            self.user_name = user_name
            self.password = password
            self.user = user
            return self.user
        else:
            return False


DATABASE = QA_Setting().client.quantaxis


info_ip_list = [{'ip': '101.227.73.20', 'port': 7709}, {'ip': '101.227.77.254', 'port': 7709}, {'ip': '114.80.63.12', 'port': 7709}, {'ip': '114.80.63.35', 'port': 7709}, {'ip': '115.238.56.198', 'port': 7709}, {'ip': '115.238.90.165', 'port': 7709}, {'ip': '124.160.88.183', 'port': 7709}, {'ip': '60.28.23.80', 'port': 7709}, {'ip': '14.215.128.18', 'port': 7709}, {'ip': '180.153.18.170', 'port': 7709}, {
    'ip': '180.153.18.171', 'port': 7709}, {'ip': '180.153.39.51', 'port': 7709}, {'ip': '202.108.253.130', 'port': 7709}, {'ip': '202.108.253.131', 'port': 7709}, {'ip': '218.108.47.69', 'port': 7709}, {'ip': '218.108.98.244', 'port': 7709}, {'ip': '218.75.126.9', 'port': 7709}, {'ip': '221.231.141.60', 'port': 7709}, {'ip': '59.173.18.140', 'port': 7709}, {'ip': '60.12.136.250', 'port': 7709}]


stock_ip_list = [{'ip': '218.75.126.9', 'port': 7709}, {'ip': '115.238.90.165', 'port': 7709}, {'ip': '124.160.88.183', 'port': 7709}, {'ip': '60.12.136.250', 'port': 7709}, {'ip': '218.108.98.244', 'port': 7709}, {'ip': '218.108.47.69', 'port': 7709}, {'ip': '180.153.39.51', 'port': 7709}, {'ip': '121.14.2.7', 'port': 7709}, {'ip': '60.28.29.69', 'port': 7709}, {'ip': '180.153.18.170', 'port': 7709}, {'ip': '180.153.18.171', 'port': 7709}, {'ip': '180.153.18.17', 'port': 7709}, {
    'ip': '61.135.142.73', 'port': 7709}, {'ip': '115.238.56.198', 'port': 7709}, {'ip': '60.191.117.167', 'port': 7709}, {'ip': 'hq.cjis.cn', 'port': 7709}, {'ip': '59.173.18.69', 'port': 7709}, {'ip': 'sztdx.gtjas.com', 'port': 7709}, {'ip': 'jstdx.gtjas.com', 'port': 7709}, {'ip': 'shtdx.gtjas.com', 'port': 7709}, {'ip': '218.9.148.108', 'port': 7709}, {'ip': '61.153.144.179', 'port': 7709}, {'ip': '61.153.209.138', 'port': 7709}, {'ip': '61.153.209.139', 'port': 7709}, {'ip': 'hq1.daton.com.cn', 'port': 7709}]

future_ip_list = [{'ip': '112.74.214.43', 'port': 7727},
                  {'ip': '59.175.238.38', 'port': 7727},
                  {'ip': '124.74.236.94', 'port': 7721},
                  {'ip': '218.80.248.229', 'port': 7721},
                  {'ip': '124.74.236.94', 'port': 7721},
                  {'ip': '58.246.109.27', 'port': 7721}
                  ]


"""
['121.14.110.210', '119.147.212.76', '113.105.73.86', '119.147.171.211', '119.147.164.57', '119.147.164.58', '61.49.50.180', '61.49.50.181',
'61.135.142.85', '61.135.149.181', '114.80.80.210', '222.73.49.15', '221.194.181.176']
"""
