"""
Scraptube
"""
import concurrent.futures
from fnmatch import fnmatch
import os
import csv
import pytube

BASE_URL = "https://youtube.com"


class SourceVideo():
    """
    SourceVideo class.
    """
    youtube_url = BASE_URL + "/watch?v"
    counter = 0
    default_path = "./output"

    def __init__(self, video_id, path=default_path, extension="mp4"):
        type(self).counter += 1
        self.video_id = str(video_id)
        self.extension = extension
        self.link = "{}={}".format(self.youtube_url, self.video_id)
        self.source = pytube.YouTube(self.link)
        self.download_path = path + "/sv_" + self.video_id + "." + self.extension
        self.csv = path + "/sv_" + self.video_id + ".csv"
        # Can be none easily should add a unit test
        self.stream = self.source.streams.get_lowest_resolution()

    def __str__(self):
        return """id = {self.video_id} title = {self.title}
                url = {self.link}"""

    @staticmethod
    def get_sec(time_str):
        """
        Get time in seconds from hh:mm:ss format.
        """
        hours, minutes, seconds = time_str.split(':')
        total_s = float(hours) * 3600 + float(minutes) * 60 + \
            float(seconds.replace(',', '.'))
        return total_s

    def download(self, path=default_path):
        """
        Downloads stream to selected folder.
        """
        self.stream.download(
            output_path=path, filename=self.video_id, filename_prefix='sv_')


class extractVideos(object):
    def __init__(self, path, youtube_ids, pattern="sv_*.csv"):
        self.path = path
        self.pattern = pattern
        self.youtube_ids = youtube_ids

    @staticmethod
    def log_video(file, row):
        with open(file, 'w+') as result_file:
            writer = csv.writer(result_file, dialect='excel')
            writer.writerow(row)

    def list_csv(self):
        csv_list = []
        for self.path, _, files in os.walk(self.path):
            for name in files:
                if fnmatch(name, self.pattern):
                    csv_list.append(os.path.join(self.path, name))
        return csv_list

    def merge_logs(self, exercise):
        csv_list = self.list_csv()
        fout = open(self.path + "/" + exercise + ".csv", "a")
        for file in csv_list:
            for line in open(file):
                fout.write(line)
        fout.close()

    def purge_logs(self):
        for self.path, _, files in os.walk(self.path):
            for name in files:
                if fnmatch(name, self.pattern):
                    os.remove(os.path.join(self.path, name))

    def download_video(self, youtube_id):
        try:
            video = SourceVideo(youtube_id, self.path)
            video.download(self.path)
            try:
                en_captions = video.source.captions['en']
                en_captions_srt = en_captions.generate_srt_captions()
            except:
                en_captions_srt = 'no captions'
            self.log_video(video.csv, [video.video_id,
                                       video.link,
                                       video.download_path,
                                       video.source.description,
                                       video.source.length,
                                       video.stream.filesize,
                                       en_captions_srt])
            print(f'Downloaded video with id {youtube_id}')
        except:
            print(f'Unable to download {youtube_id}')

    def parallel_download(self):
        with concurrent.futures.ThreadPoolExecutor() as executor:
            executor.map(self.download_video, self.youtube_ids)
