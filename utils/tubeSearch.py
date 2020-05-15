#!../venv/bin/python3
import ffmpeg
import pytube
import youtube_search

import json
import re
import urllib.request

class sourceVideo:

    youtube_url = "http://youtube.com/watch?v"
    num_videos = 0
    default_path = "../data"

    def __init__(self, id, file_ext="mp4", resolution="360p", language="en"):
        self.id = id
        self.resolution = resolution
        self.extension = file_ext
        self.link = "{}={}".format(self.youtube_url, self.id)
        self.source = pytube.YouTube(self.link)

        # Can be none easily should add a unit test
        self.stream = self.source.streams.filter(
            file_extension=file_ext).get_by_resolution(resolution)

        self.title = self.stream.title
        self.filesize = self.stream.filesize
        self.captions = self.source.captions[language].generate_srt_captions()

        sourceVideo.num_videos += 1

    def download(self, path="../data"):
        self.stream.download(
            output_path=path, filename=self.id, filename_prefix='sv_')

    def __str__(self):
        pass


results = youtube_search.YoutubeSearch(
    'workout videos', max_results=2).to_json()

results_dict = json.loads(results)
print(results_dict)
video1 = sourceVideo(results_dict['videos'][1]['id'])
print(video1.link)
print(video1.title)
print(video1.resolution)
video1.download()
