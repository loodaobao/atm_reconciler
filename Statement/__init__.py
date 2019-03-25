import pickle
from os.path import abspath, join, dirname
import pandas as pd
import sys
import os
import numpy as np
import csv
import re
import datetime
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
    def __init__(self, recompile_bulk_transactions = False):

        self._project_root = os.getcwd()
        self._new_statement_path =join(self._project_root,"AppData/Data.csv")
        self._appdata_path = join(self._project_root, "AppData")
        self._fixes_instruction_path = join(self._project_root,"AppData/fixes.csv")
        self._bulk_transaction_pickle_path = join(self._appdata_path,"bulk_transaction.pickle")
        self._record_path = join(self._project_root,"Records")
        self._statement = None
        self._cleaned = False
        self._fixed = False
        self._recompile_bulk_transactions = recompile_bulk_transactions
    def _get_fixes_instructions(self):
        df = pd.read_csv(self._fixes_instruction_path)
        for column in df.columns:
            if df[column].dtype == np.dtype(np.object):
                df[column] = df[column].str.upper()
        df[txt.FIXES_HEADER_DATE] = pd.to_datetime(df[txt.FIXES_HEADER_DATE])
        return df
    def _clean(self):
        if self._cleaned:
            return
        else:
            df = pd.read_csv(self._new_statement_path)
            for column in df.columns:
                if df[column].dtype == np.dtype(np.object):
                    df[column] = df[column].str.upper()
            df[txt.STATEMENT_HEADER_DATE] = df[txt.STATEMENT_HEADER_DATE].apply(
                                                                                lambda x: datetime.datetime.strftime(
                                                                                        datetime.datetime.strptime(x,"%d/%m/%Y"),
                                                                                        "%m/%d/%Y"
                                                                                        )
                                                                                )


            self._statement = df
            self._statement[txt.STATEMENT_HEADER_DATE] = pd.to_datetime(self._statement[txt.STATEMENT_HEADER_DATE])
            self._cleaned = True
            return
    def _apply_fix_to_statement(self, instruction):
        error_company_number = instruction[txt.FIXES_HEADER_COMPANY_NAME]
        error_company_name = self.error_company_names[error_company_number]
        error_company_account = self.westpac_accounts[error_company_name]
        relevant_date = instruction[txt.FIXES_HEADER_DATE]
        error_type = instruction[txt.FIXES_HEADER_ERROR_TYPE]
        error_ref = instruction[txt.FIXES_HEADER_EXISTING_REF]
        inserted_credit_debit = instruction[txt.FIXES_HEADER_INSERTED_CREDIT_DEBIT]
        inserted_amount = instruction[txt.FIXES_HEADER_INSERTED_AMOUNT]
        inserted_ref = instruction[txt.FIXES_HEADER_INSERTED_REF]
        old_tid = instruction[txt.FIXES_HEADER_OLD_TID]
        new_tid = instruction[txt.FIXES_HEADER_NEW_TID]
        error_item_number = instruction[txt.FIXES_HEADER_ITEM_NUMBER]
        #ERROR_TYPE(1=CHANGE_REFERENCE, 2=TID_CHANGE, 3=INSERT_NEW_TRANSACTION, 4=DELETE_ROW)
        if error_type == 1:
            self._change_description(error_company_account, error_ref, inserted_ref, relevant_date)
        elif error_type == 2:
            self._change_tid(old_tid, new_tid, relevant_date)
        elif error_type == 3:
            self._insert_new_transaction(
                                            error_company_account,
                                            relevant_date,
                                            inserted_credit_debit,
                                            inserted_amount,
                                            inserted_ref,
                                            error_item_number
                                        )
        elif error_type == 4:
            self._delete_row(error_company_account, error_ref, relevant_date)

    def _change_tid(self,old_tid, new_tid, threshold_date):
        old_tid_re = "".join(["[{}]".format(x) for x in old_tid])
        old_tid_re = "({})".format(old_tid_re)
        filter = (self._statement[txt.STATEMENT_HEADER_NARRATIVE].str.contains(old_tid)) & (self._statement[txt.STATEMENT_HEADER_DATE]<=threshold_date)
        changed_narratives = self._statement.loc[filter,[txt.STATEMENT_HEADER_NARRATIVE]].replace(old_tid_re, new_tid, regex=True)
        self._statement.loc[filter,[txt.STATEMENT_HEADER_NARRATIVE]] = changed_narratives
    def _delete_row(self, error_company_account, error_ref, relevant_date):
        filter = (
            (self._statement[txt.STATEMENT_HEADER_ACCOUNT]==error_company_account) &\
            (self._statement[txt.STATEMENT_HEADER_NARRATIVE] == error_ref)&\
            (self._statement[txt.STATEMENT_HEADER_DATE] == relevant_date)
        )
        found_transactions_length = len(self._statement[filter])
        assert found_transactions_length != 0
        self._statement = self._statement[~filter]
    def _change_description(self, error_company_account, error_ref, inserted_ref, relevant_date):
        filter = (
            (self._statement[txt.STATEMENT_HEADER_ACCOUNT]==error_company_account) &\
            (self._statement[txt.STATEMENT_HEADER_NARRATIVE] == error_ref)&\
            (self._statement[txt.STATEMENT_HEADER_DATE] == relevant_date)
        )

        assert 1==len(self._statement[filter])
        self._statement.loc[filter,[txt.STATEMENT_HEADER_NARRATIVE]] = inserted_ref
    def _insert_new_transaction(self,
                                error_company_account,
                                relevant_date,
                                inserted_credit_debit,
                                inserted_amount,
                                inserted_ref,
                                error_item_number

                                ):
        inserted_ref = "FIX_ITEM_NUMBER_{} = {}".format(error_item_number, inserted_ref)
        data_row = [
                error_company_account,
                relevant_date,
                inserted_ref,
                inserted_amount if inserted_credit_debit == 1 else np.nan,
                inserted_amount if inserted_credit_debit == 2 else np.nan,
                np.nan,
                np.nan
            ]
        corrected_df = pd.DataFrame(
                [data_row],
                columns=self._statement.columns
            )
        self._statement = self._statement.append(corrected_df, ignore_index=True)

    def _get_bulk_transactions_file_names(self):
        try:
            return self._all_orders
        except:
            all_orders = [
                            x[:-4] for x in os.listdir(self._appdata_path) \
                                if len(x.split(".")[0]) == 10 or \
                                (len(x.split(".")[0])==12 and "VS" in x)
                        ]
            self._all_orders = all_orders
            return all_orders



    def _read_bulk_transaction_file(self,company_account, file_name, bulk_transactions_list):
        csv_path = join(self._appdata_path, "{}.csv".format(file_name))
        date_str = file_name[4:6]+"/"+file_name[6:8]+"/"+file_name[:4]
        df = pd.read_csv(csv_path,names=
                        [
                            "BSB",
                            "ACCOUNT",
                            "NAME",
                            "NOTE",
                            "AMOUNT",
                            "ATM_ID"
                        ])
        for ind, row in df.iterrows():
            data_row = [
                company_account,
                date_str,
                row["ATM_ID"].replace(u'\xa0',""),
                row["AMOUNT"],
                np.nan,
                np.nan,
                np.nan


            ]

            bulk_transactions_list.append(data_row)

    def save_records(self):
        today = str(datetime.datetime.today().date()).replace("-","")
        self._get_bulk_transactions_dataframe().to_csv(join(self._record_path,"bulk_{}.csv".format(today)))
        self._statement.to_csv(join(self._record_path,"statement_{}.csv".format(today)))


    def _get_bulk_transactions_dataframe(self):
        try:
            return self._bulk
        except:
            bulk_transactions_file_names = self._get_bulk_transactions_file_names()
            if self._recompile_bulk_transactions:
                print("recompiling bulk")

                bulk_transactions_list = []
                for file_name in bulk_transactions_file_names:
                    if "VS" in file_name:
                        company_account = self.westpac_accounts[txt.VENUE_SMART]
                    else:
                        company_account = self.westpac_accounts[txt.ATMCO]
                    self._read_bulk_transaction_file(company_account, file_name, bulk_transactions_list)

            else:
                print("using pickle...")
                if not os.path.isfile(self._bulk_transaction_pickle_path):
                    print("pickle of bulk trans doesn't exist")
                    self._recompile_bulk_transactions = True
                    return self._get_bulk_transactions_dataframe()
                else:
                    infile = open(self._bulk_transaction_pickle_path,'rb')
                    bulk_transactions_list = pickle.load(infile)
                    infile.close()
                    last_update_date = datetime.datetime.strptime(bulk_transactions_list[-1][1],"%m/%d/%Y")
                    print("last_entry date = {}".format(last_update_date))
                    needed_file_names = [
                        x for x in bulk_transactions_file_names if datetime.datetime.strptime(x[:8], "%Y%m%d")>last_update_date
                    ]
                    print("needed_file_count = {}".format(len(needed_file_names)))

                    for file_name in needed_file_names:
                        if "VS" in file_name:
                            company_account = self.westpac_accounts[txt.VENUE_SMART]
                        else:
                            company_account = self.westpac_accounts[txt.ATMCO]
                        self._read_bulk_transaction_file(company_account, file_name, bulk_transactions_list)
            bulk_transactions_df =pd.DataFrame(bulk_transactions_list, columns=self._statement.columns)
            outfile = open(self._bulk_transaction_pickle_path,'wb')
            pickle.dump(bulk_transactions_list, outfile)
            outfile.close()
            bulk_transactions_df[txt.STATEMENT_HEADER_DATE] = pd.to_datetime(bulk_transactions_df[txt.STATEMENT_HEADER_DATE])
            self._bulk = bulk_transactions_df
            return self._bulk







    def _remove_bulk_transactions_from_statement(self):
        # bulk_transactions_file_names = self._get_bulk_transactions_file_names()
        #([12]\d{3}(0[1-9]|1[0-2])(0[1-9]|[12]\d|3[01])(0[1-9]|[12]\d|3[01])([V][S]))
        #([12]\d{3}(0[1-9]|1[0-2])(0[1-9]|[12]\d|3[01])(0[1-9]|[12]\d|3[01]))
        atmco_regex = "([12]\d{3}(0[1-9]|1[0-2])(0[1-9]|[12]\d|3[01])(0[1-9]|[12]\d|3[01]))"
        vs_regex = "([12]\d{3}(0[1-9]|1[0-2])(0[1-9]|[12]\d|3[01])(0[1-9]|[12]\d|3[01])([V][S]))"


        self._statement = self._statement[~(
            (self._statement[txt.STATEMENT_HEADER_NARRATIVE].str.contains(atmco_regex)) |\
            (self._statement[txt.STATEMENT_HEADER_NARRATIVE].str.contains(vs_regex))
            )
        ]


    def _break_down_bulk_transactions(self):
        self._remove_bulk_transactions_from_statement()
        bulk_transactions_df = self._get_bulk_transactions_dataframe()

        self._statement = self._statement.append(bulk_transactions_df, ignore_index=True)

    def _execute_fix_instructions(self):
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

    def _fix(self):
        #Apply change-tid instructions only after other fixes are applied.
        if not self._cleaned:
            self._clean()
        self._execute_fix_instructions()
        self._extract_tids()
        self._check_not_funded_tids()

        self._statement.sort_values(txt.STATEMENT_HEADER_DATE, inplace=True)

        self._fixed = True
    def setup(self):
        self._clean()
        self._break_down_bulk_transactions()
        self._fix()

    def get_statement_by_company_name(self, company_name = None):
        if company_name == None:
                return self._statement
        else:
            return self._statement[self._statement[txt.STATEMENT_HEADER_ACCOUNT]==self.westpac_accounts[company_name]]
    def get_statement_by_tid(self, tid):
        return self._statement[self._statement[txt.STATEMENT_HEADER_TID]==tid]


    def _extract_tids(self):
        regex = "([0-9][A-Z][0-9][0-9][0-9][0-9][0-9][A-Z])|([0][0][0][0-9][0-9][0-9][0-9][0-9])|([0-9][0-9][0-9][P][0-9][0-9][0-9][0-9])"
        regex_result =  self._statement[txt.STATEMENT_HEADER_NARRATIVE].str.extract(regex)
        regex_result.fillna("",inplace= True)
        self._statement[txt.STATEMENT_HEADER_TID] = regex_result[0] + regex_result[1] + regex_result[2]
    def _check_not_funded_tids(self):
        funded_tids = self._get_all_funded_tids()
        self._statement[txt.STATEMENT_HEADER_FUNDED] = self._statement[txt.STATEMENT_HEADER_TID].isin(funded_tids)
    def _get_all_funded_tids(self):
        return self._statement[~self._statement[txt.STATEMENT_HEADER_DEBIT].isnull()][txt.STATEMENT_HEADER_TID].unique().tolist()
