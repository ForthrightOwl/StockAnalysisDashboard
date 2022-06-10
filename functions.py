import json
try:
    """For Python 3.0 and later"""
    from urllib.request import urlopen
except ImportError:
      """Fall back to Python 2's urllib2"""
      from urllib2 import urlopen
import pandas as pd


API_KEY="27fa7a7c3d3da5a299b15db12745f4f5"

"""Styling parameters"""
BACKGROUND_COLOR = "#edf3f4"
CONTENT_COLOR = "white"
TEXT_COLOR = "#718BA5"
BORDER_COLOR = "#8EA9C1"
FONT = "Times New Roman"
comparison_group = ["AAPL", "GOOG", "FB", "NFLX"]

"""Financial statement import"""
def request_fs(statement, ticker, limit, api_key):
  URL = f"https://financialmodelingprep.com/api/v3/{statement}/{ticker}?limit={limit}&apikey={api_key}"
  response = urlopen(URL)
  data = response.read().decode("utf-8")
  return pd.DataFrame(json.loads(data))

"""Price data import"""
def request_price_data(ticker, api_key):
  URL = f"https://financialmodelingprep.com/api/v3/historical-chart/4hour/{ticker}?apikey={api_key}"
  response = urlopen(URL)
  data = response.read().decode("utf-8")
  df = pd.DataFrame(json.loads(data))
  df["Date"] = pd.to_datetime(df["date"]).dt.date
  df = df.groupby("Date").first()
  df = df.drop(columns="date")
  return df

"""List of S&P 500 constituents import"""
def sp500_const(api_key):
  URL = f"https://financialmodelingprep.com/api/v3/sp500_constituent?apikey={api_key}"
  response = urlopen(URL)
  data = response.read().decode("utf-8")
  df = pd.DataFrame(json.loads(data))
  return df



"""Following functions merely calculate time series multiples data"""
def price_earnings(ticker, api_key):
  price = request_price_data(ticker, api_key)
  ins = request_fs("income-statement", ticker, 400, api_key)
  ins.set_index(pd.to_datetime(ins["calendarYear"]).dt.year, inplace=True)
  price.reset_index(inplace=True)
  price["calendarYear"] = pd.to_datetime(price["Date"]).dt.year -1
  pe = price[["close", "Date", "calendarYear"]]
  pe.set_index("calendarYear", inplace=True)
  pe["Earnings"] = pe.index.map(ins["eps"])
  pe.reset_index(inplace=True)
  pe.set_index("Date", inplace=True)
  pe["P/E"] = pe["close"] / pe["Earnings"]
  return pe["P/E"]

def ev_ebitda(ticker, api_key):
  price = request_price_data(ticker, api_key)
  ins = request_fs("income-statement", ticker, 400, api_key)
  ins.set_index(pd.to_datetime(ins["calendarYear"]).dt.year, inplace=True)
  bs = request_fs("balance-sheet-statement", ticker, 400, api_key)
  bs.set_index(pd.to_datetime(bs["calendarYear"]).dt.year, inplace=True)
  price.reset_index(inplace=True)
  price["calendarYear"] = pd.to_datetime(price["Date"]).dt.year -1
  pe = price[["close", "Date", "calendarYear"]]
  pe.set_index("calendarYear", inplace=True)
  pe["totalDebt"] = pe.index.map(bs["totalDebt"])
  pe["cashAndCashEquivalents"] = pe.index.map(bs["cashAndCashEquivalents"])
  pe["weightedAverageShsOut"] = pe.index.map(ins["weightedAverageShsOut"])
  pe["EBITDA"] = pe.index.map(ins["ebitda"])
  pe.reset_index(inplace=True)
  pe.set_index("Date", inplace=True)
  pe["EV"] = (pe["close"]*pe["weightedAverageShsOut"]) + pe["totalDebt"] - pe["cashAndCashEquivalents"]
  pe["EV/EBITDA"] =  pe["EV"] / pe["EBITDA"]
  return pe["EV/EBITDA"]

def price_fcfe(ticker, api_key):
  price = request_price_data(ticker, api_key)
  ins = request_fs("income-statement", ticker, 400, api_key)
  ins.set_index(pd.to_datetime(ins["calendarYear"]).dt.year, inplace=True)
  cf = request_fs("cash-flow-statement", ticker, 400, api_key)
  cf.set_index(pd.to_datetime(cf["calendarYear"]).dt.year, inplace=True)
  price.reset_index(inplace=True)
  price["calendarYear"] = pd.to_datetime(price["Date"]).dt.year - 1
  pe = price[["close", "Date", "calendarYear"]]
  pe.set_index("calendarYear", inplace=True)
  pe["weightedAverageShsOut"] = pe.index.map(ins["weightedAverageShsOut"])
  pe["OCF"] = pe.index.map(cf['netCashProvidedByOperatingActivities'])
  pe["PPE"] = pe.index.map(cf['investmentsInPropertyPlantAndEquipment'])
  pe['debtRepayment'] = pe.index.map(cf['debtRepayment'])
  pe.reset_index(inplace=True)
  pe.set_index("Date", inplace=True)
  pe["FCFE"] = pe["OCF"] + pe["PPE"] + pe["debtRepayment"]
  pe["P/FCFE"] = (pe["close"]*pe["weightedAverageShsOut"]) / (pe["FCFE"])
  return pe["P/FCFE"]

"""This function calculates the average ratio of the comparison group"""
def avg_ratio(ratio_function, comp_group, api_key):
  first = comp_group[0]
  rest = comp_group[1:]
  ratio = ratio_function(first, api_key)
  for instance in rest:
    ratio = ratio.add(ratio_function(instance, api_key), fill_value=0)
  ratio = ratio.divide(len(comp_group))
  return ratio

"""Calculates the difference between the ratio of a given stock and the average of the comparison group"""
def stock_comparison_difference(stock, comp_group, ratio_function, api_key):
  ratio = ratio_function(stock, api_key)
  ratio = ratio.sub(avg_ratio(ratio_function, comp_group, api_key))
  ratio = ratio.rename("ratio_diff")
  return ratio

"""Turns the ratio difference into a percentile ranking"""
def stock_comparison_difference_percentile(stock, comp_group, ratio_function, api_key):
  df = pd.DataFrame(stock_comparison_difference(stock, comp_group, ratio_function, api_key))
  df["pct_rank"] = df["ratio_diff"].rank(pct=True)
  return df["pct_rank"]