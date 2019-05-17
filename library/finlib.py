import pandas as pd
from yahoofinancials import YahooFinancials
import requests
from datetime import datetime
from bs4 import BeautifulSoup

class Company(object):

    def __init__(self,ticker):
        self.ticker = ticker.upper()
        self.financials = YahooFinancials(ticker)
        self.timeframe = 'annual'
        self.balance_sheet = None
        self.income_statement = None
        self.cash_flow_statement = None
        self.key_statistics = None
        self.historical_eps = None
        self.price_data = None
        self.new_corporate_tax_rate = 0.21
        self.old_corporate_tax_rate = 0.35
        self.risk_free_ror = 0.025
        self.market_ror = 0.098

    def __set_balance_sheet(self):
        if str(type(self.balance_sheet)) == "<class 'NoneType'>":
            try:
                self.balance_sheet = self.financials.get_financial_stmts(self.timeframe,'balance')['balanceSheetHistory'][self.ticker]
                self.balance_sheet = self.__clean_statement_timestamp(self.balance_sheet)
            except:
                return None

    def __set_income_statement(self):
        if str(type(self.income_statement)) == "<class 'NoneType'>":
            try:
                self.income_statement = self.income_statement = self.financials.get_financial_stmts(self.timeframe,'income')['incomeStatementHistory'][self.ticker]
                self.income_statement = self.__clean_statement_timestamp(self.income_statement)
            except:
                return None

    def __set_cash_flow_statement(self):
        if str(type(self.cash_flow_statement)) == "<class 'NoneType'>":
            try:
                self.cash_flow_statement = self.cash_flow_statement = self.financials.get_financial_stmts(self.timeframe,'cash')['cashflowStatementHistory'][self.ticker]
                self.cash_flow_statement = self.__clean_statement_timestamp(self.cash_flow_statement)
            except:
                return None

    def __set_key_statistics(self):
        if str(type(self.key_statistics)) == "<class 'NoneType'>":
            try:
                self.key_statistics = self.financials.get_key_statistics_data()
            except:
                return None

    def __set_historical_eps(self):
        if str(type(self.historical_eps)) == "<class 'NoneType'>":
            url = 'https://www.nasdaq.com/earnings/report/{}'.format(self.ticker)
            page = requests.get(url)
            if page.status_code == 200:
                soup = BeautifulSoup(page.text,'html.parser')
                eps_list = []
                td = soup.find_all('td')
                counter = 0
                for i in td[2::5]:
                    try:
                        test = float(i.get_text())
                        counter += 1
                    except:
                        break
                for i in range(counter*5):
                    eps_list.append(list(soup.find_all('td'))[i].get_text())
                self.historical_eps = pd.DataFrame({'textdate':eps_list[0::5],'timestamp':eps_list[1::5],'eps':eps_list[2::5],'consensus_eps':eps_list[3::5],'surprise':eps_list[4::5]})
                self.historical_eps = self.historical_eps.iloc[::-1]
                self.historical_eps.reset_index(inplace=True,drop=True)
            else:
                return None

    def __set_price_data(self):
        if str(type(self.price_data)) == "<class 'NoneType'>":
            try:
                self.price_data = pd.DataFrame(self.financials.get_historical_price_data('1800-01-01',str(datetime.now())[:10],'daily')[self.ticker]['prices'])
            except:
                pass

    def __clean_statement_timestamp(self,statement):
        for i in statement:
                for j in i.keys():
                    i[j[:4]] = i.pop(j)
        return statement

    def __get_specific_year(self,statement,year):
        for i in statement:
            if str(list(i.keys())[0]) == str(year):
                return i['{}'.format(year)]

    def __json_to_dataframe(self,data):
        columns = []
        for i in data:
            for j in i.keys():
                columns.append(j)
        df = pd.DataFrame(data[0])
        for i in range(len(columns)):
            df[columns[i]] = pd.DataFrame(data[i])
        df = df[df.columns[::-1]]
        return df

    def set_risk_free_ror(self,risk_free_ror):
        self.risk_free_ror = risk_free_ror

    def set_market_ror(self,market_ror):
        self.market_ror = market_ror

    def check_risk_free_ror(self):
        return self.risk_free_ror

    def check_market_ror(self):
        return self.market_ror

    def check_old_corporate_tax_rate(self):
        return self.old_corporate_tax_rate

    def check_new_corporate_tax_rate(self):
        return self.new_corporate_tax_rate

    def get_balance_sheet(self):
        self.__set_balance_sheet()
        df = self.__json_to_dataframe(self.balance_sheet)
        return df

    def get_income_statement(self):
        self.__set_income_statement()
        df = self.__json_to_dataframe(self.income_statement)
        return df

    def get_cash_flow_statement(self):
        self.__set_cash_flow_statement()
        df = self.__json_to_dataframe(self.cash_flow_statement)
        return df

    def get_key_statistics(self):
        self.__set_key_statistics()
        ser = pd.Series(self.key_statistics[self.ticker])
        return ser

    def get_historical_eps(self):
        self.__set_historical_eps()
        return self.historical_eps

    def get_price_data(self):
        self.__set_price_data()
        return self.price_data

    def check_ticker(self):
        return self.ticker

    def revenue(self,year):
        self.__set_income_statement()
        try:
            return self.__get_specific_year(self.income_statement,year)['totalRevenue']
        except:
            return None

    def total_expenses(self,year):
        self.__set_income_statement()
        self.__set_cash_flow_statement()
        try:
            operating_expenses = self.__get_specific_year(self.income_statement,year)['totalOperatingExpenses']
            interest = self.__get_specific_year(self.income_statement,year)['interestExpense']
            tax = self.__get_specific_year(self.income_statement,year)['incomeTaxExpense']
            depreciation = self.__get_specific_year(self.cash_flow_statement,year)['depreciation']
            return abs(operating_expenses) + abs(interest) + abs(tax) + abs(depreciation)
        except:
            return None

    def operating_expenses(self,year):
        self.__set_income_statement()
        try:
            return self.__get_specific_year(self.income_statement,year)['totalOperatingExpenses']
        except:
            return None

    def outstanding_shares(self):
        self.__set_key_statistics()
        try:
            return self.get_key_statistics()['sharesOutstanding']
        except:
            return None

    def share_price(self):
        self.__set_price_data()
        try:
            return float(self.price_data[-1:]['close'])
        except:
            return None

    def market_value(self):
        try:
            return self.share_price()*self.outstanding_shares()
        except:
            return None

    def liquid_assets(self,year):
        self.__set_balance_sheet()
        try:
            return self.__get_specific_year(self.balance_sheet,year)['cash'] + self.__get_specific_year(self.balance_sheet,year)['shortTermInvestments']
        except:
            return None

    def total_debt(self,year):
        self.__set_balance_sheet()
        try:
            return self.__get_specific_year(self.balance_sheet,year)['shortLongTermDebt']+self.__get_specific_year(self.balance_sheet,year)['longTermDebt']
        except:
            return None

    def tax(self,year):
        self.__set_income_statement()
        try:
            return abs(self.__get_specific_year(self.income_statement,year)['incomeTaxExpense'])
        except:
            return None

    def interest(self,year):
        self.__set_income_statement()
        try:
            return self.__get_specific_year(self.income_statement,year)['interestExpense']
        except:
            return None

    def depreciation(self,year):
        self.__set_cash_flow_statement()
        try:
            return self.__get_specific_year(self.cash_flow_statement,year)['depreciation']
        except:
            return None

    def cost_of_revenue(self,year):
        self.__set_income_statement()
        try:
            return self.__get_specific_year(self.income_statement,year)['costOfRevenue']
        except:
            return None

    def total_receivables(self,year):
        self.__set_balance_sheet()
        try:
            return self.__get_specific_year(self.balance_sheet,year)['netReceivables']
        except:
            return None

    def total_liabilities(self,year):
        self.__set_balance_sheet()
        try:
            return self.__get_specific_year(self.balance_sheet,year)['totalLiab']
        except:
            return None

    def total_assets(self,year):
        self.__set_balance_sheet()
        try:
            return self.__get_specific_year(self.balance_sheet,year)['totalAssets']
        except:
            return None

    def total_capital(self,year):
        self.__set_balance_sheet()
        try:
            return self.__get_specific_year(self.balance_sheet,year)['totalStockholderEquity'] + self.total_debt(year)
        except:
            return None

    def total_equity(self,year):
        try:
            return self.total_assets(year) - self.total_liabilities(year)
        except:
            return None

    def capital_expenditures(self,year):
        self.__set_cash_flow_statement()
        try:
            return self.__get_specific_year(self.cash_flow_statement,year)['capitalExpenditures']
        except:
            return None

    def net_income(self,year):
        self.__set_income_statement()
        try:
            return self.__get_specific_year(self.income_statement,year)['netIncome']
        except:
            return None

    def gross_profit(self,year):
        self.__set_income_statement()
        try:
            return self.__get_specific_year(self.income_statement,year)['grossProfit']
        except:
            return None

    def earnings_per_share(self):
        try:
            return self.financials.get_earnings_per_share()
        except:
            return None

    def pe_ratio(self):
        try:
            return self.financials.get_pe_ratio()
        except:
            return None

    def enterprise_value(self):
        try:
            return self.get_key_statistics()['enterpriseValue']
        except:
            return None

    def ebit(self,year):
        self.__set_income_statement()
        try:
            return self.__get_specific_year(self.income_statement,year)['ebit']
        except:
            return None

    def ebitda(self,year):
        try:
            temp_net_income = abs(self.net_income(year))
            temp_tax = abs(self.tax(year))
            temp_interest = abs(self.interest(year))
            temp_depreciation = abs(self.depreciation(year))
            return temp_net_income + temp_tax + temp_interest + temp_depreciation
        except:
            return None

    def quick_ratio(self,year):
        try:
            temp_liquid_assets = abs(self.liquid_assets(year))
            temp_receivables = abs(self.total_receivables(year))
            temp_liabilities = abs(self.total_liabilities(year))
            return (temp_liquid_assets+temp_receivables)/temp_liabilities
        except:
            return None

    def income_continuing_operations_margin(self,year):
        try:
            temp_ebit = self.ebit(year)
            temp_revenue = abs(self.revenue(year))
            return temp_ebit/temp_revenue
        except:
            return None

    def net_margin(self,year):
        try:
            temp_net_income = self.net_income(year)
            temp_revenue = self.revenue(year)
            return temp_net_income/temp_revenue
        except:
            return None

    def return_on_assets(self,year):
        try:
            ending_year = year
            beginning_year = year - 1
            temp_net_income = self.net_income(year)
            beginning_total_assets = abs(self.total_assets(beginning_year))
            ending_total_assets = abs(self.total_assets(ending_year))
            return temp_net_income/((beginning_total_assets+ending_total_assets)/2)
        except:
            return None

    def return_on_capital(self,year):
        try:
            ending_year = year
            beginning_year = year - 1
            if ending_year >= 2018:
                temp_ebit = self.ebit(year)
                temp_tax_rate = self.new_corporate_tax_rate
                beginning_total_capital = abs(self.total_capital(beginning_year))
                ending_total_capital = abs(self.total_capital(ending_year))
                return (temp_ebit*(1-temp_tax_rate))/((beginning_total_capital+ending_total_capital)/2)
            elif ending_year < 2018:
                temp_ebit = self.ebit(year)
                temp_tax_rate = self.old_corporate_tax_rate
                beginning_total_capital = abs(self.total_capital(beginning_year))
                ending_total_capital = abs(self.total_capital(ending_year))
                return (temp_ebit*(1-temp_tax_rate))/((beginning_total_capital+ending_total_capital)/2)
        except:
            return None

    def return_on_equity(self,year):
        try:
            temp_ebit = self.ebit(year)
            temp_total_equity = abs(self.total_equity(year))
            return temp_ebit/temp_total_equity
        except:
            return None

    def cash_flow_operations(self,year):
        try:
            temp_revenue = abs(self.revenue(year))
            temp_operating_expenses = abs(self.operating_expenses(year))
            return temp_revenue-temp_operating_expenses
        except:
            return None

    def free_cash_flow(self,year):
        try:
            if year >= 2018:
                temp_cfo = self.cash_flow_operations(year)
                temp_interest = self.interest(year)
                temp_tax_rate = self.new_corporate_tax_rate
                temp_capex = self.capital_expenditures(year)
                return temp_cfo + (temp_interest*(1-temp_tax_rate)) - temp_capex
            elif year < 2018:
                temp_cfo = self.cash_flow_operations(year)
                temp_interest = self.interest(year)
                temp_tax_rate = self.old_corporate_tax_rate
                temp_capex = self.capital_expenditures(year)
                return temp_cfo + (temp_interest*(1-temp_tax_rate)) - temp_capex
        except:
            return None

    def beta(self):
        try:
            return self.financials.get_beta()
        except:
            return None

    def cost_of_equity(self):
        try:
            return self.risk_free_ror+(self.beta()*(self.market_ror-self.risk_free_ror))
        except:
            return None

    def gross_profit_margin(self,year):
        try:
            return (self.revenue(year)-self.cost_of_revenue(year))/self.revenue(year)
        except:
            return None

    def operating_profit_margin(self,year):
        try:
            return self.ebit(year)/self.revenue(year)
        except:
            return None

    def net_profit_margin(self,year):
        try:
            return self.net_income(year)/self.revenue(year)
        except:
            return None

    def short_ratio(self):
        try:
            return self.get_key_statistics()['shortRatio']
        except:
            return None
