"""Prediksi bahan makanan dengan EfficientNetB0 tanpa rescale eksternal.

Model efficientnetb0_baru_norescale.keras harus dilatih dengan preprocessing
yang sama: input piksel mentah 0-255. Jangan membagi gambar dengan 255 di sini.
"""

import json
import os
import time
import uuid

import numpy as np
from flask import Flask, jsonify, request
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
from werkzeug.utils import secure_filename

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(
    BASE_DIR, "model", "efficientnetb0_baru_final_tanpa_augmentasi.keras"
)
CLASS_PATH = os.path.join(BASE_DIR, "model", "class_indices_tanpa_augmentasi.json")
TEMP_DIR = os.path.join(BASE_DIR, "temp")
IMG_SIZE = (224, 224)
CONFIDENCE_THRESHOLD = 45.0
IMG_EXT = {".jpg", ".jpeg", ".png", ".bmp", ".gif", ".webp"}

# Load model sekali saat server dimulai, bukan setiap request.
try:
    model = load_model(MODEL_PATH)
    print(f"Model CNN berhasil dimuat: {MODEL_PATH}")
except Exception as exc:
    print(f"Gagal memuat model CNN dari {MODEL_PATH}: {exc}")
    model = None

try:
    with open(CLASS_PATH, "r", encoding="utf-8") as file:
        class_indices = json.load(file)
    class_names = [
        name for name, _ in sorted(class_indices.items(), key=lambda item: item[1])
    ]
    print(f"{len(class_names)} kelas dimuat.")
except Exception as exc:
    print(f"Gagal membaca daftar kelas dari {CLASS_PATH}: {exc}")
    class_names = []

if model is not None and class_names:
    output_count = int(model.output_shape[-1])
    if output_count != len(class_names):
        raise RuntimeError(
            f"Model memiliki {output_count} keluaran, tetapi daftar kelas "
            f"memiliki {len(class_names)} kelas."
        )


def predict_food_image(img_path):
    """Prediksi satu gambar.

    response_time_ms mencakup membaca/mengubah ukuran gambar dan inferensi CNN.
    Tidak mencakup upload file melalui jaringan.
    """
    started = time.perf_counter()

    if model is None or not class_names:
        return {
            "error": "Model atau daftar kelas belum dimuat dengan benar.",
            "response_time_ms": round((time.perf_counter() - started) * 1000, 2),
        }

    try:
        img = image.load_img(
            img_path,
            target_size=IMG_SIZE,
            color_mode="rgb",
        )
        arr = image.img_to_array(img)  # float32, piksel 0-255; tanpa /255
        arr = np.expand_dims(arr, axis=0)

        # Panggilan ini menunggu hasil prediksi selesai.
        probabilities = model.predict(arr, verbose=0)[0]
        top_indices = np.argsort(probabilities)[::-1][:3]
        best_index = int(top_indices[0])
        confidence = round(float(probabilities[best_index]) * 100, 2)
        elapsed_ms = (time.perf_counter() - started) * 1000
        is_accepted = confidence >= CONFIDENCE_THRESHOLD
        result = {
            "predicted_label": class_names[best_index],
            "confidence": confidence,
            "is_accepted": is_accepted,
            "confidence_threshold": CONFIDENCE_THRESHOLD,
            "index": best_index,
            "top3": [
                {
                    "label": class_names[int(index)],
                    "confidence": round(float(probabilities[index]) * 100, 2),
                }
                for index in top_indices
            ],
            "response_time_ms": round(elapsed_ms, 2),
            "response_time_seconds": round(elapsed_ms / 1000, 4),
        }
        print(
            f"[CNN] Prediksi: {result['predicted_label']} | "
            f"Confidence: {result['confidence']:.2f}% | "
            f"Waktu inferensi: {elapsed_ms:.2f} ms ({elapsed_ms / 1000:.4f} detik)",
            flush=True,
        )
        return result
    except Exception as exc:
        return {
            "error": f"Gambar gagal diproses: {exc}",
            "response_time_ms": round((time.perf_counter() - started) * 1000, 2),
        }


