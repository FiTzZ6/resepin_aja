import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Dense, Dropout, GlobalAveragePooling2D, BatchNormalization
from tensorflow.keras.optimizers import AdamW
from tensorflow.keras.applications import EfficientNetB0
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint
from sklearn.utils.class_weight import compute_class_weight
import numpy as np
import os

# === SETUP DATASET PATH ===
base_dir = os.path.join(os.getcwd(), 'dataset')
train_dir = os.path.join(base_dir, 'train')
valid_dir = os.path.join(base_dir, 'valid')

# === DATA AUGMENTATION ===
train_datagen = ImageDataGenerator(
    rescale=1./255,
    rotation_range=25,
    width_shift_range=0.1,
    height_shift_range=0.1,
    shear_range=0.15,
    zoom_range=0.2,
    horizontal_flip=True,
    brightness_range=[0.7, 1.3],
    fill_mode='nearest'
)
valid_datagen = ImageDataGenerator(rescale=1./255)

# === LOAD DATA ===
train_data = train_datagen.flow_from_directory(
    train_dir,
    target_size=(224, 224),
    batch_size=32,
    class_mode='categorical',
    shuffle=True
)

valid_data = valid_datagen.flow_from_directory(
    valid_dir,
    target_size=(224, 224),
    batch_size=32,
    class_mode='categorical',
    shuffle=False
)

# === CLASS WEIGHTS ===
class_weights = compute_class_weight(
    class_weight='balanced',
    classes=np.unique(train_data.classes),
    y=train_data.classes
)
class_weights = dict(enumerate(class_weights))
print("Class Weights:", class_weights)

# === BASE MODEL ===
base_model = EfficientNetB0(
    input_shape=(224, 224, 3),
    include_top=False,
    weights='imagenet'
)
base_model.trainable = False  # Freeze dulu

# === BUILD MODEL ===
x = base_model.output
x = GlobalAveragePooling2D()(x)
x = Dense(512, activation='relu', kernel_regularizer=tf.keras.regularizers.l2(0.001))(x)
x = BatchNormalization()(x)
x = Dropout(0.4)(x)
x = Dense(256, activation='relu', kernel_regularizer=tf.keras.regularizers.l2(0.001))(x)
x = BatchNormalization()(x)
x = Dropout(0.3)(x)
output = Dense(train_data.num_classes, activation='softmax')(x)

model = Model(inputs=base_model.input, outputs=output)

# === OPTIMIZER & LR SCHEDULE ===
lr_schedule = tf.keras.optimizers.schedules.CosineDecayRestarts(
    initial_learning_rate=1e-4,
    first_decay_steps=10,
    t_mul=2.0,
    m_mul=0.8,
    alpha=1e-6
)
optimizer = AdamW(learning_rate=lr_schedule, weight_decay=1e-5)

model.compile(optimizer=optimizer,
              loss='categorical_crossentropy',
              metrics=['accuracy'])

# === CALLBACKS ===
callbacks = [
    EarlyStopping(monitor='val_loss', patience=10, restore_best_weights=True, verbose=1),
    ModelCheckpoint("model/best_model.keras", monitor="val_accuracy", save_best_only=True, verbose=1)
]

# === TRAINING TAHAP 1 (freeze base) ===
history = model.fit(
    train_data,
    validation_data=valid_data,
    epochs=20,
    callbacks=callbacks,
    class_weight=class_weights
)

# === FINE-TUNING TAHAP 2 ===
base_model.trainable = True
for layer in base_model.layers[:-60]:  # hanya buka 60 layer terakhir
    layer.trainable = False

fine_tune_optimizer = AdamW(learning_rate=1e-5, weight_decay=1e-6)
model.compile(optimizer=fine_tune_optimizer,
              loss='categorical_crossentropy',
              metrics=['accuracy'])

fine_tune_history = model.fit(
    train_data,
    validation_data=valid_data,
    epochs=30,
    callbacks=callbacks,
    class_weight=class_weights
)

# === SAVE FINAL MODEL ===
os.makedirs("model", exist_ok=True)
model.save("model/efficientnetb0_final.keras")

print("✅ Model EfficientNetB0 selesai dilatih & disimpan di 'model/efficientnetb0_final.keras'")
