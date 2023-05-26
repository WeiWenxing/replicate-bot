import matplotlib.pyplot as plt
import logging

from colorizers import *
from PIL import Image, ImageOps
import numpy as np
from io import BytesIO


def byte_of_image(img, mode='JPEG'):
    img_buffer = BytesIO()
    img.save(img_buffer, mode)
    img_buffer.seek(0)
    return img_buffer


def grey_img(image):
    gray = ImageOps.grayscale(image)
    return gray


def color_img(image):
    colorizer_eccv16 = eccv16(pretrained=True).eval()
    colorizer_siggraph17 = siggraph17(pretrained=True).eval()

    # default size to process images is 256x256
    # grab L channel in both original ("orig") and resized ("rs") resolutions
    # img = load_img(opt.img_path)
    img = np.asarray(image)
    if img.ndim == 2:
        img = np.tile(img[:, :, None], 3)

    (tens_l_orig, tens_l_rs) = preprocess_img(img, HW=(256, 256))

    # colorizer outputs 256x256 ab map
    # resize and concatenate to original L channel
    img_bw = postprocess_tens(tens_l_orig, torch.cat((0 * tens_l_orig, 0 * tens_l_orig), dim=1))
    out_img_eccv16 = postprocess_tens(tens_l_orig, colorizer_eccv16(tens_l_rs).cpu())
    out_img_siggraph17 = postprocess_tens(tens_l_orig, colorizer_siggraph17(tens_l_rs).cpu())

    input = Image.fromarray((img_bw * 255).astype(np.uint8))
    out_eccv16 = Image.fromarray((out_img_eccv16 * 255).astype(np.uint8))
    out_siggraph17 = Image.fromarray((out_img_siggraph17 * 255).astype(np.uint8))
    return input, out_eccv16, out_siggraph17
