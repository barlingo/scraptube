#!./venv/bin/python3
import urllib.parse
from random import randint
import time
import logging
from bs4 import BeautifulSoup
from selenium import webdriver

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter(
    '%(asctime)s | %(name)s | %(levelname)s | %(message)s')

file_handler = logging.FileHandler(__name__ + ".log")
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)

stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.INFO)
stream_handler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.addHandler(stream_handler)


class YoutubeSearch:

    def __init__(self, search_terms, max_results=None, max_scroll=100):
        self.search_terms = search_terms
        self.max_scroll = max_scroll
        self.max_results = max_results
        self.videos = self.search()
        self.count = len(self.videos)

    def search(self):

        encoded_search = urllib.parse.quote(self.search_terms)
        base_url = "https://youtube.com"
        url = f"{base_url}/results?search_query={encoded_search}"
        response = self.request_driver(url)
        results = []
        while not results:
            results = self.parse_lxml(response)

        if self.max_results is not None and len(results) > self.max_results:
            return results[:self.max_results]

        logger.info(
            f'Found {len(results)} youtube videos for {self.search_terms}')
        return results

    def parse_lxml(self, soup):
        videos = soup.findAll(
            'a', {"class": "yt-simple-endpoint style-scope ytd-video-renderer"})

        video_id_list = []

        for video in videos:
            find = str(video)
            video_id = find[(find.find("href"))+15:(find.find("id="))-2]
            if (video_id.find("imple")) == -1:
                video_id_list.append(video_id)

        return video_id_list

    def request_driver(self, url):
        command = "window.scrollTo(0, document.documentElement.scrollHeight);"
        driver = webdriver.Firefox()
        driver.get(url)
        time.sleep(randint(1, 3))
        for _ in range(0, self.max_scroll):
            driver.execute_script(command)
            time.sleep(randint(1, 3))

        response = BeautifulSoup(driver.page_source, "lxml")
        driver.quit()
        return response

    def to_list(self):
        return self.videos
