#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import os
import math
import numpy as np
from PIL import Image
from skimage import io, exposure
from tqdm import tqdm

Image.MAX_IMAGE_PIXELS = 1000000000


def crop_image_label_pair(image_path, label_path, out_dir, crop_size):

	image_basename, _ = os.path.splitext(os.path.basename(image_path))

	image = io.imread(image_path)
	image = image[:, :, :3] # remove alpha channel

	label = io.imread(label_path)
	label = label[:, :, :3] # remove alpha channel

	h, w, _ = image.shape
	
	yi_max, xi_max = int(float(h) / float(crop_size)), int(float(w) / float(crop_size))

	for yi in range(yi_max):
		for xi in range(xi_max):

			left = xi * crop_size
			top = yi * crop_size
			right = left + crop_size
			bottom = top + crop_size

			image_crop = image[top:bottom, left:right]

			if exposure.is_low_contrast(image_crop, fraction_threshold=0.005):
				continue # do not save all-black or all-white images

			label_crop = label[top:bottom, left:right]

			h_crop, w_crop, _ = image_crop.shape
			out_image = np.empty(shape=(h_crop, w_crop * 2, 3), dtype=np.uint8)
			out_image[:, :w_crop] = image_crop
			out_image[:, w_crop:] = label_crop

			out_path = os.path.join(out_dir, "{}_{}_{}.png".format(image_basename, yi, xi))
			io.imsave(out_path, out_image)


def gen_train_val_crops(root_dir, data_list, out_dir, crop_size):

	with open(data_list) as f:
		scenes = f.readlines()

	for scene in scenes:
		scene = scene.rstrip()

		print("Loading {} ...".format(scene))

		image_path = os.path.join(root_dir, "{}.png".format(scene))
		label_path = os.path.join(root_dir, "{}_Annotated_Cars.png".format(scene))

		crop_image_label_pair(image_path, label_path, out_dir, crop_size)

	print("Done!")


if __name__ == "__main__":

	parser = argparse.ArgumentParser()

	parser.add_argument('--root_dir', help='Root directory for cowc ground_truth_sets dir',
						default='../../data/cowc/datasets/ground_truth_sets')
	parser.add_argument('--data_list', help='Path to a text listing up source cowc image and label data',
						default='../../data/cowc_processed/train_val/train_val.txt')
	parser.add_argument('--out_dir', help='Output directory',
						default='../../data/cowc_processed/train_val/crop/data')
	parser.add_argument('--crop_size', help='Crop size in px', 
						default=256)

	args = parser.parse_args()

	gen_train_val_crops(args.root_dir, args.data_list, args.out_dir, args.crop_size)