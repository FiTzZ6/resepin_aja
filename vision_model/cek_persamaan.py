import os
import hashlib

def get_file_hashes(folder):
    hashes = {}
    for root, dirs, files in os.walk(folder):
        for file in files:
            path = os.path.join(root, file)
            with open(path, 'rb') as f:
                h = hashlib.md5(f.read()).hexdigest()
            hashes[h] = path
    return hashes

train_hashes = get_file_hashes("dataset/dataset_jadi/train_augmented")
valid_hashes = get_file_hashes("dataset/dataset_jadi/valid")

duplikat = set(train_hashes.keys()) & set(valid_hashes.keys())

if duplikat:
    print(f"⚠️ Ditemukan {len(duplikat)} gambar duplikat!")
    for h in list(duplikat)[:5]:
        print(f" - Train: {train_hashes[h]}")
        print(f" - Valid: {valid_hashes[h]}")
else:
    print("✅ Tidak ada duplikat, data bersih!")