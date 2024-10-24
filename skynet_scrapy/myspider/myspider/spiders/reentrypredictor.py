import scrapy
from datetime import date
import calendar
import pandas as pd
from myspider.items import ReentrypredictorItem
from datetime import date, datetime
from tqdm import tqdm
import os


class ReentrypredictorSpider(scrapy.Spider):
    name = "reentrypredictor"
    allowed_domains = ["aerospace.org"]
    start_urls = ["https://aerospace.org/reentries/grid?field_reentry_type_target_id%5B%5D=32&field_reentry_sighting_value=All&format_select=table&reentry_timezone_selector=UTC"]
    custom_settings = {
        'ITEM_PIPELINES': {
            'myspider.pipelines.ReentrypredictorPipeline': 400,
            },
        'LOG_LEVEL': 'CRITICAL',
    }

    def __init__(self, *args, **kwargs):
        super(ReentrypredictorSpider, self).__init__(*args, **kwargs)
        self.total_count = 0
        self.processed_count = 0
        self.actual_item_count = 1
        self.scraped_items = []

    def parse_limit(self, prediction):
        month_list = []
        month_list_one, month_list_two, month_list_three = ['Jan', 'Feb', 'March', 'Apr'], ['May', 'Jun', 'Jul', 'Aug'], ['Sep', 'Oct','Nov', 'Dec']
        today = date.today()
        curr_month = calendar.month_abbr[today.month]
        curr_year = today.year
        if curr_month in month_list_one and curr_year == int(prediction.css('.views-field-field-predicted-reentry-time .field-data time::text').get().split(' ')[2]):
            month_list = month_list_one[:]
        if curr_month in month_list_two and curr_year == int(prediction.css('.views-field-field-predicted-reentry-time .field-data time::text').get().split(' ')[2]):
            month_list = month_list_two[:]
        if curr_month in month_list_three and curr_year == int(prediction.css('.views-field-field-predicted-reentry-time .field-data time::text').get().split(' ')[2]):
            month_list = month_list_three[:]
        #print(month_list)
        return month_list

    # def parse(self, response):
    #     data_list = []
    #     predictions = response.css('.even')
    #     odd_predictions = response.css('.odd')
    #     for odd_prediction in odd_predictions:
    #         predictions.append(odd_prediction)
    #     stop_parsing = False

    #     for prediction in predictions:
    #         if self.parse_limit(prediction) == []:
    #             break

    #         if prediction.css('.views-field-field-predicted-reentry-time .field-data time::text').get().split(' ')[0] not in self.parse_limit(prediction):
    #             stop_parsing = True
    #         if prediction.css('.views-field-field-predicted-reentry-time .field-data time::text').get().split(' ')[0] in self.parse_limit(prediction):

    #             reentrypredictor_item = ReentrypredictorItem()
    #             reentrypredictor_item['object'] = prediction.css('.views-field-title .field-data a::text').get()
    #             reentrypredictor_item['mission'] = prediction.css('.views-field-field-mission .field-data::text').get().strip()
    #             reentrypredictor_item['reentry_type'] = prediction.css('.views-field-field-reentry-type .field-data::text').get().strip()
    #             reentrypredictor_item['launch_date'] = prediction.css('.views-field-field-launched .field-data time::text').get()
    #             reentrypredictor_item['predicted_reentry_date'] = prediction.css('.views-field-field-predicted-reentry-time .field-data time::text').get()
    #             base_url = 'https://aerospace.org/reentries/'
    #             prediction_url = base_url + prediction.css('.views-field-title .field-data a::text').get().split(" ")[-1].replace(')', '')
    #             yield scrapy.Request(prediction_url, callback=self.parse_prediction_page, cb_kwargs={'reentrypredictor_item': reentrypredictor_item})

    #     next_page = response.css('li.pager__item--next a::attr(href)').get()
    #     print(next_page)
    #     if next_page is not None and not stop_parsing:
    #         next_page_url = f'https://aerospace.org/reentries/grid{next_page}'
    #         print(next_page_url)
    #         yield response.follow(next_page_url, callback = self.parse)

    def parse(self, response):
        data_list = []
        curr_year = date.today().year
        predictions = response.css('.even')
        odd_predictions = response.css('.odd')
        for odd_prediction in odd_predictions:
            predictions.append(odd_prediction)
        stop_parsing = False
        self.total_count = len(predictions)
        #progress_bar = tqdm(predictions, dynamic_ncols=True)
        progress_bar = tqdm(total=self.total_count, desc=f'Aerospace Scraping Progress Page {self.actual_item_count}', unit='item')
        for prediction in predictions:

            # if self.parse_limit(prediction) == []:
            #     self.total_count -= 1
            #     break
            if int(prediction.css('.views-field-field-predicted-reentry-time .field-data time::text').get().split(' ')[2]) != curr_year:
                # self.total_count -= 1
                stop_parsing = True
            if int(prediction.css('.views-field-field-predicted-reentry-time .field-data time::text').get().split(' ')[2]) == curr_year:
                #actual_item_count += 1
                reentrypredictor_item = ReentrypredictorItem()
                reentrypredictor_item['object'] = prediction.css('.views-field-title .field-data a::text').get()
                reentrypredictor_item['mission'] = prediction.css('.views-field-field-mission .field-data::text').get().strip()
                reentrypredictor_item['reentry_type'] = prediction.css('.views-field-field-reentry-type .field-data::text').get().strip()
                reentrypredictor_item['launch_date'] = prediction.css('.views-field-field-launched .field-data time::text').get()
                reentrypredictor_item['predicted_reentry_date'] = prediction.css('.views-field-field-predicted-reentry-time .field-data time::text').get()
                #base_url = 'https://aerospace.org/reentries/'
                #prediction_url = base_url + prediction.css('.views-field-title .field-data a::text').get().split(" ")[-1].replace(')', '')
                prediction_url = f"https://aerospace.org{prediction.css('.field-data a').attrib['href']}"
                yield scrapy.Request(prediction_url, callback=self.parse_prediction_page, cb_kwargs={'reentrypredictor_item': reentrypredictor_item})
                #progress_bar.set_description(f'Processing: {prediction}')
                progress_bar.update(1)

        next_page = response.css('li.pager__item--next a::attr(href)').get()
        #print(next_page)
        if next_page is not None and not stop_parsing:
            self.actual_item_count += 1
            next_page_url = f'https://aerospace.org/reentries/grid{next_page}'
            #print(next_page_url)
            yield response.follow(next_page_url, callback = self.parse)
        progress_bar.close()

    def parse_prediction_page(self, response, reentrypredictor_item):
        table_rows = response.css('table tr')
        reentrypredictor_item['norad_num'] = table_rows[7].css('td div::text').get()
        reentrypredictor_item['cospar_num'] = table_rows[6].css('td::text').get()
        yield reentrypredictor_item
        self.scraped_items.append(reentrypredictor_item)
        self.processed_count += 1

    def closed(self, reason):
        if self.total_count > 0:
            if self.actual_item_count > 0:
                self.total_count *= self.actual_item_count
            # print(self.processed_count)
            # print(self.total_count)
            # print(self.actual_item_count)
            percentage_completed = (self.processed_count / self.total_count) * 100
            print(f"\tAerospace Scraping progress: {percentage_completed:.2f}% completed.")
            print(f'\t{self.processed_count} valid predicted re-entries out a total of {self.total_count} scraped')
            print('\tPopulating CSV')
            current_datetime = datetime.now().strftime('%m-%d-%Y_%H-%M-%S')
            current_month_year = date.today().strftime('%B_%Y')
            folder_name = os.path.join('CSVs/AEROSPACE', current_month_year)
            os.makedirs(folder_name, exist_ok=True)
            csv_filename = os.path.join(folder_name, f'aerospace_data_{current_datetime}.csv')
            df = pd.DataFrame(self.scraped_items)
            df.to_csv(csv_filename, index=False)
            print(f'\tScraped data exported to {csv_filename}\n')