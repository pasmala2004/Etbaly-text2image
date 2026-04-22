# Hunyuan3D Text2Image Server

This is the text-to-image server for the Etbaly 3D Printing App.
It uses HunyuanDiT to generate images from text descriptions,
which are then sent to the shape generation server to create 3D models.

---

## What This Server Does
User types: "a coffee mug"
↓
HunyuanDiT generates an image
↓
Image sent to Shape Generation server
↓
STL file generated
↓
Ready to print!

---

## Requirements

- Lightning.ai account (separate from shape generation account)
- GPU: T4 (available on Lightning.ai free tier)
- Python 3.12
- ~8GB VRAM

---

## First Time Setup (Do This Once)

### 1. Clone the repo
```bash
git clone https://github.com/YOURUSERNAME/YOURREPO.git
cd Hunyuan3D-2
```

### 2. Install PyTorch
```bash
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
```

### 3. Install requirements
```bash
pip install -r requirements.txt
pip install -e .
```

### 4. Install additional dependencies
```bash
pip install flask pillow diffusers accelerate tiktoken sentencepiece
```

### 5. Fix version conflicts
```bash
pip uninstall numpy scikit-learn -y
pip install numpy==1.26.4
pip install scikit-learn
pip install transformers --upgrade
pip install diffusers --upgrade
```

### 6. Test import works
```bash
python -c "from hy3dgen.text2image import HunyuanDiTPipeline; print('OK!')"
```

---

## Every Session (Do This Every Time You Restart)

### Step 1: Switch to GPU
Click CPU button at top of Lightning.ai and select T4 GPU

### Step 2: Start the server
```bash
cd ~/Hunyuan3D-2
python text2image_api.py
```
Wait until you see:
Model ready!
Running on http://0.0.0.0:8080
First run downloads the model (~5GB) — takes 5-10 minutes.
After that loads from cache instantly.

### Step 3: Get your new URL
Click the plug icon in Lightning.ai top bar.
Copy the URL next to port 8080:
https://8080-XXXXXXXXXXXXXX.cloudspaces.litng.ai

### Step 4: Update the backend
```bash
bash update_text2image_url.sh
```
Paste the new URL when asked.

### Step 5: Verify
```bash
curl https://YOUR-NEW-URL/health
```
Should return:
```json
{"status": "running"}
```

---

## API Endpoints

### Health Check
GET /health
Returns: {"status": "running"}

### Generate Image (returns base64)
POST /generate-image
Content-Type: application/json
Body: {
"prompt": "a simple coffee mug",
"seed": 0
}
Returns: {
"success": true,
"image_base64": "...",
"prompt": "a simple coffee mug",
"seed": 0
}

### Generate Image (returns PNG file)
POST /generate-image-file
Content-Type: application/json
Body: {
"prompt": "a simple coffee mug",
"seed": 0
}
Returns: PNG file

---

## Prompt Tips

The model works best with:
- Simple object descriptions
- White background objects
- Single objects (not scenes)

Good prompts:
"a simple coffee mug"
"a small toy car"
"a phone stand"
"a vase with simple shape"
"a chess piece, king"

Bad prompts:
"a beautiful sunset"      <- not an object
"people sitting at cafe"  <- scene not object
"abstract art"            <- not 3D printable

The model automatically adds:
- White background
- 3D style
- Best quality

---

## How Prompts Work

The model is Chinese-based (HunyuanDiT by Tencent).
It automatically adds Chinese style prompts:

```python
# Your prompt
"a coffee mug"

# Gets combined with (Chinese):
+ ",白色背景,3D风格,最佳质量"
# Translation: white background, 3D style, best quality
```

English prompts work fine — the Chinese additions just improve 3D printing quality.

---

## Using the Seed Parameter

The seed controls randomness:
```json
{"prompt": "a coffee mug", "seed": 0}   <- always same result
{"prompt": "a coffee mug", "seed": 1}   <- slightly different
{"prompt": "a coffee mug", "seed": 42}  <- different again
```

Use the same seed to reproduce the same image.

---

## Troubleshooting

### ModuleNotFoundError: No module named 'hy3dgen'
```bash
# Always run from inside the repo folder
cd ~/Hunyuan3D-2
python text2image_api.py
```

### tiktoken error
```bash
pip install tiktoken
```

### sentencepiece/spiece.model error
```bash
# Delete corrupted cache and reinstall
rm -rf ~/.cache/huggingface/hub/models--Tencent-Hunyuan--HunyuanDiT-v1.1-Diffusers-Distilled
pip install sentencepiece
```

### transformers version conflict
```bash
pip install transformers --upgrade
pip install diffusers --upgrade
```

### numpy error
```bash
pip uninstall numpy scikit-learn -y
pip install numpy==1.26.4
pip install scikit-learn
```

### Out of VRAM
The T4 has 15GB VRAM.
HunyuanDiT uses ~8GB.
If you get VRAM errors:
```bash
# Check current usage
nvidia-smi

# Clear cache between requests if needed
import torch
torch.cuda.empty_cache()
```

---

## VRAM Usage

| Model | VRAM |
|-------|------|
| HunyuanDiT text2image | ~8GB |
| Available on T4 | 15GB |
| Remaining | ~7GB |

This is why text2image runs on a separate Lightning.ai account
from the shape generation server.

---

## GPU Hours

Lightning.ai gives 35 free GPU hours per month.
- Switch to CPU when not generating
- Switch to GPU only when running text2image_api.py
- Monitor usage at lightning.ai/settings

---

## Backend Integration

The backend connects to this server via:
POST https://etbaly-backend.vercel.app/api/v1/admin/ai/set-text2image-url
Body: {"url": "YOUR_LIGHTNING_URL"}
GET https://etbaly-backend.vercel.app/api/v1/admin/ai/text2image-url

---

## Full Architecture
User types text prompt
↓
Backend calls POST /generate-image
↓
Text2Image Server (this server)
HunyuanDiT generates PNG image
↓
Backend calls POST /generate on Shape Server
↓
Shape Server generates STL file
↓
User downloads STL file

---

## Project Structure
Hunyuan3D-2/
├── text2image_api.py          <- This server
├── update_text2image_url.sh   <- URL updater script
├── hy3dgen/
│   └── text2image.py          <- HunyuanDiT pipeline
└── requirements.txt

---

## Tech Stack

| Component | Technology |
|-----------|------------|
| Text2Image Model | HunyuanDiT-v1.1 (Tencent) |
| API Server | Flask (Python) |
| GPU Platform | Lightning.ai (separate account) |
| Backend | Express.js (Vercel) |

EOF
Then push it:
bashgit add README_TEXT2IMAGE.md
git commit -m "Add text2image server README"
git push origin main
