"""
vedit module

"""
import os
import cv2
from os import walk
# from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip
# import moviepy.editor


class Subclip():
    """
    VideoSubClip
    """
    counter = 0
    default_path = "./chunks"

    def __init__(self, video_path, start, end, path=default_path,
                 file_ext='mp4'):
        type(self).counter += 1
        self.org_basename = os.path.basename(video_path)
        self.name = str(type(self).counter) + "_" + \
            os.path.splitext(self.org_basename)[0]
        self.filename = path + "/" + self.name + '.' + file_ext
        self.duration, _ = self.get_duration()

        # ffmpeg_extract_subclip(video_path, start, end, targetname=self.filename)


class MainVideoProcessing():

    def __init__(self, path):
        self.video_path = path
        self.duration = self.get_duration()

    def get_duration(self):
        video = cv2.VideoCapture(self.video_path)
        duration = video.get(cv2.CAP_PROP_POS_MSEC)
        frame_count = video.get(cv2.CAP_PROP_FRAME_COUNT)
        return duration, frame_count


def list_path(path):
    filenames_list = []
    paths_list = []
    for (dirpath, _, filenames) in walk(path):
        filenames_list.extend(filenames)
        paths_list.append(dirpath)

    paths_list = paths_list[1:]
    return filenames_list, paths_list


def process_files(path):
    filenames_list, _ = list_path(path)
    count = 0
    for filename in filenames_list:
        count += 1
        if not filename.endswith('.csv'):
            video_path = f'{path}/{filename}'
            video = MainVideoProcessing(video_path)
            print(video.duration)
        break
