import os
from pytube import YouTube
import subprocess
from math import floor, ceil
from typing import Dict, Tuple, List
from threading import Thread
import cv2 as cv
from PIL import Image
import json

from utils.image_sim import percept_score, wlet_score

class Frame:
    
    def __init__(self, key_frame: bool, time_stamp: float, frame_id: int) -> None:
        self.key_frame = key_frame
        self.time_stamp = time_stamp
        self.frame_num = frame_id
    
    
    def __str__(self) -> str:
        return f"Key Frame: {self.key_frame}  Time Stamp: {self.time_stamp}  Frame Number: {self.frame_num}"


class FrameChain:

    def __init__(self, *args):
                # print(base)
        # base = base.split()
        # subprocess.check_output(base)
        self.frames: List[Frame] = [f for f in args]
        self.anchor = self.frames[0]

        self.offsets = [abs(self.frames[i].time_stamp - self.anchor.time_stamp) for i in range(1, len(self.frames))]

        self.frame_paths: List[str] = None

    def add_file_names(self, file_names: List[str]) -> None:
        self.frame_paths = file_names

    def __iter__(self):
        return iter(self.frames)
    
    def __len__(self):
        return len(self.frames)


#  make code support parallization to make it quicker
#  download videos off of labels
class VideoHandle:

    def __init__(self, 
                 url: str, 
                 video_id: str = None,
                 mode: str = "exp", 
                 video_path: str = "videos/", 
                 save_path: str = "video",
                 annot_path: str = "blank.json",
                 record_id: str = None,
                 labels: str = "",
                 max_res: int = None) -> None:

        self.url = url
        self.video_id = video_id if video_id != None else url.split("=")[-1]
        self.video_path = video_path
        
        self.dur_sec: float = None

        self.end_time: float = None
        
        self.frame_map: Dict[int, Frame] = {}
        
        self.step_size: float = .1

        self.func = lambda t: .2 * 2 ** t # 0. if t == 0 else .2 * 2 ** t 

        self.save_path = save_path if save_path[-1] == "/" else save_path + '/'

        self.annot_path: str = annot_path
        self.contents = None
        with open(annot_path, 'r') as f:
             self.contents = json.load(f)

        self.rec_id = record_id
        self.labels = labels
        

        self.save_path = save_path + video_id + "/"

        os.mkdir(f"{video_path}{save_path}{video_id}/")


    def download_video(self) -> None:
        # do we want highest resolution of video?
        # how do we want to select the key frames?
        yt = YouTube(self.url)
        yt = yt.streams.get_highest_resolution().download(self.video_path)
        
        os.rename(yt, f"{self.video_path}video.mp4")


    def _get_attr(self, name, v)-> Tuple[bool, str]:
        
        idx = v.index(f"{name}=")
        
        v = v[idx:]
        v = v.split()

        val = v[0].split("=")[1]
        return idx!=-1, val
   

    '''
    Converts desired time stamp to frame
    '''
    def sec_to_frame(self, sec: float) -> Frame:
        return self.frame_map[floor(sec/self.dur_sec)]


    '''
    Parses frame string metadata.
    '''
    def parse_frame(self, frame: str) -> Frame: 
       
        is_kf = bool(int(self._get_attr("key_frame", frame)[1]))
        frame_id = int(self._get_attr("pts", frame)[1])/1001
        time_stamp = float(self._get_attr("timestamp_time", frame)[1])

        return Frame(is_kf, time_stamp, int(frame_id))
    

    '''
    Anchor frame are key frames. Selects anchor frame near a time stamp. 
    '''
    def get_anchor(self, sec: float, dir: str = "right", threshold: float = float('inf')) -> Frame:
        
        _dir: float = 1. if dir == "right" else -1.
        
        curr_sec = sec
        curr_frame = self.sec_to_frame(curr_sec)
        
        while not curr_frame.key_frame:
            curr_sec = curr_sec + _dir * self.dur_sec

            if curr_sec < 0 or curr_sec > self.end_time or abs(curr_sec - sec) > threshold:
                raise Exception("No key frame found around time")

            curr_frame = self.sec_to_frame(curr_sec)

        return curr_frame
    
    
    # do we want to get > than 4 anchors (ex. for big videos)
    # do we care abt over lapping frames (idt it matters so much, but if we want to check for it)

    '''
    Here we select n anchor frames at specific portions of the video.
    '''
    def get_mult_anchors(self, anchors = 4, threshold: float = float('inf')) -> List[Frame]:
        

        if self.end_time / 12 < 3:  # 3 represents the length of video after key frame
            raise Exception("Overlapping key frames neighbors")

        seconds = []
        
        mults = (1/12, 5/12, 7/12, 11/12)  # would like to change how this is implemented

        for m in mults:
            seconds.append(m * self.end_time)
        
        anchor_frames = []
        dir = "right"

        for a in range(anchors):
            if a % 2 == 0: dir = "right"
            else: dir = "left"

            frame = self.get_anchor(seconds[a], dir, threshold)
            
            if a > 0: # checks for overlapping frames
                if False and frame.time_stamp - anchor_frames[-1].time_stamp < 3:
                    raise Exception("Overlapping key frames neighbors")

            anchor_frames.append(frame)
    
        return anchor_frames


    '''
    Gets n frames after a specific frame
    '''
    def get_frames_after(self, frame: Frame, cnt: int = 5, dir: str = "right", throw_excep: bool = True) -> List[Frame]:
        
        _dir: float = 1. if dir == "right" else -1.

        frames: List[Frame] = []

        curr_sec = frame.time_stamp

        for t in range(cnt):
            curr_sec = curr_sec + _dir * self.func(t)

            if curr_sec < 0 or curr_sec > self.end_time:
                if throw_excep: raise Exception(f"Can't get {cnt} frames after desired frame")
                else: return frames
            
            frame = self.sec_to_frame(curr_sec)
            frames.append(frame)
        
        return frames
    

    '''
    Gets n frames after a set of anchor frames
    '''
    def gen_frames(self, cnt: int = 5, throw_excep: bool = True) -> List[FrameChain]:
        dir: str = None  # direction to choose frames from

        generated: List[FrameChain] = []  # store key frame + generated frame in list
        anchors = self.get_mult_anchors()  # generate anchor frames
        
        for idx, frame in enumerate(anchors):
            if idx % 2 == 0: dir = "right"
            else: dir = "left"

            frames = self.get_frames_after(frame, cnt, dir = dir, throw_excep = throw_excep)
            frames.insert(0, frame)

            chain = FrameChain(*frames)
            generated.append(chain)

        return generated


    '''
    Saves all anchor frame chains at once as file
    '''
    def save_frames_at_once(self, frames: List[FrameChain]) -> None:

        seq = ""

        for idx, chain in enumerate(frames):
            for idx2, frame in enumerate(chain):
                if idx != len(frames)-1 or idx2 != len(chain) - 1: seq += f"eq(n\,{frame.frame_num})+"
                else: seq += f"eq(n\,{frame.frame_num})"

        base = f"/home/vivan/ffmpeg/ffmpeg -i {self.video_path}video.mp4 -vf select={seq} -vsync 0 {self.video_path}{self.save_path}frame_%d.png".split()
        subprocess.check_output(base)


    '''
    Runs bash cmd
    '''
    def run_cmd(self, cmd: str):
        subprocess.check_output(cmd.split())
        print("done")


    '''
    Saves video anchor frame chains (with custom names) as file
    '''
    def save_frames(self, frames: List[FrameChain]) -> None:

        runners = []

        data = {}

        t_idx = 0

        for anchor, chain in enumerate(frames):

            data[f"anchor{anchor}"] = chain.anchor.time_stamp
            file_paths = []
            for idx2, frame in enumerate(chain):
                offset = 0
                if idx2 != 0:
                    offset = chain.offsets[idx2-1]
                
                file_name = f"{self.video_path}{self.save_path}frame_{t_idx}_{str(offset)[:3]}_{anchor}.png"
                file_paths.append(file_name)
                base = f"/home/vivan/ffmpeg/ffmpeg -i {self.video_path}video.mp4 -vf select=eq(n\,{frame.frame_num}) -vsync 0 {file_name}"

                t = Thread(target=self.run_cmd, args=(base,))
                runners.append(t)

                t_idx += 1
            
            chain.add_file_names(file_paths)

        for runner in runners:
            runner.start()
        
        for runner in runners:
            runner.join()


        for anchor, chain in enumerate(frames):
            total_score: float = 0.
            for idx, frame_path in enumerate(chain.frame_paths):
                if idx == 0: continue
                anch = Image.open(chain.frame_paths)
                img = Image.open(frame_path)

                total_score += wlet_score(anch, img)

            total_score /= len(chain.frame_paths)-1

            data[f"anchor{anchor}_wscore"] = total_score 


        if self.rec_id != None:
            data["record_id"] = self.rec_id 

        data["length"] = self.end_time
        data["frame_rate"] = floor(1./self.dur_sec)

        if self.labels != None:
            data["record_id"] = self.labels 

        data["frame_cnt"] = t_idx+1
        data["labels"] = self.labels

        self.contents[self.video_id] = data

        with open(self.annot_path, "w") as f:
            json.dump(self.contents, f, indent=4)


    '''
    Parses frames of video as list
    '''
    def get_frames(self) -> None:
        cmd = f'/home/vivan/ffmpeg/ffprobe -select_streams v -show_frames {self.video_path}video.mp4'.split()
        out = subprocess.check_output(cmd).decode("utf-8")

        res = out.replace("\n"," ").split("[FRAME]")[1:] 

        for idx, frame in enumerate(res):
            durr = self._get_attr("pkt_duration_time", frame)

            if not durr[0]: continue  # not very elegant

            self.dur_sec = float(durr[1])
            
            self.frame_map[idx] = self.parse_frame(frame)
        
        self.end_time = list(self.frame_map.values())[-1].time_stamp
        
        print("Video Statistics")
        print(f"Video Length: {self.end_time}")


    '''
    Process whole video
    '''
    def run(self, verbose: bool = False) -> None:
        self.download_video()
        self.get_frames()

        gen = self.gen_frames()

        self.save_frames(gen)

        if verbose:
            for chain in gen:
                for fr in chain:
                    print(fr)
        
                print()
                print()
                print()


