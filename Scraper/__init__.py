import pandas as pd
import requests
from bs4 import BeautifulSoup
import os
import datetime
import sys
from multiprocessing import Pool
from monthdelta import monthdelta

class Scraper:
    def __init__(self):
        self.session = None
        self._login_response = None
        self._portal_account = "sellis@goldfieldsmoney.com.au"
        self._portal_password = "DWOWHTHZ"
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


    def _get_tid_urls(self):
        try:
            return self._tid_to_url
        except:
            if not self._login_response:
                self._login()
            tid_to_url = {}
            if self._login_response.status_code == 200:
                front_page_bs4 = BeautifulSoup(self._login_response.text,"lxml")
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
                        tid = tid.replace(" ","")
                        tid_to_url[tid] = url
            else:
                print("ATM Co Portal: Login Failed")
            self._tid_to_url = tid_to_url
            return self._tid_to_url
    def _get_data_df(self, tid, year,month ):
        print(tid, month, year)
        tids_to_url = self._get_tid_urls()

        url ="https://www.atmco-treasury.com/{activity_url}&month={month}:{year}".format(
            activity_url = tids_to_url[tid],
            month=month,
            year=year
        )
        print(url)
        res = self.session.get(url)
        bs = BeautifulSoup(res.text.replace("\r", "").replace("\t", "").replace("\n", ""),"lxml")
        collected_monthly_data = []
        for index, row in enumerate(bs.select("tr")):
            collected_row = []
            if index!=0:
                tds = row.select("td")
                for ind, td in enumerate(tds):
                    if ind < 1:
                        continue
                    if td.select("div"):
                        tex = td.select("div")[0].text
                    else:
                        tex = td.text
                    tex = tex.replace(" ","").replace("$","").replace("-","")
                    if tex=="":tex="0"
                    collected_row.append(tex)
            else:
                continue
            collected_monthly_data.append(collected_row)


        headers = ["TID","CARRY_FORWARD","CASH_ORDERS","NUM_TRANS","DATE","SETTLEMENTS","CREDITS","REBANK"]
        df = pd.DataFrame(collected_monthly_data, columns = headers)
        return df

    def _scrape_all(self, tid):
        start_date = "2017/11/01"
        start_date_obj = datetime.datetime.strptime(start_date,"%Y/%m/%d")
        today = datetime.datetime.today().date()
        today_year = today.year
        today_month = today.month
        different_in_months = 12*(today_year - start_date_obj.year) + (today_month - start_date_obj.month)
        args = ((tid, (start_date_obj+monthdelta(i)).year,  (start_date_obj+monthdelta(i)).month) for i in range(different_in_months+1))
        pool = Pool(10)
        results = pool.starmap(self._get_data_df, args)
        main_df = results[0]
        for df in results[1:]:
            main_df = main_df.append(df, ignore_index=True)
        print(main_df)
        return main_df
