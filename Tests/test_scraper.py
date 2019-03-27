from Scraper import Scraper
import pytest
import datetime
from multiprocessing import Pool
import threading
from queue import Queue
from os.path import abspath, join, dirname
import pickle
@pytest.fixture(scope="function")
def timing():
    start = datetime.datetime.now()
    yield
    finish = datetime.datetime.now()
    print("\nusing time = {}".format(finish-start))

@pytest.fixture(scope= "session")
def scrape():
    scraper = Scraper()
    scraper._login()
    yield scraper

def test_scraper_login(scrape):
    assert scrape._login_response.status_code == 200

def test_scraper_all(scrape, timing):

    all_tids = scrape._get_tid_urls()
    tids = all_tids.keys()
    dfs = {}
    for tid in tids:
        result = scrape._scrape_all(tid)
        dfs[tid] = result

    with open(join(scrape.statement._project_root,"crawel.pickle"),"wb") as f:
        pickle.dump(dfs,f)
