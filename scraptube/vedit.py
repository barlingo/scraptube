"""
vedit module

"""
import os
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip
# import moviepy.editor


class VideoSubClip():
    """
    VideoSubClip
    """
    counter = 0
    default_path = "./output"

    def __init__(self, video_path, start, end, path=default_path,
                 file_ext='mp4'):
        type(self).counter += 1
        self.org_basename = os.path.basename(video_path)
        self.name = str(type(self).counter) + "_" + \
            os.path.splitext(self.org_basename)[0]
        self.filename = path + "/" + self.name + '.' + file_ext
        ffmpeg_extract_subclip(video_path, start, end,
                               targetname=self.filename)
