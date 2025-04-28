# Filename: sample_preprocessor.py
# Programmer(s): Abdurrahman Alyajouri
# Date: 4/22/2025
# Purpose: The purpose of this program is to preprocess a sentence image sample
#          to clean up noise as best as possible, desaturate the image, and more, 
#          in order to feed the neural network models only absolutely necessary information.

import os
import numpy as np 
import skimage.io as io
from skimage import transform
from skimage.color import rgb2gray
from skimage.util import img_as_float, invert
from scipy.ndimage import center_of_mass, shift

# in house libs
from common import get_output_path, people, total_sentences

def process(person, id):
    img = invert(img_as_float(rgb2gray(io.imread(get_output_path(person, id)))))

    # force pixel values below a 'threshold' to be zero, this clears up alot of visible noise
    # from the scanned samples.
    threshold = 0.0
    img[img < threshold] = 0

    # center image contents based on the pixel coordinates of the "center of mass".
    com = center_of_mass(img)
    shift_vector = (np.array(img.shape) / 2) - np.array(com)
    centered_img = shift(img, shift=shift_vector, order=0, mode='constant', cval=0.0)
    centered_img = (centered_img * (2**8 - 1)).astype(np.uint8)
    io.imsave(get_output_path(person, id), centered_img)

def main():
    for person in people:
        for i in range(total_sentences):
            process(person, i + 1)

if __name__ == "__main__":
    main()
