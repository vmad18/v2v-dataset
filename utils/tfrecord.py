import os
from contextlib import nullcontext
import tensorflow as tf
import codecs
import numpy as np
import requests


class VideoData:

    def __init__(self, id: str, labels: list[str]):
        pass


class ProcessRecords:

    def __init__(self, records: str, video_path: str):
        self.records = records
        self.video_path = video_path

        self.files = [] 

        for file in os.listdir(records):
            self.files.append(f"{records}{file}")

    def process(self):

        f = open(self.video_path, 'w+')
        for file in self.files:
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
            
            print(len(all_feats.values()))

            for idx, video in enumerate(all_feats.values()):
                
                vid_id = codecs.decode(video['id'][0].bytes_list.value[0], 'utf-8')
                
                # labels = codecs.decode(video["labels"][0].bytes_list.value, 'utf-8')
                # print(video["labels"][0])
                # print(type(video["labels"][0]))
                
                link =  f"https://data.yt8m.org/2/j/i/{vid_id[0:2]}/{vid_id}.js"     
                page = requests.get(link, verify=False)
                
                print(idx)

                try:
                    yt_url = page.text[2:-2].split(',')[1]
                    f.write(f"{yt_url} {vid_id} \n")
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
