#!./venv/bin/python3
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip
# import moviepy.editor
import os


class VideoSubClip(object):
    counter = 0
    default_path = "./output"

    def __init__(self, video_path, start, end, path=default_path,
                 file_ext='mp4'):
        type(self).clips_num += 1
        self.org_basename = os.path.basename(video_path)
        self.name = os.path.splitext(self.org_basename)[0] + f'_{start}_{end}'
        self.filename = self.name + '.' + file_ext
        ffmpeg_extract_subclip(video_path, start, end,
                               target_name=self.filename)
