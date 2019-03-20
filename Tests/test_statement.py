from pytest import fixture
from Statement import Statement
import pickle
import os
import Texts as txt
import datetime
@fixture(scope="function")
def timing():
    start = datetime.datetime.now()

    yield
    finish = datetime.datetime.now()
    print("\nusing time = {}".format(finish-start))
@fixture(scope= "session")
def statement():
    session_statement = Statement(recompile_bulk_transactions = False)
    yield session_statement

def test_fix(timing,statement):

    statement._clean()
    old_credits = statement._statement[txt.STATEMENT_HEADER_CREDIT].sum()
    old_debits = statement._statement[txt.STATEMENT_HEADER_DEBIT].sum()
    statement._break_down_bulk_transactions()
    statement._fix()
    fixed_credits = statement._statement[txt.STATEMENT_HEADER_CREDIT].sum()
    fixed_debits = statement._statement[txt.STATEMENT_HEADER_DEBIT].sum()
    assert fixed_credits - fixed_debits == old_credits - old_debits

def test_get_company(timing, statement):
    atmco_statement = statement.get_company(txt.ATMCO)
    unique_accounts = atmco_statement[txt.STATEMENT_HEADER_ACCOUNT].unique()
    assert 1 == len(unique_accounts)
    assert statement.westpac_accounts[txt.ATMCO] == unique_accounts[0]
