from flask import Flask, request, send_file, jsonify
import cv2
import numpy as np
import mediapipe as mp
from PIL import Image
import io
import os

app = Flask(__name__)

@app.route('/process', methods=['POST'])
def process_image():
    file = request.files['image']
    image = cv2.imdecode(np.frombuffer(file.read(), np.uint8), cv2.IMREAD_COLOR)
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    mp_selfie_segmentation = mp.solutions.selfie_segmentation
    with mp_selfie_segmentation.SelfieSegmentation(model_selection=1) as segmenter:
        results = segmenter.process(image_rgb)
        mask = results.segmentation_mask
        condition = mask > 0.5

        # Feather mask
        mask_blurred = cv2.GaussianBlur(mask, (21, 21), 0)
        alpha = (mask_blurred * 255).astype(np.uint8)

        # Foreground
        foreground_rgba = np.dstack((image_rgb, alpha))
        fg_img = Image.fromarray(foreground_rgba)
        fg_io = io.BytesIO()
        fg_img.save(fg_io, format='PNG')
        fg_io.seek(0)

        # Background Blur
        light_blur = cv2.GaussianBlur(image_rgb, (15, 15), 0)
        heavy_blur = cv2.GaussianBlur(image_rgb, (111, 111), 0)

        mask_inv = 1.0 - mask
        mask_inv = cv2.GaussianBlur(mask_inv, (31, 31), 0)
        mask_inv = np.clip(mask_inv, 0.0, 1.0)[..., None]
        background_blurred = (mask_inv * heavy_blur + (1 - mask_inv) * light_blur).astype(np.uint8)

        bg_img = Image.fromarray(background_blurred)
        bg_io = io.BytesIO()
        bg_img.save(bg_io, format='PNG')
        bg_io.seek(0)

        return jsonify({
            'foreground': '/get_image/fg',
            'background': '/get_image/bg'
        })

@app.route('/get_image/<which>')
def get_image(which):
    path = 'output_foreground.png' if which == 'fg' else 'output_background.png'
    return send_file(path, mimetype='image/png')

if __name__ == '__main__':
    app.run(debug=True)