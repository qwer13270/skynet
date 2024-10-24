import scrapy
import pandas as pd
from io import StringIO
from myspider.items import Planet4589Item
from tqdm import tqdm
from datetime import date, datetime
import os

class Planet4589spiderSpider(scrapy.Spider):
    name = "planet4589spider"
    allowed_domains = ["planet4589.org"]
    start_urls = ["https://planet4589.org/space/gcat/tsv/cat/satcat.tsv"]
    custom_settings = {
        'ITEM_PIPELINES': {
            'myspider.pipelines.Planet4589Pipeline': 300,
            },
        'LOG_LEVEL': 'CRITICAL',
    }

    def __init__(self, *args, **kwargs):
        super(Planet4589spiderSpider, self).__init__(*args, **kwargs)
        self.total_count = 0
        self.processed_count = 0
        self.scraped_items = []

    def get_orbit_type(self, dataframe):
        orbit_mapping = {
        'ATM': 'Atmospheric',
        'SO': 'Suborbital',
        'TA': 'Trans-Atm.',
        'LLEO/E': 'Lower LEO/Equatorial',
        'LLEO/I': 'Lower LEO/Intermediate',
        'LLEO/P': 'Lower LEO/Polar',
        'LLEO/S': 'Lower LEO/Sun-Sync',
        'LLEO/R': 'Lower LEO/Retrograde',
        'LEO/E': 'Upper LEO/Equatorial',
        'LEO/I': 'Upper LEO/Intermediate',
        'LEO/P': 'Upper LEO/Polar',
        'LEO/S': 'Upper LEO/Sun-Sync',
        'LEO/R': 'Upper LEO/Retrograde',
        'MEO': 'Medium Earth Orbit',
        'HEO': 'Highly Elliptical Orbit',
        'HEO/M': 'Molniya',
        'GTO': 'Geotransfer',
        'GEO/S': 'Stationary',
        'GEO/I': 'Inclined GEO',
        'GEO/T': 'Synchronous',
        'GEO/D': 'Drift GEO',
        'GEO/SI': 'Inclined GEO',
        'GEO/ID': 'Inclined Drift',
        'GEO/NS': 'Near-sync',
        'VHEO': 'Very High Earth Orbit',
        'DSO': 'Deep Space Orbit',
        'CLO': 'Cislunar/Translunar',
        'EEO': 'Earth Escape',
        'HCO': 'Heliocentric',
        'PCO': 'Planetocentric',
        'SSE': 'Solar System Escape'
        }
        dataframe['orbit_type'] = dataframe['OpOrbit'].map(orbit_mapping)

    def parse(self, response):
        #set default data_status
        default_data_status = 10
        source_string = f'JMSatcat{datetime.now().strftime("%m_%y")}'
        tsv = StringIO(response.text)
        df = pd.read_csv(tsv, sep='\t', dtype=str)
        df = df.drop(0)
        df.rename(columns={"#JCAT": "JCAT"}, inplace=True)
        df = df[df['LDate'].str.startswith('2023')]
        #change data_status = 2 for re-entered sats
        #for sats with Status == 'R'
        df['data_status'] = default_data_status
        df['source_used_for_orbital_data'] = source_string
        df.loc[df['Status'] == 'R', 'data_status'] = 2
        self.get_orbit_type(df)
        # df = df[df['Status'].str.startswith('O')]
        #print(f'length = {len(df)}')
        #print(df)
        
        self.total_count = len(df)
        progress_bar = tqdm(total=self.total_count, desc='New Launches Scraping Progress', unit='item')

        for index, row in df.iterrows():
            sat_item = Planet4589Item()
            for field in sat_item.fields:
                value = row.get(field)
                sat_item[field] = str(value).strip()
            yield sat_item
            self.processed_count += 1
            self.scraped_items.append(sat_item)
            progress_bar.update(1)
        progress_bar.close()

    def closed(self, reason):
        if self.total_count > 0:
            percentage_completed = (self.processed_count / self.total_count) * 100
            print(f"\tNew Launches Scraping progress: {percentage_completed:.2f}% completed.")
            print('\tPopulating CSV now')
            current_datetime = datetime.now().strftime('%m-%d-%Y_%H-%M-%S')
            current_month_year = date.today().strftime('%B_%Y')
            folder_name = os.path.join('CSVs/UCS_NEW', current_month_year)
            os.makedirs(folder_name, exist_ok=True)
            csv_filename = os.path.join(folder_name, f'ucs_new_launches_{current_datetime}.csv')
            df = pd.DataFrame(self.scraped_items)
            df.to_csv(csv_filename, index=False)
            print(f'\tScraped data exported to {csv_filename}\n')