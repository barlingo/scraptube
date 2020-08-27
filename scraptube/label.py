
"""
vedit module
"""
import os
import logging
import tkinter
from tkinter import ttk
import datetime
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
    'label': 'A',
    'delete': 'D'
}

with open('labels.txt') as file:
    file_content = file.readlines()
LABELS = [x.strip() for x in file_content]

logger.debug(f"Detected labels: {LABELS}")


class LabelApp:
    bar_width = 310

    def __init__(self, app, app_title, video_source=0, dict_value=None):
        self.app = app
        self.app_title = app_title
        self.app.title(self.app_title)
        self.video_source = video_source
        self.video_dest = self.video_source.replace('output', 'clean', 1)
        self.video_query = re.search(
            './output/(.*?)/(.*?)', self.video_source).group(1)
        self.cap = VideoCapture(self.video_source)
        logger.info(f"{self.cap.yt_id} | Started App.")
        self.flag_label_map = {key: False for key in LABELS}
        self.pause_flag = True
        if dict_value:
            self.label_video_map = dict_value
        else:
            self.label_video_map = {'video': self.video_source,
                                    'exercise': [],
                                    'start': [],
                                    'end': []}

        self.app.bind('<KeyPress>', self.on_key_press)
        self.__create_items()
        self.__pack_items()

        # After it is called once, the update method
        #  will be automatically called every delay milliseconds
        self.delay = 15
        self.update_video()
        self.update_table()
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
        elif event.keysym == KEY_FUNC_MAP['delete']:
            self.delete_label()

    def close_save(self, save_flag):
        if save_flag:
            self.save_json()
            logger.debug(f"{self.cap.yt_id} | Saved json file.")
        self.app.destroy()
        logger.debug(f"{self.cap.yt_id} | Closed file.")

    def place_label(self):
        frame = self.cap.get_frame_num()
        label = self.label.get()

        if not self.flag_label_map[label]:
            # Create dictionary with end frames marked as the end
            self.label_video_map['exercise'].append(label)
            self.label_video_map['start'].append(frame)
            logger.info(
                f"{self.cap.yt_id} | Start label: {label} at frame {frame}.")
            self.flag_label_map[label] = True
        elif self.flag_label_map[label]:
            # Overwrites end with new frame number
            self.label_video_map['end'].append(frame)
            logger.info(
                f"{self.cap.yt_id} | End label: {label} at frame {frame}.")
            self.flag_label_map[label] = False
            index = len(self.label_video_map['exercise']) - 1
            label = self.label_video_map['exercise'][index]
            start = self.label_video_map['start'][index]
        self.update_label_text()
        self.update_table()

    def delete_label(self):
        frame = self.cap.get_frame_num()

        if frame in self.label_video_map['start']:
            index = self.label_video_map['start'].index(frame)
            label = self.label_video_map['exercise'][index]
            try:
                end = self.label_video_map['end'][index]
            except:
                end = None
            self.del_entry_from_map(index)
            text = f'Deleted entry for: {label}, from frame {frame} to {end}'
            self.flag_label_map[label] = False
        elif frame in self.label_video_map['end']:
            index = self.label_video_map['end'].index(frame)
            label = self.label_video_map['exercise'][index]
            start = self.label_video_map['start'][index]
            self.del_entry_from_map(index)
            text = f'Deleted entry for: {label}, from frame {start} to {frame}'
            self.flag_label_map[label] = False
        else:
            text = "No label found to be deleted."

        self.label_text.set(text)
        self.update_table()

    def del_entry_from_map(self, index):
        del self.label_video_map['exercise'][index]
        del self.label_video_map['start'][index]
        try:
            del self.label_video_map['end'][index]
        except:
            pass
        self.tree.delete(index)

    def update_all(self):
        self.update_headline()
        self.update_frame()
        self.update_label_text()

    def update_video(self):
        # Get a frame from the video source
        self.update_all()

        if self.pause_flag:
            self.app.after(self.delay, self.update_video)

    def update_frame(self):
        ret, frame = self.cap.get_frame()
        if ret:
            self.photo = ImageTk.PhotoImage(
                image=Image.fromarray(frame))
            self.canvas.create_image(0, 0, image=self.photo, anchor=tkinter.NW)

    def update_headline(self):
        frame = self.cap.get_frame_num() + 1
        time = self.cap.get_time()
        update_str = (f'ID: {self.cap.yt_id}    '
                      f'Frame: {frame}/{self.cap.t_frames}   '
                      f'Time: {time}/{self.cap.t_time_str}   ')
        self.head_text.set(update_str)

    def update_table(self):
        for pos, _ in enumerate(self.label_video_map['exercise']):
            try:
                label = self.label_video_map['exercise'][pos]
                start = self.label_video_map['start'][pos]
            except IndexError:
                pass
            try:
                end = self.label_video_map['end'][pos]
                self.tree.delete(pos)
            except IndexError:
                end = ''
            except tkinter.TclError:
                pass
            values = (label, start, end)
            self.tree.insert("", pos, iid=pos, values=values)

    def update_label_text(self):
        frame = self.cap.get_frame_num()

        if frame in self.label_video_map['start']:
            index = self.label_video_map['start'].index(frame)
            exercise = self.label_video_map['exercise'][index]
            text = f'Start label: {exercise}'
        elif frame in self.label_video_map['end']:
            index = self.label_video_map['end'].index(frame)
            exercise = self.label_video_map['exercise'][index]
            text = f'End label: {exercise}'
        else:
            text = ""
        self.label_text.set(text)

    def video_pause(self):
        if self.pause_flag:
            self.pause_flag = False
        else:
            self.pause_flag = True
            self.app.after(self.delay, self.update_video)

    def video_forward(self, step):
        self.cap.forward(step - 1)
        self.update_all()

    def video_backward(self, step):
        self.cap.backward(step + 1)
        self.update_all()

    def save_json(self):
        filename = os.path.splitext(self.video_source)[0] + '.json'
        with open(filename, 'w') as file:
            json.dump(self.label_video_map, file, indent=4)

    def __create_items(self):
        self.canvas = tkinter.Canvas(self.app, width=self.cap.width,
                                     height=self.cap.height)

        self.columns = ('Label', 'Start', 'End')
        self.tree = ttk.Treeview(
            self.app, columns=self.columns, show='headings')
        for header in self.columns:
            self.tree.heading(header, text=header)
        # Buttons to select
        self.label_text = tkinter.StringVar()
        self.head_text = tkinter.StringVar()
        self.headline = tkinter.Label(self.app, textvariable=self.head_text,
                                      font=("Helvetica", 12))
        self.labeline = tkinter.Label(self.app, textvariable=self.label_text,
                                      font=("Helvetica Bold", 12))
        b_text = f"Skip video ({KEY_FUNC_MAP['skip']})"
        self.btn_skip = tkinter.Button(self.app,
                                       text=b_text,
                                       width=30,
                                       command=lambda: self.close_save(False))

        b_text = f"Close video and save labels ({KEY_FUNC_MAP['close_save']})"
        self.btn_quit = tkinter.Button(self.app,
                                       text=b_text,
                                       width=30,
                                       command=lambda: self.close_save(True))

        b_text = f"Place Label ({KEY_FUNC_MAP['label']})"
        self.btn_label = tkinter.Button(self.app,
                                        text=b_text,
                                        width=30,
                                        command=self.place_label)

        b_text = f"Delete Label ({KEY_FUNC_MAP['delete']})"
        self.btn_delete = tkinter.Button(self.app,
                                         text=b_text,
                                         width=30,
                                         command=self.delete_label)

        self.label = tkinter.StringVar(self.app)
        self.label.set(LABELS[0])

        self.opt = tkinter.OptionMenu(self.app, self.label, *LABELS)
        self.opt.config(width=30, font=('Helvetica', 12))

        b_text = f"{KEY_FUNC_MAP['jump_step']} Forward ({KEY_FUNC_MAP['jump_fwd']})"
        self.btn_jmp_fwd = tkinter.Button(self.app,
                                          text=b_text,
                                          width=10,
                                          command=lambda: self.video_forward(KEY_FUNC_MAP['jump_step']))

        b_text = f"1 Forward ({KEY_FUNC_MAP['fwd']})"
        self.btn_fwd = tkinter.Button(self.app,
                                      text=b_text,
                                      width=10,
                                      command=lambda: self.video_forward(1))

        b_text = f"Pause/Play ({KEY_FUNC_MAP['pause_play']})"
        self.btn_pause_play = tkinter.Button(self.app,
                                             text=b_text,
                                             width=15,
                                             command=self.video_pause)

        b_text = f"{KEY_FUNC_MAP['jump_step']} Back ({KEY_FUNC_MAP['jump_back']})"
        self.btn_jmp_back = tkinter.Button(self.app,
                                           text=b_text,
                                           width=10,
                                           command=lambda: self.video_backward(KEY_FUNC_MAP['jump_step']))

        b_text = f"1 Back ({KEY_FUNC_MAP['back']})"
        self.btn_back = tkinter.Button(self.app,
                                       text=b_text,
                                       width=10,
                                       command=lambda: self.video_backward(1))

    def __pack_items(self):
        self.labeline.pack(side=tkinter.TOP, anchor=tkinter.CENTER)
        self.headline.pack(side=tkinter.TOP, anchor=tkinter.CENTER)
        self.update_headline()
        self.btn_skip.pack(
            side=tkinter.TOP, anchor=tkinter.CENTER, expand=True)
        self.btn_quit.pack(
            side=tkinter.TOP, anchor=tkinter.CENTER, expand=True)
        self.btn_label.pack(
            side=tkinter.TOP, anchor=tkinter.CENTER, expand=True)
        self.btn_delete.pack(
            side=tkinter.TOP, anchor=tkinter.CENTER, expand=True)
        self.opt.pack(side=tkinter.TOP, anchor=tkinter.CENTER, expand=True)
        self.tree.pack(side=tkinter.BOTTOM)
        self.canvas.pack()
        self.btn_jmp_fwd.pack(side=tkinter.RIGHT,
                              anchor=tkinter.N, expand=True)
        self.btn_fwd.pack(side=tkinter.RIGHT, anchor=tkinter.SE, expand=True)
        self.btn_pause_play.pack(
            side=tkinter.RIGHT, anchor=tkinter.CENTER, expand=True)
        self.btn_jmp_back.pack(
            side=tkinter.LEFT, anchor=tkinter.SW, expand=True)
        self.btn_back.pack(side=tkinter.LEFT, anchor=tkinter.SW, expand=True)


