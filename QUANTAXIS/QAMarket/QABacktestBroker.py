# coding :utf-8
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


import datetime

from QUANTAXIS.QAFetch.QAQuery import (QA_fetch_future_day,
                                       QA_fetch_future_min, QA_fetch_index_day,
                                       QA_fetch_index_min, QA_fetch_stock_day,
                                       QA_fetch_stock_min)
from QUANTAXIS.QAFetch.QATdx import (QA_fetch_get_future_day,
                                     QA_fetch_get_future_min,
                                     QA_fetch_get_index_day,
                                     QA_fetch_get_index_min,
                                     QA_fetch_get_stock_day,
                                     QA_fetch_get_stock_min)
from QUANTAXIS.QAMarket.QABroker import QA_Broker
from QUANTAXIS.QAMarket.QADealer import QA_Dealer
from QUANTAXIS.QAUtil.QADate import QA_util_to_datetime
from QUANTAXIS.QAUtil.QALogs import QA_util_log_info
from QUANTAXIS.QAUtil.QAParameter import (AMOUNT_MODEL, BROKER_TYPE, ORDER_MODEL,
                                          ENGINE_EVENT, MARKET_EVENT, FREQUENCE,
                                          MARKET_TYPE, BROKER_EVENT)
from QUANTAXIS.QAMarket.QAOrderHandler import QA_OrderHandler
from QUANTAXIS.QAEngine.QAEvent import QA_Event


