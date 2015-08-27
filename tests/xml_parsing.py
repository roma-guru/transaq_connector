# -*- coding: utf-8 -*-
"""
Created on Wed Aug 05 17:09:45 2015

@author: Roma
"""

import unittest as ut
from structures import *
from datetime import datetime as dt


class TestClientOrders(ut.TestCase):
    @classmethod
    def setUpClass(cls):
        xml = open('tests/orders.xml').read()
        cls.obj = ClientOrderPacket.parse(xml)

    def test_packet(self):
        self.assertIsInstance(self.obj, ClientOrderPacket)
        self.assertEqual(len(self.obj.items), 4)

    def test_order1(self):
        o = self.obj.items[0]
        self.assertIsInstance(o, Order)
        self.assertEqual(o.id, 4581)
        self.assertEqual(o.order_no, 2693279377)
        self.assertEqual(o.secid, 21)
        self.assertEqual(o.board, 'TQBR')
        self.assertEqual(o.seccode, 'MTSI')
        self.assertEqual(o.value, 7539.3)
        self.assertEqual(o.client, 'test/C282166')
        self.assertEqual(o.status, 'matched')
        self.assertEqual(o.buysell, 'B')
        self.assertEqual(o.time, dt(2015,8,10,16,11,30))
        self.assertEqual(o.broker_ref, '')
        self.assertEqual(o.accrued_int, 0.0)
        self.assertEqual(o.settle_code, 'Y2')
        self.assertEqual(o.balance, 0)
        self.assertEqual(o.price, 0)
        self.assertEqual(o.quantity, 3)
        self.assertEqual(o.hidden, 0)
        self.assertEqual(o.yld, 0)
        self.assertEqual(o.withdraw_time, None)
        # self.assertEqual(o.condition, None)
        self.assertEqual(o.max_commission, 0)
        self.assertEqual(o.result, '')

    def test_order2(self):
        o = self.obj.items[1]
        self.assertIsInstance(o, Order)
        self.assertEqual(o.id, 4531)
        self.assertEqual(o.order_no, 2693271069)
        self.assertEqual(o.secid, 21)
        self.assertEqual(o.board, 'TQBR')
        self.assertEqual(o.seccode, 'MTSI')
        self.assertEqual(o.value, 7264.5)
        self.assertEqual(o.client, 'test/C282166')
        self.assertEqual(o.status, 'active')
        self.assertEqual(o.buysell, 'S')
        self.assertEqual(o.time, dt(2015,8,10,16,05,20))
        self.assertEqual(o.broker_ref, '')
        self.assertEqual(o.accrued_int, 0.0)
        self.assertEqual(o.settle_code, 'Y2')
        self.assertEqual(o.balance, 3)
        self.assertEqual(o.price, 242.15)
        self.assertEqual(o.quantity, 3)
        self.assertEqual(o.hidden, 0)
        self.assertEqual(o.yld, 0)
        self.assertEqual(o.withdraw_time, None)
        # self.assertEqual(o.condition, None)
        self.assertEqual(o.max_commission, 0)
        self.assertEqual(o.result, '')

    def test_order3(self):
        o = self.obj.items[2]
        self.assertIsInstance(o, TakeProfit)
        self.assertEqual(o.id, 4571)
        self.assertEqual(o.order_no, 2693279377)
        self.assertEqual(o.secid, 21)
        self.assertEqual(o.board, 'TQBR')
        self.assertEqual(o.seccode, 'MTSI')
        self.assertEqual(o.client, 'test/C282166')
        self.assertEqual(o.status, 'tp_executed')
        self.assertEqual(o.buysell, 'B')
        self.assertEqual(o.canceller, '00000282166')
        self.assertEqual(o.alltrade_no, 2693113024)
        self.assertEqual(o.author, '00000282166')
        self.assertEqual(o.valid_before, dt(2015,8,10,16,30))
        self.assertEqual(o.accept_time, dt(2015,8,10,16,11,26))
        self.assertEqual(o.activation_price, 242.0)
        self.assertEqual(o.quantity, 3)
        self.assertEqual(o.extremum, 239.11)
        self.assertEqual(o.level, 239.12)
        self.assertEqual(o.correction, 0.01)
        self.assertEqual(o.withdraw_time, None)
        self.assertEqual(o.result, u"TP исполнен")

    def test_order4(self):
        o = self.obj.items[3]
        self.assertIsInstance(o, StopLoss)
        self.assertEqual(o.id, 4561)
        self.assertEqual(o.secid, 21)
        self.assertEqual(o.board, 'TQBR')
        self.assertEqual(o.seccode, 'MTSI')
        self.assertEqual(o.client, 'test/C282166')
        self.assertEqual(o.status, 'watching')
        self.assertEqual(o.buysell, 'B')
        self.assertEqual(o.canceller, '00000282166')
        self.assertEqual(o.author, '00000282166')
        self.assertEqual(o.valid_before, dt(2015,8,10,16,30))
        self.assertEqual(o.accept_time, dt(2015,8,10,16,11,26))
        self.assertEqual(o.activation_price, 243.0)
        self.assertEqual(o.quantity, 3)
        self.assertEqual(o.use_credit, True)
        self.assertEqual(o.withdraw_time, None)


