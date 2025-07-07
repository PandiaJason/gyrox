import cv2, numpy as np, mediapipe as mp
from PIL import Image
import os, uuid

def segment_person(image_path, output_dir="backend/static/output"):
    os.makedirs(output_dir, exist_ok=True)

    image = cv2.imread(image_path)
    rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    with mp.solutions.selfie_segmentation.SelfieSegmentation(model_selection=1) as seg:
        mask = seg.process(rgb).segmentation_mask
        mask_blur = cv2.GaussianBlur(mask, (21, 21), 0)
        alpha = (mask_blur * 255).astype(np.uint8)

        fg_rgba = np.dstack((rgb, alpha))
        blurred = cv2.GaussianBlur(rgb, (15, 15), 0)
        heavy = cv2.GaussianBlur(rgb, (111, 111), 0)
        inv = cv2.GaussianBlur(1 - mask, (31, 31), 0)[..., None]
        bg = (inv * heavy + (1 - inv) * blurred).astype(np.uint8)

        fg_img = Image.fromarray(fg_rgba)
        bg_img = Image.fromarray(bg)

        uid = uuid.uuid4().hex
        fg_filename = f"foreground_{uid}.png"
        bg_filename = f"background_{uid}.png"

        fg_path = os.path.join(output_dir, fg_filename)
        bg_path = os.path.join(output_dir, bg_filename)

        fg_img.save(fg_path)
        bg_img.save(bg_path)

        # Return relative paths for the frontend to access via /static/
        return {
            "foreground": f"output/{fg_filename}",
            "background": f"output/{bg_filename}"
        }