class QA_BacktestBroker(QA_Broker):
    """
    QUANTAXIS Broker 部分

    回测
    股票/指数/期货/债券/ETF/基金
    @yutiansut


    对于不同的市场规则:
    股票市场 t+1
    期货/期权/加密货币市场 t+0

    股票/加密货币市场不允许卖空
    期货/期权市场允许卖空

    t+1的市场是
    当日的买入 更新持仓- 不更新可卖数量- 资金冻结
    当日的卖出 及时更新可用资金

    t+0市场是:
    当日买入 即时更新持仓和可卖
    当日卖出 即时更新

    卖空的规则是
    允许无仓位的时候卖出证券(按市值和保证金比例限制算)
    """

    def __init__(self, commission_fee_coeff=0.0015, if_nondatabase=False):
        """[summary]


        Keyword Arguments:
            commission_fee_coeff {[type]} -- [description] (default: {0})
            environment {[type]} -- [description] (default: {RUNNING_ENVIRONMENT})
            if_nondatabase {[type]} -- [description] (default: {False})
        """
        super().__init__()
        self.dealer = QA_Dealer(commission_fee_coeff)
        self.order_handler = QA_OrderHandler()
        self.engine = {
            MARKET_TYPE.STOCK_CN: self.dealer.backtest_stock_dealer}

        self.fetcher = {(MARKET_TYPE.STOCK_CN, FREQUENCE.DAY): QA_fetch_stock_day, (MARKET_TYPE.STOCK_CN, FREQUENCE.FIFTEEN_MIN): QA_fetch_stock_min,
                        (MARKET_TYPE.STOCK_CN, FREQUENCE.ONE_MIN): QA_fetch_stock_min, (MARKET_TYPE.STOCK_CN, FREQUENCE.FIVE_MIN): QA_fetch_stock_min,
                        (MARKET_TYPE.STOCK_CN, FREQUENCE.THIRTY_MIN): QA_fetch_stock_min, (MARKET_TYPE.STOCK_CN, FREQUENCE.SIXTY_MIN): QA_fetch_stock_min,
                        (MARKET_TYPE.INDEX_CN, FREQUENCE.DAY): QA_fetch_index_day, (MARKET_TYPE.INDEX_CN, FREQUENCE.FIFTEEN_MIN): QA_fetch_index_min,
                        (MARKET_TYPE.INDEX_CN, FREQUENCE.ONE_MIN): QA_fetch_index_min, (MARKET_TYPE.INDEX_CN, FREQUENCE.FIVE_MIN): QA_fetch_index_min,
                        (MARKET_TYPE.INDEX_CN, FREQUENCE.THIRTY_MIN): QA_fetch_index_min, (MARKET_TYPE.INDEX_CN, FREQUENCE.SIXTY_MIN): QA_fetch_index_min,
                        (MARKET_TYPE.FUND_CN, FREQUENCE.DAY): QA_fetch_index_day, (MARKET_TYPE.FUND_CN, FREQUENCE.FIFTEEN_MIN): QA_fetch_index_min,
                        (MARKET_TYPE.FUND_CN, FREQUENCE.ONE_MIN): QA_fetch_index_min, (MARKET_TYPE.FUND_CN, FREQUENCE.FIVE_MIN): QA_fetch_index_min,
                        (MARKET_TYPE.FUND_CN, FREQUENCE.THIRTY_MIN): QA_fetch_index_min, (MARKET_TYPE.FUND_CN, FREQUENCE.SIXTY_MIN): QA_fetch_index_min}


        self.commission_fee_coeff = commission_fee_coeff
        self.market_data = None
        self.if_nondatabase = if_nondatabase
        self.name = BROKER_TYPE.BACKETEST
        self._quotation = {}  # 一个可以缓存数据的dict
        self.broker_data = None

    def run(self, event):
        if event.event_type is MARKET_EVENT.QUERY_DATA:
            # 查询数据部分
            code = event.code
            frequence = event.frequence
            start = event.start
            end = start if event.end is None else event.end
            market_type = event.market_type
            try:
                res = self.broker_data.select_time(
                    start, end).select_code(code).to_numpy()
            except:
                res = self.fetcher[(market_type, frequence)](
                    code, start, end, frequence=frequence)
            if event.callback:
                event.callback(res)
            else:
                return res
        elif event.event_type is MARKET_EVENT.QUERY_ORDER:
            self.order_handler.run(event)
        elif event.event_type is ENGINE_EVENT.UPCOMING_DATA:
            new_marketdata_dict = event.market_data.dicts
            for item in new_marketdata_dict.keys():
                if item not in self._quotation.keys():
                    self._quotation[item] = new_marketdata_dict[item]
            # if self.broker_data is None:
            #     self.broker_data = event.market_data
            # else:
            #     self.broker_data.append(event.market_data)
            # self.broker_data=event.market_data

        elif event.event_type is BROKER_EVENT.RECEIVE_ORDER:
            self.order_handler.run(event)
            self.run(QA_Event(event_type=BROKER_EVENT.TRADE, broker=self))
        elif event.event_type is BROKER_EVENT.TRADE:
            event = self.order_handler.run(event)

            event.message = 'trade'
            if event.callback:
                event.callback(event)
        elif event.event_type is BROKER_EVENT.SETTLE:
            self.order_handler.run(event)
            if event.callback:
                event.callback('settle')

    def receive_order(self, event):
        """
        get the order and choice which market to trade

        """
        order = event.order

        if 'market_data' in event.__dict__.keys():
            self.market_data = self.get_market(
                order) if event.market_data is None else event.market_data
        else:
            self.market_data = self.get_market(order)

        order = self.warp(order)

        return self.dealer.deal(order, self.market_data)

    def warp(self, order):
        """对order/market的封装

        [description]

        Arguments:
            order {[type]} -- [description]

        Returns:
            [type] -- [description]
        """

        # 因为成交模式对时间的封装

        if order.order_model == ORDER_MODEL.MARKET:

            if order.frequence is FREQUENCE.DAY:
                # exact_time = str(datetime.datetime.strptime(
                #     str(order.datetime), '%Y-%m-%d %H-%M-%S') + datetime.timedelta(day=1))

                order.date = order.datetime[0:10]
                order.datetime = '{} 09:30:00'.format(order.date)
            elif order.frequence in [FREQUENCE.ONE_MIN,FREQUENCE.FIVE_MIN,FREQUENCE.FIFTEEN_MIN,FREQUENCE.THIRTY_MIN,FREQUENCE.SIXTY_MIN]:
                print(order.datetime)
                exact_time = str(datetime.datetime.strptime(
                    str(order.datetime), '%Y-%m-%d %H:%M:%S') + datetime.timedelta(minutes=1))
                order.date = exact_time[0:10]
                order.datetime = exact_time
            self.market_data = self.get_market(order)
            if self.market_data is None:
                return order
            order.price = (float(self.market_data["high"]) +
                           float(self.market_data["low"])) * 0.5
        elif order.order_model == ORDER_MODEL.NEXT_OPEN:
            try:
                exact_time = str(datetime.datetime.strptime(
                    str(order.datetime), '%Y-%m-%d %H-%M-%S') + datetime.timedelta(day=1))
                order.date = exact_time[0:10]
                order.datetime = '{} 09:30:00'.format(order.date)
            except:
                order.datetime = '{} 15:00:00'.format(order.date)
            self.market_data = self.get_market(order)
            if self.market_data is None:
                return order
            order.price = float(self.market_data["close"])
        elif order.order_model == ORDER_MODEL.CLOSE:

            try:
                order.datetime = self.market_data.datetime
            except:
                if len(str(order.datetime)) == 19:
                    pass
                else:
                    order.datetime = '{} 15:00:00'.format(order.date)
            self.market_data = self.get_market(order)
            if self.market_data is None:
                return order
            order.price = float(self.market_data["close"])

        elif order.order_model == ORDER_MODEL.STRICT:
            '加入严格模式'
            if order.frequence is FREQUENCE.DAY:
                exact_time = str(datetime.datetime.strptime(
                    order.datetime, '%Y-%m-%d %H-%M-%S') + datetime.timedelta(day=1))

                order.date = exact_time[0:10]
                order.datetime = '{} 09:30:00'.format(order.date)
            elif order.frequence in [FREQUENCE.ONE_MIN,FREQUENCE.FIVE_MIN,FREQUENCE.FIFTEEN_MIN,FREQUENCE.THIRTY_MIN,FREQUENCE.SIXTY_MIN]:
                exact_time = str(datetime.datetime.strptime(
                    order.datetime, '%Y-%m-%d %H-%M-%S') + datetime.timedelta(minute=1))
                order.date = exact_time[0:10]
                order.datetime = exact_time
            self.market_data = self.get_market(order)
            if self.market_data is None:
                return order
            if order.towards == 1:
                order.price = float(self.market_data["high"])
            else:
                order.price = float(self.market_data["low"])


        return order

    def get_market(self, order):
        """get_market func

        [description]

        Arguments:
            order {orders} -- [description]

        Returns:
            [type] -- [description]
        """

        # 首先判断是否在_quotation里面

        if (order.datetime, order.code) in self._quotation.keys():
            return self._quotation[(QA_util_to_datetime(order.datetime), order.code)]

        else:
            try:
                data = self.fetcher[(order.market_type, order.frequence)](
                    code=order.code, start=order.datetime, end=order.datetime, format='json')[0]
                if 'vol' in data.keys() and 'volume' not in data.keys():
                    data['volume'] = data['vol']
                elif 'vol' not in data.keys() and 'volume' in data.keys():
                    data['vol'] = data['volume']
                return data
            except Exception as e:
                QA_util_log_info('MARKET_ENGING ERROR: {}'.format(e))
                return None