class TestClientTrades(ut.TestCase):
    @classmethod
    def setUpClass(cls):
        xml = open('tests/trades.xml').read()
        cls.obj = ClientTradePacket.parse(xml)

    def test_trade1(self):
        o = self.obj.items[0]
        self.assertIsInstance(o, ClientTrade)
        self.assertEqual(o.secid, 21)
        self.assertEqual(o.id, 2693113027)
        self.assertEqual(o.order_no, 2693279377)
        self.assertEqual(o.board, 'TQBR')
        self.assertEqual(o.seccode, 'MTSI')
        self.assertEqual(o.client, 'test/C282166')
        self.assertEqual(o.buysell, 'B')
        self.assertEqual(o.time, dt(2015,8,10,16,11,30))
        self.assertEqual(o.broker_ref, '')
        self.assertEqual(o.value, 7180.5)
        self.assertEqual(o.commission, 0)
        self.assertEqual(o.price, 239.35)
        self.assertEqual(o.quantity, 3)
        self.assertEqual(o.items, 30)
        self.assertEqual(o.current_position, 30)
        self.assertEqual(o.accrued_int, 0)
        self.assertEqual(o.trade_type, 'T')
        self.assertEqual(o.settle_code, 'Y2')

    def test_trade2(self):
        o = self.obj.items[1]
        self.assertIsInstance(o, ClientTrade)
        self.assertEqual(o.secid, 21)
        self.assertEqual(o.id, 2692109248)
        self.assertEqual(o.order_no, 2692232421)
        self.assertEqual(o.board, 'TQBR')
        self.assertEqual(o.seccode, 'MTSI')
        self.assertEqual(o.client, 'test/C282166')
        self.assertEqual(o.buysell, 'S')
        self.assertEqual(o.time, dt(2015,8,9,15,32,40))
        self.assertEqual(o.broker_ref, '')
        self.assertEqual(o.value, 2415.2)
        self.assertEqual(o.commission, 0)
        self.assertEqual(o.price, 241.52)
        self.assertEqual(o.quantity, 1)
        self.assertEqual(o.items, 10)
        self.assertEqual(o.current_position, -10)
        self.assertEqual(o.accrued_int, 0)
        self.assertEqual(o.trade_type, 'T')
        self.assertEqual(o.settle_code, 'Y2')

    def test_packet(self):
        self.assertIsInstance(self.obj, ClientTradePacket)
        self.assertEqual(len(self.obj.items), 2)


