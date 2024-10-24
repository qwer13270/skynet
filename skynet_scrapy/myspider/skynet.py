from myspider.spiders.orbitalfocusspider import OrbitalfocusspiderSpider
from myspider.spiders.planet4589 import Planet4589spiderSpider
from myspider.spiders.reentrypredictor import ReentrypredictorSpider
from myspider.spiders.ntwoyo import NtwoYOSpider
from myspider.spiders.nanosats import NanoSatsSpider
from myspider.spiders.thespacereport import TheSpaceReportSpider
from myspider.spiders.ucsdata import UcsdataSpider
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from myspider.Gatherer import Gatherer
from myspider.deletions import Deletions
from twisted.internet import defer

# def main():
#     spiders = [Planet4589spiderSpider, ReentrypredictorSpider, OrbitalfocusspiderSpider]
#     settings = get_project_settings()
#     process = CrawlerProcess(settings)
#     process.crawl(OrbitalfocusspiderSpider)
#     process.crawl(Planet4589spiderSpider)
#     process.crawl(ReentrypredictorSpider)
#     process.crawl(UcsdataSpider)
#     process.start()
#     gatherer = Gatherer()
#     gatherer.gather()
#     deletion = Deletions()
#     deletion.MarkDeletions()

## need to run the crawlers sequentially
@defer.inlineCallbacks
def run_spiders_sequentially(spiders, process):
    for spider_cls in spiders:
        yield process.crawl(spider_cls)
    process.stop()
    defer.returnValue(None)

#PUT CODE HERE TO EXECUTE AFTER SPIDERS 
#HAVE FINISHED RUNNING
def run_after_spiders_finished(result):
    gatherer = Gatherer()
    gatherer.gather()
    #deletion = Deletions()
    #deletion.MarkDeletions()
    
    return result

def main():
    spiders = [
        Planet4589spiderSpider,
        ReentrypredictorSpider,
        OrbitalfocusspiderSpider,
        NtwoYOSpider,
        NanoSatsSpider,
        TheSpaceReportSpider,
        UcsdataSpider,
    ]
    
    settings = get_project_settings()
    process = CrawlerProcess(settings)

    deferred = run_spiders_sequentially(spiders, process)
    deferred.addBoth(lambda _: process.stop())

    # Add a callback to the deferred to run code after spiders have finished
    deferred.addBoth(run_after_spiders_finished)

    process.start()

if __name__ == '__main__':
    main()