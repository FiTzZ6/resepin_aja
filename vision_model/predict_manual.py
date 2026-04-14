import tensorflow as tf
from tensorflow.keras.preprocessing.image import load_img, img_to_array
from tensorflow.keras.models import load_model
import numpy as np
import os

# === KONFIGURASI ===
MODEL_PATH = "model/efficientnetb0_final.keras"   # ubah sesuai model kamu
CLASS_DIR = "dataset/dataset_jadi/train_augmented"               # digunakan untuk ambil label kelas
IMG_PATH = r"C:\xampp\htdocs\resepin_aja\vision_model\dataset\dataset_jadi\aug_0_38.jpg"    # ubah ke path gambar yang mau diuji

# === LOAD MODEL ===
print(f"📦 Memuat model dari: {MODEL_PATH}")
model = load_model(MODEL_PATH)

# === AMBIL LABEL DARI TRAIN FOLDER ===
class_names = sorted(os.listdir(CLASS_DIR))
print(f"📚 Total kelas terdeteksi: {len(class_names)}")

# === FUNGSI PREDIKSI ===
def predict_image(img_path, threshold=55):
    img = load_img(img_path, target_size=(224, 224))
    img_array = img_to_array(img) / 255.0
    img_array = np.expand_dims(img_array, axis=0)

    pred = model.predict(img_array)
    class_idx = np.argmax(pred[0])
    label = class_names[class_idx]
    confidence = np.max(pred[0]) * 100

    print("\n🖼️ Hasil Prediksi:")
    print(f"   • Gambar   : {os.path.basename(img_path)}")

    if confidence < threshold:
        print(f"   • Label    : Gambar ini tidak ada")
        print(f"   • Confidence : {confidence:.2f}% (di bawah threshold {threshold}%)")
        return "Gambar ini tidak ada", confidence
    else:
        print(f"   • Label    : {label}")
        print(f"   • Confidence : {confidence:.2f}%")
        return label, confidence

# === PANGGIL FUNGSI ===
predict_image(IMG_PATH)