class TestClientPortfolio(ut.TestCase):
    @classmethod
    def setUpClass(cls):
        xml = open('tests/portfolio.xml').read()
        cls.obj = ClientPortfolio.parse(xml)

    def test_portfolio_tplus(self):
        o = self.obj
        self.assertIsInstance(o, ClientPortfolio)
        self.assertEqual(o.client, 'test/C282166')
        self.assertEqual(o.coverage_fact, 56325.08)
        self.assertEqual(o.coverage_plan, 56325.08)
        self.assertEqual(o.coverage_crit, 56325.08)
        self.assertEqual(o.open_equity, 291368.30)
        self.assertEqual(o.equity, 291076.74)
        self.assertEqual(o.cover, 291076.74)
        self.assertEqual(o.init_margin, 516.78)
        self.assertEqual(o.pnl_income, 3.84)
        self.assertEqual(o.pnl_intraday, -295.4)
        self.assertEqual(o.leverage, 1)
        self.assertEqual(o.margin_level, 516.78)
        self.assertTrue(o.money)
        self.assertEqual(o.money.open_balance, 290855.36)
        self.assertEqual(o.money.bought, 106537.60)
        self.assertEqual(o.money.sold, 106242.20)
        self.assertEqual(o.money.balance, 290559.96)
        self.assertEqual(o.money.settled, 0)
        self.assertEqual(o.money.tax, 0)
        self.assertTrue(o.money.value_parts and len(o.money.value_parts)==3)
        _o = o.money.value_parts[0]
        self.assertEqual(_o.register, 'C')
        self.assertEqual(_o.open_balance, 190855.36)
        self.assertEqual(_o.balance, 190855.36)
        self.assertEqual(_o.bought, 0)
        self.assertEqual(_o.sold, 0)
        self.assertEqual(_o.settled, 0)
        _o = o.money.value_parts[1]
        self.assertEqual(_o.register, 'T0')
        self.assertEqual(_o.open_balance, 100000.00)
        self.assertEqual(_o.balance, 100000.00)
        self.assertEqual(_o.bought, 0)
        self.assertEqual(_o.sold, 0)
        self.assertEqual(_o.settled, 0)
        _o = o.money.value_parts[2]
        self.assertEqual(_o.register, 'Y2')
        self.assertEqual(_o.open_balance, 0)
        self.assertEqual(_o.balance, -295.4)
        self.assertEqual(_o.bought, 106537.60)
        self.assertEqual(_o.sold, 106242.20)
        self.assertEqual(_o.settled, 0)
        self.assertTrue(o.securities and len(o.securities)==2)
        _o = o.securities[0]
        self.assertEqual(_o.secid, 1)
        self.assertEqual(_o.market, 1)
        self.assertEqual(_o.seccode, 'GAZP')
        self.assertEqual(_o.price, 172.26)
        self.assertEqual(_o.open_balance, 3)
        self.assertEqual(_o.bought, 0)
        self.assertEqual(_o.sold, 0)
        self.assertEqual(_o.balance, 3)
        self.assertEqual(_o.buying, 0)
        self.assertEqual(_o.selling, 0)
        self.assertEqual(_o.cover, 516.78)
        self.assertEqual(_o.init_margin, 516.78)
        self.assertEqual(_o.riskrate_long, 100)
        self.assertEqual(_o.riskrate_short, 100)
        self.assertEqual(_o.pnl_income, 3.84)
        self.assertEqual(_o.pnl_intraday, 0)
        self.assertEqual(_o.max_buy, 1687)
        self.assertEqual(_o.max_sell, 1693)
        self.assertTrue(_o.value_parts and len(_o.value_parts)==1)
        _o = _o.value_parts[0]
        self.assertEqual(_o.register, 'T0')
        self.assertEqual(_o.open_balance, 3)
        self.assertEqual(_o.balance, 3)
        self.assertEqual(_o.bought, 0)
        self.assertEqual(_o.sold, 0)
        self.assertEqual(_o.settled, 0)
        _o = o.securities[1]
        self.assertEqual(_o.secid, 21)
        self.assertEqual(_o.market, 1)
        self.assertEqual(_o.seccode, 'MTSI')
        self.assertEqual(_o.price, 241.76)
        self.assertEqual(_o.open_balance, 0)
        self.assertEqual(_o.bought, 440)
        self.assertEqual(_o.sold, 440)
        self.assertEqual(_o.balance, 0)
        self.assertEqual(_o.buying, 0)
        self.assertEqual(_o.selling, 0)
        self.assertEqual(_o.cover, 0)
        self.assertEqual(_o.init_margin, 0)
        self.assertEqual(_o.riskrate_long, 100)
        self.assertEqual(_o.riskrate_short, 100)
        self.assertEqual(_o.pnl_income, 0)
        self.assertEqual(_o.pnl_intraday, -295.4)
        self.assertEqual(_o.max_buy, 120)
        self.assertEqual(_o.max_sell, 120)
        self.assertTrue(_o.value_parts and len(_o.value_parts)==1)
        _o = _o.value_parts[0]
        self.assertEqual(_o.register, 'Y2')
        self.assertEqual(_o.open_balance, 0)
        self.assertEqual(_o.balance, 0)
        self.assertEqual(_o.bought, 440)
        self.assertEqual(_o.sold, 440)
        self.assertEqual(_o.settled, 0)


