# Filename: sample_segmenter.py
# Programmer(s): Abdurrahman Alyajouri
# Date: 4/22/2025
# Purpose: The purpose of this program is to take our raw handwriting sample pages
#          (5 sentences per page, 2 inches apart, 1 inch left margin, starting at 1.5 inches from the top), and segment 
#          each page to create samples containing a single sentence.

import numpy as np 
import skimage.io as io

# in house libs
from common import get_input_path, get_output_path, people, sheet_resolution, total_sentences

# size of the sentence sheets we used, in inches.
sentence_sheet_shape = (11, 8.5)

# inch to pixel conversion functions.
def itopx(inches_x, img):
    ppi = img.shape[1] // sentence_sheet_shape[1]
    return int(inches_x * ppi)

def itopy(inches_y, img):
    ppi = img.shape[0] // sentence_sheet_shape[0]
    return int(inches_y * ppi)

def itop(inch_coords, img):
    return (itopy(inch_coords[0], img), itopx(inch_coords[1], img))

def segment(person, id):
    # inset sheet image into a fixed resolution blank canvas to maintain consistent segment resolutions.
    tmp_img = io.imread(get_input_path(person, id + 1))
    img = np.ones((sheet_resolution[0], sheet_resolution[1], 3), dtype=np.uint8) + 255
    img[0:tmp_img.shape[0], 0:tmp_img.shape[1], :] = tmp_img[0:min(tmp_img.shape[0], img.shape[0]), 0:min(tmp_img.shape[1], img.shape[1]), :]
    print(img.shape)
    for i in range(5):
        # inch based coordinates
        # start at one inch from the top, step one inch to cover the sentence, then step 2 inches down * the number of sentences we have processed
        # to get to the next sentence. constant left margin of 0.8 inches is used.
        tl = (0.8 + 2 * i, 0.8)
        br = (tl[0] + 1.1, img.shape[1])

        # convert to pixel coordinates.
        tl = itop(tl, img)
        br = itop(br, img)
        crop = img[tl[0]:br[0], tl[1]:br[1], :]
        io.imsave(get_output_path(person, i + 5 * id + 1), crop)
        print(crop.shape)

def main():
    for person in people:
        for i in range(int(total_sentences // 5)):
            segment(person, i)
            
    # testing
    # import matplotlib.pyplot as plt
    # plt.imshow(crop, interpolation="nearest")
    # plt.show()

if __name__ == "__main__":
    main()
