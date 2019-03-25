from Reconciler import Reconciler
from ATM import ATM
from Statement import Statement
import pickle
import os
import Texts as txt
import datetime
import pytest

@pytest.fixture(scope="function")
def timing():
    start = datetime.datetime.now()
    yield
    finish = datetime.datetime.now()
    print("\nusing time = {}".format(finish-start))
@pytest.fixture(scope= "session")
def statement():
    session_statement = Statement(recompile_bulk_transactions = False)
    yield session_statement

def test_fixing_maintains_balances(timing,statement):
    statement._clean()
    old_credits = statement._statement[txt.STATEMENT_HEADER_CREDIT].sum()
    old_debits = statement._statement[txt.STATEMENT_HEADER_DEBIT].sum()
    statement.setup()
    fixed_credits = statement._statement[txt.STATEMENT_HEADER_CREDIT].sum()
    fixed_debits = statement._statement[txt.STATEMENT_HEADER_DEBIT].sum()
    starting_balance = (fixed_credits - fixed_debits)  - (old_credits - old_debits)
    assert starting_balance == 3000000

def test_get_statement_by_company_name(timing, statement):
    atmco_statement = statement.get_statement_by_company_name(txt.ATMCO)
    unique_accounts = atmco_statement[txt.STATEMENT_HEADER_ACCOUNT].unique()
    assert unique_accounts[0] == statement.westpac_accounts[txt.ATMCO]

def test_vs_oustanding_events(timing, statement):
    vs = statement.get_statement_by_company_name(txt.VENUE_SMART)
    vs_non_atm = vs[vs[txt.STATEMENT_HEADER_TID]==""]
    vs_non_facility = vs_non_atm[~(vs_non_atm[txt.STATEMENT_HEADER_NARRATIVE].str.contains("TRACK_FACILITY"))]
    vs_event = vs_non_facility[vs_non_facility[txt.STATEMENT_HEADER_NARRATIVE].str.contains("TRACK_EVENT_")]
    event_outstanding = vs_event[txt.STATEMENT_HEADER_CREDIT].sum() - vs_event[txt.STATEMENT_HEADER_DEBIT].sum()
    difference = vs_non_facility[txt.STATEMENT_HEADER_CREDIT].sum()-vs_non_facility[txt.STATEMENT_HEADER_DEBIT].sum() - event_outstanding
    print("\ndifference = {}".format(difference))
    assert vs_non_facility[txt.STATEMENT_HEADER_CREDIT].sum()-vs_non_facility[txt.STATEMENT_HEADER_DEBIT].sum() == event_outstanding

@pytest.mark.xfail
def test_atmco_non_atm_balance(timing, statement):
    atmco =statement.get_statement_by_company_name(txt.ATMCO)
    non_atm = atmco[atmco[txt.STATEMENT_HEADER_TID]==""]
    total_facility_limit = non_atm[(non_atm[txt.STATEMENT_HEADER_NARRATIVE].str.contains("TRACK_FACILITY"))][txt.STATEMENT_HEADER_CREDIT].sum()-\
    non_atm[(non_atm[txt.STATEMENT_HEADER_NARRATIVE].str.contains("FACILITY"))][txt.STATEMENT_HEADER_DEBIT].sum()
    difference =  non_atm[txt.STATEMENT_HEADER_CREDIT].sum()-non_atm[txt.STATEMENT_HEADER_DEBIT].sum() - total_facility_limit
    print("\ndifference = {}".format(difference))
    assert non_atm[txt.STATEMENT_HEADER_CREDIT].sum()-non_atm[txt.STATEMENT_HEADER_DEBIT].sum() == total_facility_limit #facility limit 3.75 mil

def test_not_funded_tids(timing, statement):
    not_funded = statement._statement[statement._statement[txt.STATEMENT_HEADER_FUNDED]==False][txt.STATEMENT_HEADER_TID].unique().tolist()
    print("not_funded atms = {}".format(",".join(not_funded)))
    assert len(not_funded) == 0

def test_save(timing, statement):
    statement.save_records()
