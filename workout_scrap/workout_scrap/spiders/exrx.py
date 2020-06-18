import scrapy
from workout_scrap.items import exrxItem
from scrapy.loader import ItemLoader


class exrxSpyder(scrapy.Spider):
    name = 'exrx'
    start_urls = [
        "https://exrx.net/Lists/Directory"
    ]

    def parse(self, response):
        for href in response.xpath("//article/div/div/div/div/div/ul/li/a/@href"):
            url = response.urljoin(href.extract())
            yield scrapy.Request(url, callback=self.parse_dir_contents)

#        for href in response.xpath("//*[@id='mainShell']/article/div/div/div/div/div/ul/li[6]//a/@href"):
#            url = response.urljoin(href.extract())
#            yield scrapy.Request(url, callback=self.parse_dir_olympic)

    def parse_dir_contents(self, response):
        for href in response.xpath("//article/div/div/div/div/div/ul/li/ul/li//a/@href"):
            url = response.urljoin(href.extract())
            yield scrapy.Request(url, callback=self.parse_exercises)

    def parse_dir_olympic(self, response):
        for href in response.xpath("//div[1]/main/article/div/div/div/ul/li//a/@href"):
            url = response.urljoin(href.extract())
            yield scrapy.Request(url, callback=self.parse_exercises)

    def parse_exercises(self, response):

        loader = ItemLoader(item=exrxItem(), selector=response)

        loader.add_xpath('video_url',
                         "//video/source/@src")
        loader.add_xpath('exercise',
                         "//h1[@class='page-title']")
        loader.add_xpath('main_muscle',
                         "//div/div/div/div/p/a[3]")
        loader.add_xpath('utility',
                         "//*[@id='mainShell']/div[1]/main/article[1]/div/div/div[1]/table/tbody/tr[1]//a")
        loader.add_xpath('mechanics',
                         "//*[@id='mainShell']/div[1]/main/article[1]/div/div/div[1]/table/tbody/tr[2]//a")
        loader.add_xpath('force_type',
                         "//*[@id='mainShell']/div[1]/main/article[1]/div/div/div[1]/table/tbody/tr[3]//a")
        yield loader.load_item()
