import os
from PIL import Image

# ==========================================================
# PATH DATASET
# ==========================================================

dataset_dirs = [
    r"C:\xampp\htdocs\resepin_aja\vision_model\dataset\dataset_baru_7sep\train_augmentasi",
    r"C:\xampp\htdocs\resepin_aja\vision_model\dataset\dataset_baru_7sep\valid",
    r"C:\xampp\htdocs\resepin_aja\vision_model\dataset\dataset_baru_7sep\test"
]

# ==========================================================
# CEK GAMBAR
# ==========================================================

total = 0
rusak = 0

for dataset_dir in dataset_dirs:

    print("\n==========================================")
    print("CEK:", dataset_dir)
    print("==========================================")

    for root, dirs, files in os.walk(dataset_dir):

        for filename in files:

            if not filename.lower().endswith(
                ('.jpg', '.jpeg', '.png', '.bmp', '.webp')
            ):
                continue

            total += 1

            filepath = os.path.join(root, filename)

            try:
                with Image.open(filepath) as img:
                    img.verify()

            except Exception as e:

                rusak += 1

                print("\n❌ GAMBAR RUSAK:")
                print(filepath)
                print("Error:", e)

print("\n==========================================")
print("HASIL PEMERIKSAAN")
print("==========================================")

print("Total gambar :", total)
print("Gambar rusak :", rusak)
print("Gambar valid :", total - rusak)

if rusak == 0:
    print("\n✅ Semua gambar valid!")
else:
    print("\n⚠️ Ada gambar yang harus dihapus/diperbaiki.")