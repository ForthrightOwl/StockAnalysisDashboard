import json
try:
    """For Python 3.0 and later"""
    from urllib.request import urlopen
except ImportError:
      """Fall back to Python 2's urllib2"""
      from urllib2 import urlopen
import pandas as pd


API_KEY = "27fa7a7c3d3da5a299b15db12745f4f5"

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
def stock_comparison_difference(stock, ratio_comp, ratio_function, api_key):
  ratio = ratio_function(stock, api_key)
  ratio = ratio.sub(ratio_comp)
  ratio = ratio.rename("ratio_diff")
  return ratio

"""Turns the ratio difference into a percentile ranking"""
def stock_comparison_difference_percentile(stock, ratio_comp, ratio_function, api_key):
  df = pd.DataFrame(stock_comparison_difference(stock, ratio_comp, ratio_function, api_key))
  df["pct_rank"] = df["ratio_diff"].rank(pct=True)
  return df["pct_rank"]

"""Following functionc calculate contributionary factors to each of the multiples"""
def price_earnings_contribution(ticker, start_date, api_key):
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
  pe["Earnings cont."] = pe["close"] - (pe.loc[start_date]["Earnings"] * pe["P/E"])
  pe["P/E cont."] = (pe["close"] - (pe["Earnings"] * pe.loc[start_date]["P/E"]))
  return pe[["Earnings cont.", "P/E cont."]]

def ev_ebitda_contribution(ticker, start_date, api_key):
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
  pe["EBITDA cont."] = pe["EV"] - (pe.loc[start_date]["EBITDA"] * pe["EV/EBITDA"])
  pe["EV/EBITDA cont."] = pe["EV"] - (pe["EBITDA"] * pe.loc[start_date]["EV/EBITDA"])
  return pe[["EBITDA cont.", "EV/EBITDA cont."]]

def price_fcfe_contribution(ticker, start_date, api_key):
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
  pe["FCFE cont."] = (pe["close"]*pe["weightedAverageShsOut"]) - (pe.loc[start_date]["FCFE"] * pe["P/FCFE"])
  pe["P/FCFE cont."] = (pe["close"]*pe["weightedAverageShsOut"]) - (pe["FCFE"] * pe.loc[start_date]["P/FCFE"])
  return pe[["FCFE cont.", "P/FCFE cont."]]

"""Following functions organize the income statement into desired formats"""
def curate_is(ins):
  ins = ins.rename(columns={"calendarYear":"Calendar year"})
  ins.set_index("Calendar year", inplace=True)
  ins = ins[["revenue", "costOfRevenue", "grossProfit", "researchAndDevelopmentExpenses", "generalAndAdministrativeExpenses", "sellingAndMarketingExpenses",
            "sellingGeneralAndAdministrativeExpenses", "depreciationAndAmortization", "otherExpenses", "operatingExpenses", "operatingIncome","interestIncome", "interestExpense",
            "totalOtherIncomeExpensesNet", "incomeBeforeTax", "incomeTaxExpense", "netIncome"]]
  ins = ins.rename(columns = {"revenue":"Revenue",
                        "costOfRevenue":"Cost of sales",
                        "grossProfit":"Gross profit",
                        "researchAndDevelopmentExpenses":"Research and development",
                        "generalAndAdministrativeExpenses":"General and administrative expenses",
                        "sellingAndMarketingExpenses":"Selling and administrative expenses",
                        "sellingAndMarketingExpenses":"Selling and marketing expenses",
                        "sellingGeneralAndAdministrativeExpenses":"Selling general and administrative expenses",
                        "otherExpenses": "Other expenses",
                        "operatingExpenses": "Total operating expenses",
                        "operatingIncome": "Operating Income",
                        "interestIncome": "Interest income",
                        "interestExpense": "Interest expense",
                        "depreciationAndAmortization": "Depreciation and amortization",
                        "totalOtherIncomeExpensesNet": "Total other income net of expenses",
                        "incomeBeforeTax": "Income before tax",
                        "incomeTaxExpense": "Income tax expense",
                        "netIncome": "Net income",
                        })
  return ins

def curate_ratio_is(ins):
  ins = curate_is(ins)
  rv = ins["Revenue"]
  ins = ins.div(rv, axis=0)
  return ins

def accessory_is(ins):
  ins = ins.copy()
  ins = ins.rename(columns={"calendarYear":"Calendar year"})
  ins.set_index("Calendar year", inplace=True)
  ins = ins[["ebitda", "weightedAverageShsOut", "eps", "weightedAverageShsOutDil", "epsdiluted"]]
  ins = ins.rename(columns={"ebitda":"EBITDA",
                      "netIncome":"Net income",
                      "weightedAverageShsOut":"Shares outstanding",
                      "eps":"EPS",
                      "weightedAverageShsOutDil": "Shares outstanding, diluted",
                      "epsdiluted":"EPS, diluted"})
  return ins

