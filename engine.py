# -*- coding: utf-8 -*-
"""
Created on Wed Aug 12 01:53:07 2015

@author: Roma
"""
from Queue import Queue, Empty
import pandas as pd
import txmlconnector as transaq
from pair.private_strategies import PHKBollinger
import time, logging, threading, sys
import sqlalchemy as sql
log = logging.getLogger('transaq.engine')


class CountDownLatch(object):
    def __init__(self, count=1):
        self.count = count
        self.lock = threading.Condition()

    def count_down(self):
        with self.lock:
            self.count -= 1
            if self.count <= 0:
                self.lock.notifyAll()

    def await(self):
        with self.lock:
            while self.count > 0:
                self.lock.wait()


class TradeEngine(object):
    stopped = False
    event_queue = None
    client_account = None
    client_portfolio = None
    my_trades = {}
    my_orders = {}
    # Здесь храним свечки ☦
    history = None
    WINDOW = 1000
    board = 'TQBR'
    period = 2
    epsila = 10
    total_invest = 30000

    def handle_txml_message(self, msg):
        if type(msg) == transaq.HistoryCandlePacket:
            self.event_queue.put(msg)
            self._candles_received += len(msg.items)
            if self._candles_received >= self.WINDOW * 2:
                self.history_latch.count_down()
        elif type(msg) == transaq.ClientAccount:
            self.client_account = msg
            self.account_latch.count_down()
        elif type(msg) == transaq.ServerStatus and msg.connected == 'error':
            sys.exit(-1)

    def run(self):
        try:
            transaq.initialize("Logs", 3, self.handle_txml_message)
            log.info(u"Подрубаюсь: %s" % repr(transaq.connect("00000282166", "yGmUmU", "78.41.194.46:3950")) )
            self.account_latch.await()
            assert self.client_account, u"Где аккаунт, сцука!"
            log.info(u"Запрос 1000 свечек %s: %s" % (self.sym1,
                                                      transaq.get_history(self.board, self.sym1, self.period, count=self.WINDOW+5)))
            log.info(u"Запрос 1000 свечек %s: %s" % (self.sym2,
                                                      transaq.get_history(self.board, self.sym2, self.period, count=self.WINDOW+5)))
            self.history_latch.await()
            for i in range(3):
                while not self.event_queue.empty():
                    evt = self.event_queue.get_nowait()
                    self.handle_event(evt)
                self.history = self.history.fillna(method='ffill', axis=1).sort_index()
                advice = self.strategy.handle_moment(self.history)
                log.info(u"Стратегический совет: %s (%s)" % advice)
                self.balance(advice)
                log.info(u"Запрос последней свечки %s: %s" % (self.sym1,
                                                              transaq.get_history(self.board, self.sym1, self.period, count=1)))
                log.info(u"Запрос последней свечки %s: %s" % (self.sym2,
                                                              transaq.get_history(self.board, self.sym2, self.period, count=1)))
                time.sleep(60*5)
        finally:
            log.info(u"Записываю ист. данные на диск")
            #self.history[self.sym1].to_sql(self.sym1, self.conn, if_exists='replace')
            #self.history[self.sym2].to_sql(self.sym2, self.conn, if_exists='replace')
            log.info(u"Отваливаюсь: %s" % transaq.disconnect())
            transaq.uninitialize()

    def handle_event(self, evt):
        if type(evt) == transaq.HistoryCandlePacket:
            sym = evt.seccode
            dates = map(lambda o: o.date, evt.items)
            ohlcv = map(lambda o: (o.open, o.high, o.low, o.close, o.volume), evt.items)
            df = pd.DataFrame(index=dates, data=ohlcv, columns=('open', 'high', 'low', 'close', 'volume'))
            bars = pd.Panel({sym: df})
            hist = self.history
            self.history = hist.reindex(items=bars.items | hist.items, major_axis=bars.major_axis | hist.major_axis,
                                        minor_axis=bars.minor_axis | hist.minor_axis, copy=False)
            self.history.update(bars)

    def __init__(self, strategy):
        super(TradeEngine, self).__init__()
        self.event_queue = Queue()
        self.strategy = strategy
        self.sym1 = self.strategy.sym1
        self.sym2 = self.strategy.sym2
        self.history = pd.Panel()
        self.account_latch = CountDownLatch(1)
        self.history_latch = CountDownLatch(1)
        self._candles_received = 0
        self.current_pos = {}
        self.conn = sql.create_engine(u"sqlite:///C:\\Users\\Roma\\Documents\\candles.db")

    def balance(self, target_pos):
        for ticker in target_pos.keys():
            target = self.total_invest * target_pos[ticker]
            current = self.current_pos.get(ticker, 0)
            if abs(target-current) > self.epsila:
                price = self.history.ix[ticker, -1, 'close']
                delta_pos = (target-current)/price//self.lots[ticker]
                if abs(delta_pos) >= 1:
                    transaq.new_order(self.board, ticker, self.client_account.id,
                                      'B' if delta_pos>0 else 'S', abs(delta_pos))

if __name__ == '__main__':
    logging.basicConfig()
    log.setLevel(logging.DEBUG)
    logging.getLogger('transaq.connector').setLevel(logging.DEBUG)
    logging.getLogger('transaq.structures').setLevel(logging.DEBUG)
    logging.getLogger('pair_trading.strategy').setLevel(logging.DEBUG)

    strategy = PHKBollinger(('SBER03', 'MTSI'), zscore_enter=-.1, zscore_exit=.7, delta=1e-10, lyambda=1e10)
    engine = TradeEngine(strategy)
    engine.run()