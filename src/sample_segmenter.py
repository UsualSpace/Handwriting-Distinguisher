# Filename: sample_segmenter.py
# Programmer(s): Abdurrahman Alyajouri
# Date: 4/22/2025
# Purpose: The purpose of this program is to take our raw handwriting sample pages
#          (5 sentences per page, 2 inches apart, 1 inch left margin, starting at 1.5 inches from the top), and segment 
#          each page to create samples containing a single sentence.

import numpy as np 
import skimage.io as io

img = io.imread("../sentences_alyajouri.jpg")
print(img.shape)

# size of the sentence sheets we used, in inches.
sentence_sheet_shape = (11, 8.5)

# inch to pixel conversion functions.
def itopy(inches_x):
    ppi = img.shape[1] // sentence_sheet_shape[1]
    return int(inches_x * ppi)

def itopx(inches_y):
    ppi = img.shape[0] // sentence_sheet_shape[0]
    return int(inches_y * ppi)

def itop(inch_coords):
    return (itopy(inch_coords[0]), itopx(inch_coords[1]))

# inch based coordinates.
tl = (1 + 2 * 4, 1)
br = (tl[0] + 1, img.shape[1])

# convert to pixel coordinates.
tl = itop(tl)
br = itop(br)

crop = img[tl[0]:br[0], tl[1]:br[1], :]
print(crop.shape)

# testing
import matplotlib.pyplot as plt
plt.imshow(crop, interpolation="nearest")
plt.show()