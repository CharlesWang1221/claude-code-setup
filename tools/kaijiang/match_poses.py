"""把五張透明姿勢圖的亮度、灰階直方圖與墨色對齊老查垂手原圖。"""

import os
import sys

import numpy as np
from PIL import Image


def region_pixels(rgb, alpha, box):
    x0, y0, x1, y1 = box
    crop = rgb[y0:y1, x0:x1]
    if alpha is None:
        return crop.reshape(-1, 3)
    mask = alpha[y0:y1, x0:x1] > 200
    return crop[mask]


def histogram_lut(source, reference):
    source_gray = np.rint(source.mean(axis=1)).astype(np.uint8)
    reference_gray = np.rint(reference.mean(axis=1)).astype(np.uint8)
    source_hist = np.bincount(source_gray, minlength=256)
    target_hist = np.bincount(reference_gray, minlength=256)
    source_cdf = np.cumsum(source_hist) / len(source_gray)
    target_cdf = np.cumsum(target_hist) / len(reference_gray)
    return np.searchsorted(target_cdf, source_cdf).clip(0, 255).astype(np.uint8)


def target_tint(reference):
    gray = reference.mean(axis=1)
    bright = reference[gray > np.percentile(gray, 50)]
    return np.median(bright - bright.mean(axis=1, keepdims=True), axis=0)


def match_one(source, shirt_ref, pants_ref):
    rgba = np.asarray(source.convert('RGBA')).copy()
    rgb = rgba[:, :, :3].astype(np.float32)
    alpha = rgba[:, :, 3]
    shirt_src = region_pixels(rgb, alpha, (260, 780, 730, 1120))
    pants_src = region_pixels(rgb, alpha, (280, 1250, 700, 1530))
    if len(shirt_src) < 1000 or len(pants_src) < 1000:
        raise ValueError('姿勢圖的衣服／褲子取樣不足，不能做直方圖對齊')
    shirt_lut = histogram_lut(shirt_src, shirt_ref)
    pants_lut = histogram_lut(pants_src, pants_ref)
    dark_src = shirt_src[shirt_src.mean(axis=1) < 120]
    dark_ref = shirt_ref[shirt_ref.mean(axis=1) < 120]
    dark_lut = histogram_lut(dark_src, dark_ref)
    shirt_tint = target_tint(shirt_ref)
    pants_tint = target_tint(pants_ref)
    gray = np.rint(rgb.mean(axis=2)).clip(0, 255).astype(np.uint8)
    y = np.arange(rgb.shape[0], dtype=np.float32)[:, None]
    pants_weight = np.clip((y - 1140) / 140, 0, 1)[..., None]
    dark_weight = np.clip((160 - gray.astype(np.float32)) / 60, 0, 1)[..., None]
    shirt_gray = dark_lut[gray].astype(np.float32)[..., None] * dark_weight + shirt_lut[gray].astype(np.float32)[..., None] * (1-dark_weight)
    shirt_mapped = shirt_gray + shirt_tint
    pants_mapped = pants_lut[gray].astype(np.float32)[..., None] + pants_tint
    rgba[:, :, :3] = np.clip(shirt_mapped * (1 - pants_weight) + pants_mapped * pants_weight, 0, 255)
    return Image.fromarray(rgba), (shirt_lut, pants_lut, dark_lut, shirt_tint, pants_tint)


def apply_existing_luts(source, settings):
    shirt_lut, pants_lut, dark_lut, shirt_tint, pants_tint = settings
    rgba = np.asarray(source.convert('RGBA')).copy()
    gray = np.rint(rgba[:, :, :3].mean(axis=2)).clip(0, 255).astype(np.uint8)
    y = np.arange(rgba.shape[0], dtype=np.float32)[:, None]
    pants_weight = np.clip((y - 1140) / 140, 0, 1)[..., None]
    dark_weight = np.clip((160 - gray.astype(np.float32)) / 60, 0, 1)[..., None]
    shirt_gray = dark_lut[gray].astype(np.float32)[..., None] * dark_weight + shirt_lut[gray].astype(np.float32)[..., None] * (1-dark_weight)
    shirt_mapped = shirt_gray + shirt_tint
    pants_mapped = pants_lut[gray].astype(np.float32)[..., None] + pants_tint
    rgba[:, :, :3] = np.clip(shirt_mapped * (1 - pants_weight) + pants_mapped * pants_weight, 0, 255)
    return Image.fromarray(rgba)


def main():
    if len(sys.argv) != 4:
        raise SystemExit('用法：python match_poses.py <老查原圖> <v11 姿勢資料夾> <v12 輸出資料夾>')
    base_path, input_dir, output_dir = sys.argv[1:4]
    os.makedirs(output_dir, exist_ok=True)
    base = np.asarray(Image.open(base_path).convert('RGB')).astype(np.float32)
    shirt_ref = region_pixels(base, None, (260, 780, 730, 1120))
    pants_ref = region_pixels(base, None, (280, 1250, 700, 1530))
    for name in ('攤手', '手指', '托腮', '胸口', '搔頭'):
        with Image.open(os.path.join(input_dir, name + '.png')) as im:
            matched, settings = match_one(im, shirt_ref, pants_ref)
        matched.save(os.path.join(output_dir, name + '.png'))
        for suffix in ('_前',):
            front_path = os.path.join(input_dir, name + suffix + '.png')
            if os.path.exists(front_path):
                with Image.open(front_path) as front:
                    apply_existing_luts(front, settings).save(os.path.join(output_dir, name + suffix + '.png'))
        sample = np.asarray(matched)
        values = region_pixels(sample[:, :, :3].astype(float), sample[:, :, 3], (260, 780, 730, 1120))
        print(name, '衣服灰階中位數', round(float(np.median(values.mean(axis=1))), 1))
    print('垂手原圖衣服灰階中位數', round(float(np.median(shirt_ref.mean(axis=1))), 1))


if __name__ == '__main__':
    main()
