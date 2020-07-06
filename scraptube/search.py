#!./venv/bin/python3
import urllib.parse
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
import time
from random import randint


class YoutubeSearch:

    def __init__(self, search_terms, max_results=None):
        self.search_terms = search_terms
        self.max_results = max_results
        self.videos = self.search()

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
        for _ in range(0, 100):
            driver.execute_script(command)
            time.sleep(randint(1, 3))

        response = BeautifulSoup(driver.page_source, "lxml")
        driver.quit()
        return response

    def to_list(self):
        return self.videos
