from flask import Flask, request, jsonify, send_file
from hy3dgen.text2image import HunyuanDiTPipeline
import torch
import base64
import uuid
import os
import io
from PIL import Image

app = Flask(__name__)

print("Loading text2image model...")
text2img = HunyuanDiTPipeline(device='cuda')
print("Model ready!")

@app.route('/', methods=['GET'])
def health():
    return jsonify({"status": "running"})

@app.route('/generate-image', methods=['POST'])
def generate_image():
    """
    Text → Image
    Input:  {"prompt": "a coffee mug", "seed": 0}
    Output: base64 encoded image
    """
    try:
        data   = request.json
        if not data or 'prompt' not in data:
            return jsonify({"error": "Missing 'prompt' field"}), 400

        prompt = data['prompt']
        seed   = data.get('seed', 0)

        print(f"Generating image for: '{prompt}'")
        image = text2img(prompt=prompt, seed=seed)

        # Convert to base64
        buffer = io.BytesIO()
        image.save(buffer, format='PNG')
        img_b64 = base64.b64encode(buffer.getvalue()).decode()

        print(f"Done!")
        return jsonify({
            "success": True,
            "image_base64": img_b64,
            "prompt": prompt,
            "seed": seed
        })

    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/generate-image-file', methods=['POST'])
def generate_image_file():
    """
    Text → Image file (PNG)
    Input:  {"prompt": "a coffee mug", "seed": 0}
    Output: PNG file directly
    """
    try:
        data   = request.json
        if not data or 'prompt' not in data:
            return jsonify({"error": "Missing 'prompt' field"}), 400

        prompt  = data['prompt']
        seed    = data.get('seed', 0)
        temp_id = str(uuid.uuid4())
        img_path = f'/tmp/{temp_id}.png'

        print(f"Generating image for: '{prompt}'")
        image = text2img(prompt=prompt, seed=seed)
        image.save(img_path)
        print(f"Done!")

        return send_file(
            img_path,
            mimetype='image/png',
            as_attachment=True,
            download_name='generated.png'
        )

    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)