from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
from werkzeug.utils import secure_filename
from segment import segment_person

# Serve frontend from the correct directory
app = Flask(__name__, static_folder='../frontend', static_url_path='')
CORS(app)

# Define folders
UPLOAD_FOLDER = 'backend/uploads'
OUTPUT_FOLDER = 'static/output'  # ✅ now points to root/static/output

# Ensure folders exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Serve index.html from frontend
@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')

# API endpoint for processing the image
@app.route('/process', methods=['POST'])
def process():
    if 'image' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    file = request.files['image']
    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

    # Run segmentation
    result = segment_person(filepath, OUTPUT_FOLDER)

    return jsonify({
        'foreground': f'/static/output/{result["foreground"]}',
        'background': f'/static/output/{result["background"]}'
    })

# Optional: serve static files if needed
@app.route('/static/output/<filename>')
def serve_output(filename):
    return send_from_directory(OUTPUT_FOLDER, filename)

if __name__ == '__main__':
    app.run(debug=True)