def accessory_ratio_is(ins):
  inst = accessory_is(ins)
  rev = curate_is(ins)
  rev = rev["Revenue"]
  inst["EBITDA"] = inst["EBITDA"] / rev
  return inst

"""Following functions organize the balance sheet into desired formats"""
def curate_bs(bs):
  bs = bs[['calendarYear', 'cashAndCashEquivalents',
       'shortTermInvestments', 'netReceivables',
       'inventory', 'otherCurrentAssets', 'totalCurrentAssets',
       'propertyPlantEquipmentNet', 'goodwill', 'intangibleAssets',
       'longTermInvestments', 'taxAssets',
       'otherNonCurrentAssets', 'totalNonCurrentAssets', 'otherAssets',
       'totalAssets', 'accountPayables', 'shortTermDebt', 'taxPayables',
       'deferredRevenue', 'otherCurrentLiabilities', 'totalCurrentLiabilities',
       'longTermDebt', 'deferredRevenueNonCurrent',
       'deferredTaxLiabilitiesNonCurrent', 'otherNonCurrentLiabilities',
       'totalNonCurrentLiabilities', 'otherLiabilities',
       'capitalLeaseObligations', 'totalLiabilities', 'preferredStock',
       'commonStock', 'retainedEarnings',
       'accumulatedOtherComprehensiveIncomeLoss',
       'othertotalStockholdersEquity', 'totalStockholdersEquity',
       'totalLiabilitiesAndStockholdersEquity', 'minorityInterest',
       'totalEquity', 'totalLiabilitiesAndTotalEquity']]
  bs = bs.rename(columns={
      "calendarYear":"Calendar Year",
      'cashAndCashEquivalents':"Cash and cash equivalents",
       'shortTermInvestments': "Short term investments",
       'netReceivables':"Net receivables",
       'inventory':"Inventory",
       'otherCurrentAssets': "Other current assets",
       'totalCurrentAssets': "Total current assets",
       'propertyPlantEquipmentNet': "Property, plant and equipment",
       'goodwill': "Goodwill",
       'intangibleAssets': "Intangible assets",
       'longTermInvestments': "Long term investments",
       'taxAssets' :"Tax assets",
       'otherNonCurrentAssets': "Other non current assets",
       'totalNonCurrentAssets': "Total non current assets",
       'otherAssets': "Other assets",
       'totalAssets': "Total assets",
       'accountPayables': "Account payables",
       'shortTermDebt': "Short term debt",
       'taxPayables': "Tax payables",
       'deferredRevenue': "Deferred revenue",
       'otherCurrentLiabilities': "Other current liabilities",
       'totalCurrentLiabilities': "Total current liabilities",
       'longTermDebt': "Long term debt",
       'deferredRevenueNonCurrent': "Deferred revenue, non current",
       'deferredTaxLiabilitiesNonCurrent': "Deferred tax liabilities, non current",
       'otherNonCurrentLiabilities': "Other non current liabilities",
       'totalNonCurrentLiabilities': "Total non current liabilities",
       'otherLiabilities': "Other liabilities",
       'capitalLeaseObligations': "Capital lease obligations",
       'totalLiabilities': "Total liabilities",
       'preferredStock': "Preferred stock",
       'commonStock': "Common stock",
       'retainedEarnings': "Retained Earnings",
       'accumulatedOtherComprehensiveIncomeLoss': "Accumulated other comprehensive income loss",
       'othertotalStockholdersEquity': "Other total stockholders equity",
       'totalStockholdersEquity': "Total stockholders Equity",
       'totalLiabilitiesAndStockholdersEquity': "Total liabilities and stockholders equity",
       'minorityInterest': "Minority interest",
       'totalEquity': "Total equity",
       'totalLiabilitiesAndTotalEquity': "Total liabilities and total equity"})
  bs.set_index("Calendar Year", inplace=True)
  return bs

def curate_ratio_bs(bs):
  bs = curate_bs(bs)
  ta = bs["Total assets"]
  bs = bs.div(ta, axis=0)
  return bs