#  store meta data in json file
#  save file as offset from anchor


'''

youtube_video_id:
    tf-record - id
    anchor1 - ts
    anchor2 - ts
    anchor3 - ts
    anchor4 - ts
    labels

'''
if __name__ == "__main__":
    
    # , "https://www.youtube.com/watch?v=KuXjwB4LzSA", "https://www.youtube.com/watch?v=r6sGWTCMz2k"
    
    # urls = ["https://www.youtube.com/watch?v=cy8r7WSuT1I"]

    # for idx, url in enumerate(urls):
    #     id = url.split("=")[-1]
    #     vh = VideoHandle(url = url, save_path=f"video{id}")
    #     vh.run(verbose=True)






    url = "https://www.youtube.com/watch?v=cy8r7WSuT1I"
    id = url.split("=")[-1]
    vh = VideoHandle(url = url, save_path=f"video_{id}", video_id=id, annot_path="annotation.json")


    # # vh.download_video()
    vh.get_frames()
    vh.get_mult_anchors()
    
    # # print(vh.get_anchor(174, "left"))
    # # vh.get_mult_anchors()
    # # # for f in vh.get_mult_anchors():
    # # #     print(f)


    gen = vh.gen_frames()

    for frame_lis in gen:
        for fr in frame_lis:
            print(fr)
        
        print()
        print()
        print()

    vh.save_frames(gen)

'''
        # print(self._get_attr("key_frame", frame), self._get_attr("pts", frame), self._get_attr("timestamp_time", frame), self._get_attr("pkt_duration_time", frame))
        #
        # print(res[0])
        # print(self._get_attr("pts", res))
        # print(self._get_attr("key_frame", res))


'''

'''
floor(second/frame_int) 

100/.033367 = = 2996.97306

2996 * 1001= 2998996

start + .2 * 2^(n) if n == 0 then start

start + .2 * (1.1)^n

start + .1 * 2^(n) 

start + .2 * n^2 


time
if time != kf:
    move up a frame
    F
'''
