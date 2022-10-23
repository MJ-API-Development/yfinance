from .context import yfinance as yf

import unittest

import datetime as _dt
import pytz as _tz
import numpy as _np

class TestPriceHistory(unittest.TestCase):
	def setUp(self):
		pass

	def tearDown(self):
		pass


	def test_duplicatingDaily(self):
		tkrs = []
		tkrs.append("IMP.JO")
		tkrs.append("BHG.JO")
		tkrs.append("SSW.JO")
		tkrs.append("BP.L")
		tkrs.append("INTC")
		test_run = False
		for tkr in tkrs:
			dat = yf.Ticker(tkr)
			tz = dat._get_ticker_tz()

			dt_utc = _tz.timezone("UTC").localize(_dt.datetime.utcnow())
			dt = dt_utc.astimezone(_tz.timezone(tz))
			if dt.time() < _dt.time(17,0):
				continue
			test_run = True

			df = dat.history(start=dt.date()-_dt.timedelta(days=7), interval="1d")

			dt0 = df.index[-2]
			dt1 = df.index[-1]
			try:
				self.assertNotEqual(dt0, dt1)
			except:
				print("Ticker = ", tkr)
				raise

		if not test_run:
			self.skipTest("Skipping test_duplicatingDaily() because only expected to fail just after market close")


	def test_duplicatingWeekly(self):
		tkrs = ['MSFT', 'IWO', 'VFINX', '^GSPC', 'BTC-USD']
		test_run = False
		for tkr in tkrs:
			dat = yf.Ticker(tkr)
			tz = dat._get_ticker_tz()

			dt = _tz.timezone(tz).localize(_dt.datetime.now())
			if dt.date().weekday() not in [1,2,3,4]:
				continue
			test_run = True

			df = dat.history(start=dt.date()-_dt.timedelta(days=7), interval="1wk")
			dt0 = df.index[-2]
			dt1 = df.index[-1]
			try:
				self.assertNotEqual(dt0.week, dt1.week)
			except:
				print("Ticker={}: Last two rows within same week:".format(tkr))
				print(df.iloc[df.shape[0]-2:])
				raise

		if not test_run:
			self.skipTest("Skipping test_duplicatingWeekly() because not possible to fail Monday/weekend")


	def test_intraDayWithEvents(self):
		# TASE dividend release pre-market, doesn't merge nicely with intra-day data so check still present

		tkr = "ICL.TA"
		# tkr = "ESLT.TA"
		# tkr = "ONE.TA"
		# tkr = "MGDL.TA"
		start_d = _dt.date.today() - _dt.timedelta(days=60)
		end_d = None
		df_daily = yf.Ticker(tkr).history(start=start_d, end=end_d, interval="1d", actions=True)
		df_daily_divs = df_daily["Dividends"][df_daily["Dividends"]!=0]
		if df_daily_divs.shape[0]==0:
			self.skipTest("Skipping test_intraDayWithEvents() because 'ICL.TA' has no dividend in last 60 days")
		
		last_div_date = df_daily_divs.index[-1]
		start_d = last_div_date.date()
		end_d = last_div_date.date() + _dt.timedelta(days=1)
		df = yf.Ticker(tkr).history(start=start_d, end=end_d, interval="15m", actions=True)
		self.assertTrue((df["Dividends"]!=0.0).any())


	def test_dailyWithEvents(self):
		# Reproduce issue #521
		tkr1 = "QQQ"
		tkr2 = "GDX"
		start_d = "2014-12-29"
		end_d = "2020-11-29"
		df1 = yf.Ticker(tkr1).history(start=start_d, end=end_d, interval="1d", actions=True)
		df2 = yf.Ticker(tkr2).history(start=start_d, end=end_d, interval="1d", actions=True)
		try:
			self.assertTrue(df1.index.equals(df2.index))
		except:
			missing_from_df1 = df2.index.difference(df1.index)
			missing_from_df2 = df1.index.difference(df2.index)
			print("{} missing these dates: {}".format(tkr1, missing_from_df1))
			print("{} missing these dates: {}".format(tkr2, missing_from_df2))
			raise

		# Test that index same with and without events:
		tkrs = [tkr1, tkr2]
		for tkr in tkrs:
			df1 = yf.Ticker(tkr).history(start=start_d, end=end_d, interval="1d", actions=True)
			df2 = yf.Ticker(tkr).history(start=start_d, end=end_d, interval="1d", actions=False)
			try:
				self.assertTrue(df1.index.equals(df2.index))
			except:
				missing_from_df1 = df2.index.difference(df1.index)
				missing_from_df2 = df1.index.difference(df2.index)
				print("{}-with-events missing these dates: {}".format(tkr, missing_from_df1))
				print("{}-without-events missing these dates: {}".format(tkr, missing_from_df2))
				raise


	def test_weeklyWithEvents(self):
		# Reproduce issue #521
		tkr1 = "QQQ"
		tkr2 = "GDX"
		start_d = "2014-12-29"
		end_d = "2020-11-29"
		df1 = yf.Ticker(tkr1).history(start=start_d, end=end_d, interval="1wk", actions=True)
		df2 = yf.Ticker(tkr2).history(start=start_d, end=end_d, interval="1wk", actions=True)
		try:
			self.assertTrue(df1.index.equals(df2.index))
		except:
			missing_from_df1 = df2.index.difference(df1.index)
			missing_from_df2 = df1.index.difference(df2.index)
			print("{} missing these dates: {}".format(tkr1, missing_from_df1))
			print("{} missing these dates: {}".format(tkr2, missing_from_df2))
			raise

		# Test that index same with and without events:
		tkrs = [tkr1, tkr2]
		for tkr in tkrs:
			df1 = yf.Ticker(tkr).history(start=start_d, end=end_d, interval="1wk", actions=True)
			df2 = yf.Ticker(tkr).history(start=start_d, end=end_d, interval="1wk", actions=False)
			try:
				self.assertTrue(df1.index.equals(df2.index))
			except:
				missing_from_df1 = df2.index.difference(df1.index)
				missing_from_df2 = df1.index.difference(df2.index)
				print("{}-with-events missing these dates: {}".format(tkr, missing_from_df1))
				print("{}-without-events missing these dates: {}".format(tkr, missing_from_df2))
				raise


	def test_monthlyWithEvents(self):
		tkr1 = "QQQ"
		tkr2 = "GDX"
		start_d = "2014-12-29"
		end_d = "2020-11-29"
		df1 = yf.Ticker(tkr1).history(start=start_d, end=end_d, interval="1mo", actions=True)
		df2 = yf.Ticker(tkr2).history(start=start_d, end=end_d, interval="1mo", actions=True)
		try:
			self.assertTrue(df1.index.equals(df2.index))
		except:
			missing_from_df1 = df2.index.difference(df1.index)
			missing_from_df2 = df1.index.difference(df2.index)
			print("{} missing these dates: {}".format(tkr1, missing_from_df1))
			print("{} missing these dates: {}".format(tkr2, missing_from_df2))
			raise

		# Test that index same with and without events:
		tkrs = [tkr1, tkr2]
		for tkr in tkrs:
			df1 = yf.Ticker(tkr).history(start=start_d, end=end_d, interval="1mo", actions=True)
			df2 = yf.Ticker(tkr).history(start=start_d, end=end_d, interval="1mo", actions=False)
			try:
				self.assertTrue(df1.index.equals(df2.index))
			except:
				missing_from_df1 = df2.index.difference(df1.index)
				missing_from_df2 = df1.index.difference(df2.index)
				print("{}-with-events missing these dates: {}".format(tkr, missing_from_df1))
				print("{}-without-events missing these dates: {}".format(tkr, missing_from_df2))
				raise


	def test_tz_dst_ambiguous(self):
		# Reproduce issue #1100

		try:
			yf.Ticker("ESLT.TA").history(start="2002-10-06", end="2002-10-09", interval="1d")
		except _tz.exceptions.AmbiguousTimeError:
			raise Exception("Ambiguous DST issue not resolved")


	def test_repair_weekly(self):
		# Sometimes, Yahoo returns prices 100x the correct value. 
		# Suspect mixup between £/pence or $/cents etc.
		# E.g. ticker PNL.L

		tkr = "PNL.L"
		start = "2020-01-01"
		end = min(_dt.date.today(), _dt.date(2023,1,1))
		dat = yf.Ticker(tkr)

		data_cols = ["Low","High","Open","Close","Adj Close"]
		df_bad = dat.history(start=start, end=end, interval="1wk", auto_adjust=False, repair=False)
		f_outlier = _np.where(df_bad[data_cols]>1000.0)
		indices = None
		if len(f_outlier[0])==0:
			self.skipTest("Skipping test_repair_weekly() because no price 100x errors to repair")

		# Outliers detected
		indices = []
		for i in range(len(f_outlier[0])):
			indices.append((f_outlier[0][i], f_outlier[1][i]))

		df = dat.history(start=start, end=end, interval="1wk", auto_adjust=False, repair=True)

		# First test - no errors left
		df_data = df[data_cols].values
		for i,j in indices:
			try:
				self.assertTrue(df_data[i,j] < 1000.0)
			except:
				print("Detected uncorrected error: idx={}, {}={}".format(df.index[i], data_cols[j], df_data[i,j]))
				# print(df.iloc[i-1:i+2])
				raise

		# Second test - all differences should be either ~1x or ~100x
		ratio = df_bad[data_cols].values/df[data_cols].values
		ratio = ratio.round(2)
		# - round near-100 ratio to 100:
		f = ratio>90
		ratio[f] = (ratio[f]/10).round().astype(int)*10 # round ratio to nearest 10
		# - now test
		f_100 = ratio==100
		f_1 = ratio==1
		self.assertTrue((f_100|f_1).all())


	def test_repair_weekly2_preSplit(self):
		# Sometimes, Yahoo returns prices 100x the correct value. 
		# Suspect mixup between £/pence or $/cents etc.
		# E.g. ticker PNL.L

		# PNL.L has a stock-split in 2022. Sometimes requesting data before 2022 is not split-adjusted.

		tkr = "PNL.L"
		start = "2020-01-06"
		end = "2021-06-01"
		import requests_cache ; session = requests_cache.CachedSession("/home/gonzo/.cache/yfinance.cache")
		dat = yf.Ticker(tkr, session=session)

		data_cols = ["Low","High","Open","Close","Adj Close"]
		df_bad = dat.history(start=start, end=end, interval="1wk", auto_adjust=False, repair=False)
		f_outlier = _np.where(df_bad[data_cols]>1000.0)
		indices = None
		if len(f_outlier[0])==0:
			self.skipTest("Skipping test_repair_weekly() because no price 100x errors to repair")

		# Outliers detected
		indices = []
		for i in range(len(f_outlier[0])):
			indices.append((f_outlier[0][i], f_outlier[1][i]))

		df = dat.history(start=start, end=end, interval="1wk", auto_adjust=False, repair=True)

		# First test - no errors left
		df_data = df[data_cols].values
		for i,j in indices:
			try:
				self.assertTrue(df_data[i,j] < 1000.0)
			except:
				print("Detected uncorrected error: idx={}, {}={}".format(df.index[i], data_cols[j], df_data[i,j]))
				# print(df.iloc[i-1:i+2])
				raise

		# Second test - all differences should be either ~1x or ~100x
		ratio = df_bad[data_cols].values/df[data_cols].values
		ratio = ratio.round(2)
		# - round near-100 ratio to 100:
		f = ratio>90
		ratio[f] = (ratio[f]/10).round().astype(int)*10 # round ratio to nearest 10
		# - now test
		f_100 = ratio==100
		f_1 = ratio==1
		try:
			self.assertTrue((f_100|f_1).all())
		except:
			f_bad = ~(f_100|f_1)
			print("df_bad[f_bad]:")
			print(df_bad[f_bad.any(axis=1)])
			print("df[f_bad]:")
			print(df[f_bad.any(axis=1)])
			print("ratio[f_bad]")
			print(ratio[f_bad])
			raise


	def test_repair_daily(self):
		# Sometimes, Yahoo returns prices 100x the correct value. 
		# Suspect mixup between £/pence or $/cents etc.
		# E.g. ticker PNL.L

		tkr = "PNL.L"
		start = "2020-01-01"
		end = min(_dt.date.today(), _dt.date(2023,1,1))
		dat = yf.Ticker(tkr)

		data_cols = ["Low","High","Open","Close","Adj Close"]
		df_bad = dat.history(start=start, end=end, interval="1d", auto_adjust=False, repair=False)
		f_outlier = _np.where(df_bad[data_cols]>1000.0)
		indices = None
		if len(f_outlier[0])==0:
			self.skipTest("Skipping test_repair_daily() because no price 100x errors to repair")

		# Outliers detected
		indices = []
		for i in range(len(f_outlier[0])):
			indices.append((f_outlier[0][i], f_outlier[1][i]))

		df = dat.history(start=start, end=end, interval="1d", auto_adjust=False, repair=True)

		# First test - no errors left
		df_data = df[data_cols].values
		for i,j in indices:
			try:
				self.assertTrue(df_data[i,j] < 1000.0)
			except:
				print("Detected uncorrected error: idx={}, {}={}".format(df.index[i], data_cols[j], df_data[i,j]))
				# print(df.iloc[i-1:i+2])
				raise

		# Second test - all differences should be either ~1x or ~100x
		ratio = df_bad[data_cols].values/df[data_cols].values
		ratio = ratio.round(2)
		# - round near-100 ratio to 100:
		f = ratio>90
		ratio[f] = (ratio[f]/10).round().astype(int)*10 # round ratio to nearest 10
		# - now test
		f_100 = ratio==100
		f_1 = ratio==1
		self.assertTrue((f_100|f_1).all())


if __name__ == '__main__':
	unittest.main()
