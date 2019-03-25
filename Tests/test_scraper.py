from Scraper import Scraper

def test_scraper_login():
    scraper = Scraper()
    scraper._login()
    assert scraper._login_response.status_code == 200
