#TANPA AUGMENTASI DAN RESCALE


import os
import json
import tensorflow as tf

from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.models import Model, load_model
from tensorflow.keras.layers import (
    Dense,
    Dropout,
    GlobalAveragePooling2D,
    BatchNormalization
)
from tensorflow.keras.applications import EfficientNetB0
from tensorflow.keras.callbacks import (
    EarlyStopping,
    ModelCheckpoint,
    ReduceLROnPlateau
)
from tensorflow.keras.optimizers import Adam

# ==========================================================
# 1. KONFIGURASI DASAR
# ==========================================================

SEED = 42

#input
IMG_SIZE = (224, 224)
#loss dan optimzer
BATCH_SIZE = 32

EPOCHS_STAGE1 = 10
EPOCHS_STAGE2 = 15

LR_STAGE1 = 1e-4
LR_STAGE2 = 1e-5

tf.keras.utils.set_random_seed(SEED)

# ==========================================================
# 2. PATH DATASET DAN MODEL
# ==========================================================

train_dir = "dataset/dataset_baru_7sep_bersih/train_augmentasi"
valid_dir = "dataset/dataset_baru_7sep_bersih/valid"

os.makedirs("model", exist_ok=True)

# Nama file model dengan suffix tanpa augmentasi
STAGE1_MODEL_PATH = (
    "model/best_effnetb0_baru_stage1_tanpa_augmentasi.keras"
)

STAGE1_FINAL_PATH = (
    "model/efficientnetb0_baru_stage1_tanpa_augmentasi.keras"
)

BEST_MODEL_PATH = (
    "model/best_effnetb0_baru_final_tanpa_augmentasi.keras"
)

FINAL_MODEL_PATH = (
    "model/efficientnetb0_baru_final_tanpa_augmentasi.keras"
)

CLASS_PATH = (
    "model/class_indices_tanpa_augmentasi.json"
)

# Pastikan folder dataset tersedia
if not os.path.isdir(train_dir):
    raise FileNotFoundError(
        f"Folder training tidak ditemukan: {train_dir}"
    )

if not os.path.isdir(valid_dir):
    raise FileNotFoundError(
        f"Folder validasi tidak ditemukan: {valid_dir}"
    )

# ==========================================================
# 3. DATA GENERATOR TANPA RESCALE DAN AUGMENTASI
# ==========================================================

# Tidak menggunakan rescale, rotation, zoom, flip, dan sebagainya.

#input
train_datagen = ImageDataGenerator()
valid_datagen = ImageDataGenerator()

train_data = train_datagen.flow_from_directory(
    train_dir,
    target_size=IMG_SIZE,
    batch_size=BATCH_SIZE,
    class_mode="categorical",
    shuffle=True,
    seed=SEED
)

valid_data = valid_datagen.flow_from_directory(
    valid_dir,
    target_size=IMG_SIZE,
    batch_size=BATCH_SIZE,
    class_mode="categorical",
    shuffle=False
)

# Pastikan kelas training dan validasi konsisten
if train_data.class_indices != valid_data.class_indices:
    raise ValueError(
        "Nama atau urutan kelas train dan valid berbeda!"
    )

num_classes = train_data.num_classes

print("\nJumlah gambar training:", train_data.samples)
print("Jumlah gambar validasi:", valid_data.samples)
print("Jumlah kelas:", num_classes)
print("Daftar kelas:", train_data.class_indices)

# Simpan pemetaan kelas
with open(CLASS_PATH, "w", encoding="utf-8") as f:
    json.dump(
        train_data.class_indices,
        f,
        ensure_ascii=False,
        indent=4
    )

# ==========================================================
# 4. MEMBANGUN MODEL EFFICIENTNETB0
# ==========================================================

# arsitektur dasar
base_model = EfficientNetB0(
    include_top=False,
    weights="imagenet",
    input_shape=IMG_SIZE + (3,)
)

# Tahap 1: bekukan seluruh backbone

#Head Layer
base_model.trainable = False

x = base_model.output
x = GlobalAveragePooling2D()(x)
x = BatchNormalization()(x)

x = Dense(
    256,
    activation="relu",
    kernel_regularizer=tf.keras.regularizers.l2(1e-4)
)(x)

x = Dropout(0.5)(x)

output = Dense(
    num_classes,
    activation="softmax"
)(x)

