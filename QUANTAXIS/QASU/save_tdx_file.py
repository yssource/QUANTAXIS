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
import pymongo

from pytdx.reader import TdxMinBarReader

from QUANTAXIS.QAUtil import (QA_Setting, QA_util_date_stamp, QA_util_log_info,
                              QA_util_time_stamp)


def QA_save_tdx_to_mongo(file_dir, client=QA_Setting.client):
    reader = TdxMinBarReader()
    __coll = client.stock_min
    __coll.create_index([('code', pymongo.ASCENDING), \
                         ('type', pymongo.ASCENDING), \
                         ('time_stamp', pymongo.ASCENDING)], unique=True)
    for a, v, files in os.walk(file_dir):

        for file in files:

            if (str(file)[0:2] == 'sh' and int(str(file)[2]) == 6) or \
                (str(file)[0:2] == 'sz' and int(str(file)[2]) == 0) or \
                    (str(file)[0:2] == 'sz' and int(str(file)[2]) == 3):

                QA_util_log_info('Now_saving ' + str(file)
                                 [2:8] + '\'s 5 min tick')
                fname = file_dir + os.sep + file
                try:
                    df = reader.get_df(fname)
                except Exception as e:
                    print('df e {}'.format(e))
                    continue
                if df is not None and not df.empty:
                    df.rename(columns ={'volume': 'vol'}, inplace =True)
                    df['code'] = str(file)[2:8]
                    # df['market'] = str(file)[0:2]
                    df['type'] = '5min'
                    df['datetime'] = [str(x) for x in list(df.index)]
                    df['date'] = [str(x)[0:10] for x in list(df.index)]
                    df['time_stamp'] = df['datetime'].apply(
                        lambda x: QA_util_time_stamp(x))
                    df['date_stamp'] = df['date'].apply(
                        lambda x: QA_util_date_stamp(x))
                    data_json = json.loads(df.to_json(orient='records'))
                    try:
                        __coll.insert_many(data_json, ordered=False)
                    except Exception as e:
                        print('db e {}'.format(e))


if __name__ == '__main__':
    file_dir = ['C:\\users\\yutiansut\\desktop\\sh5fz',
                'C:\\users\\yutiansut\\desktop\\sz5fz']
    file_dir = ['/home/jimmy/workspace/tdx/data/vipdoc/sh/fzline/', '/home/jimmy/workspace/tdx/data/vipdoc/sz/fzline/']
    for item in file_dir:
        QA_save_tdx_to_mongo(item)
