import scrapy
from myspider.items import OrbitalfocusItem
from tqdm import tqdm
from datetime import date, datetime
import os
import pandas as pd

class OrbitalfocusspiderSpider(scrapy.Spider):
    name = "orbitalfocusspider"
    allowed_domains = ["orbitalfocus.uk"]
    start_urls = ["http://orbitalfocus.uk/Diaries/Launches/Decays.php"]
    custom_settings = {
        'ITEM_PIPELINES': {
            'myspider.pipelines.OrbitalfocusPipeline': 500,
            },
        'LOG_LEVEL': 'CRITICAL',
    }

    def __init__(self, *args, **kwargs):
        super(OrbitalfocusspiderSpider, self).__init__(*args, **kwargs)
        self.total_count = 0
        self.processed_count = 0
        self.scraped_items = []

    def parse(self, response):
        satellites = response.css('center')[3].css('.bodyrow')
        self.total_count = len(satellites)

        progress_bar = tqdm(total=self.total_count, desc='OrbitalFocus Scraping Progress', unit='item')
        
        for satellite in satellites:
            self.processed_count += 1
            orbitalfocus_item = OrbitalfocusItem()
            #NORAD Number
            orbitalfocus_item['cat_no'] = satellite.css('td::text')[0].get()
            #COSPAR Number
            orbitalfocus_item['designation'] = satellite.css('td::text')[1].get()
            orbitalfocus_item['name'] = satellite.css('td strong::text')[0].get()
            orbitalfocus_item['date'] = satellite.css('td strong::text')[1].get()
            yield orbitalfocus_item
            self.scraped_items.append(orbitalfocus_item)
            progress_bar.update(1)
        progress_bar.close()

    def closed(self, reason):
        if self.total_count > 0:
            percentage_completed = (self.processed_count / self.total_count) * 100
            print(f"\tOrbitalFocus Scraping progress: {percentage_completed:.2f}% completed.")
            print('\tPopulating CSV')
            current_datetime = datetime.now().strftime('%m-%d-%Y_%H-%M-%S')
            current_month_year = date.today().strftime('%B_%Y')
            folder_name = os.path.join('CSVs/ORBITALFOCUS', current_month_year)
            os.makedirs(folder_name, exist_ok=True)
            csv_filename = os.path.join(folder_name, f'orbitalfocus_data_{current_datetime}.csv')
            df = pd.DataFrame(self.scraped_items)
            df.to_csv(csv_filename, index=False)
            print(f'\tScraped data exported to {csv_filename}\n')