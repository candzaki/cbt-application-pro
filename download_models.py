import os
import urllib.request

models_dir = os.path.join("static", "models")
os.makedirs(models_dir, exist_ok=True)

base_url = "https://raw.githubusercontent.com/justadudewhohacks/face-api.js/master/weights/"

files = [
    "tiny_face_detector_model-weights_manifest.json",
    "tiny_face_detector_model-shard1",
    "face_landmark_68_model-weights_manifest.json",
    "face_landmark_68_model-shard1",
    "face_recognition_model-weights_manifest.json",
    "face_recognition_model-shard1",
    "face_recognition_model-shard2"
]

for file in files:
    print(f"Downloading {file}...")
    urllib.request.urlretrieve(base_url + file, os.path.join(models_dir, file))
    
print("All models downloaded!")
