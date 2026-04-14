import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.models import load_model
import numpy as np
import os

# === Path model dan dataset ===
MODEL_PATH = "model/efficientnetb0_final.keras"   # ubah ke model terbaikmu
TEST_DIR = "dataset/dataset_jadi/train_augmented"

# === Load model terbaik ===
print(f"📦 Memuat model dari: {MODEL_PATH}")
model = load_model(MODEL_PATH)

# === Data Generator untuk test ===
test_datagen = ImageDataGenerator(rescale=1./255)

test_data = test_datagen.flow_from_directory(
    TEST_DIR,
    target_size=(224, 224),
    batch_size=32,
    class_mode='categorical',
    shuffle=False   # penting supaya urutan label sama
)

# === Evaluasi performa ===
loss, acc = model.evaluate(test_data)
print("\n📊 HASIL EVALUASI TEST SET")
print(f"   • Akurasi Test : {acc * 100:.2f}%")
print(f"   • Loss Test    : {loss:.4f}")

# === Prediksi detail (opsional) ===
pred = model.predict(test_data)
pred_labels = np.argmax(pred, axis=1)
true_labels = test_data.classes

# === Confusion Matrix (opsional tapi berguna) ===
from sklearn.metrics import classification_report, confusion_matrix
import seaborn as sns
import matplotlib.pyplot as plt

class_names = list(test_data.class_indices.keys())

print("\n📋 Laporan Klasifikasi:")
print(classification_report(true_labels, pred_labels, target_names=class_names))

# === Visualisasi Confusion Matrix ===
cm = confusion_matrix(true_labels, pred_labels)
plt.figure(figsize=(12, 10))
sns.heatmap(cm, annot=False, cmap='Blues', xticklabels=class_names, yticklabels=class_names)
plt.title("Confusion Matrix (Test Set)")
plt.xlabel("Predicted Label")
plt.ylabel("True Label")
plt.tight_layout()
plt.show()