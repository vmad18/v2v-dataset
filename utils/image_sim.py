import numpy as np
from skimage.metrics import structural_similarity as ssim
from skimage.metrics import mean_squared_error as mse
import os

from PIL import Image
from imagehash import whash, phash
import cv2 as cv


def sim_score(im1, im2) -> float:
    score, diff = ssim(im1, im2, full=True)
    return score


def wlet_score(im1, im2) -> float:
    w_1 = whash(im1)
    w_2 = whash(im2)

    score = (w_1 - w_2) / len(w_1.hash) ** 2
    return 1. - score


def percept_score(im1, im2) -> float:
    p_1 = phash(im1)
    p_2 = phash(im2)

    score = (p_1 - p_2) / len(p_1.hash) ** 2
    return 1. - score


def main() -> None:

    path = ""

    total_score: float = 0.
    files = {}

    for p in os.listdir(path): files[int(p.split("_")[1])] = p

    for anchor, frame_path in enumerate(files.keys()):
        if anchor % 6 == 0:
            if anchor != 0: print(total_score)
            anch = Image.open(path+files[anchor])
            total_score = 0
            continue
        
        frame_path = files[anchor]

        img = Image.open(path+frame_path)
        score = w_score(anch, img)
        print(score)
        total_score += score/(6-1)
        # print("MSE: " + str(mse(img, anch)))

    print(total_score)


if __name__ == "__main__":
    main()