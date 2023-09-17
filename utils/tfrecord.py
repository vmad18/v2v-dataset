import os

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
from contextlib import nullcontext
import tensorflow as tf
import codecs
import numpy as np
import requests
from time import sleep


class VideoData:

    def __init__(self, id: str, labels: list[str]):
        pass


class ProcessRecords:

    def __init__(self, records: str, video_path: str):
        self.records = records
        self.video_path = video_path

        self.files = []

        self.all_videos_ds = {}

        for file in os.listdir(records):

            if file.split(".")[-1] != "tfrecord": continue

            self.files.append(f"{records}{file}")

        self.process()

    def process(self):

        print(f"Processing {len(self.files)} TF-Record file(s)... \n")
        sleep(3)

        for i, file in enumerate(self.files):
            dataset = tf.data.TFRecordDataset(file)

            all_feats = {}
            for idx, raw_record in enumerate(dataset):

                byt = raw_record.numpy()

                example = tf.train.Example()
                example.ParseFromString(byt)

                features = {}
                for k, v in example.features.feature.items():
                    kind = v.WhichOneof('kind')

                    size = len(getattr(v, kind).value)

                    if k in features:
                        kind2, size2 = features[k]

                        if kind != kind2:
                            kind = None
                        if size != size2:
                            size = None

                    features[k] = (v, size)

                all_feats[idx] = features

            self.all_videos_ds[i] = all_feats

            print(f"Number of videos in record: {file.split('/')[-1]} - {len(all_feats.values())}")

        print(f"Total number of videos: {len(self.all_videos_ds)}")
        print("Finished...")
        sleep(3)
        print("\n")

    def save_contents_to_file(self, file: str) -> None:

        print(f"Saving contents of TF-Records to file: {file}")

        sleep(3)

        f = open(file, 'w+')

        for i, all_feats in enumerate(self.all_videos_ds.values()):
            for idx, video in enumerate(all_feats.values()):
                f.write(f"Video Number {idx} in {self.files[i].split('/')[-1]} \n")
                for feature in video.values():
                    f.write(str(feature))

                for _ in range(10):
                    f.write("\n")
        f.close()

    def save_videos(self) -> None:

        print("Saving YT URL links to file... ")
        sleep(3)

        f = open(self.video_path, 'w+')
        for all_feats in self.all_videos_ds.values():
            for idx, video in enumerate(all_feats.values()):

                vid_id = codecs.decode(video['id'][0].bytes_list.value[0], 'utf-8')
                vid_labels = '-'.join([str(i) for i in video['labels'][0].int64_list.value])

                link = f"https://data.yt8m.org/2/j/i/{vid_id[0:2]}/{vid_id}.js"
                page = requests.get(link, verify=False)

                # print(idx)

                try:
                    yt_url = page.text[2:-2].split(',')[1]
                    f.write(f"{yt_url} {vid_id} {vid_labels}\n")
                except:
                    continue

        f.close()


def main() -> None:
    process = ProcessRecords("records/", "video_records.txt")
    process.process()


if __name__ == "__main__":
    main()

#     
#
# raw_dataset = tf.data.TFRecordDataset("trainpj.tfrecord")
#
# output = ""
#
# all_feats = {}
#
# for idx, raw_record in enumerate(raw_dataset):
#     
#     byt = raw_record.numpy()
#
#     example = tf.train.Example()
#     example.ParseFromString(byt)
#     
#     features = {} 
#     for k, v in example.features.feature.items():
#         kind = v.WhichOneof('kind')
#
#         size = len(getattr(v, kind).value)
#
#         if k in features:
#             kind2, size2 = features[k]
#
#             if kind != kind2:
#                 kind = None
#             if size != size2:
#                 size = None
#
#         features[k] = (v, size)
#
#     all_feats[idx] = features
#
# # with open("inside.txt", "w") as text_file:
# #     text_file.write(output)
# import codecs
#
#
#
# for video in all_feats.values():
#     print(video['id'][0])
#     print(video['labels'][0])
#
#     print("")
#     print("")
#     print("")
#     print("")
#
#
# print(all_feats.__sizeof__())
# print(all_feats)
#
# print(features['id'][0])
# print(
