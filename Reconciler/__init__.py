import sys
from os.path import abspath, join, dirname
import pandas as pd
import numpy as np

project_dir = join(dirname('__file__'),"..")
sys.path.insert(0,project_dir)

import Texts as txt
from abc import ABC, abstractmethod, abstractproperty
from ATM import ATM
import datetime
from Statement import Statement

class Reconciler():
    westpac_accounts = {
                            txt.ATMCO: 36022431156,
                            txt.VENUE_SMART: 36022436029,
                            txt.CASH_POINT: 36022444889
                        }
    def __init__(self, statement = None):
        if not statement:
            statement = Statement()
            statement.setup()

        self.statement =statement
        self.atms = {x:ATM(x,statement.get_statement_by_tid(x)) for x in statement._get_all_funded_tids()}
    def get_summary(self, tid):
        if tid not in self.atms:
            print("This TID does not exist in the bank statement. Please try again...")
            return
        atm = self.atms[tid]

        summary = """
        TID: {tid}
        Current Balance: {balance:,}
        {company_balance}
        Days To Last Activity: {days_to_last_activity}
        Last Funding Date: {last_funding_date}
        Last Inflow Date: {last_inflow_date}

        Last Transactions:

        {last_transactions}
        """.format(
        tid = tid,
        balance=  atm.get_balance(),
        company_balance = atm.get_company_balance(return_type = str),
        days_to_last_activity = atm.get_days_to_last_activity(),
        last_funding_date = atm.get_last_funding_date().date(),
        last_inflow_date = atm.get_last_inflow_date().date(),
        last_transactions = atm.get_last_activity_summary()
        )
        print(summary)

    def get_balances(self):
        df = self.statement.get_statement_by_company_name(company_name = None)
        df = pd.pivot_table(df,
                            index = txt.STATEMENT_HEADER_TID,
                            columns = [txt.STATEMENT_HEADER_ACCOUNT],
                            aggfunc = np.sum
                            )[[txt.STATEMENT_HEADER_CREDIT,txt.STATEMENT_HEADER_DEBIT]]
        balances = df[txt.STATEMENT_HEADER_DEBIT]-df[txt.STATEMENT_HEADER_CREDIT]
        balances.to_csv("balances_{}.csv".format(datetime.datetime.today().date()))
        return balances

    def identify_idle_tids(self):
        try:
            return self._idle_tids
        except:

            all_idle = []
            for tid, atm in self.atms.items():
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
            df.to_csv("idle_{}.csv".format(datetime.datetime.today().date()),index=False)
            self._idle_tids = df
            return df
