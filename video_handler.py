import os
from pytube import YouTube
import subprocess
import re


class VideoHandle:

    def __init__(self, url: str, mode: str = "exp", video_path: str = "videos/", max_res: int = None) -> None:
       
        self.url = url
        self.video_path = video_path

        self.end_time: float = None
        
    
    def download_video(self) -> None:
        # do we want highest resolution of video?
        # how do we want to select the key frames?
        yt = YouTube(self.url)
        yt = yt.streams.filter(res="720p").first().download(self.video_path)
        
        os.rename(yt, f"{self.video_path}video.mp4")

    def _get_attr(self, name, v)-> any:
        
        idx = v.index(f"{name}=")
        
        v = v[idx:]
        v = v.split()

        val = v[0].split("=")[1]
        return val
    
    def parse_frame(self, frame: int) -> None: 
        pass

    def get_frames(self) -> None:
        cmd = f'ffprobe -select_streams v -show_frames {self.video_path}video.mp4'.split()
        out = subprocess.check_output(cmd).decode("utf-8")
        
        res = out.replace("\n"," ").split("[FRAME]")[1:][3]

        print(res)
        print(self._get_attr("pts", res))


if __name__ == "__main__":
    vh = VideoHandle(url = "https://www.youtube.com/watch?v=jTYmyM--T68")
    
    # vh.download_video()
    vh.get_frames()