class TestServerStatuses(ut.TestCase):
    @classmethod
    def setUpClass(cls):
        xml = open('tests/server_statuses.xml').readlines()
        cls.statuses = map(ServerStatus.parse, xml)

    def test_server_status1(self):
        o = self.statuses[0]
        self.assertEqual(o.id, 0)
        self.assertEqual(o.connected, "false")
        self.assertEqual(o.text, None)
        self.assertEqual(o.timezone, "Arab Standard Time")
        self.assertEqual(o.text, None)
        self.assertEqual(o.recover, False)

    def test_server_status2(self):
        o = self.statuses[1]
        self.assertEqual(o.id, 0)
        self.assertEqual(o.connected, "true")
        self.assertEqual(o.text, None)
        self.assertEqual(o.timezone, "Arab Standard Time")
        self.assertEqual(o.text, None)
        self.assertEqual(o.recover, False)

    def test_server_status3(self):
        o = self.statuses[2]
        self.assertEqual(o.id, None)
        self.assertEqual(o.connected, "error")
        self.assertEqual(o.text, u"Пользователь с таким идентификатором уже подключен к серверу")
        self.assertEqual(o.timezone, None)
        self.assertEqual(o.recover, False)


class TestHistoryCandles(ut.TestCase):
    @classmethod
    def setUpClass(cls):
        xml = open('tests/candles.xml').read()
        cls.obj = HistoryCandlePacket.parse(xml)

    def test_packet(self):
        o = self.obj
        self.assertIsInstance(o, HistoryCandlePacket)
        self.assertEqual(len(o.items), 3)
        self.assertEqual(o.board, 'TQBR')
        self.assertEqual(o.seccode, 'VTBR')
        self.assertEqual(o.period, 1)
        self.assertEqual(o.status, 1)

    def test_candle1(self):
        o = self.obj.items[1]
        self.assertEqual(o.date, dt(2015,8,11,23,8))
        self.assertEqual(o.open, 0.1037)
        self.assertEqual(o.close, 0.1037)
        self.assertEqual(o.high, 0.1037)
        self.assertEqual(o.low, 0.1037)
        self.assertEqual(o.volume, 257485)
        self.assertEqual(o.open_interest, None)


class TestDateTimeMapper(ut.TestCase):
    def setUp(self):
        self.mapper = NullableDateTimeMapper(timeformat)

    def test_null(self):
        self.assertEqual(self.mapper.to_python(None), None)
        self.assertEqual(self.mapper.to_python('0'), None)

    def test_norm(self):
        self.assertEqual(self.mapper.to_python('11.08.2015 23:08:00'), dt(2015,8,11,23,8))