class VideoCapture():

    def __init__(self, video_source=0):
        # Open the video source
        self.vid = cv2.VideoCapture(video_source)
        if not self.vid.isOpened():
            raise ValueError("Unable to open video source", video_source)

        # Get video source width and height
        self.width = self.vid.get(cv2.CAP_PROP_FRAME_WIDTH)
        self.height = self.vid.get(cv2.CAP_PROP_FRAME_HEIGHT)
        self.fps = int(self.vid.get(cv2.CAP_PROP_FPS))
        self.t_frames = int(self.vid.get(cv2.CAP_PROP_FRAME_COUNT))
        self.t_secs = int(self.t_frames / self.fps)
        self.t_time_str = str(datetime.timedelta(seconds=self.t_secs))
        self.yt_id = os.path.basename(video_source).split(".mp4")[
            0].split("_")[1]

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

    def get_time(self):
        if self.vid.isOpened():
            frame = int(self.vid.get(cv2.CAP_PROP_POS_FRAMES))
            secs = int(frame / self.fps)
            time_str = str(datetime.timedelta(seconds=secs))
            return time_str
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
        logger.debug(f"Procesing folder {subfolder_path}")
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
        file_infos = []

        for main_dir, sub_dir, filenames in os.walk(self.subfolder_path):
            for filename in filenames:
                file_path = f'{self.subfolder_path}/{filename}'
                size = os.path.getsize(file_path)
                file_infos.append([size, filename, file_path])

        # filenames = [path.replace(del_str, '') for path in file_paths]
        file_infos.sort(key=lambda s: s[0])
        filenames = [row[1] for row in file_infos]
        file_paths = [row[2] for row in file_infos]

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
