import scrapy
from workout_scrap.items import MuscleStrengthItem
from scrapy.loader import ItemLoader


class MuscleStretghSpyder(scrapy.Spider):
    name = 'muscle_strength'
    start_urls = [
        "https://www.muscleandstrength.com/exercises/"
    ]

    def parse(self, response):
        for href in response.xpath("//div[@class='cell']/a/@href"):
            url = response.urljoin(href.extract())
            yield scrapy.Request(url, callback=self.parse_dir_contents)

    def parse_dir_contents(self, response):
        for href in response.xpath("//h5[@class='exerciseName']/a/@href"):
            url = response.urljoin(href.extract())
            yield scrapy.Request(url, callback=self.parse_exercises)

        next_page = response.xpath(
            "//li[@class='pager-next']/a/@href").extract_first()
        if next_page is not None:
            next_page_link = response.urljoin(next_page)
            yield scrapy.Request(next_page_link, callback=self.parse_dir_contents)

    def parse_exercises(self, response):

        loader = ItemLoader(item=MuscleStrengthItem(), selector=response)

        loader.add_xpath('video_url',
                         "//video/source/@src")
        loader.add_xpath('youtube_url',
                         "//iframe/@src")
        loader.add_xpath('exercise',
                         "//h1[@class='no-header']")
        loader.add_xpath('main_muscle',
                         "//ul[@class='dataList']/li[1]/div")
        loader.add_xpath('exc_type',
                         "//ul[@class='dataList']/li[2]/div")
        loader.add_xpath('equipment',
                         "//ul[@class='dataList']/li[3]/div")
        loader.add_xpath('mechanics',
                         "//ul[@class='dataList']/li[4]/div")
        loader.add_xpath('force_type',
                         "//ul[@class='dataList']/li[5]/div")
        loader.add_xpath('exp_level',
                         "//ul[@class='dataList']/li[6]/div")
        loader.add_xpath('extra_muscles',
                         "//ul[@class='dataList']/li[7]/div")
        yield loader.load_item()
