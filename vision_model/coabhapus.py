import os, shutil
import numpy as np
from tensorflow.keras.applications.resnet50 import ResNet50, preprocess_input
from tensorflow.keras.preprocessing import image
from tensorflow.keras.models import Model
from tqdm import tqdm
import cv2

# === Folder Dataset ===
folder = r"C:\xampp\htdocs\resepin_aja\vision_model\dataset\dataset_jadi\valid\jahe"
dup_folder = os.path.join(folder, "_duplicates")
removed_folder = os.path.join(folder, "_removed")

os.makedirs(dup_folder, exist_ok=True)
os.makedirs(removed_folder, exist_ok=True)

# === Load Model ResNet50 ===
base = ResNet50(weights='imagenet', include_top=False, pooling='avg')
model = Model(inputs=base.input, outputs=base.output)

# === List Semua Gambar ===
files = [f for f in os.listdir(folder) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
files.sort()

# === Fungsi embedding (dengan augmentasi ringan) ===
def get_all_embeddings(img_path):
    try:
        img = image.load_img(img_path, target_size=(224, 224))
        arr = image.img_to_array(img)
        variants = [arr]

        variants.append(np.fliplr(arr))
        variants.append(np.flipud(arr))
        variants.append(cv2.rotate(arr, cv2.ROTATE_90_CLOCKWISE))
        variants.append(cv2.rotate(arr, cv2.ROTATE_90_COUNTERCLOCKWISE))
        variants.append(cv2.rotate(arr, cv2.ROTATE_180))

        embeddings = []
        for v in variants:
            x = np.expand_dims(v, axis=0)
            x = preprocess_input(x)
            feat = model.predict(x, verbose=0)[0]
            feat = feat / (np.linalg.norm(feat) + 1e-10)
            embeddings.append(feat)

        return embeddings
    except Exception as e:
        print("❌ Gagal:", img_path, e)
        return []

# === Generate embeddings ===
embeddings = {}
for fname in tqdm(files, desc="🔍 Generating embeddings"):
    path = os.path.join(folder, fname)
    embeddings[fname] = get_all_embeddings(path)

# === DETEKSI DUPLIKAT ===
threshold = 0.80
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

print("\n✅ Duplicate selesai")
print(f"Total duplicate: {len(os.listdir(dup_folder))}")

# ========================
# BATASI JUMLAH DATA
# ========================
print("\n📊 Mengatur jumlah dataset (25–30)...")

files_clean = [f for f in os.listdir(folder) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
total = len(files_clean)

print(f"Jumlah setelah hapus duplikat: {total}")

# 🔥 Jika lebih dari 30 → pindahkan ke _removed
if total > 30:
    np.random.shuffle(files_clean)
    to_remove = files_clean[30:]

    for f in to_remove:
        shutil.move(os.path.join(folder, f), os.path.join(removed_folder, f))

    print(f"🗑️ Dipindahkan {len(to_remove)} gambar ke _removed")

# ⚠️ Jika kurang dari 25
elif total < 25:
    print("⚠️ Data kurang dari 25! Sebaiknya tambah dataset.")

# Final
final_files = [f for f in os.listdir(folder) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
print(f"✅ Jumlah akhir dataset: {len(final_files)} gambar")
print(f"📁 Folder duplicate: {dup_folder}")
print(f"📁 Folder removed: {removed_folder}")