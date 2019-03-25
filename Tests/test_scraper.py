from Scraper import Scraper
import pytest


@pytest.fixture(scope= "session")
def scrape():
    scraper = Scraper()
    scraper._login()
    yield scraper

def test_scraper_login(scrape):
    assert scrape._login_response.status_code == 200
def test_scraper_get_tid_urls(scrape):
    tid_to_url = scrape._get_tid_urls()
    assert len(tid_to_url) != 0