def accessory_bs(bs):
  bs = bs[['calendarYear', 'totalLiabilities', 'totalEquity', 'cashAndCashEquivalents',
             'shortTermInvestments', 'netReceivables', 'totalCurrentLiabilities', 'totalCurrentAssets']]
  bs = bs.rename(columns={'calendarYear': "Calendar Year"})
  bs.set_index("Calendar Year", inplace=True)
  bs["Leverage"] = bs['totalLiabilities'] / bs['totalEquity']
  bs["Quick ratio"] = (bs['cashAndCashEquivalents'] + bs['shortTermInvestments'] + bs['netReceivables']) / bs['totalCurrentLiabilities']
  bs["Working capital"] = bs['totalCurrentAssets'] - bs['totalCurrentLiabilities']
  bs = bs[["Leverage", "Quick ratio", "Working capital"]]
  return bs

"""Following functions organize the cash flow statement into desired formats"""
def curate_cf(cf):
  cf = cf[['calendarYear', 'netIncome',
       'depreciationAndAmortization', 'deferredIncomeTax',
       'stockBasedCompensation', 'changeInWorkingCapital',
       'accountsReceivables', 'inventory', 'accountsPayables',
       'otherWorkingCapital', 'otherNonCashItems',
       'netCashProvidedByOperatingActivities',
       'investmentsInPropertyPlantAndEquipment', 'acquisitionsNet',
       'purchasesOfInvestments', 'salesMaturitiesOfInvestments',
       'otherInvestingActivites', 'netCashUsedForInvestingActivites',
       'debtRepayment', 'commonStockIssued', 'commonStockRepurchased',
       'dividendsPaid', 'otherFinancingActivites',
       'netCashUsedProvidedByFinancingActivities',
       'effectOfForexChangesOnCash', 'netChangeInCash',
       'cashAtBeginningOfPeriod', 'cashAtEndOfPeriod',
       ]]
  cf = cf.rename(columns={
      'calendarYear': "Calendar Year",
      'netIncome': "Net income",
       'depreciationAndAmortization': "Depreciationa and amortization",
       'deferredIncomeTax': "Deferred income tax",
       'stockBasedCompensation': "Stock based compensation",
       'changeInWorkingCapital': "Change in working capital",
       'accountsReceivables': "Accounts receivables",
       'inventory': "Inventory",
       'accountsPayables': "Accounts payables",
       'otherWorkingCapital': "Other working capital",
       'otherNonCashItems': "Other non cash items",
       'netCashProvidedByOperatingActivities': "Net cash provided by operating activities",
       'investmentsInPropertyPlantAndEquipment': "Investments in PPE",
       'acquisitionsNet': "Acquisitions net",
       'purchasesOfInvestments': "Purchases of investments",
       'salesMaturitiesOfInvestments': "Sales and maturities of investments",
       'otherInvestingActivites': "Other investing activities",
       'netCashUsedForInvestingActivites': "Net cash used for investing activities",
       'debtRepayment': "Debt repayments",
       'commonStockIssued': "Common stock issued",
       'commonStockRepurchased': "Common stock repurchased",
       'dividendsPaid': "Dividends Paid",
       'otherFinancingActivites': "Other financing activities",
       'netCashUsedProvidedByFinancingActivities': "Net cash used or provided by financing activities",
       'effectOfForexChangesOnCash': "Effect of forex changes on cash",
       'netChangeInCash': "Net change in cash",
       'cashAtEndOfPeriod': "Cash at the end of period",
       'cashAtBeginningOfPeriod': "Cash at beginning of period"
         })
  cf.set_index("Calendar Year", inplace=True)
  return cf

def curate_ratio_cf(cf):
  cf = curate_cf(cf)
  ta = cf["Net income"]
  cf = cf.div(ta, axis=0)
  return cf

def accessory_cf(cf):
  cf = cf[['calendarYear', 'operatingCashFlow', 'capitalExpenditure', 'freeCashFlow']]
  cf["capitalExpenditure"] = cf["capitalExpenditure"] * -1
  cf = cf.rename(columns={
      'calendarYear':"Calendar Year",
      'operatingCashFlow': "Operating cash flow",
      'capitalExpenditure': "Capital expenditure",
      'freeCashFlow': "Free cash flow"
         })
  cf.set_index("Calendar Year", inplace=True)
  return cf

def accessory_ratio_cf(cf):
  cf = accessory_cf(cf)
  ni = curate_cf("AAPL")
  ni = ni["Net income"]
  cf = cf.div(ni, axis=0)
  return cf

"""Computes the specified function for each component in the comp group, adds them all together then divides by the length of the comp group. """
def comp_avg(comp_group, function):
  df = function(comp_group[0])
  comp_group_2 = comp_group[1:]
  for comp in comp_group_2:
    df = df.add(function(comp), fill_value=0)
  df = df.divide(len(comp_group))
  return df
