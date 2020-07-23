
"""
vedit module
"""
import os
import logging
import tkinter
from os import walk
import json
import re
import cv2
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip

from PIL import Image
from PIL import ImageTk


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter(
    '%(asctime)s | %(name)s | %(levelname)s | %(message)s')

file_handler = logging.FileHandler(__name__ + ".log")
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)

stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.INFO)
stream_handler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.addHandler(stream_handler)

KEY_FUNC_MAP = {
    'back': 'H',
    'fwd': 'L',
    'jump_back': 'J',
    'jump_fwd': 'K',
    'jump_step': 50,
    'close_save': 'Q',
    'skip': 'S',
    'pause_play': 'space',
    'label': 'A'
}

with open('labels.txt') as file:
    file_content = file.readlines()
LABELS = [x.strip() for x in file_content]

logger.debug(f"Detected labels: {LABELS}")


class LabelApp:

    def __init__(self, app, app_title, video_source=0):
        self.app = app
        self.app_title = app_title
        self.app.title(self.app_title)
        self.video_source = video_source
        self.video_dest = self.video_source.replace('output', 'clean', 1)
        self.video_query = re.search(
            './output/(.*?)/(.*?)', self.video_source).group(1)
        self.cap = VideoCapture(self.video_source)
        self.flag_label_map = {key: False for key in LABELS}
        self.pause_flag = True
        self.label_video_map = {'video': self.video_source,
                                'exercise': [],
                                'start': [],
                                'end': []}

        # Create a canvas that can fit the above video source size
        self.canvas = tkinter.Canvas(
            app, width=self.cap.width, height=self.cap.height)
        self.app.bind('<KeyPress>', self.on_key_press)

        # Buttons to select

        self.btn_skip = tkinter.Button(app,
                                       text=f"Skip video ({KEY_FUNC_MAP['skip']})",
                                       width=30,
                                       command=lambda: self.close_save(False))
        self.btn_skip.pack(
            side=tkinter.TOP, anchor=tkinter.CENTER, expand=True)

        self.btn_quit = tkinter.Button(app,
                                       text=f"Close and Save Video ({KEY_FUNC_MAP['close_save']})",
                                       width=30,
                                       command=lambda: self.close_save(True))
        self.btn_quit.pack(
            side=tkinter.TOP, anchor=tkinter.CENTER, expand=True)

        self.btn_label = tkinter.Button(app,
                                        text=f"Place Label ({KEY_FUNC_MAP['label']})",
                                        width=30,
                                        command=self.place_label)
        self.btn_label.pack(
            side=tkinter.TOP, anchor=tkinter.CENTER, expand=True)

        self.label = tkinter.StringVar(self.app)
        self.label.set(LABELS[0])
        self.opt = tkinter.OptionMenu(self.app, self.label, *LABELS)
        self.opt.config(width=30, font=('Helvetica', 12))
        self.opt.pack(side=tkinter.TOP, anchor=tkinter.CENTER, expand=True)
        self.canvas.pack()

        self.btn_jmp_fwd = tkinter.Button(app,
                                          text=f"{KEY_FUNC_MAP['jump_step']} Forward ({KEY_FUNC_MAP['jump_fwd']})",
                                          width=10,
                                          command=lambda: self.video_forward(KEY_FUNC_MAP['jump_step']))
        self.btn_jmp_fwd.pack(side=tkinter.RIGHT,
                              anchor=tkinter.N, expand=True)

        self.btn_fwd = tkinter.Button(app, text=f"1 Forward ({KEY_FUNC_MAP['fwd']})",
                                      width=10,
                                      command=lambda: self.video_forward(1))
        self.btn_fwd.pack(side=tkinter.RIGHT, anchor=tkinter.SE, expand=True)

        self.btn_pause_play = tkinter.Button(app,
                                             text=f"Pause/Play ({KEY_FUNC_MAP['pause_play']})",
                                             width=15,
                                             command=self.video_pause)
        self.btn_pause_play.pack(
            side=tkinter.RIGHT, anchor=tkinter.CENTER, expand=True)

        self.btn_jmp_back = tkinter.Button(app,
                                           text=f"{KEY_FUNC_MAP['jump_step']} Back ({KEY_FUNC_MAP['jump_back']})",
                                           width=10,
                                           command=lambda: self.video_backward(KEY_FUNC_MAP['jump_step']))
        self.btn_jmp_back.pack(
            side=tkinter.LEFT, anchor=tkinter.SW, expand=True)

        self.btn_back = tkinter.Button(app,
                                       text=f"1 Back ({KEY_FUNC_MAP['back']})",
                                       width=10,
                                       command=lambda: self.video_backward(1))
        self.btn_back.pack(side=tkinter.LEFT, anchor=tkinter.SW, expand=True)

        # After it is called once, the update method
        #  will be automatically called every delay milliseconds
        self.delay = 15
        self.update_video()
        self.app.mainloop()

    def on_key_press(self, event):
        if event.keysym == KEY_FUNC_MAP['fwd']:
            self.video_forward(1)
        elif event.keysym == KEY_FUNC_MAP['back']:
            self.video_backward(1)
        elif event.keysym == KEY_FUNC_MAP['jump_fwd']:
            self.video_forward(KEY_FUNC_MAP['jump_step'])
        elif event.keysym == KEY_FUNC_MAP['jump_back']:
            self.video_backward(KEY_FUNC_MAP['jump_step'])
        elif event.keysym == 'F':
            self.cap.get_frame_num()
        elif event.keysym == KEY_FUNC_MAP['pause_play']:
            self.video_pause()
        elif event.keysym == KEY_FUNC_MAP['close_save']:
            self.close_save(True)
        elif event.keysym == KEY_FUNC_MAP['skip']:
            self.close_save(False)
        elif event.keysym == KEY_FUNC_MAP['label']:
            self.place_label()

    def close_save(self, save_flag):
        if save_flag:
            self.save_json()
        self.app.destroy()

    def place_label(self):
        frame = self.cap.get_frame_num()
        label = self.label.get()

        if not self.flag_label_map[label]:
            # Create dictionary with end frames marked as the end
            self.label_video_map['exercise'].append(label)
            self.label_video_map['start'].append(frame)
            print(f"Starting labeling as {label} at frame {frame}.")
            self.flag_label_map[label] = True
        elif self.flag_label_map[label]:
            # Overwrites end with new frame number
            self.label_video_map['end'].append(frame)
            print(f"Ended labeling as {label} at frame {frame}.")
            self.flag_label_map[label] = False

    def update_video(self):
        # Get a frame from the video source
        self.update_frame()

        if self.pause_flag:
            self.app.after(self.delay, self.update_video)

    def update_frame(self):
        ret, frame = self.cap.get_frame()
        if ret:
            self.photo = ImageTk.PhotoImage(
                image=Image.fromarray(frame))
            self.canvas.create_image(0, 0, image=self.photo, anchor=tkinter.NW)

    def video_pause(self):
        if self.pause_flag:
            self.pause_flag = False
        else:
            self.pause_flag = True
            self.app.after(self.delay, self.update_video)

    def video_forward(self, step):
        self.cap.forward(step - 1)
        self.update_frame()

    def video_backward(self, step):
        self.cap.backward(step + 1)
        self.update_frame()

    def save_json(self):
        filename = os.path.splitext(self.video_source)[0] + '.json'
        with open(filename, 'w') as file:
            json.dump(self.label_video_map, file, indent=4)


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
            if not file_path.endswith('.csv') or file_path.endswith('.json'):
                json_file = os.path.splitext(file_path)[0] + '.json'
                if not os.path.isfile(json_file):
                    LabelApp(tkinter.Tk(), self.name, file_path)
                    count += 1
            if count == 5:
                break
