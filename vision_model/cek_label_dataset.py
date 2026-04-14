import os
from collections import Counter
from tensorflow.keras.preprocessing.image import ImageDataGenerator

# === PATH DATASET ===
base_dir = os.path.join(os.getcwd(), 'dataset', 'dataset_jadi')
train_dir = os.path.join(base_dir, 'train_augmented')
valid_dir = os.path.join(base_dir, 'valid')
test_dir = os.path.join(base_dir, 'test')

# === DATA GENERATOR ===
datagen = ImageDataGenerator(rescale=1./255)

train_data = datagen.flow_from_directory(
    train_dir,
    target_size=(224, 224),
    batch_size=32,
    class_mode='categorical'
)

valid_data = datagen.flow_from_directory(
    valid_dir,
    target_size=(224, 224),
    batch_size=32,
    class_mode='categorical'
)

test_data = datagen.flow_from_directory(
    test_dir,
    target_size=(224, 224),
    batch_size=32,
    class_mode='categorical'
)

# === CEK LABEL + JUMLAH GAMBAR ===
def check_dataset_info(data_dir, data_flow, name):
    print(f"\n🧩 Dataset: {name}")
    print(f"Total class: {len(data_flow.class_indices)}")
    print("Class:", list(data_flow.class_indices.keys()))

    # Total gambar
    total_images = data_flow.samples
    print(f"Total gambar: {total_images}")

    # Jumlah gambar per class
    class_counts = Counter(data_flow.classes)
    idx_to_class = {v: k for k, v in data_flow.class_indices.items()}

    print("Distribusi gambar per class:")
    for class_idx, count in class_counts.items():
        print(f" - {idx_to_class[class_idx]}: {count}")

    # Cek folder yang tidak terbaca
    actual_folders = sorted(os.listdir(data_dir))
    read_labels = list(data_flow.class_indices.keys())

    missing_labels = [f for f in actual_folders if f not in read_labels]
    if missing_labels:
        print("⚠️ Folder tidak terbaca / kosong:", missing_labels)
    else:
        print("✅ Semua folder terbaca")

    return total_images

# === CEK SEMUA DATASET ===
train_total = check_dataset_info(train_dir, train_data, "TRAIN")
valid_total = check_dataset_info(valid_dir, valid_data, "VALIDATION")
test_total  = check_dataset_info(test_dir, test_data, "TEST")

# === PERBANDINGAN DATASET ===
total_all = train_total + valid_total + test_total

print("\n📊 Perbandingan Dataset:")
print(f"Train      : {train_total} ({train_total/total_all:.1%})")
print(f"Validation : {valid_total} ({valid_total/total_all:.1%})")
print(f"Test       : {test_total} ({test_total/total_all:.1%})")
print(f"Total      : {total_all}")
