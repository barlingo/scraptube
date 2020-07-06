"""
Scraptube
"""
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
        self.video_id = video_id
        self.extension = extension
        self.link = "{}={}".format(self.youtube_url, self.video_id)
        self.source = pytube.YouTube(self.link)
        self.download_path = path + "/sv_" + self.video_id + "." + self.extension
        # Can be none easily should add a unit test
        self.stream = self.source.streams.first()

        self.title = self.stream.title
        self.filesize = self.stream.filesize

    def __str__(self):
        size = round(self.filesize * 1e-6, 2)
        return """id = {self.video_id} title = {self.title}
                size = {size}MB url = {self.link}"""

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
