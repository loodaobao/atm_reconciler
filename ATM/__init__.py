import sys
from os.path import abspath, join, dirname
import datetime

project_dir = join(dirname('__file__'),"..")
sys.path.insert(0,project_dir)
import Texts as txt

class ATM:
    def __init__(self, tid, statement_df):
        self._tid = tid
        self._statement_df = statement_df
        self._total_debits = statement_df[txt.STATEMENT_HEADER_DEBIT].sum()
        self._total_credits= statement_df[txt.STATEMENT_HEADER_CREDIT].sum()
        self._operating_companies = statement_df[txt.STATEMENT_HEADER_ACCOUNT].unique().tolist()
    def get_operating_companies(self):
        return "/".join([str(x) for x in self._operating_companies])
    def get_last_activity_summary(self):
        return self._statement_df[-10:].to_string(index_names=False, justify='left')

    def get_tid(self):
        return self._tid
    def get_company_balance(self, return_type = dict):
        balances = {}
        for company in self._operating_companies:
            statement_for_company = self._statement_df[self._statement_df[txt.STATEMENT_HEADER_ACCOUNT]==company]
            balances[company] = statement_for_company[txt.STATEMENT_HEADER_DEBIT].sum() - statement_for_company[txt.STATEMENT_HEADER_CREDIT].sum()
        if return_type == dict:
            return balances
        elif return_type == str:
            combined_text = ""
            company_balance_text= "{account} Balance: {balance:,}\n\t"
            for account, balance in balances.items():
                combined_text += company_balance_text.format(account = account, balance= balance)
            return combined_text

    def get_balance(self):
        return self._total_debits - self._total_credits

    def get_last_funding_date(self):
        debits = self._statement_df[~(self._statement_df[txt.STATEMENT_HEADER_DEBIT].isnull())]
        try:
            return self._statement_df[~(self._statement_df[txt.STATEMENT_HEADER_DEBIT].isnull())].iloc[-1][txt.STATEMENT_HEADER_DATE]
        except:
            print("{} has no funidng date".format(self._tid))
            return None
    def get_last_inflow_date(self):
        try:
            return self._statement_df[~(self._statement_df[txt.STATEMENT_HEADER_CREDIT].isnull())].iloc[-1][txt.STATEMENT_HEADER_DATE]
        except:
            print("{} has no inflow date".format(self._tid))
            return None
    def get_days_to_last_activity(self):
        if self.get_last_inflow_date():
            time_delta = datetime.datetime.today() - self.get_last_inflow_date()
        else:
            time_delta = datetime.datetime.today() - self.get_last_funding_date()
        return time_delta.days
