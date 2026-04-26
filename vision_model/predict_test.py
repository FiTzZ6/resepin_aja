import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.models import load_model
import numpy as np
import os

from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    accuracy_score,
    precision_score,
    recall_score,
    f1_score
)

import seaborn as sns
import matplotlib.pyplot as plt

# =========================
# PATH
# =========================
MODEL_PATH = "model/efficientnetb0_final.keras"
TEST_DIR = "dataset/dataset_jadi/test"

# =========================
# LOAD MODEL
# =========================
print(f"📦 Memuat model dari: {MODEL_PATH}")
model = load_model(MODEL_PATH)

# =========================
# DATA TEST
# =========================
test_datagen = ImageDataGenerator(rescale=1./255)

test_data = test_datagen.flow_from_directory(
    TEST_DIR,
    target_size=(224, 224),
    batch_size=32,
    class_mode='categorical',
    shuffle=False  # WAJIB untuk evaluasi
)

# =========================
# EVALUASI DASAR
# =========================
loss, acc = model.evaluate(test_data)

print("\n📊 HASIL EVALUASI TEST SET")
print(f"   • Akurasi Test : {acc * 100:.2f}%")
print(f"   • Loss Test    : {loss:.4f}")

# =========================
# PREDIKSI
# =========================
pred = model.predict(test_data)
pred_labels = np.argmax(pred, axis=1)
true_labels = test_data.classes

class_names = list(test_data.class_indices.keys())

# =========================
# METRIK LENGKAP
# =========================
accuracy = accuracy_score(true_labels, pred_labels)
precision = precision_score(true_labels, pred_labels, average='weighted')
recall = recall_score(true_labels, pred_labels, average='weighted')
f1 = f1_score(true_labels, pred_labels, average='weighted')

print("\n📊 METRIK EVALUASI MODEL")
print(f"   • Akurasi  : {accuracy * 100:.2f}%")
print(f"   • Precision: {precision * 100:.2f}%")
print(f"   • Recall   : {recall * 100:.2f}%")
print(f"   • F1-Score : {f1 * 100:.2f}%")

# =========================
# CLASSIFICATION REPORT
# =========================
print("\n📋 Laporan Klasifikasi:")
print(classification_report(true_labels, pred_labels, target_names=class_names))

# =========================
# CONFUSION MATRIX
# =========================
cm = confusion_matrix(true_labels, pred_labels)

plt.figure(figsize=(12, 10))
sns.heatmap(cm, annot=False, cmap='Blues',
            xticklabels=class_names,
            yticklabels=class_names)

plt.title("Confusion Matrix (Test Set)")
plt.xlabel("Predicted Label")
plt.ylabel("True Label")
plt.tight_layout()
plt.show()