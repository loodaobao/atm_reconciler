from pytest import fixture
from Statement import Statement
import pickle
import os
import Texts as txt

def test_fix():
    statement = Statement()
    statement._clean()
    old_credits = statement._statement[txt.STATEMENT_HEADER_CREDIT].sum()
    old_debits = statement._statement[txt.STATEMENT_HEADER_DEBIT].sum()
    statement._fix()
    fixed_credits = statement._statement[txt.STATEMENT_HEADER_CREDIT].sum()
    fixed_debits = statement._statement[txt.STATEMENT_HEADER_DEBIT].sum()
    assert fixed_credits - fixed_debits == old_credits - old_debits
    statement._statement.to_csv("test.csv", index=False)
