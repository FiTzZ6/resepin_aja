import os
import numpy as np
from tensorflow.keras.preprocessing.image import ImageDataGenerator, img_to_array, load_img, array_to_img

# === PATH DATASET ===
base_dir = os.path.join(os.getcwd(), 'dataset','dataset1', 'train')
augmented_dir = os.path.join(os.getcwd(), 'dataset','dataset1', 'train_augmented')

os.makedirs(augmented_dir, exist_ok=True)

# === SETUP AUGMENTASI ===
datagen = ImageDataGenerator(
    rotation_range=30,
    width_shift_range=0.2,
    height_shift_range=0.2,
    shear_range=0.15,
    zoom_range=0.3,
    horizontal_flip=True,
    brightness_range=[0.6, 1.4],
    fill_mode='nearest'
)

# === LOOP SETIAP KELAS ===
for class_name in os.listdir(base_dir):
    class_path = os.path.join(base_dir, class_name)
    save_path = os.path.join(augmented_dir, class_name)
    os.makedirs(save_path, exist_ok=True)

    images = [f for f in os.listdir(class_path) if f.lower().endswith(('jpg', 'jpeg', 'png'))]

    print(f"🧩 Augmenting class '{class_name}' ({len(images)} images)...")

    for img_name in images:
        img_path = os.path.join(class_path, img_name)
        img = load_img(img_path)
        x = img_to_array(img)
        x = np.expand_dims(x, axis=0)

        # Generate 4 variasi baru per gambar (jadi total 5x lipat)
        aug_iter = datagen.flow(x, batch_size=1, save_to_dir=save_path,
                                save_prefix='aug', save_format='jpg')
        for i in range(4):
            next(aug_iter)

print("✅ Augmentasi selesai! Gambar hasil disimpan di folder 'valid_augmented'")
