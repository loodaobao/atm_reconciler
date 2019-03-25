from Reconciler import Reconciler
from ATM import ATM
from Statement import Statement
import pickle
import os
import Texts as txt
import datetime
import pytest

@pytest.fixture(scope= "session")
def statement():
    st = Statement(recompile_bulk_transactions = False)
    st.setup()
    yield st

def test_atm_get_last_funding_date(statement):
    tid = "9V26722D"
    atm = ATM(tid, statement.get_statement_by_tid(tid))
    assert atm.get_last_funding_date() == datetime.datetime.strptime("03/20/2019","%m/%d/%Y")

def test_atm_get_last_inflow_date(statement):
    tid = "00081907"
    atm = ATM(tid, statement.get_statement_by_tid(tid))
    assert atm.get_last_inflow_date() ==  datetime.datetime.strptime("08/09/2018","%m/%d/%Y")
