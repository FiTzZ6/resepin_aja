import os, shutil
import numpy as np
from tensorflow.keras.applications.resnet50 import ResNet50, preprocess_input
from tensorflow.keras.preprocessing import image
from tensorflow.keras.models import Model
from tqdm import tqdm
import cv2

# === Folder Dataset ===
folder = r"C:\xampp\htdocs\resepin_aja\vision_model\dataset\train\ground_turmeric"
dup_folder = os.path.join(folder, "_duplicates")
os.makedirs(dup_folder, exist_ok=True)

# === Load Model ResNet50 ===
base = ResNet50(weights='imagenet', include_top=False, pooling='avg')
model = Model(inputs=base.input, outputs=base.output)

# === List Semua Gambar ===
files = [f for f in os.listdir(folder) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
files.sort()

# === Fungsi untuk menghasilkan embedding (termasuk rotasi & flip) ===
def get_all_embeddings(img_path):
    """Kembalikan list embedding dari gambar asli + augmentasi (mirror dan rotasi)."""
    try:
        img = image.load_img(img_path, target_size=(224, 224))
        arr = image.img_to_array(img)
        variants = [arr]

        # Tambahkan mirror dan rotasi
        variants.append(np.fliplr(arr))   # flip horizontal
        variants.append(np.flipud(arr))   # flip vertical
        variants.append(cv2.rotate(arr, cv2.ROTATE_90_CLOCKWISE))
        variants.append(cv2.rotate(arr, cv2.ROTATE_90_COUNTERCLOCKWISE))
        variants.append(cv2.rotate(arr, cv2.ROTATE_180))

        # Buat embeddings untuk semua varian
        embeddings = []
        for v in variants:
            x = np.expand_dims(v, axis=0)
            x = preprocess_input(x)
            feat = model.predict(x, verbose=0)[0]
            feat = feat / (np.linalg.norm(feat) + 1e-10)
            embeddings.append(feat)
        return embeddings
    except Exception as e:
        print("❌ Gagal proses:", img_path, e)
        return []

# === Hitung Embeddings untuk Semua Gambar ===
embeddings = {}
for fname in tqdm(files, desc="🔍 Generating embeddings"):
    path = os.path.join(folder, fname)
    embeddings[fname] = get_all_embeddings(path)

# === Bandingkan antar gambar ===
threshold = 0.80  # threshold mirroring biasanya cocok di 0.75–0.85
kept = []

for fname, feats in embeddings.items():
    is_dup = False
    for kname in kept:
        for f1 in feats:
            for f2 in embeddings[kname]:
                sim = float(np.dot(f1, f2))
                if sim >= threshold:
                    print(f"🗑️ Duplicate: {fname} -> {kname} (sim={sim:.3f})")
                    shutil.move(os.path.join(folder, fname), os.path.join(dup_folder, fname))
                    is_dup = True
                    break
            if is_dup:
                break
        if is_dup:
            break
    if not is_dup:
        kept.append(fname)

print("\n=== HASIL AKHIR ===")
print(f"Total file duplikat dipindahkan: {len(os.listdir(dup_folder))}")
print(f"File hasil disimpan di folder: {dup_folder}")
