#!./venv/bin/python3
import pytube


class SourceVideo(object):
    youtube_url = "http://youtube.com/watch?v"
    counter = 0
    default_path = "./output"

    def __init__(self, video_id, file_ext="mp4", resolution="360p",
                 language="en", path=default_path):
        type(self).counter += 1

        self.id = video_id
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

    def __str__(self):
        return ("id = {}\ntitle = {}\nresolution = {}\nfile extension = {}\n"
                "size = {}MB\nurl = {}\n"
                ).format(self.id, self.title, self.resolution, self.extension,
                         round(self.filesize * 1e-6, 2), self.link)

    def download(self, path=default_path):
        self.stream.download(
            output_path=path, filename=self.id, filename_prefix='sv_')
        self.download_path = path + "/sv_" + self.id + "." + self.extension
