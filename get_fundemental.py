import requests 
from bs4 import BeautifulSoup
import time
import logging
import pandas as pd
from datetime import date


from utils import *

logging.basicConfig(
    filename="log_fundemental.txt",
    level=logging.INFO,  # Set the logging level to INFO
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)


class AAStock_scrapper():
    def __init__(self, stock_symbol):
        
        self.base_url = 'http://www.aastocks.com/tc/stocks/quote/detail-quote.aspx?symbol='
        self.stock_symbol = stock_symbol
        self.headers = {'User-Agent':
                        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
                       'Origin':'http://www.aastocks.com',
                       'Referer':'http://www.aastocks.com/tc/stocks/quote/detail-quote.aspx'}
        
    def fetch_data(self):
        self.sess = requests.session()
        response = self.sess.get(self.base_url+self.stock_symbol, headers = self.headers)
        
        if response.status_code == 200:
            self.res = response.text
        else:
            log_error("Error fetching data for stock symbol %s.  Status code: %s"%(self.stock_symbol, response.status_code))
    def parse_data(self):
        data_dict={}
        soup = BeautifulSoup(self.res,'html.parser')
        quote_boxes = soup.find_all('div',class_='quote-box')
        for i, quote_box in enumerate(quote_boxes):
            title = quote_box.find('div',class_='float_l ss1')
            content = quote_box.find('div',class_='float_r cls ss2')
            
            if i == 0:
                if 'N/A' not in content.text:
                    avg_price = float(content.text)
                else:
                    avg_price = 'N/A'
                data_dict['avg_price']=avg_price
            elif i == 1:
                if 'N/A' not in content.text:
                    short_amt = float(translator(content.text.split('/')[0]))
                    short_pct = float(content.text.split('/')[1].replace('%',''))/100
                else:
                    short_amt = 'N/A'
                    short_pct = 'N/A'
                data_dict['short_amount'] = short_amt
                data_dict['short_pct'] = short_pct
            elif i == 2:
                if '無盈利' not in content.text:
                    pe_ratio = float(content.text.split('/')[0])
                else:
                    pe_ratio = 'deficit'
                data_dict['pe_ratio'] = pe_ratio
            elif i ==3 :
                if 'N/A' not in content.text:
                    eps = float(content.text)
                else:
                    eps = 'N/A'
                data_dict['eps'] = eps
            elif i ==4:
                if 'N/A' not in content.text:
                    earning_yield = float(content.text.split('/')[0].replace('%',''))/100
                else:
                    earning_yield = 'N/A'
                data_dict['earning_yield']=earning_yield
            elif i ==5:
                if 'N/A' not in content.text:
                    dividend_ratio = float(content.text.split('/')[0].replace('%',''))/100
                    dividend_per_share =float(content.text.split('/')[1])
                else:
                    dividend_ratio='N/A'
                    dividend_per_share='N/A'
                data_dict['dividend_ratio']=dividend_ratio
                data_dict['dividend_per_share']=dividend_per_share
            elif i ==6:
                if 'N/A' not in content.text:
                    pb_ratio = float(content.text.split('/')[0])
                    nav_per_share = float(content.text.split('/')[1])
                else:
                    pb_ratio = 'N/A'
                    nav_per_share = 'N/A'
                data_dict['pb_ratio']=pb_ratio
                data_dict['nav_per_share']=nav_per_share
            elif i == 7:
                if 'N/A' not in content.text:
                    cap_flow = float(translator(content.text))
                else:
                    cap_flow ='N/A'
                data_dict['cap_flow']=cap_flow
            elif i == 8:
                if 'N/A' not in content.text:
                    volume_ratio = float(content.text.split('/')[0])
                    rate_ratio = float(content.text.split('/')[1].replace('%',''))/100
                else:
                    volume_ratio='N/A'
                    rate_ratio='N/A'
                data_dict['volume_ratio']=volume_ratio
                data_dict['rate_ratio']=rate_ratio

            elif i == 9:
                if 'N/A' not in content.text:
                    turnover_rate = float(content.text.replace('%',''))/100
                else:
                    turnover_rate = 'N/A'
                data_dict['turnover_rate']=turnover_rate
            elif i == 10:
                if 'N/A' not in content.text:
                    volatility = float(content.text.replace('%',''))/100
                else:
                    volatility = 'N/A'
                data_dict['volatility']=volatility
            elif i == 11:
                if 'N/A' not in content.text:
                    avg_volume_90 = float(translator(content.text))
                else:
                    avg_volume_90 ='N/A'
                data_dict['avg_volume_90']=avg_volume_90
            elif i == 12:
                if 'N/A' not in content.text:
                    market_cap = float(translator(content.text))
                else:
                    market_cap = 'N/A'
                data_dict['market_cap']=market_cap
        return data_dict
    
if __name__ == '__main__':
    stocklist=[27,66,101,175,241,267,288,291,316,669,823,960,981,992]
    today_dict = {}
    today = date.today()
    formatted_date = today.strftime("%Y%m%d")


    for stock in stocklist:
        stock = "{:0>5}".format(stock)
        logging.info('Start scrapping '+stock)
        scrapper = AAStock_scrapper(stock)
        scrapper.fetch_data()
        today_dict["{:0>5}".format(stock)] = scrapper.parse_data()
        time.sleep(5)
    
    
    df = pd.DataFrame.from_dict(today_dict).T
    df.to_csv('data/fundemental/'+formatted_date+'.csv', encoding='UTF-8')