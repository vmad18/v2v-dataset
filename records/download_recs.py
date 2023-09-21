import os
import subprocess
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--num", type=int, default=0, help="downloads num videos")

url = "http://us.data.yt8m.org/2/video/train/"

file_loc = "records/names.txt"

file_names = []

def main() -> None:
    args = parser.parse_args()
    
    file = open(file_loc, 'r')
    
    lines = file.readlines()
    
    for line in lines: file_names.append(line.strip())

    for f in file_names[:args.num]:
        print(f"Downloading {f}...")

        cmd = f"wget {url+f} -P records/"
        subprocess.run(cmd.split()) 

if __name__ == "__main__":
    main()