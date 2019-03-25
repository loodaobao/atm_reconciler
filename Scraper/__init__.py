
import requests
from bs4 import BeautifulSoup
import os
import sys

class Scraper:
    def __init__(self):
        self.session = None
        self._login_response = None
        self._portal_account = os.environ["SELLIS"]
        self._portal_password = os.environ["PW"]
    def _login(self):
        if not self._portal_password or not self._portal_password:
            print("Environment variable is not set. exiting...")
            sys.exit()
        url = "https://www.atmco-treasury.com/login.asp"
        sess = requests.session()
        sess.headers.update(
            {
                "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
                "Accept-Encoding":"gzip, deflate, br",
                "Accept-Language": "en-AU,en-US;q=0.9,en;q=0.8,zh;q=0.7,zh-TW;q=0.6",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests":"1",
                "Referer":"https://www.atmco-treasury.com/atms.asp",
                "Host": "www.atmco-treasury.com",
                "Cache-Control": "max-age=0",
                "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36",

            }
        )
        # res = sess.get(url)
        url_login = "https://www.atmco-treasury.com/login.asp?login=true"
        payload = {"email": self._portal_account,"password": self._portal_password}
        response = sess.post(url_login, data=payload)
        self._login_response = response
        self.session = sess


    def get_tid_urls(self):
        try:
            return self._tid_to_url
        except:
            if not self._login_response:
                self._login()
            tid_to_url = {}
            if self._login_response.status_code == 200:
                front_page_bs4 = BeautifulSoup(self._login_response.text)
                for row in front_page_bs4.select("tr"):
                    a_tags_in_row = row.select("td div a")
                    tid_tag = [x for x in a_tags_in_row if x.get("href") is not None \
                    and "activity" in x.get("href")]

                    if tid_tag:

                        url = tid_tag[0].get("href")
                        tid = [x.text for x in row.select("td div") \
                        if x.text is not None and len(x.text.replace(" ",""))==8 and \
                            (
                                "000" in x.text or\
                                 "9V" in x.text or\
                                 x.text[3]=="P"
                            )
                        ][0]
                        tid_to_url[tid] = url
            else:
                print("ATM Co Portal: Login Failed")
            self._tid_to_url = tid_to_url
            return tid_url
