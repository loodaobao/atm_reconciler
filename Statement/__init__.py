import pickle
from os.path import abspath, join, dirname
import pandas as pd
import sys
import os

project_dir = join(dirname('__file__'),"..")
sys.path.insert(0,project_dir)

class Statement:
    def __init__(self):
        self.new_raw_df = pd.read_csv("Data.csv")
        self._project_root = os.getcwd()
        self._appdata_path = join(self._project_root, "AppData")
        self._pick_path = join(self._appdata_path, "statement.pickle")
    def _load_previous_statement(self):
        try:
            return pickle.load(open(self._pick_path,"rb"))
        except Exception as e:
            return None
