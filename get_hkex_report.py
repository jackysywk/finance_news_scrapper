import requests
import logging
from bs4 import BeautifulSoup
from utils import *
from datetime import date, timedelta
import pandas as pd
import time
logging.basicConfig(
    filename="log_hkex.txt",
    level=logging.INFO,  # Set the logging level to INFO
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)


def get_date_range(period):
    end_date = date.today()
    
    if period == "1d":
        start_date = end_date - timedelta(days=1)
    elif period == "1w":
        start_date = end_date - timedelta(weeks=1)
    elif period == "1m":
        start_date = end_date.replace(day=1)
    
    return start_date.strftime("%Y%m%d"), end_date.strftime("%Y%m%d")
class HKEX_scrapper():
    def __init__(self, period="1d", pages=1):
        self.base_url = "https://www1.hkexnews.hk/search/titlesearch.xhtml?lang=zh"
        start_date, end_date = get_date_range(period)
        self.res=[]
        self.data_dict={}
        self.pages = pages
        self.parameters = parameters = {
                            "lang": "ZH",
                            "category": 0,
                            "market": "SEHK",
                            "searchType": 0,
                            "documentType": -1,
                            "t1code": -2,
                            "t2Gcode": -2,
                            "t2code": -2,
                            "stockId": "",
                            "from": start_date,
                            "to": end_date,
                            "MB-Daterange": 0,
                        }
        self.headers =  {"Content-Type":"application/x-www-form-urlencoded",
                        "Origin":"https://www1.hkexnews.hk",
                        "Referer":"https://www1.hkexnews.hk/search/titlesearch.xhtml?lang=zh",
                        "Sec-Ch-Ua-Mobile":"?0",
                        "Sec-Ch-Ua-Platform":"macOS",
                        "Upgrade-Insecure-Requests":"1",
                        "User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36"
                        }
    def fetch_data(self):
        for i in range(0,self.pages):
            print("Downloading page "+str(i))
            time.sleep(1)
            self.parameters["rowRange"] = i*100
            res = requests.post(self.base_url, data=self.parameters, headers=self.headers)

            if res.status_code == 200:
                logging.info("POST request successful. Downloaded page "+str(i+1))
                self.res.append(res.text)
            else:
                logging.error("POST request failed")
                logging.error("Status code:"+str(res.status_code))
    def parse_data(self):
        
        for res in self.res:
            soup = BeautifulSoup(res,'html.parser')
            items = soup.find("tbody").find_all("tr")
            for item in items:
                
                item = item.find_all("td")
                time = item[0].text.replace("發放時間: ","").strip()
                stockId = item[1].text.replace("股份代號: ","").strip()
                stockName = item[2].text.replace("股份簡稱: ","").strip()
                title = item[3].find("div",class_="headline").text.strip()
                url = item[3].find("div",class_="doc-link").find("a")['href']
                i=len(self.data_dict)
                self.data_dict[i]={}
                self.data_dict[i]['time']=time
                self.data_dict[i]['stockId']=stockId
                self.data_dict[i]['stockName']=stockName
                self.data_dict[i]['title']=title
                self.data_dict[i]['url'] = url


if __name__ == "__main__":
    today = date.today()
    formatted_date = today.strftime("%Y%m%d")
    scraper = HKEX_scrapper(period="1m", pages=2)
    scraper.fetch_data()
    scraper.parse_data()
    df = pd.DataFrame.from_dict(scraper.data_dict).T
    df.to_csv('data/hkex/'+formatted_date+'.csv', encoding='UTF-8')


