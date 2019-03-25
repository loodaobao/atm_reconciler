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

def test_identify_idle_tids(statement):
    reco = Reconciler(statement)
    reco.get_idle_tids()

def test_get_balance(statement):
    reco = Reconciler(statement)
    reco.get_balances()