class TestGlobalParse(ut.TestCase):
    def test_candles(self):
        xml = open('tests/candles.xml').read()
        obj = parse(xml)
        self.assertTrue(obj and isinstance(obj,HistoryCandlePacket))

    def test_portfolio(self):
        xml = open('tests/portfolio.xml').read()
        obj = parse(xml)
        self.assertTrue(obj and isinstance(obj,ClientPortfolio))

    def test_orders(self):
        xml = open('tests/orders.xml').read()
        obj = parse(xml)
        self.assertTrue(obj and isinstance(obj,ClientOrderPacket))

    def test_trades(self):
        xml = open('tests/trades.xml').read()
        obj = parse(xml)
        self.assertTrue(obj and isinstance(obj,ClientTradePacket))


class TestEntity(ut.TestCase):
    def test_some(self):
        xml = "<babe id=\"1\"/>"
        o = Entity.parse(xml)
        self.assertIsInstance(o, Entity)
        self.assertEqual(o.id, 1)


class TestError(ut.TestCase):
    def test_some(self):
        xml = "<error>This babe is too hot</error>"
        o = Error.parse(xml)
        self.assertEqual(o.text, "This babe is too hot")


class TestCmdResults(ut.TestCase):
    def test_success(self):
        xml = "<result success=\"true\"/>"
        o = CmdResult.parse(xml)
        self.assertEqual(o.success, True)

    def test_fail(self):
        xml = u"<result success=\"false\"><message>Соединение не установлено...</message></result>"
        o = CmdResult.parse(xml)
        self.assertEqual(o.success, False)
        self.assertEqual(o.text, u"Соединение не установлено...")


class TestClientAccount(ut.TestCase):
    @classmethod
    def setUpClass(cls):
        xml = open('tests/account.xml').read()
        cls.obj = ClientAccount.parse(xml)

    def test_account(self):
        o = self.obj
        self.assertEqual(o.id, "test/C282166")
        self.assertEqual(o.active, True)
        self.assertEqual(o.currency, "RUR")
        self.assertEqual(o.type, "leverage")
        self.assertEqual(o.ml_intraday, 1)
        self.assertEqual(o.ml_overnight, 1)


class TestMarkets(ut.TestCase):
    def test_some(self):
        xml = "<market id=\"1\">ММВБ</market>"
        o = Market.parse(xml)
        self.assertEqual(o.id, 1)
        self.assertEqual(o.name, u"ММВБ")


class TestSecurity(ut.TestCase):
    @classmethod
    def setUpClass(cls):
        xml = open('tests/securities.xml').read()
        cls.obj = SecurityPacket.parse(xml)

    def test_packet(self):
        self.assertIsInstance(self.obj, SecurityPacket)
        self.assertEqual(len(self.obj.items), 3)

    def test_sec1(self):
        o = self.obj.items[1]
        self.assertEqual(o.id, 1)
        self.assertEqual(o.active, True)
        self.assertEqual(o.seccode, 'GAZP')
        self.assertEqual(o.sectype, 'SHARE')
        self.assertEqual(o.board, 'TQBR')
        self.assertEqual(o.market, 1)
        self.assertEqual(o.name, u"Газпром ао")
        self.assertEqual(o.decimals, 2)
        self.assertEqual(o.minstep, .01)
        self.assertEqual(o.lotsize, 1)
        self.assertEqual(o.point_cost, 1)
        self.assertEqual(o.timezone.strip(), "Arab Standard Time")
        self.assertEqual(o.credit_allowed, True)
        self.assertEqual(o.bymarket_allowed, True)
        self.assertEqual(o.nosplit_allowed, True)
        self.assertEqual(o.immediate_allowed, True)
        self.assertEqual(o.cancelbalance_allowed, True)


class TestQuotations(ut.TestCase):
    pass


class TestSubscribedTicks(ut.TestCase):
    @classmethod
    def setUpClass(cls):
        xml = open('tests/alltrades.xml').read()
        cls.obj = TradePacket.parse(xml)

    def test_packet(self):
        self.assertIsInstance(self.obj, TradePacket)
        self.assertEqual(len(self.obj.items), 3)

    def test_tik1(self):
        o = self.obj.items[1]
        self.assertEqual(o.id, 2691161113)
        self.assertEqual(o.secid, 14)
        self.assertEqual(o.seccode, 'SBER03')
        self.assertEqual(o.board, 'TQBR')
        self.assertEqual(o.time, dt(2015,8,8,23,6,36))
        self.assertEqual(o.price, 102.5)
        self.assertEqual(o.quantity, 118)
        self.assertEqual(o.buysell, 'B')
        self.assertEqual(o.trade_period, 'N')
        self.assertEqual(o.open_interest, None)


