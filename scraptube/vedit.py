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


CTRL = {
    'back': 'H',
    'fwd': 'L',
    'jump_back': 'J',
    'jump_fwd': 'K',
    'jump_step': 50,
    'close': 'Q',
    'pause_play': 'space'
}

LABELS = {
    'general': 'E',
    'relabel': 'R',
    'label': 'A',
    'reset': 'C'
}


class LabelApp:

    def __init__(self, window, window_title, video_source=0):
        self.window = window
        self.main_label = window_title
        self.window.title(self.main_label)
        self.video_source = video_source
        self.video_dest = self.video_source.replace('output', 'clean', 1)
        self.video_query = re.search(
            './output/(.*?)/(.*?)', self.video_source).group(1)
        self.cap = VideoCapture(self.video_source)
        self.pause_flag = True
        self.label_flag = False
        self.relabel_flag = False
        self.gen_label_flag = False
        self.label_dict = {'video': self.video_source,
                           'exercise': [],
                           'start': [],
                           'end': []}

        # Create a canvas that can fit the above video source size
        self.canvas = tkinter.Canvas(
            window, width=self.cap.width, height=self.cap.height)
        self.window.bind('<KeyPress>', self.on_key_press)

        self.canvas.pack()
        # Buttons to select

        self.btn_jmp_fwd = tkinter.Button(window,
                                          text=f"{CTRL['jump_step']} Forward ({CTRL['jump_fwd']})",
                                          width=10,
                                          command=self.video_forward(CTRL['jump_step']))
        self.btn_jmp_fwd.pack(side=tkinter.RIGHT,
                              anchor=tkinter.N, expand=True)

        self.btn_jmp_back = tkinter.Button(window,
                                           text=f"{CTRL['jump_step']} Back ({CTRL['jump_back']})",
                                           width=10,
                                           command=self.video_backward(CTRL['jump_step']))
        self.btn_jmp_back.pack(
            side=tkinter.LEFT, anchor=tkinter.SW, expand=True)

        self.btn_fwd = tkinter.Button(window, text=f"1 Forward ({CTRL['fwd']})",
                                      width=10,
                                      command=self.video_forward(1))
        self.btn_fwd.pack(side=tkinter.RIGHT, anchor=tkinter.SE, expand=True)

        self.btn_back = tkinter.Button(window,
                                       text=f"1 Back ({CTRL['back']})",
                                       width=10,
                                       command=self.video_backward(1))
        self.btn_back.pack(side=tkinter.LEFT, anchor=tkinter.SW, expand=True)

        self.btn_pause_play = tkinter.Button(window,
                                             text=f"Pause/Play ({CTRL['pause_play']})",
                                             width=15,
                                             command=self.video_pause())
        self.btn_pause_play.pack(
            side=tkinter.RIGHT, anchor=tkinter.CENTER, expand=True)

        self.entry_label = tkinter.Entry(window)
        self.canvas.create_window(320, 12,  window=self.entry_label)

        # After it is called once, the update method will be automatically called every delay milliseconds
        self.delay = 15
        self.update_video()
        print("reachead maind loop")
        self.window.mainloop()

    def on_key_press(self, event):
        if event.keysym == CTRL['fwd']:
            self.video_forward(1)
        elif event.keysym == CTRL['back']:
            self.video_backward(1)
        elif event.keysym == CTRL['jump_fwd']:
            self.video_forward(CTRL['jump_step'])
        elif event.keysym == CTRL['jump_back']:
            self.video_backward(CTRL['jump_step'])
        elif event.keysym == 'F':
            self.cap.get_frame_num()
        elif event.keysym == CTRL['pause_play']:
            self.video_pause()
        elif event.keysym == CTRL['close']:
            self.close()
        elif event.keysym == LABELS['label']:
            self.place_label()
        elif event.keysym == LABELS['relabel']:
            self.relabel_clip()
        elif event.keysym == LABELS['general']:
            self.general_label()

    def close(self):
        print(self.label_dict)
        self.window.destroy()

    def general_label(self):
        frame = self.cap.get_frame_num()
        label = 'general'

        if not self.gen_label_flag:
            # Create dictionary with end frames marked as the end
            self.label_dict['exercise'].append(label)
            self.label_dict['start'].append(frame)
            print(f"Starting labeling as {label} at frame {frame}.")
            self.gen_label_flag = True
        elif self.gen_label_flag:
            # Overwrites end with new frame number
            self.label_dict['end'].append(frame)
            print(f"Ended labeling as {label} at frame {frame}.")
            self.gen_label_flag = False

    def place_label(self):
        frame = self.cap.get_frame_num()
        label = self.main_label

        if not self.label_flag:
            # Create dictionary with end frames marked as the end
            self.label_dict['exercise'].append(label)
            self.label_dict['start'].append(frame)
            print(f"Starting labeling as {label} at frame {frame}.")
            self.label_flag = True
        elif self.label_flag:
            # Overwrites end with new frame number
            self.label_dict['end'].append(frame)
            print(f"Ended labeling as {label} at frame {frame}.")
            self.label_flag = False

    def relabel_clip(self):
        frame = self.cap.get_frame_num()
        label = self.entry_label.get()

        if label == '':
            print("No new label entered in field.")
        else:
            if not self.relabel_flag:
                self.label_dict['exercise'].append(label)
                self.label_dict['start'].append(frame)
                print(f"Starting labeling as {label} at frame {frame}.")
                self.relabel_flag = True
            elif self.relabel_flag:
                self.label_dict['end'].append(frame)
                print(f"Ended labeling as {label} at frame {frame}.")
                self.relabel_flag = False

    def update_video(self):
        # Get a frame from the video source
        self.update_frame()

        if self.pause_flag:
            self.window.after(self.delay, self.update_video)

    def update_frame(self):
        ret, frame = self.cap.get_frame()
        if ret:
            self.photo = PIL.ImageTk.PhotoImage(
                image=PIL.Image.fromarray(frame))
            self.canvas.create_image(0, 0, image=self.photo, anchor=tkinter.NW)

    def video_pause(self):
        if self.pause_flag:
            self.pause_flag = False
        else:
            self.pause_flag = True
            self.window.after(self.delay, self.update_video)

    def video_forward(self, step):
        self.cap.forward(step - 1)
        self.update_frame()

    def video_backward(self, step):
        self.cap.backward(step + 1)
        self.update_frame()


class VideoCapture():

    def __init__(self, video_source=0):
        # Open the video source
        self.vid = cv2.VideoCapture(video_source)
        if not self.vid.isOpened():
            raise ValueError("Unable to open video source", video_source)

        # Get video source width and height
        self.width = self.vid.get(cv2.CAP_PROP_FRAME_WIDTH)
        self.height = self.vid.get(cv2.CAP_PROP_FRAME_HEIGHT)
        self.total_frames = int(self.vid.get(cv2.CAP_PROP_FRAME_COUNT))

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

    def get_frame_num(self):
        if self.vid.isOpened():
            frame_num = int(self.vid.get(cv2.CAP_PROP_POS_FRAMES))
            return frame_num
        else:
            return None

    def backward(self, num_frames):
        if self.vid.isOpened():
            frame_current = self.get_frame_num()
            if frame_current:
                frame_new = frame_current - num_frames
                self.vid.set(cv2.CAP_PROP_POS_FRAMES, frame_new)

    def forward(self, num_frames):
        if self.vid.isOpened():
            frame_current = self.get_frame_num()
            if frame_current:
                frame_new = frame_current + num_frames
                self.vid.set(cv2.CAP_PROP_POS_FRAMES, frame_new)

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
