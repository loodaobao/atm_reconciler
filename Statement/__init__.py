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
        error_company_names = [
            txt.ATMCO,
            txt.VENUE_SMART,
            txt.CASH_POINT
        ]
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
    def _apply_fix_to_statement(self, instruction):
        error_company_number = instruction[txt.FIXES_HEADER_COMPANY_NAME]
        error_company_name = self.error_company_names[error_company_number]
        error_account = self.westpac_accounts[error_company_name]
        relevant_date = instruction[txt.FIXES_HEADER_DATE]
        error_type = instruction[txt.FIXES_HEADER_ERROR_TYPE]
        error_ref = instruction[txt.FIXES_HEADER_EXISTING_REF]
        inserted_credit_debit = instruction[txt.FIXES_HEADER_INSERTED_CREDIT_DEBIT]
        inserted_amount = instruction[txt.FIXES_HEADER_INSERTED_AMOUNT]
        inserted_ref = instruction[txt.FIXES_HEADER_INSERTED_REF]
        old_tid = instruction[txt.FIXES_HEADER_OLD_TID]
        new_tid = instruction[txt.FIXES_HEADER_NEW_TID]
        #ERROR_TYPE(1=CHANGE_REFERENCE, 2=TID_CHANGE, 3=INSERT_NEW_TRANSACTION, 4=DELETE_ROW)
        if error_type == 1:
            self._change_description(error_company_account, error_ref, inserted_ref)
        elif error_type == 2:
            self._change_tid(old_tid, new_tid)
        elif error_type == 3:
            self._insert_new_transaction(
                                            error_company_account,
                                            relevant_date,
                                            inserted_credit_debit,
                                            inserted_amount,
                                            inserted_ref
                                        )
        elif error_type == 4:
            self._delete_row(error_company_account, error_ref)
    def _delete_row(self, error_company_account, error_ref):
        assert 1==len(
                self.statement[
                                (
                                    (self.statement[txt.STATEMENT_HEADER_ACCOUNT]==error_company_account) &\
                                    (self.statement[txt.STATEMENT_HEADER_NARRATIVE] == error_ref)
                                )
                                ]
            )
        self.statement = self.statement[
                                ~(
                                    (self.statement[txt.STATEMENT_HEADER_ACCOUNT]==error_company_account) &\
                                    (self.statement[txt.STATEMENT_HEADER_NARRATIVE] == error_ref)
                                )
                                ]
    def _fix(self):
        #Apply change-tid instructions only after other fixes are applied.
        if not self._cleaned:
            self._clean()
        fixes_instructions = self._get_fixes_instructions()

        change_tid_instructions = fixes_instructions[
                                        fixes_instructions[txt.FIXES_HEADER_ERROR_TYPE]  == 2
                                        ]
        other_instructions = fixes_instructions[
                                        fixes_instructions[txt.FIXES_HEADER_ERROR_TYPE]  != 2
                                        ]
        for index, instruction in other_instructions.iterrows():
            self._apply_fix_to_statement(instruction)
        for index, instruction in change_tid_instructions.iterrows():
            self._apply_fix_to_statement(instruction)
