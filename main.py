import os

import argparse
from utils.tfrecord import ProcessRecords

parser = argparse.ArgumentParser()

parser.add_argument("--video", help="t/true/1 saves YT urls in TF-records to file")
parser.add_argument("--content", help="t/true/1 saves all TF-record contents to file")

accepts = ('1', 't', "true")

def main(records_path: str = "records/", to_file: str = "video_records.txt") -> None:
    
    args = parser.parse_args()

    process = ProcessRecords(records_path, to_file)
    
    if args.video in accepts:
        process.save_videos()

    if args.content in accepts:
        process.save_contents_to_file("contents.txt")

if __name__ == "__main__":
    main()


'''
import os
from utils.tfrecord import ProcessRecords
from video_handler import VideoHandle


def main() -> None:
    
    base_yt = "https://www.youtube.com/watch?v="

    process = ProcessRecords("records/", "video_records.txt")
    process.process()

    videos = open('myfile.txt', 'r')
    video_lines = videos.readlines()

    for video in video_lines:
        yt_id, rec_id = video.split()
        
        vh = VideoHandle(base_yt=yt_id, yt_id=yt_id, record_id=rec_id, annot_path="annotation.json")
        vh.run()

        break


if __name__ == "__main__":
    main()
'''