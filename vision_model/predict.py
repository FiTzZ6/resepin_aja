import tensorflow as tf
from tensorflow.keras.preprocessing import image
import numpy as np
import os

# === LOAD MODEL ===
model_path = os.path.join(os.getcwd(), "model", "model.h5")
model = tf.keras.models.load_model(model_path)

# === LABEL NAMES ===
class_indices = {
    0: "ayam",
    1: "ikan",
    2: "telur",
    3: "sayur",
    4: "nasi"
    # sesuaikan dengan isi dataset kamu
}

def predict_image(img_path):
    img = image.load_img(img_path, target_size=(150, 150))
    img_array = image.img_to_array(img) / 255.0
    img_array = np.expand_dims(img_array, axis=0)

    predictions = model.predict(img_array)
    predicted_class = np.argmax(predictions[0])
    confidence = np.max(predictions[0])

    label = class_indices.get(predicted_class, "Tidak diketahui")

    print(f"Gambar: {img_path}")
    print(f"Prediksi: {label} ({confidence:.2f})")

    return {"label": label, "confidence": float(confidence)}

# === Contoh Uji Coba ===
if __name__ == "__main__":
    result = predict_image("contoh.jpg")
    print(result)
