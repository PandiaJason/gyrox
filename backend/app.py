from flask import Flask, request, send_from_directory, jsonify
from flask_cors import CORS
import os
from segment import segment_person

app = Flask(__name__, static_folder="static")
CORS(app)

@app.route('/process', methods=['POST'])
def process():
    file = request.files.get('image')
    if not file:
        return {"error": "no file"}, 400

    temp = os.path.join("backend/static", "input.jpg")
    file.save(temp)
    out = segment_person(temp)

    return jsonify({
        "foreground": f"/static/{out['foreground']}",
        "background": f"/static/{out['background']}"
    })

@app.route('/')
def index():
    return send_from_directory("../frontend", 'index.html')