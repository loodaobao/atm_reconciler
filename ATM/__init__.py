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
    def get_tid(self):
        return self._tid

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
