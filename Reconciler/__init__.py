import sys
from os.path import abspath, join, dirname
import pandas as pd

project_dir = join(dirname('__file__'),"..")
sys.path.insert(0,project_dir)

import Texts as txt
from abc import ABC, abstractmethod, abstractproperty


class Reconciler():
    westpac_accounts = {
                            txt.ATMCO: 36022431156,
                            txt.VENUE_SMART: 36022436029,
                            txt.CASH_POINT: 36022444889
                        }
    def __init__(self, statement):
        self.statement = statement.get_statement()
    def get_balance(self, tid=None):
        if tid:
            relevant_transactions = self.statement[self.statement[txt.STATEMENT_HEADER_TID]==tid]
            balance = relevant_transactions[txt.STATEMENT_HEADER_DEBIT].sum() - relevant_transactions[txt.STATEMENT_HEADER_CREDIT].sum()
            return balance
        else:
            grouped_statement_by_tid  = self.statement.groupby([txt.STATEMENT_HEADER_TID])
            balance_df = grouped_statement_by_tid[txt.STATEMENT_HEADER_DEBIT].sum() -  grouped_statement_by_tid[txt.STATEMENT_HEADER_CREDIT].sum()
            return balance_df
