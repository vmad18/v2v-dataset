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

