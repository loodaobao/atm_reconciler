import sys
from os.path import abspath, join, dirname
import pandas as pd

project_dir = join(dirname('__file__'),"..")
sys.path.insert(0,project_dir)

import Texts as txt
from abc import ABC, abstractmethod, abstractproperty
from ATM import ATM

class Reconciler():
    westpac_accounts = {
                            txt.ATMCO: 36022431156,
                            txt.VENUE_SMART: 36022436029,
                            txt.CASH_POINT: 36022444889
                        }
    def __init__(self, statement):
        self.statement = statement
    def identify_idle_tids(self):
        funded_tids = self.statement._get_all_funded_tids()
        all_idle = []
        for tid in funded_tids:
            atm = ATM(tid, self.statement.get_statement_by_tid(tid))
            days_to_last_activity = atm.get_days_to_last_activity()
            last_funding_date = atm.get_last_funding_date()
            last_inflow_date = atm.get_last_inflow_date()
            balance = atm.get_balance()
            if days_to_last_activity > 15 and balance !=0:
                data = [
                    atm.get_operating_companies(),
                    tid,
                    days_to_last_activity,
                    last_inflow_date,
                    last_funding_date,
                    balance
                    ]
                all_idle.append(data)
        df = pd.DataFrame(all_idle, columns=[txt.STATEMENT_HEADER_ACCOUNT, txt.STATEMENT_HEADER_TID,"days_to_last_activity","LAST_INFLOW_DATE","LAST_FUNDING_DATE","BALANCE"])
        df.to_csv("idle.csv",index=False)
