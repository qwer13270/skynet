from typing import Iterable
import scrapy
from scrapy.http import Request
from myspider.items import NtwoYOItem
from tqdm import tqdm
from datetime import date, datetime
import pandas as pd
import os
import psycopg2
import re
from dotenv import load_dotenv

#get env variables from .env
load_dotenv()

class NtwoYOSpider(scrapy.Spider):
 
    name = "ntwoyospider"
    allowed_domains = ["n2yo.com"]
    
    custom_settings = {
        'ITEM_PIPELINES': {
            'myspider.pipelines.NtwoYOPipeline': 600,
            },
        'LOG_LEVEL': 'CRITICAL',
    }
 
    def __init__(self):
        self.scraped_items = list()
        # hostname = 'localhost'
        # username = 'skynetapp'
        # password = 'skynet'
        # database = 'skynetapp' # not necessary
        # port = 5432 # using default
        
        hostname = os.getenv('DB_HOST')
        username = os.getenv('DB_USER')
        password = os.getenv('DB_PASSWORD')
        #database = os.getenv('DB_NAME')

        self.connection = psycopg2.connect(host=hostname, user=username, password=password)
        self.cur = self.connection.cursor()
        self.cur_set_period = self.connection.cursor()
        #Check if the column exists in the table
        check_column_query = f"""
            SELECT EXISTS (
                SELECT 1
                FROM information_schema.columns
                WHERE table_name = 'planet4589'
                AND column_name = 'period'
            );
        """
        # Execute the query to check if the column exists
        self.cur.execute(check_column_query)
        column_exists = self.cur.fetchone()[0]
        #print(f'col exists: {column_exists}')
        if not column_exists:
            add_column_query = f"ALTER TABLE planet4589 ADD COLUMN Period VARCHAR(255);"
            self.cur.execute(add_column_query)
            self.connection.commit()

    def start_requests(self):
        self.cur.execute("SELECT satcat FROM planet4589 WHERE period IS NULL")
        base_url = "https://www.n2yo.com/satellite/?s="
        for norad in self.cur:
            url = base_url + str(norad[0])
            # print(url)
            yield Request(url)

    def parse(self, response):
        ntwoyoitem = NtwoYOItem()
        res = response.text
        norad = re.search(r"=([0-9]+)", response.request.url)[1]
        ntwoyoitem["NORAD"] = norad
        period = re.search(r"Period.+?([0-9]+\.[0-9]+)", res)
        #print(f'checking norad: {norad}')
        if period == None:
            # ntwoyoitem["Period"] = "NULL"
            ntwoyoitem["Period"] = None

        else:
            ntwoyoitem["Period"] = period[1]
            # print(period[1])

        yield ntwoyoitem
        
        self.set_period(norad, period[1])
        self.scraped_items.append(ntwoyoitem)
        
    def set_period(self, norad, period):
        print(f'getting period = {period} for norad = {norad}')
        query = f'UPDATE planet4589 SET period = %s WHERE satcat = %s'
        self.cur_set_period.execute(query, (period, norad))
        self.connection.commit()


    def closed(self, reason):
        self.cur.close()
        self.cur_set_period.close()
        self.connection.close()
        current_datetime = datetime.now().strftime('%m-%d-%Y_%H-%M-%S')
        current_month_year = date.today().strftime('%B_%Y')
        folder_name = os.path.join('CSVs/N2YO', current_month_year)
        os.makedirs(folder_name, exist_ok=True)
        csv_filename = os.path.join(folder_name, f'N2YO_{current_datetime}.csv')
        df = pd.DataFrame(self.scraped_items)
        # print(df)
        df.to_csv(csv_filename, index=False)
        print(f'Scraped data exported to {csv_filename}')