class TestSubscribedBidAsks(ut.TestCase):
    @classmethod
    def setUpClass(cls):
        xml = open('tests/quotes.xml').read()
        cls.obj = QuotePacket.parse(xml)

    def test_packet(self):
        self.assertIsInstance(self.obj, QuotePacket)
        self.assertEqual(len(self.obj.items), 3)

    def test_quote1(self):
        o = self.obj.items[1]
        self.assertEqual(o.secid, 3)
        self.assertEqual(o.board, 'TQBR')
        self.assertEqual(o.seccode, 'LKOH')
        self.assertEqual(o.price, 1750.29)
        self.assertEqual(o.buy, None)
        self.assertEqual(o.sell, -1)
        self.assertEqual(o.yld, 0)

    def test_quote2(self):
        o = self.obj.items[0]
        self.assertEqual(o.secid, 1)
        self.assertEqual(o.board, 'TQBR')
        self.assertEqual(o.seccode, 'GAZP')
        self.assertEqual(o.price, 169.7)
        self.assertEqual(o.buy, 1)
        self.assertEqual(o.sell, None)
        self.assertEqual(o.yld, 0)


class TestClientPositions(ut.TestCase):
    @classmethod
    def setUpClass(cls):
        xml = open('tests/positions.xml').read()
        cls.obj = PositionPacket.parse(xml)

    def test_packet(self):
        self.assertIsInstance(self.obj, PositionPacket)
        self.assertEqual(len(self.obj.items), 3)

    def test_pos1(self):
        o = self.obj.items[0]
        self.assertIsInstance(o, SecurityPosition)
        self.assertEqual(o.secid, 1)
        self.assertEqual(o.market, 1)
        self.assertEqual(o.client, 'test/C282166')
        self.assertEqual(o.seccode, 'GAZP')
        self.assertEqual(o.name, u"Газпром ао")
        self.assertEqual(o.saldo_in, 3)
        self.assertEqual(o.saldo_min, 0)
        self.assertEqual(o.bought, 0)
        self.assertEqual(o.sold, 0)
        self.assertEqual(o.saldo, 3)
        self.assertEqual(o.order_buy, 0)
        self.assertEqual(o.order_sell, 0)

    def test_pos2(self):
        o = self.obj.items[1]
        self.assertIsInstance(o, SecurityPosition)
        self.assertEqual(o.secid, 21)
        self.assertEqual(o.market, 1)
        self.assertEqual(o.client, 'test/C282166')
        self.assertEqual(o.seccode, 'MTSI')
        self.assertEqual(o.name, u"МТС-ао")
        self.assertEqual(o.saldo_in, 0)
        self.assertEqual(o.saldo_min, 0)
        self.assertEqual(o.bought, 0)
        self.assertEqual(o.sold, 0)
        self.assertEqual(o.saldo, 0)
        self.assertEqual(o.order_buy, 0)
        self.assertEqual(o.order_sell, 0)

    def test_pos3(self):
        o = self.obj.items[2]
        self.assertIsInstance(o, MoneyPosition)
        self.assertEqual(o.market, [1])
        self.assertEqual(o.client, 'test/C282166')
        self.assertEqual(o.asset, 'FOND_MICEX')
        self.assertEqual(o.name, u"Рубли РФ КЦБ ММВБ")
        self.assertEqual(o.saldo_in, 290855.36)
        self.assertEqual(o.saldo, 290855.36)
        self.assertEqual(o.bought, 0)
        self.assertEqual(o.sold, 0)
        self.assertEqual(o.order_buy, 0)
        self.assertEqual(o.order_buy_cond, 0)
        self.assertEqual(o.commission, 0)


