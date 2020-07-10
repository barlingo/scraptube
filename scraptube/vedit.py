"""
vedit module

"""
import os
from os import walk
import cv2
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip
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

        ffmpeg_extract_subclip(video_path, start, end,
                               targetname=self.filename)


class MainVideoProcessing():

    def __init__(self, path):
        self.video_path = path
        self.fps, self.seconds, self.frames = self.get_duration()

    def get_duration(self):
        video = cv2.VideoCapture(self.video_path)
        fps = video.get(cv2.CAP_PROP_FPS)
        frames = video.get(cv2.CAP_PROP_FRAME_COUNT)
        seconds = frames / fps
        return fps, seconds, frames

    def split_into_subclips(self, step, path):
        for start in range(0, int(self.seconds), step):
            end = start + step
            _ = Subclip(self.video_path, start, end, path)


class SubFolderProcessing():
    def __init__(self, subfolder_path):
        self.subfolder_path = subfolder_path
        self.filenames = self.ls_videos()
        self.total_files = len(self.filenames)
        self.name = os.path.basename(os.path.normpath(self.subfolder_path))

    def process_files(self, step):
        for filename in self.filenames:
            if not filename.endswith('.csv'):
                video_path = f'{self.subfolder_path}/{filename}'
                video = MainVideoProcessing(video_path)
                video.split_into_subclips(step, path=self.subfolder_path)
                os.remove(video_path)

    def ls_videos(self):
        filenames_list = []
        for (_, _, filenames) in walk(self.subfolder_path):
            filenames_list.extend(filenames)

        return filenames_list


class MainFolderProcessing():

    def __init__(self, main_path):
        self.main_folder_path = main_path
        self.paths = self.ls_subfolders()

    def ls_subfolders(self):
        filenames_list = []
        paths_list = []
        for (dirpath, _, filenames) in walk(self.main_folder_path):
            filenames_list.extend(filenames)
            paths_list.append(dirpath)

        paths_list = paths_list[1:]
        return filenames_list, paths_list

    def process_subfolders(self, step):
        for subfolder in self.paths:
            processor = SubFolderProcessing(subfolder)
            processor.process_files(step)