def _save_upload(file_storage):
    """Simpan unggahan dengan nama acak dan validasi ekstensi."""
    if not file_storage or not file_storage.filename:
        return None

    filename = secure_filename(file_storage.filename)
    extension = os.path.splitext(filename)[1].lower()
    if extension not in IMG_EXT:
        return None

    os.makedirs(TEMP_DIR, exist_ok=True)
    saved_path = os.path.join(TEMP_DIR, f"{uuid.uuid4().hex}{extension}")
    file_storage.save(saved_path)
    return saved_path


app = Flask(__name__)
# Batas ukuran unggahan 10 MB untuk menghindari file terlalu besar.
app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024


@app.errorhandler(413)
def file_too_large(_error):
    return jsonify({"error": "Ukuran gambar melebihi batas 10 MB."}), 413


@app.route("/predict_image", methods=["POST"])
def predict_image_api():
    request_started = time.perf_counter()

    if "file" not in request.files:
        return (
            jsonify(
                {
                    "error": "Tidak ada file gambar yang dikirim.",
                    "request_processing_time_ms": round(
                        (time.perf_counter() - request_started) * 1000, 2
                    ),
                }
            ),
            400,
        )

    path = _save_upload(request.files["file"])
    if path is None:
        return (
            jsonify(
                {
                    "error": "File kosong atau format gambar tidak didukung.",
                    "request_processing_time_ms": round(
                        (time.perf_counter() - request_started) * 1000, 2
                    ),
                }
            ),
            400,
        )

    try:
        result = predict_food_image(path)
    finally:
        try:
            os.remove(path)
        except OSError:
            app.logger.warning("Tidak dapat menghapus file sementara: %s", path)

    # Termasuk penyimpanan unggahan dan prediksi; tidak termasuk transfer jaringan.
    request_elapsed_ms = (time.perf_counter() - request_started) * 1000
    result["request_processing_time_ms"] = round(request_elapsed_ms, 2)
    result["request_processing_time_seconds"] = round(request_elapsed_ms / 1000, 4)
    print(
        f"[REQUEST] Total pemrosesan server: {request_elapsed_ms:.2f} ms "
        f"({request_elapsed_ms / 1000:.4f} detik)",
        flush=True,
    )
    status_code = 500 if "error" in result else 200
    return jsonify(result), status_code


@app.route("/predict_images", methods=["POST"])
def predict_multiple_images():
    request_started = time.perf_counter()
    files = request.files.getlist("files[]")

    if not files or not any(f and f.filename for f in files):
        return (
            jsonify(
                {
                    "status": "error",
                    "message": "Tidak ada file gambar yang dikirim.",
                    "request_processing_time_ms": round(
                        (time.perf_counter() - request_started) * 1000, 2
                    ),
                }
            ),
            400,
        )

    results = []
    errors = []

    for file_storage in files:
        path = _save_upload(file_storage)
        if path is None:
            errors.append(
                {
                    "filename": secure_filename(file_storage.filename or ""),
                    "error": "Format gambar tidak didukung atau nama file kosong.",
                }
            )
            continue

        try:
            prediction = predict_food_image(path)
        finally:
            try:
                os.remove(path)
            except OSError:
                app.logger.warning("Tidak dapat menghapus file sementara: %s", path)

        if "error" in prediction:
            errors.append(
                {
                    "filename": secure_filename(file_storage.filename or ""),
                    "error": prediction["error"],
                }
            )
        else:
            prediction["filename"] = secure_filename(file_storage.filename or "")
            results.append(prediction)

    return jsonify(
        {
            "status": "success" if results else "error",
            "data": results,
            "errors": errors,
            "request_processing_time_ms": round(
                (time.perf_counter() - request_started) * 1000, 2
            ),
        }
    ), (200 if results else 400)


if __name__ == "__main__":
    print("🚀 Flask image server berjalan di port 5001...")
    app.run(host="127.0.0.1", port=5001, debug=False)