model = Model(
    inputs=base_model.input,
    outputs=output
)

# ==========================================================
# 5. COMPILE STAGE 1
# ==========================================================

#loss dan optimzer
model.compile(
    optimizer=Adam(learning_rate=LR_STAGE1),
    loss="categorical_crossentropy",
    metrics=["accuracy"]
)

# ==========================================================
# 6. CALLBACK STAGE 1
# ==========================================================

callbacks_stage1 = [
    ModelCheckpoint(
        STAGE1_MODEL_PATH,
        monitor="val_loss",
        save_best_only=True,
        mode="min",
        verbose=1
    ),

    EarlyStopping(
        monitor="val_loss",
        patience=4,
        restore_best_weights=True,
        mode="min",
        verbose=1
    ),

    ReduceLROnPlateau(
        monitor="val_loss",
        factor=0.5,
        patience=2,
        min_lr=1e-7,
        mode="min",
        verbose=1
    )
]

# ==========================================================
# 7. TRAINING STAGE 1: FEATURE EXTRACTION
# ==========================================================

print("\n==========================================")
print("STAGE 1: FEATURE EXTRACTION")
print("==========================================\n")

history1 = model.fit(
    train_data,
    epochs=EPOCHS_STAGE1,
    validation_data=valid_data,
    callbacks=callbacks_stage1
)

# Muat model terbaik berdasarkan val_loss
model = load_model(STAGE1_MODEL_PATH)

# Simpan model terbaik Stage 1 dengan nama terpisah
model.save(STAGE1_FINAL_PATH)

print("\nModel Stage 1 tersimpan:")
print(STAGE1_FINAL_PATH)


# ==========================================================
# STAGE 2: FINE-TUNING TERBATAS
# ==========================================================

print("\n==========================================")
print("STAGE 2: FINE-TUNING")
print("==========================================\n")

# Muat checkpoint terbaik Stage 1
model = load_model(STAGE1_MODEL_PATH)

# Bekukan semua layer terlebih dahulu

#Lapisan Tahap 2
for layer in model.layers:
    layer.trainable = False

# Buka 20 layer terakhir untuk fine-tuning.
# BatchNormalization tetap dibekukan agar lebih stabil.
for layer in model.layers[-20:]:
    if not isinstance(
        layer,
        tf.keras.layers.BatchNormalization
    ):
        layer.trainable = True

print("Jumlah layer:", len(model.layers))
print(
    "Layer yang dapat dilatih:",
    sum(1 for layer in model.layers if layer.trainable)
)

# Compile ulang dengan learning rate lebih kecil
model.compile(
    optimizer=Adam(learning_rate=LR_STAGE2),
    loss="categorical_crossentropy",
    metrics=["accuracy"]
)


# ==========================================================
# 9. CALLBACK STAGE 2
# ==========================================================

callbacks_stage2 = [
    #ModelCheckpoint
    ModelCheckpoint(
        BEST_MODEL_PATH,
        monitor="val_loss",
        save_best_only=True,
        mode="min",
        verbose=1
    ),

#EarlyStopping
    EarlyStopping(
        monitor="val_loss",
        patience=4,
        restore_best_weights=True,
        mode="min",
        verbose=1
    ),

#reduceLROnPlateau
    ReduceLROnPlateau(
        monitor="val_loss",
        factor=0.5,
        patience=2,
        min_lr=1e-7,
        mode="min",
        verbose=1
    )
]

# ==========================================================
# 10. TRAINING STAGE 2
# ==========================================================

history2 = model.fit(
    train_data,
    epochs=EPOCHS_STAGE2,
    validation_data=valid_data,
    callbacks=callbacks_stage2
)

# ==========================================================
# 11. SIMPAN MODEL TERBAIK STAGE 2
# ==========================================================

best_model = load_model(BEST_MODEL_PATH)

best_model.save(FINAL_MODEL_PATH)

print("\n==========================================")
print("TRAINING SELESAI")
print("==========================================")

print("\nModel terbaik Stage 1:")
print(STAGE1_FINAL_PATH)

print("\nModel terbaik Stage 2:")
print(FINAL_MODEL_PATH)

print("\nFile pemetaan kelas:")
print(CLASS_PATH)

print("\nModel siap digunakan untuk prediksi.")
