import numpy as np
from skimage.metrics import structural_similarity as ssim
from skimage.metrics import mean_squared_error as mse
import os
import cv2 as cv


def sim_score(im1, im2) -> float:
    score, diff = ssim(im1, im2, full=True)
    return score


def main() -> None:

    path = "videoo0QRuWydJjw/"

    total_score: float = 0.
    files = {}

    for p in os.listdir(path): files[int(p.split("_")[1])] = p

    for anchor, frame_path in enumerate(files.keys()):
        if anchor % 6 == 0:
            print(total_score)
            anch = cv.imread(path+files[anchor], 0)
            total_score = 0
            continue
        
        frame_path = files[anchor]

        img = cv.imread(path+frame_path, 0)
        score = sim_score(anch, img)
        total_score += score/(6-1)
        # print("MSE: " + str(mse(img, anch)))

    print(total_score)


if __name__ == "__main__":
    main()