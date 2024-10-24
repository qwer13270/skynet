import scrapy
import requests
import pandas as pd
from tqdm import tqdm
from myspider.items import UcsdataItem
from io import BytesIO
import psycopg2
from datetime import date, datetime
import os
import re
from dotenv import load_dotenv

#get env variables from .env
load_dotenv()

class UcsdataSpider(scrapy.Spider):
    name = "ucsdataspider"
    allowed_domains = ["ucsusa.org"]
    start_urls = ["https://www.ucsusa.org/resources/satellite-database"]
    custom_settings = {
        'ITEM_PIPELINES': {
            'myspider.pipelines.UcsdataPipeleine': 100,
            },
        'LOG_LEVEL': 'CRITICAL',
    }

    def __init__(self, *args, **kwargs):
        super(UcsdataSpider, self).__init__(*args, **kwargs)
        self.total_count = 0
        self.processed_count = 0
        self.scraped_items = []
        #to access database for data_status
        # hostname = 'localhost'  # this will be universal
        # username = 'skynetapp'  # create a new user with name: 'skynetapp'
        # password = 'skynet'  # make the password 'skynet' when you create the new user
        # # database = 'skynet' # we don't need this for this to work

        hostname = os.getenv('DB_HOST')
        username = os.getenv('DB_USER')
        password = os.getenv('DB_PASSWORD')
        #database = os.getenv('DB_NAME')

        self.connection = psycopg2.connect(host=hostname, user=username, password=password)
        self.cur = self.connection.cursor()

    #helper to retrieve reentry_sats
    def gather_reentry_sats(self):
        try:
            table_name = 'aero'
            column_name = 'cospar_num'
            query_r = f'SELECT {column_name} from {table_name}'
            self.cur.execute(query=query_r)
            self.connection.commit()
            rows = self.cur.fetchall()
            result_list = [list(row) for row in rows]
            cospar_list = []
            for row in result_list:
                cospar_list.append(row[0].strip())
        except Exception as e:
            print(f'Exception: {e}')
        finally:
            self.cur.close()
            self.connection.close()
        #print(cospar_list)
        #input()
        return cospar_list

    def parse(self, response):
        #default data status
        default_data_status = 10
        excel_url = response.css('.column-section .main-region ul li a').attrib['href']
        excel_url = f'https://ucsusa.org{excel_url}'
        print(f'URL for UCS Dataset: {excel_url}')
        response = requests.get(excel_url)
        excel_content = BytesIO(response.content)
        df = pd.read_excel(excel_content)
        #clean up messy UCS entries.
        df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)
        df = df.drop(['Comments', 
                      'Unnamed: 28', 
                      'Source.2',
                      'Source.3',
                      'Source.4',
                      'Source.5',
                      'Source.6',
                      'Unnamed: 37',
                      'Unnamed: 38',
                      'Unnamed: 39',
                      'Unnamed: 40',
                      'Unnamed: 41',
                      'Unnamed: 42',
                      'Unnamed: 43',
                      'Unnamed: 44',
                      'Unnamed: 45',
                      'Unnamed: 46',
                      'Unnamed: 47',
                      'Unnamed: 48',
                      'Unnamed: 49',
                      'Unnamed: 50',
                      'Unnamed: 51',
                      'Unnamed: 52',
                      'Unnamed: 53',
                      'Unnamed: 54',
                      'Unnamed: 55',
                      'Unnamed: 56',
                      'Unnamed: 57',
                      'Unnamed: 58',
                      'Unnamed: 59',
                      'Unnamed: 60',
                      'Unnamed: 61',
                      'Unnamed: 62',
                      'Unnamed: 63',
                      'Unnamed: 64',
                      'Unnamed: 65',
                      'Unnamed: 66',
                      'Unnamed: 67'], axis=1)
        
        column_dic = {
            'Name of Satellite, Alternate Names': 'full_name',
            'Current Official Name of Satellite': 'official_name',
            'Country/Org of UN Registry': 'country',
            'Country of Operator/Owner': 'owner_country',
            'Operator/Owner': 'owner',
            'Users': 'users',
            'Purpose': 'purpose',
            'Detailed Purpose': 'detail_purpose',
            'Class of Orbit': 'orbit_class',
            'Type of Orbit': 'orbit_type',
            'Longitude of GEO (degrees)': 'in_geo',
            'Perigee (km)': 'perigee',
            'Apogee (km)': 'apogee',
            'Eccentricity': 'eccentricity',
            'Inclination (degrees)': 'inclination',
            'Period (minutes)': 'period',
            'Launch Mass (kg.)': 'mass',
            'Dry Mass (kg.)': 'dry_mass',
            'Power (watts)': 'power',
            'Date of Launch': 'launch_date',
            'Expected Lifetime (yrs.)': 'expected_lifetime',
            'Contractor': 'contractor',
            'Country of Contractor': 'contractor_country',
            'Launch Site': 'launch_site',
            'Launch Vehicle': 'launch_vehicle',
            'COSPAR Number': 'cospar',
            'NORAD Number': 'norad',
            'Source Used for Orbital Data': 'source_used_for_orbital_data',
            'Source': 'source',
            'Source.1': 'additional_source',
        }
        df.rename(columns=column_dic, inplace=True)
        df['launch_date'] = df['launch_date'].apply(lambda x: re.search(r'\d{4}-\d{2}-\d{2}', str(x)).group() if re.search(r'\d{4}-\d{2}-\d{2}', str(x)) else None)
        #set default_data_status for every sat, this will change
        #when we get re_entry sats etc.
        df['data_status'] = default_data_status
        #get rows which have conflicting cospar duplicates
        #and set data_status = 5 for them
        duplicate_rows = df[df.duplicated(subset='cospar', keep=False)]
        df.loc[duplicate_rows.index, 'data_status'] = 5
        #access aero to gather reentry satellites's cospar
        #change data_status = 2 for re-entered sats
        cospar_list = self.gather_reentry_sats()
        df.loc[df['cospar'].isin(cospar_list), 'data_status'] = 2
        df['id'] = df.reset_index().index + 1
        filtered_df_cospar = df[df['data_status'] == 2]
        filtered_df_dupes = df[df['data_status'] == 5]
        #print(filtered_df_cospar)
        #input()
        #print(filtered_df_dupes)
        self.total_count = len(df)
        progress_bar = tqdm(total=self.total_count, desc='Latest UCS Excel Scraping Progress', unit='item')

        for index, row in df.iterrows():
            ucs_item = UcsdataItem()
            for field in ucs_item.fields:
                value = row.get(field)
                ucs_item[field] = str(value).strip()
            yield ucs_item
            self.processed_count += 1
            self.scraped_items.append(ucs_item)
            progress_bar.update(1)
        progress_bar.close()

    def closed(self, reason):
        if self.total_count > 0:
            percentage_completed = (self.processed_count / self.total_count) * 100
            print(f"\tLatest UCS Excel Scraping progress: {percentage_completed:.2f}% completed.")
            print('\tPopulating CSV now')
            current_datetime = datetime.now().strftime('%m-%d-%Y_%H-%M-%S')
            current_month_year = date.today().strftime('%B_%Y')
            folder_name = os.path.join('CSVs/UCS_MASTER', current_month_year)
            os.makedirs(folder_name, exist_ok=True)
            csv_filename = os.path.join(folder_name, f'ucs_master_{current_datetime}.csv')
            df = pd.DataFrame(self.scraped_items)
            df.to_csv(csv_filename, index=False)
            print(f'\tScraped data exported to {csv_filename}\n')