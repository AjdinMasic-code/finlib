import pandas as pd
from yahoofinancials import YahooFinancials
import matplotlib.pyplot as plt
import requests
from bs4 import BeautifulSoup

class Formulas(object):

    def total_expenses(operating_expenses,interest,tax,depreciation):
        return abs(operating_expenses) + abs(interest) + abs(tax) + abs(depreciation)

    def net_income(revenue,total_expenses):
        return abs(revenue)-(abs(total_expenses))

    def gross_profit(revenue,operating_expenses):
        return abs(revenue)-(abs(operating_expenses))

    def earnings_per_share(net_income,outstanding_shares):
        return abs(net_income)/abs(outstanding_shares)

    def pe_ratio(share_price,earnings_per_share):
        return abs(share_price)/abs(earnings_per_share)

    def enterprise_value(market_value,liquid_assets,total_debt):
        return abs(market_value) - abs(liquid_assets) + abs(total_debt)

    def ebitda(net_income,tax,interest,depreciation,amortization):
        return abs(net_income)+abs(tax)+abs(interest)+abs(depreciation)+abs(amortization)

    def ebit(revenue,cost_of_goods_sold,operating_expenses,depreciation,amortization):
        return abs(revenue) - abs(cost_of_goods_sold) - abs(operating_expenses) - abs(depreciation) - abs(amortization)

    def quick_ratio(liquid_assets,receivables,liabilities):
        return (abs(liquid_assets)+abs(receivables))/abs(liabilities)

    def income_continuing_operations_margin(ebit,revenue):
        return abs(ebit)/abs(revenue)

    def net_margin(net_income,revenue):
        return abs(net_income)/abs(revenue)

    def return_on_assets(net_income,beginning_total_assets,ending_total_assets):
        return abs(net_income)/((abs(beginning_total_assets)+abs(ending_total_assets))/2)

    def return_on_capital(ebit,corporate_tax_rate,beginning_total_capital,ending_total_capital):
        return (abs(ebit)*(1-abs(corporate_tax_rate)))/((abs(beginning_total_capital)+abs(ending_total_capital))/2)

    def return_on_equity(income_continuing_operations,total_equity):
        return abs(income_continuing_operations)/abs(total_equity)

    def growth_rate(beginning_figure,ending_figure):
        return (abs(ending_figure)-abs(beginning_figure))/abs(beginning_figure)

    def cash_flow_operations(revenue,operating_expenses):
        return abs(revenue-operating_expenses)

    def free_cash_flow(cash_flow_operations,interest,corporate_tax_rate,capital_expenditures):
        return abs(cash_flow_operations) + (abs(interest)*(1-abs(corporate_tax_rate))) - abs(capital_expenditures)

    def beta(risk_free_ror,security_ror,market_ror):
        return (abs(stocks_ror)-abs(risk_free_ror))/(abs(market_ror)-abs(risk_free_ror))

    def cost_of_equity(risk_free_ror, beta, market_ror):
        return abs(risk_free_ror)+(abs(beta)*(abs(market_ror)-abs(risk_free_ror)))

    def gross_profit_margin(revenue, cost_of_goods_sold):
        return (abs(revenue)-abs(cost_of_goods_sold))/abs(revenue)

    def operating_profit_margin(ebit,revenue):
        return abs(ebit)/abs(revenue)

    def net_profit_margin(net_income,revenue):
        return abs(net_income)/abs(revenue)

    def short_outstanding_ratio(shares_short,outstanding_shares):
        return abs(shares_short)/abs(outstanding_shares)

class DataRetrieval(object):

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

    def __set_balance_sheet(self):
        if self.balance_sheet == None:
            try:
                self.balance_sheet = self.financials.get_financial_stmts(self.timeframe,'balance')['balanceSheetHistory'][self.ticker]
                self.balance_sheet = self.__clean_statement_timestamp(self.balance_sheet)
            except:
                return "Error: Could not retrieve balance sheet"

    def __set_income_statement(self):
        if self.income_statement == None:
            try:
                self.income_statement = self.income_statement = self.financials.get_financial_stmts(self.timeframe,'income')['incomeStatementHistory'][self.ticker]
                self.income_statement = self.__clean_statement_timestamp(self.income_statement)
            except:
                return "Error: Could not retrieve income statement"

    def __set_cash_flow_statement(self):
        if self.cash_flow_statement == None:
            try:
                self.cash_flow_statement = self.cash_flow_statement = self.financials.get_financial_stmts(self.timeframe,'cash')['cashflowStatementHistory'][self.ticker]
                self.cash_flow_statement = self.__clean_statement_timestamp(self.cash_flow_statement)
            except:
                return "Error: Could not retrieve cash flow statement"

    def __set_key_statistics(self):
        if self.key_statistics == None:
            try:
                self.key_statistics = self.financials.get_key_statistics_data()
            except:
                return "Error: Could not retrieve key statistics"

    def __set_historical_eps(self):
        if self.historical_eps == None:
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
                return "Error: Could not connect to NASDAQ website"

    def __set_price_data(self):
        if self.price_data == None:
            try:
                self.price_data = pd.DataFrame(self.financials.get_historical_price_data('1800-01-01',str(datetime.now())[:10],'daily')[self.ticker]['prices'])
            except:
                "Error: Could not retrieve historical price data"

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
            return Formulas.total_expenses(operating_expenses,interest,tax,depreciation)
        except:
            return None


    def operating_expenses(self,year):
        self.__set_cash_flow_statement()
        try:
            return self.__get_specific_year(self.cash_flow_statement,year)['totalOperatingExpenses']
        except:
            return None

    def outstanding_shares(self):
        self.__set_key_statistics()
        try:
            return self.key_statistics[self.ticker]['sharesOutstanding']
        except:
            return None

    def share_price(self):
        pass

    def market_value(self):
        pass

    def liquid_assets(self):
        pass

    def total_debt(self):
        pass

    def total_debt(self):
        pass

    def tax(self):
        return Formulas.gross_profit(self.revenue(),self.operating_expenses()) * (1-self.corporate_tax_rate)

    def interest(self):
        pass

    def depreciation(self):
        pass

    def amortization(self):
        pass

    def cost_of_goods_sold(self):
        pass

    def receivables(self):
        pass

    def liabilities(self):
        pass

    def total_assets(self):
        pass

    def total_capital(self):
        pass

    def total_equity(self):
        pass

    def capital_expenditures(self):
        pass
