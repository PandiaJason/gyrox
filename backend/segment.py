import cv2, numpy as np, mediapipe as mp
from PIL import Image
import os, uuid

def segment_person(image_path, output_dir="backend/static"):
    os.makedirs(output_dir, exist_ok=True)

    image = cv2.imread(image_path)
    rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    with mp.solutions.selfie_segmentation.SelfieSegmentation(model_selection=1) as seg:
        mask = seg.process(rgb).segmentation_mask
        mask_blur = cv2.GaussianBlur(mask, (21,21), 0)
        alpha = (mask_blur * 255).astype(np.uint8)

        fg_rgba = np.dstack((rgb, alpha))
        blurred = cv2.GaussianBlur(rgb, (15,15), 0)
        heavy = cv2.GaussianBlur(rgb, (111,111), 0)
        inv = cv2.GaussianBlur(1-mask, (31,31), 0)[..., None]
        bg = (inv * heavy + (1-inv) * blurred).astype(np.uint8)

        fg_img = Image.fromarray(fg_rgba)
        bg_img = Image.fromarray(bg)

        uid = uuid.uuid4().hex
        fg_path = f"foreground_clear_{uid}.png"
        bg_path = f"background_blurred_{uid}.png"

        fg_img.save(os.path.join(output_dir, fg_path))
        bg_img.save(os.path.join(output_dir, bg_path))

        return {"foreground": fg_path, "background": bg_path}