"""
vedit module

"""
import shutil
import os
import tkinter
from os import walk
import cv2
import re
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip
# import moviepy.editor

import PIL.Image
import PIL.ImageTk
import time


class LabelApp:
    def __init__(self, window, window_title, video_source=0):
        self.window = window
        self.window.title(window_title)
        self.video_source = video_source
        self.video_dest = self.video_source.replace('output', 'clean', 1)
        self.video_query = re.search(
            './output/(.*?)/(.*?)', self.video_source).group(1)
        self.vid = VideoCapture(self.video_source)

        # Create a canvas that can fit the above video source size
        self.canvas = tkinter.Canvas(
            window, width=self.vid.width, height=self.vid.height)
        self.window.bind('<KeyPress>', self.on_key_press)
        self.canvas.pack()

        # Buttons to select
        self.btn_keep = tkinter.Button(
            window, text="Keep (K)", width=20, command=self.keep_video)
        self.btn_keep.pack(anchor=tkinter.CENTER, expand=True)

        self.btn_delete = tkinter.Button(
            window, text="Delete (D)", width=20, command=self.delete_video)
        self.btn_delete.pack(anchor=tkinter.CENTER, expand=True)

        self.btn_relabel = tkinter.Button(
            window, text="Relabel (R)", width=20, command=self.relabel_video)
        self.btn_relabel.pack(anchor=tkinter.CENTER, expand=True)

        self.btn_relabel = tkinter.Button(
            window, text="Skip (S)", width=20, command=self.skip)
        self.btn_relabel.pack(anchor=tkinter.CENTER, expand=True)

        self.entry_label = tkinter.Entry(window)
        self.canvas.create_window(320, 12,  window=self.entry_label)

        # After it is called once, the update method will be automatically called every delay milliseconds
        self.delay = 15
        self.update()
        self.window.mainloop()

    def keep_video(self):
        # Move cleaned file to a different destination
        os.makedirs(os.path.dirname(self.video_dest), exist_ok=True)
        shutil.move(self.video_source, self.video_dest)
        self.window.destroy()

    def skip(self):
        self.window.destroy()

    def relabel_video(self):
        label = self.entry_label.get()
        if label == '':
            print("No label entered")
        else:
            print(f'Moving file to {label}')
            self.video_dest = self.video_dest.replace(self.video_query, label)
            os.makedirs(os.path.dirname(self.video_dest), exist_ok=True)
            shutil.move(self.video_source, self.video_dest)
        self.window.destroy()

    def delete_video(self):
        self.window.destroy()
        os.remove(self.video_source)

    def on_key_press(self, event):
        if event.keysym == 'K':
            self.keep_video()
        elif event.keysym == 'D':
            self.delete_video()
        elif event.keysym == 'R':
            self.relabel_video()
        elif event.keysym == 'S':
            self.skip()

    def update(self):
        # Get a frame from the video source
        ret, frame = self.vid.get_frame()

        if ret:
            self.photo = PIL.ImageTk.PhotoImage(
                image=PIL.Image.fromarray(frame))
            self.canvas.create_image(0, 0, image=self.photo, anchor=tkinter.NW)

        self.window.after(self.delay, self.update)


class VideoCapture:
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
        counter = 0
        for start in range(0, int(self.seconds), step):
            end = start + step
            self.extract_clip(counter, start, end, path)
            counter += 1

    def extract_clip(self, counter, start, end, path):
        main_name = os.path.basename(self.video_path)
        name = str(counter) + "_" + os.path.splitext(main_name)[0]
        targetname = path + "/" + name + '.mp4'
        ffmpeg_extract_subclip(self.video_path, start, end, targetname)


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
        count = 0
        for file_path in self.file_paths:
            if not file_path.endswith('.csv'):
                LabelApp(tkinter.Tk(), self.name, file_path)
            if count == 500:
                break
            count += 1


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
