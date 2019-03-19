from pytest import fixture
from Statement import Statement
import pickle
import os
def test_init():
    statement = Statement()
    assert statement != None
