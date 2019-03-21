import sys
from os.path import abspath, join, dirname
import pandas as pd

project_dir = join(dirname('__file__'),"..")
sys.path.insert(0,project_dir)

import Texts as txt
from abc import ABC, abstractmethod, abstractproperty


class Reconciler(ABC):
    westpac_accounts = {
                            txt.ATMCO: 36022431156,
                            txt.VENUE_SMART: 36022436029,
                            txt.CASH_POINT: 36022444889
                        }
    def __init__(self, statement):
        self.company_name = company_name
        self.account = self.westpac_accounts[company_name]
        self.statement = statement
