import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.models import Model, load_model
from tensorflow.keras.layers import Dense, Dropout, GlobalAveragePooling2D, BatchNormalization
from tensorflow.keras.applications import EfficientNetB0
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint, ReduceLROnPlateau
from tensorflow.keras.optimizers import Adam
import os

# === Konfigurasi dasar ===
IMG_SIZE = (224, 224)
BATCH_SIZE = 32
EPOCHS_STAGE1 = 20
EPOCHS_STAGE2 = 20
LR_STAGE1 = 1e-4
LR_STAGE2 = 1e-5

# === Path dataset ===
train_dir = "dataset/dataset_jadi/train_augmented"
valid_dir = "dataset/dataset_jadi/valid"

# Pastikan folder model ada
os.makedirs("model", exist_ok=True)

# === Data Generator ===
train_datagen = ImageDataGenerator(
    rescale=1./255,
    rotation_range=20,
    zoom_range=0.2,
    width_shift_range=0.1,
    height_shift_range=0.1,
    horizontal_flip=True
)

valid_datagen = ImageDataGenerator(rescale=1./255)

train_data = train_datagen.flow_from_directory(
    train_dir,
    target_size=IMG_SIZE,
    batch_size=BATCH_SIZE,
    class_mode='categorical',
    shuffle=True
)

valid_data = valid_datagen.flow_from_directory(
    valid_dir,
    target_size=IMG_SIZE,
    batch_size=BATCH_SIZE,
    class_mode='categorical',
    shuffle=False
)

# === Model Base EfficientNetB0 ===
base_model = EfficientNetB0(
    include_top=False,
    weights='imagenet',
    input_shape=IMG_SIZE + (3,)
)
base_model.trainable = False  # Tahap 1: hanya head layer yang dilatih

# === Head Layer ===
x = base_model.output
x = GlobalAveragePooling2D()(x)
x = BatchNormalization()(x)
x = Dense(512, activation='relu')(x)
x = Dropout(0.4)(x)
output = Dense(train_data.num_classes, activation='softmax')(x)

model = Model(inputs=base_model.input, outputs=output)

# === Compile Model (Stage 1) ===
model.compile(
    optimizer=Adam(learning_rate=LR_STAGE1),
    loss='categorical_crossentropy',
    metrics=['accuracy']
)

# === Callback ===
callbacks_stage1 = [
    ModelCheckpoint(
        "model/best_effnetb0_stage1.keras",
        monitor='val_accuracy',
        save_best_only=True,
        verbose=1
    ),
    EarlyStopping(
        monitor='val_loss',
        patience=6,
        restore_best_weights=True,
        verbose=1
    ),
    ReduceLROnPlateau(
        monitor='val_loss',
        factor=0.5,
        patience=3,
        min_lr=1e-6,
        verbose=1
    )
]

# === TRAINING STAGE 1 ===
print("\n🚀 Training Tahap 1 (Feature Extraction) Dimulai...\n")
history1 = model.fit(
    train_data,
    epochs=EPOCHS_STAGE1,
    validation_data=valid_data,
    callbacks=callbacks_stage1
)

# Simpan hasil stage 1
model.save("model/efficientnetb0_stage1.keras")
print("\n✅ Model tahap 1 selesai disimpan ke 'model/efficientnetb0_stage1.keras'\n")

# === TRAINING STAGE 2 (Fine-Tuning) ===
print("🔥 Training Tahap 2 (Fine-Tuning) Dimulai...\n")

# Unfreeze seluruh layer EfficientNet
for layer in model.layers:
    layer.trainable = True

# Compile ulang dengan learning rate lebih kecil
model.compile(
    optimizer=Adam(learning_rate=LR_STAGE2),
    loss='categorical_crossentropy',
    metrics=['accuracy']
)

# Callback tahap 2
callbacks_stage2 = [
    ModelCheckpoint(
        "model/best_effnetb0_final.keras",
        monitor='val_accuracy',
        save_best_only=True,
        verbose=1
    ),
    EarlyStopping(
        monitor='val_loss',
        patience=6,
        restore_best_weights=True,
        verbose=1
    ),
    ReduceLROnPlateau(
        monitor='val_loss',
        factor=0.5,
        patience=3,
        min_lr=1e-7,
        verbose=1
    )
]

history2 = model.fit(
    train_data,
    epochs=EPOCHS_STAGE2,
    validation_data=valid_data,
    callbacks=callbacks_stage2
)

# Simpan model final
model.save("model/efficientnetb0_final.keras")
print("\n✅ Model akhir (fine-tuned) selesai disimpan ke 'model/efficientnetb0_final.keras'\n")

print("🎯 Training selesai! Model siap digunakan untuk prediksi.")
