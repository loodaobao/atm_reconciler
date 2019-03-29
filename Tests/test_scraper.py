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


def test_scrape_2(scrape, timing):
    scrape._scrape_all()
