from pytest import fixture
from Statement import Statement
import pickle
import os
def test_init():
    statement = Statement()
    assert statement != None

def test_load_previous_statement():
    statement = Statement()
    previous_statemenet = statement._load_previous_statement()
    if os.path.isfile(statement._pick_path):
        assert previous_statemenet != None
    else:
        assert previous_statemenet == None
