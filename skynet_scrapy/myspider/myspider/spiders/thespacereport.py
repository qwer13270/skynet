from typing import Iterable
import scrapy
from myspider.items import TheSpaceReportItem
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium import webdriver
from tqdm import tqdm
from datetime import date, datetime
import pandas as pd
import os
import re
import time
import psycopg2
import logging
from dotenv import load_dotenv

#get env variables from .env
load_dotenv()

class TheSpaceReportSpider(scrapy.Spider):

    name = "thespacereportspider"
    # allowed_domains = ["thespacereport.org"]
    start_urls = ["https://www.thespacereport.org/resources/launch-log-2023/"]

    custom_settings = {
        'ITEM_PIPELINES': {
            'myspider.pipelines.TheSpaceReportPipeline': 800,
            },
        'LOG_LEVEL': 'CRITICAL',
    }

    def __init__(self):
        self.scraped_items = list()
        options = Options()
        options.headless = True

        ### path to chromedriver
        ### 1. either have an executable in the same directory as in the next line
        #service = Service(executable_path="chromedriver") # for all platforms (hopefully)
        ### 2. or place the executable in your path as in the next line
        service = Service(executable_path='/usr/local/bin/chromedriver') # default setup is for macos
        ### put # in front of line above and remove from the line below if you are on ubuntu
        #service = Service(executable_path="chromium.chromedriver") # for ubuntu (linux in general)

        options.add_argument('--disable-dev-shm-usage')
        self.driver = webdriver.Chrome(options=options, service=service)

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
        self.add_column_if_not('planet4589', 'launch_vehicle', 'VARCHAR(255)')
        self.add_column_if_not('planet4589', 'launch_site', 'VARCHAR(255)')
        self.add_column_if_not('planet4589', 'mission_sector', 'VARCHAR(255)')

    def add_column_if_not(self, table_name, column_name, column_type):
        # Check if the column exists in the table
        check_column_query = """
            SELECT EXISTS (
                SELECT 1
                FROM information_schema.columns
                WHERE table_name = %s
                AND column_name = %s
            );
        """
        # Execute the query to check if the column exists
        self.cur.execute(check_column_query, (table_name, column_name))
        column_exists = self.cur.fetchone()[0]
        
        if not column_exists:
            # Add the column if it doesn't exist
            add_column_query = f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type};"
            self.cur.execute(add_column_query)
            self.connection.commit()

    def parse(self, response):
        url = response.url
        self.driver.get(url)
        time.sleep(1.5)

        table_body = self.driver.find_element(By.TAG_NAME, "tbody")
        condition = True

        while(condition):

            table_body = self.driver.find_element(By.TAG_NAME, "tbody")

            for tr in table_body.find_elements(By.TAG_NAME, "tr"):
                thespacereportitem = TheSpaceReportItem()
                tds = tr.find_elements(By.TAG_NAME, "td")
                launchid = thespacereportitem["LaunchID"] = tds[0].text
                thespacereportitem["DateTime"] = tds[1].text
                launch_vehicle = thespacereportitem["LaunchVehicle"] = tds[2].text
                thespacereportitem["OperatorCountry"] = tds[3].text
                launch_site = thespacereportitem["LaunchSite"] = tds[4].text
                thespacereportitem["Status"] = tds[5].text
                mission_sector = thespacereportitem["MissionSector"] = tds[6].text
                thespacereportitem["Crewed"] = tds[7].text
                thespacereportitem["FirstStageRecovery"] = tds[8].text

                yield thespacereportitem
                print(f'LaunchID(Cospar): {thespacereportitem["LaunchID"]}')
                # set data on planet4589table
                self.set_data(launch_vehicle=launch_vehicle, launch_site=launch_site, mission_sector=mission_sector, launchid=launchid, connection=self.connection)
                self.scraped_items.append(thespacereportitem)

            stop = self.driver.find_element(By.ID, "table_3_info")
            temp = re.search(r"([0-9]+) of ([0-9]+)", stop.text)
            condition = int(temp[1]) < int(temp[2])

            next = self.driver.find_element(By.ID, "table_3_next")
            self.driver.execute_script("arguments[0].click();", next)
            time.sleep(1.5)

    def set_data(self, launch_vehicle, launch_site, mission_sector, launchid, connection):
        print(f'getting launch vehicle {launch_vehicle} for cospar {launchid}')
        #query = "UPDATE planet4589 SET launch_vehicle = %s WHERE piece LIKE %s"
        query = "UPDATE planet4589 SET launch_vehicle = %s, launch_site = %s, mission_sector = %s WHERE piece LIKE %s"


        with connection.cursor() as cure:
            try:
                #like_pattern = f"'{launchid}%'"
                #launch_vehicle_quoted = f"'{launch_vehicle}'"
                like_pattern = f'{launchid}%'
                launch_vehicle_quoted = f'{launch_vehicle}'
                launch_site_quoted = f'{launch_site}'
                mission_sector_quoted = f'{mission_sector}'
                print(f"Executing query: {query % (launch_vehicle_quoted, launch_site_quoted, mission_sector_quoted, like_pattern)}")
                #input()
                cure.execute(query, (launch_vehicle_quoted, launch_site_quoted, mission_sector_quoted, like_pattern))
                print(f"Rows affected: {cure.rowcount}")
                connection.commit()
                print("Query executed successfully!")
            except Exception as e:
                connection.rollback()
                print(f"Error executing query: {e}")
                import traceback
                traceback.print_exc()

    def closed(self, reason):
        self.driver.quit()
        current_datetime = datetime.now().strftime('%m-%d-%Y_%H-%M-%S')
        current_month_year = date.today().strftime('%B_%Y')
        folder_name = os.path.join('CSVs/THESPACEREPORT', current_month_year)
        os.makedirs(folder_name, exist_ok=True)
        csv_filename = os.path.join(folder_name, f'TheSpaceReport_{current_datetime}.csv')
        df = pd.DataFrame(self.scraped_items)
        df.to_csv(csv_filename, index=False)
        print(f'Scraped data exported to {csv_filename}')
