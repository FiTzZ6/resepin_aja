import os
import numpy as np
from flask import Flask, request, jsonify
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image

app = Flask(__name__)

MODEL_PATH = os.path.join(os.path.dirname(__file__), "model", "efficientnetb0_final.keras")

try:
    model = load_model(MODEL_PATH)
    print("✅ Model CNN berhasil dimuat.")
except Exception as e:
    print(f"❌ Gagal memuat model CNN: {e}")
    model = None

class_names = [
    'avocado', 'black_beans', 'butter', 'capsicum', 'carrots', 'chicken', 
    'corn', 'cucumber', 'eggplant', 'garlic', 'ginger', 'green_onions', 
    'honey', 'lemon', 'plum_tomatoes', 'potatoes', 'purple_onion', 
    'spinach', 'telur', 'yellow_onion'
]

def predict_food_image(img_path):
    if model is None:
        return {"error": "Model belum dimuat dengan benar."}

    img = image.load_img(img_path, target_size=(224, 224))
    img_array = image.img_to_array(img) / 255.0
    img_array = np.expand_dims(img_array, axis=0)

    preds = model.predict(img_array)
    pred_idx = int(np.argmax(preds[0]))
    confidence = float(np.max(preds[0]))

    return {
        "predicted_label": class_names[pred_idx],
        "confidence": round(confidence * 100, 2),
        "index": pred_idx
    }

# ✅ Tambahkan endpoint ini!
@app.route("/predict_image", methods=["POST"])
def predict_image_api():
    if "file" not in request.files:
        return jsonify({"error": "Tidak ada file gambar yang dikirim"}), 400

    file = request.files["file"]
    img_path = os.path.join("temp", file.filename)

    os.makedirs("temp", exist_ok=True)
    file.save(img_path)

    result = predict_food_image(img_path)

    os.remove(img_path)  # hapus file sementara setelah diprediksi

    return jsonify(result)

@app.route("/predict_images", methods=["POST"])
def predict_multiple_images():
    if "files[]" not in request.files:
        return jsonify({"status": "error", "message": "Tidak ada file"}), 400

    files = request.files.getlist("files[]")
    results = []

    os.makedirs("temp", exist_ok=True)

    for file in files:
        path = os.path.join("temp", file.filename)
        file.save(path)

        pred = predict_food_image(path)
        os.remove(path)

        if "error" not in pred:
            results.append(pred)

    return jsonify({
        "status": "success",
        "data": results
    })


if __name__ == "__main__":
    print("🚀 Flask image server running on port 5000...")
    app.run(port=5001)
