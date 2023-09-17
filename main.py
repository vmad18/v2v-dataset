import os

import argparse
import numpy as np
from utils.tfrecord import ProcessRecords
from video_handler import VideoHandle
from time import sleep

parser = argparse.ArgumentParser()

parser.add_argument("--video", help="t/true/1 saves YT urls in TF-records to file")
parser.add_argument("--content", help="t/true/1 saves all TF-record contents to file")
parser.add_argument("--num", type=int, default=1, help="specify the number of videos to process")
parser.add_argument("--read_file", default=0, help="t/true/1 read from saved video file or load them")

accepts = ('1', 't', "true")


def process_videos(args) -> None:
    base_yt = "https://www.youtube.com/watch?v="

    process = ProcessRecords("records/", "video_records.txt")
    process.process()

    videos = open('video_records.txt', 'r')
    video_lines = np.array(videos.readlines())

    gen = np.random.default_rng(np.random.randint(100, 2000))
    splices = gen.integers(low=0, high=len(video_lines), size=args.num)

    print(f"Reading videos:\n {video_lines[splices]}")

    for video in video_lines[splices]:
        yt_id, rec_id, label_id = video.split()
        yt_id = yt_id.replace('\"', "")

        try:
            vh = VideoHandle(url=(base_yt + yt_id).strip('\"'), video_id=yt_id, record_id=rec_id, labels=label_id,
                             annot_path="annotation.json")
            vh.run()
        except Exception as e:
            print(e)
            sleep(10)


def main(records_path: str = "records/", to_file: str = "video_records.txt") -> None:
    args = parser.parse_args()

    process = ProcessRecords(records_path, to_file)

    if args.video in accepts:
        print("Parsing video urls")
        print()
        print()
        if not (args.read_file in accepts):
            process.save_videos()
        print("Parsing videos...")
        process_videos(args)

    if args.content in accepts:
        process.save_contents_to_file("contents.txt")


if __name__ == "__main__":
    main()

    # arr = np.arange(0, 2000)

    # rng = np.random.default_rng(np.random.randint(100, 2000))
    # rints = rng.integers(low=0, high=len(arr), size=100)

    # print(arr[rints])

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
