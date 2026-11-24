import os
import json
import csv

import numpy as np
import tensorflow as tf
from tensorflow.keras.models import load_model

from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
)

import seaborn as sns
import matplotlib.pyplot as plt

# ==========================================================
# KONFIGURASI
# ==========================================================
# Model hasil train_model_norescale.py (input piksel mentah 0-255).
MODEL_PATH = "model/efficientnetb0_baru_final_tanpa_augmentasi.keras"
CLASS_INDEX_PATH = "model/class_indices_tanpa_augmentasi.json"
# Folder hasil bersihkan_dataset.py
TEST_DIR = "dataset/dataset_baru_7sep_bersih/test"

BATCH_SIZE = 32
SHOW_PLOT = True   # False kalau hanya ingin menyimpan gambar
OUT_DIR = "model"

IMG_EXT = (".jpg", ".jpeg", ".png", ".bmp", ".gif")

REPORT_PATH = os.path.join(OUT_DIR, "test_laporan_klasifikasi_TANPAAUGMENTASI.txt")
CM_PATH = os.path.join(OUT_DIR, "test_confusion_matrix_TANPAAUGMENTASI.png")
CM_NORM_PATH = os.path.join(OUT_DIR, "test_confusion_matrix_normalisasi_TANPAAUGMENTASI.png")
WRONG_PATH = os.path.join(OUT_DIR, "test_prediksi_salah_TANPAAUGMENTASI.csv")

for p in (MODEL_PATH, CLASS_INDEX_PATH):
    if not os.path.isfile(p):
        raise FileNotFoundError(f"Berkas tidak ditemukan: {p}")
if not os.path.isdir(TEST_DIR):
    raise FileNotFoundError(f"Folder test tidak ditemukan: {TEST_DIR}")
os.makedirs(OUT_DIR, exist_ok=True)

# ==========================================================
# URUTAN KELAS (harus sama dengan saat training)
# ==========================================================
with open(CLASS_INDEX_PATH, "r", encoding="utf-8") as f:
    class_indices = json.load(f)
class_names = [n for n, _ in sorted(class_indices.items(), key=lambda kv: kv[1])]
NUM_CLASSES = len(class_names)

test_subdirs = sorted(
    d for d in os.listdir(TEST_DIR) if os.path.isdir(os.path.join(TEST_DIR, d))
)
if set(test_subdirs) != set(class_names):
    print("Kelas hanya di model :", sorted(set(class_names) - set(test_subdirs)))
    print("Kelas hanya di test  :", sorted(set(test_subdirs) - set(class_names)))
    raise ValueError("Daftar kelas folder test tidak sama dengan saat training.")

tidak_didukung = [
    os.path.join(dp, fn)
    for dp, _, names in os.walk(TEST_DIR)
    for fn in names
    if not fn.lower().endswith(IMG_EXT)
]
if tidak_didukung:
    print(f"{len(tidak_didukung)} berkas berekstensi tidak didukung, contoh:")
    for p in tidak_didukung[:10]:
        print("  ", p)
    raise RuntimeError("Jalankan bersihkan_dataset.py dulu (sekarang sudah mencakup folder test).")

# ==========================================================
# LOAD MODEL
# ==========================================================
print(f"Memuat model dari: {MODEL_PATH}")
model = load_model(MODEL_PATH, compile=False)
model.compile(loss=tf.keras.losses.CategoricalCrossentropy(), metrics=["accuracy"])
IMG_SIZE = tuple(model.input_shape[1:3])
print("Ukuran input model:", IMG_SIZE)

# ==========================================================
# DATA TEST (TANPA rescale=1./255)
# ==========================================================
# EfficientNet Keras sudah punya lapisan Rescaling/Normalization di dalam
# modelnya. Memberi rescale=1./255 di sini membuat input terlalu gelap
# dan akurasi anjlok, jadi piksel dibiarkan 0-255.
test_ds = tf.keras.utils.image_dataset_from_directory(
    TEST_DIR,
    labels="inferred",
    label_mode="categorical",
    class_names=class_names,
    image_size=IMG_SIZE,
    batch_size=BATCH_SIZE,
    shuffle=False,  # WAJIB untuk evaluasi
)
file_paths = list(test_ds.file_paths)

true_labels = np.concatenate([np.argmax(y.numpy(), axis=1) for _, y in test_ds])
xb, _ = next(iter(test_ds))
print(f"Rentang piksel batch: {float(tf.reduce_min(xb)):.1f} - {float(tf.reduce_max(xb)):.1f}")
if float(tf.reduce_max(xb)) <= 1.5:
    raise RuntimeError("Piksel terlihat sudah diskalakan ke 0-1. Hapus rescale/pembagian 255.")