class TestLimitsTPlus(ut.TestCase):
    @classmethod
    def setUpClass(cls):
        xml = open('tests/limits_t+.xml').read()
        cls.obj = ClientLimitsTPlus.parse(xml)

    def test_limits(self):
        o = self.obj
        self.assertIsInstance(o, ClientLimitsTPlus)
        self.assertEqual(o.client, 'test/C282166')
        self.assertEqual(len(o.securities), 2)
        _o = o.securities[0]
        self.assertEqual(_o.secid, 21)
        self.assertEqual(_o.market, 1)
        self.assertEqual(_o.seccode, 'MTSI')
        self.assertEqual(_o.max_buy, 136)
        self.assertEqual(_o.max_sell, 100)
        _o = o.securities[1]
        self.assertEqual(_o.secid, 1)
        self.assertEqual(_o.market, 1)
        self.assertEqual(_o.seccode, 'GAZP')
        self.assertEqual(_o.max_buy, 1432)
        self.assertEqual(_o.max_sell, 1438)


class TestPits(ut.TestCase):
    @classmethod
    def setUpClass(cls):
        xml = open('tests/pits.xml').read()
        cls.obj = SecurityPitPacket.parse(xml)

    def test_packet(self):
        self.assertIsInstance(self.obj, SecurityPitPacket)
        self.assertEqual(len(self.obj.items), 3)

    def test_pit1(self):
        o = self.obj.items[1]
        self.assertEqual(o.seccode, 'GAZP')
        self.assertEqual(o.board, 'TQBR')
        self.assertEqual(o.market, 1)
        self.assertEqual(o.decimals, 2)
        self.assertEqual(o.minstep, .01)
        self.assertEqual(o.lotsize, 1)
        self.assertEqual(o.point_cost, 1)


class TestBoards(ut.TestCase):
    @classmethod
    def setUpClass(cls):
        xml = open('tests/boards.xml').read()
        cls.obj = BoardPacket.parse(xml)

    def test_packet(self):
        self.assertIsInstance(self.obj, BoardPacket)
        self.assertEqual(len(self.obj.items), 3)

    def test_board1(self):
        o = self.obj.items[1]
        self.assertEqual(o.id, 'TQBR')
        self.assertEqual(o.market, 1)
        self.assertEqual(o.type, 1)


class TestMarketOrderAbility(ut.TestCase):
    def test_some(self):
        xml = '<marketord secid="1" seccode="GAZP" permit="yes" />'
        o = MarketOrderAbility.parse(xml)
        self.assertEqual(o.secid, 1)
        self.assertEqual(o.seccode, 'GAZP')
        self.assertEqual(o.permitted, True)


class TestCreditAbility(ut.TestCase):
    def test_some(self):
        xml = '<overnight status="true"/>'
        o = CreditAbility.parse(xml)
        self.assertEqual(o.overnight, True)
        self.assertEqual(o.intraday, False)


@ut.skip('No data for sec_info')
class TestSecInfo(ut.TestCase):
    @classmethod
    def setUpClass(cls):
        xml = open('tests/secinfo.xml').read()
        cls.obj = SecInfo.parse(xml)

    def test_secinfo(self):
        o = self.obj
        self.assertEqual(o.secname, '')


@ut.skip('No data for sec_info_upd')
class TestSecInfoUpd(ut.TestCase):
    @classmethod
    def setUpClass(cls):
        xml = open('tests/secinfoupd.xml').read()
        cls.obj = SecInfo.parse(xml)

    def test_secinfo_upd(self):
        o = self.obj
        self.assertEqual(o.secname, '')

@ut.skip('No data for mct portfolio')
class TestPortfolioMCT(ut.TestCase):
    @classmethod
    def setUpClass(cls):
        xml = open('tests/portfolio_mct.xml').read()
        cls.obj = ClientPortfolioMCT.parse(xml)

    def test(self):
        o = self.obj
        self.assertEqual(o.secname, '')


if __name__ == '__main__':
    ut.main()
