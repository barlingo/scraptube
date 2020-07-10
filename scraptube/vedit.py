"""
vedit module

"""
import os
import tkinter
from os import walk
import cv2
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip
# import moviepy.editor

import PIL.Image
import PIL.ImageTk
import time


class App:
    def __init__(self, window, window_title, video_source=0):
        self.window = window
        self.window.title(window_title)
        self.video_source = video_source

        # open video source (by default this will try to open the computer webcam)
        self.vid = MyVideoCapture(self.video_source)

        # Create a canvas that can fit the above video source size
        self.canvas = tkinter.Canvas(
            window, width=self.vid.width, height=self.vid.height)
        self.canvas.pack()

        # Button that lets the user take a snapshot
        self.btn_snapshot = tkinter.Button(
            window, text="Snapshot", width=50, command=self.snapshot)
        self.btn_snapshot.pack(anchor=tkinter.CENTER, expand=True)

        # After it is called once, the update method will be automatically called every delay milliseconds
        self.delay = 15
        self.update()

        self.window.mainloop()

    def snapshot(self):
        # Get a frame from the video source
        ret, frame = self.vid.get_frame()

        if ret:
            cv2.imwrite("frame-" + time.strftime("%d-%m-%Y-%H-%M-%S") +
                        ".jpg", cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))

    def update(self):
        # Get a frame from the video source
        ret, frame = self.vid.get_frame()

        if ret:
            self.photo = PIL.ImageTk.PhotoImage(
                image=PIL.Image.fromarray(frame))
            self.canvas.create_image(0, 0, image=self.photo, anchor=tkinter.NW)

        self.window.after(self.delay, self.update)


class MyVideoCapture:
    def __init__(self, video_source=0):
        # Open the video source
        self.vid = cv2.VideoCapture(video_source)
        if not self.vid.isOpened():
            raise ValueError("Unable to open video source", video_source)

        # Get video source width and height
        self.width = self.vid.get(cv2.CAP_PROP_FRAME_WIDTH)
        self.height = self.vid.get(cv2.CAP_PROP_FRAME_HEIGHT)

    def get_frame(self):
        if self.vid.isOpened():
            ret, frame = self.vid.read()
            if ret:
                # Return a boolean success flag and the current frame converted to BGR
                return (ret, cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            else:
                return (ret, None)
        else:
            return (ret, None)

    # Release the video source when the object is destroyed
    def __del__(self):
        if self.vid.isOpened():
            self.vid.release()


# Create a window and pass it to the Application object


class InspectClip():
    def __init__(self, clip_path):
        self.clip_path = clip_path

    def visualize(self):
        App(tkinter.Tk(), self.clip_path, self.clip_path)


class InspectSubFolder():
    def __init__(self):
        pass


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


class MainVideoClipping():

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
        self.filenames, self.file_paths = self.ls_videos()
        self.total_files = len(self.filenames)
        self.name = os.path.basename(os.path.normpath(self.subfolder_path))

    def clip_files(self, step):
        for file_path in self.file_paths:
            if not file_path.endswith('.csv'):
                video = MainVideoClipping(file_path)
                video.split_into_subclips(step, path=self.subfolder_path)
                os.remove(file_path)
        # Require to update list of files
        self.filenames, self.file_paths = self.ls_videos()

    def ls_videos(self):
        filenames = []
        file_paths = []
        for (_, _, filename) in walk(self.subfolder_path):
            filenames.extend(filename)
        for file in filenames:
            file_path = f'{self.subfolder_path}/{file}'
            file_paths.append(file_path)

        return filenames, file_paths

    def label_videos(self):
        for file_path in self.file_paths:
            if not file_path.endswith('.csv'):
                clip = InspectClip(file_path)
                clip.visualize()
                break


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
