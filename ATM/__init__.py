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
        self._operating_companies = statement_df[txt.STATEMENT_HEADER_ACCOUNT].unique()
    def get_balance(self):
        return self._total_debits - self._total_credits

    def get_last_funding_date(self):
        return self._statement_df[self._statement_df[txt.STATEMENT_HEADER_DEBIT]!=0].iloc[-1][txt.STATEMENT_HEADER_DATE]

    def get_last_inflow_date(self):
        return self._statement_df[self._statement_df[txt.STATEMENT_HEADER_CREDIT]!=0].iloc[-1][txt.STATEMENT_HEADER_DATE]

    def get_days_to_last_inflow(self):
        time_delta = datetime.datetime.today() - self.get_last_inflow_date()
        return time_delta.days
