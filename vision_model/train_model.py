import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Dense, Dropout, GlobalAveragePooling2D, BatchNormalization, Input
from tensorflow.keras.optimizers import AdamW
from tensorflow.keras.applications import EfficientNetB0
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint, ReduceLROnPlateau
from sklearn.utils.class_weight import compute_class_weight
from tensorflow.keras.utils import load_img, img_to_array
import numpy as np
import os
import matplotlib.pyplot as plt
import random

# === SEED UNTUK REPRODUCIBILITY ===
SEED = 42
tf.random.set_seed(SEED)
np.random.seed(SEED)
random.seed(SEED)

# === PATH DATASET ===
base_dir = os.path.join(os.getcwd(), 'dataset')
train_dir = os.path.join(base_dir, 'train_augmented')
valid_dir = os.path.join(base_dir, 'valid')
test_dir = os.path.join(base_dir, 'test')

# === DATA GENERATOR ===
train_datagen = ImageDataGenerator(
    rescale=1./255,
    rotation_range=15,
    zoom_range=0.15,
    horizontal_flip=True,
    width_shift_range=0.1,
    height_shift_range=0.1,
    fill_mode='nearest'
)

valid_datagen = ImageDataGenerator(rescale=1./255)
test_datagen = ImageDataGenerator(rescale=1./255)

train_data = train_datagen.flow_from_directory(
    train_dir,
    target_size=(224, 224),
    batch_size=32,
    class_mode='categorical',
    shuffle=True,
    seed=SEED
)

valid_data = valid_datagen.flow_from_directory(
    valid_dir,
    target_size=(224, 224),
    batch_size=32,
    class_mode='categorical',
    shuffle=False
)

test_data = test_datagen.flow_from_directory(
    test_dir,
    target_size=(224, 224),
    batch_size=32,
    class_mode='categorical',
    shuffle=False
)

# === CLASS WEIGHTS (imbalance handling) ===
class_weights = compute_class_weight(
    class_weight='balanced',
    classes=np.unique(train_data.classes),
    y=train_data.classes
)
class_weights = dict(enumerate(class_weights))
print("\n📊 Class Weights:", class_weights)

# === BASE MODEL ===
input_tensor = Input(shape=(224, 224, 3))
base_model = EfficientNetB0(include_top=False, weights='imagenet', input_tensor=input_tensor)

# Freeze semua layer dulu
for layer in base_model.layers:
    layer.trainable = False

# === MODEL HEAD ===
x = base_model.output
x = GlobalAveragePooling2D()(x)
x = BatchNormalization()(x)
x = Dense(512, activation='relu')(x)
x = Dropout(0.4)(x)
x = Dense(256, activation='relu')(x)
x = Dropout(0.3)(x)
output = Dense(train_data.num_classes, activation='softmax')(x)

model = Model(inputs=base_model.input, outputs=output)

# === TRAINING SETUP (Tahap 1) ===
optimizer = AdamW(learning_rate=3e-4, weight_decay=1e-5)
model.compile(
    optimizer=optimizer,
    loss='categorical_crossentropy',
    metrics=['accuracy']
)

os.makedirs("model", exist_ok=True)
callbacks = [
    EarlyStopping(monitor='val_loss', patience=8, restore_best_weights=True, verbose=1),
    ModelCheckpoint("model/best_effnet_stage1.keras", monitor="val_accuracy", save_best_only=True, verbose=1),
    ReduceLROnPlateau(monitor='val_loss', factor=0.5, patience=3, min_lr=1e-6, verbose=1)
]

print("\n🚀 Mulai Training Tahap 1 (Feature Extraction)...\n")
history1 = model.fit(
    train_data,
    validation_data=valid_data,
    epochs=30,
    callbacks=callbacks,
    class_weight=class_weights
)

# === FINE-TUNING (Tahap 2) ===
for layer in base_model.layers[-100:]:
    layer.trainable = True  # buka sebagian layer belakang

fine_tune_optimizer = AdamW(learning_rate=1e-5, weight_decay=1e-6)
model.compile(
    optimizer=fine_tune_optimizer,
    loss='categorical_crossentropy',
    metrics=['accuracy']
)

callbacks_finetune = [
    EarlyStopping(monitor='val_loss', patience=10, restore_best_weights=True, verbose=1),
    ModelCheckpoint("model/best_effnet_finetuned.keras", monitor="val_accuracy", save_best_only=True, verbose=1),
    ReduceLROnPlateau(monitor='val_loss', factor=0.5, patience=4, min_lr=1e-7, verbose=1)
]

print("\n🔧 Mulai Training Tahap 2 (Fine-Tuning)...\n")
history2 = model.fit(
    train_data,
    validation_data=valid_data,
    epochs=40,
    callbacks=callbacks_finetune,
    class_weight=class_weights
)

# === SIMPAN MODEL FINAL ===
model.save("model/efficientnetb0_final.keras")
print("\n✅ Model selesai dilatih & disimpan ke 'model/efficientnetb0_final.keras'")

# === EVALUASI ===
test_loss, test_acc = model.evaluate(test_data)
print(f"\n📈 Akurasi Test: {test_acc:.4f} | Loss: {test_loss:.4f}")

# === VISUALISASI ===
def plot_history(hist1, hist2):
    acc = hist1.history['accuracy'] + hist2.history['accuracy']
    val_acc = hist1.history['val_accuracy'] + hist2.history['val_accuracy']
    loss = hist1.history['loss'] + hist2.history['loss']
    val_loss = hist1.history['val_loss'] + hist2.history['val_loss']

    plt.figure(figsize=(12, 5))
    plt.subplot(1, 2, 1)
    plt.plot(acc, label='Train Accuracy')
    plt.plot(val_acc, label='Validation Accuracy')
    plt.legend()
    plt.title('Accuracy')
    plt.subplot(1, 2, 2)
    plt.plot(loss, label='Train Loss')
    plt.plot(val_loss, label='Validation Loss')
    plt.legend()
    plt.title('Loss')
    plt.show()

plot_history(history1, history2)

# === PREDIKSI GAMBAR CONTOH ===
def predict_image(img_path):
    img = load_img(img_path, target_size=(224, 224))
    img_array = img_to_array(img) / 255.0
    img_array = np.expand_dims(img_array, axis=0)

    pred = model.predict(img_array)
    class_idx = np.argmax(pred[0])
    label = list(train_data.class_indices.keys())[class_idx]
    conf = np.max(pred[0])

    print(f"\n🖼️ {os.path.basename(img_path)} → {label} ({conf:.2f})")
    return {"label": label, "confidence": float(conf)}

if __name__ == "__main__":
    test_img = r"C:\Users\fikri\Downloads\telur.jpg"
    predict_image(test_img)