test_ds = test_ds.prefetch(tf.data.AUTOTUNE)

# ==========================================================
# EVALUASI DASAR
# ==========================================================
loss, acc = model.evaluate(test_ds, verbose=1)

print("\nHASIL EVALUASI TEST SET")
print(f"   Jumlah gambar  : {len(true_labels)}")
print(f"   Akurasi Test   : {acc * 100:.2f}%")
print(f"   Loss Test      : {loss:.4f}  (tanpa label smoothing)")

# ==========================================================
# PREDIKSI
# ==========================================================
pred = model.predict(test_ds, verbose=0)
pred_labels = np.argmax(pred, axis=1)
confidence = pred.max(axis=1)

# ==========================================================
# METRIK LENGKAP
# ==========================================================
accuracy = accuracy_score(true_labels, pred_labels)
kw = dict(zero_division=0)
precision_w = precision_score(true_labels, pred_labels, average="weighted", **kw)
recall_w = recall_score(true_labels, pred_labels, average="weighted", **kw)
f1_w = f1_score(true_labels, pred_labels, average="weighted", **kw)
precision_m = precision_score(true_labels, pred_labels, average="macro", **kw)
recall_m = recall_score(true_labels, pred_labels, average="macro", **kw)
f1_m = f1_score(true_labels, pred_labels, average="macro", **kw)

print("\nMETRIK EVALUASI MODEL")
print(f"   Akurasi            : {accuracy * 100:.2f}%")
print(f"   Precision (weighted): {precision_w * 100:.2f}%   (macro: {precision_m * 100:.2f}%)")
print(f"   Recall    (weighted): {recall_w * 100:.2f}%   (macro: {recall_m * 100:.2f}%)")
print(f"   F1-Score  (weighted): {f1_w * 100:.2f}%   (macro: {f1_m * 100:.2f}%)")

# ==========================================================
# CLASSIFICATION REPORT
# ==========================================================
report = classification_report(
    true_labels, pred_labels,
    labels=list(range(NUM_CLASSES)), target_names=class_names,
    digits=3, zero_division=0,
)
print("\nLaporan Klasifikasi:")
print(report)
with open(REPORT_PATH, "w", encoding="utf-8") as f:
    f.write(report)
print("Laporan disimpan:", REPORT_PATH)

# ==========================================================
# CONFUSION MATRIX
# ==========================================================
cm = confusion_matrix(true_labels, pred_labels, labels=list(range(NUM_CLASSES)))


def gambar_cm(matrix, judul, path, fmt=None):
    plt.figure(figsize=(14, 12))
    sns.heatmap(matrix, annot=False, cmap="Blues",
                xticklabels=class_names, yticklabels=class_names)
    plt.title(judul)
    plt.xlabel("Predicted Label")
    plt.ylabel("True Label")
    plt.xticks(rotation=90, fontsize=7)
    plt.yticks(rotation=0, fontsize=7)
    plt.tight_layout()
    plt.savefig(path, dpi=150)
    print("Disimpan:", path)


gambar_cm(cm, "Confusion Matrix (Test Set)", CM_PATH)
cm_norm = cm / np.clip(cm.sum(axis=1, keepdims=True), 1, None)
gambar_cm(cm_norm, "Confusion Matrix Ternormalisasi per Kelas (Test Set)", CM_NORM_PATH)

# ==========================================================
# KESALAHAN TERBANYAK + DAFTAR PREDIKSI SALAH
# ==========================================================
off = cm.copy()
np.fill_diagonal(off, 0)
pairs = sorted(
    ((off[i, j], class_names[i], class_names[j])
     for i in range(NUM_CLASSES) for j in range(NUM_CLASSES) if off[i, j] > 0),
    reverse=True,
)[:10]
print("\nKesalahan terbanyak (sebenarnya -> prediksi):")
for n, a, b in pairs:
    print(f"  {a} -> {b}: {n}x")

with open(WRONG_PATH, "w", newline="", encoding="utf-8-sig") as f:
    w = csv.writer(f)
    w.writerow(["berkas", "kelas_sebenarnya", "kelas_prediksi", "keyakinan"])
    for path, t, p, c in zip(file_paths, true_labels, pred_labels, confidence):
        if t != p:
            w.writerow([path, class_names[t], class_names[p], f"{c:.3f}"])
print("Daftar prediksi salah:", WRONG_PATH)

if SHOW_PLOT:
    plt.show()