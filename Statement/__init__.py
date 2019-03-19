import pickle
from os.path import abspath, join, dirname
import pandas as pd
import sys
import os
import numpy as np

project_dir = join(dirname('__file__'),"..")
sys.path.insert(0,project_dir)

import Texts as txt

class Statement:
        westpac_accounts = {
                                txt.ATMCO: 36022431156,
                                txt.VENUE_SMART: 36022436029,
                                txt.CASH_POINT: 36022444889
                            }
    def __init__(self):

        self._project_root = os.getcwd()
        self._new_statement_path =join(self._project_root,"AppData/Data.csv")
        self._appdata_path = join(self._project_root, "AppData")
        self._fixes_instruction_path = join(self._project_root,"AppData/fixes.csv")
        self._statement = None
        self._cleaned = False
        self._fixed = False
    def _get_fixes_instructions(self):
        df = pd.read_csv(self._fixes_instruction_path)
        for column in df.columns:
            if df[column].dtype == np.dtype(np.object):
                df[column] = df[column].str.upper()
        return df
    def _clean(self):
        if self._cleaned:
            return
        else:
            df = pd.read_csv(self._new_statement_path)
            for column in df.columns:
                if df[column].dtype == np.dtype(np.object):
                    df[column] = df[column].str.upper()
            self._statement = df
            self._cleaned = True
            return
    def _fix(self):
        if not self._cleaned:
            self._clean()
        fixes_instructions = self._get_fixes_instructions()
        for index, instruction in fixes_instructions.iterrows():
            error_company = instruction[txt.FIXES_HEADER_COMPANY_NAME]
            error_date = instruction[txt.FIXES_HEADER_ERROR_DATE]
            error_type = instruction[txt.FIXES_HEADER_ERROR_TYPE]
