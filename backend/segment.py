import cv2
import numpy as np
import mediapipe as mp
from PIL import Image
import os

def segment_person(image_path, output_dir="backend/static"):
    image = cv2.imread(image_path)
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    mp_selfie_segmentation = mp.solutions.selfie_segmentation
    with mp_selfie_segmentation.SelfieSegmentation(model_selection=1) as segmenter:
        results = segmenter.process(image_rgb)
        mask = results.segmentation_mask
        condition = mask > 0.5

        # Feathered alpha for sticker effect
        mask_blurred = cv2.GaussianBlur(mask, (21, 21), 0)
        alpha = (mask_blurred * 255).astype(np.uint8)
        foreground_rgba = np.dstack((image_rgb, alpha))
        Image.fromarray(foreground_rgba).save(os.path.join(output_dir, "foreground_clear.png"))

        # Background blur layers
        light_blur = cv2.GaussianBlur(image_rgb, (15, 15), 0)
        heavy_blur = cv2.GaussianBlur(image_rgb, (111, 111), 0)
        mask_inv = 1.0 - mask
        mask_inv = cv2.GaussianBlur(mask_inv, (31, 31), 0)
        mask_inv = np.clip(mask_inv, 0.0, 1.0)[..., None]
        background_blurred = (mask_inv * heavy_blur + (1 - mask_inv) * light_blur).astype(np.uint8)
        Image.fromarray(background_blurred).save(os.path.join(output_dir, "background_blurred.png"))

        # Final 3D composite
        composite_ultra = np.where(condition[..., None], image_rgb, background_blurred)
        Image.fromarray(composite_ultra.astype(np.uint8)).save(os.path.join(output_dir, "composite_3d.png"))

        return {
            "foreground": "static/foreground_clear.png",
            "background_blurred": "static/background_blurred.png",
            "composite": "static/composite_3d.png"
        }
