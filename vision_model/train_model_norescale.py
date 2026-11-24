#MEMAKAI AUGMENTASI ONLINE TETAPI TIDAK MEMAKAI RESCALE


import os
import json
import random

import numpy as np
import tensorflow as tf
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from sklearn.metrics import classification_report, confusion_matrix
from tensorflow.keras import layers
from tensorflow.keras.models import Model
from tensorflow.keras.applications import EfficientNetB0, EfficientNetB2
from tensorflow.keras.callbacks import (
    EarlyStopping,
    ModelCheckpoint,
    ReduceLROnPlateau,
    CSVLogger,
)
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.regularizers import l2

# ==========================================================
# 1. KONFIGURASI
# ==========================================================
# "B0" = 224px (seperti sebelumnya). Ganti ke "B2" (260px) kalau setelah
# regularisasi di bawah akurasi validasi masih rendah.
BACKBONE = "B0"
BACKBONES = {
    "B0": (EfficientNetB0, (224, 224)),
    "B2": (EfficientNetB2, (260, 260)),
}
BACKBONE_CLS, IMG_SIZE = BACKBONES[BACKBONE]

BATCH_SIZE = 32
SEED = 42

EPOCHS_STAGE1 = 10
EPOCHS_STAGE2 = 30

LR_STAGE1 = 1e-3            # hanya head, backbone beku
LR_STAGE2 = 3e-5            # fine-tuning sebagian backbone
UNFREEZE_LAST_LAYERS = 100  # coba 80 / 100 / 150, bandingkan val_loss

LABEL_SMOOTHING = 0.1
MAX_GAP = 0.08              # selisih akurasi latih-validasi yang masih wajar

# peluang per batch: CutMix, MixUp, sisanya hanya augmentasi biasa
CUTMIX_PROB = 0.35
MIXUP_PROB = 0.35
MIXUP_ALPHA = 0.4

CEK_DUPLIKAT = True         # cek gambar valid yang mirip dengan gambar latih

random.seed(SEED)
np.random.seed(SEED)
tf.keras.utils.set_random_seed(SEED)

# ==========================================================
# 2. PATH
# ==========================================================
# SARAN: kalau punya folder gambar ASLI (tanpa augmentasi offline), pakai itu
# di sini. Augmentasi online di bawah sudah cukup, dan duplikat hasil augmentasi
# offline membuat model gampang menghafal.
# Folder "_bersih" dibuat oleh bersihkan_dataset.py (jalankan sekali sebelum training).
train_dir = "dataset/dataset_baru_7sep_bersih/train_augmentasi"
valid_dir = "dataset/dataset_baru_7sep_bersih/valid"

os.makedirs("model", exist_ok=True)

STAGE1_BEST = "model/best_effnetb0_baru_norescale_stage1.keras"
STAGE2_BEST = "model/best_effnetb0_baru_norescale_final.keras"
MODEL_FINAL = "model/efficientnetb0_baru_norescale.keras"
CLASS_INDEX_PATH = "model/class_indices_baru_norescale.json"
CURVE_PATH = "model/kurva_pelatihan_norescale.png"
REPORT_PATH = "model/laporan_klasifikasi_norescale.txt"
CM_PATH = "model/confusion_matrix_norescale.png"
DUP_PATH = "model/duplikat_valid_vs_train.txt"

IMG_EXT = (".jpg", ".jpeg", ".png", ".bmp", ".gif")

for d in (train_dir, valid_dir):
    if not os.path.isdir(d):
        raise FileNotFoundError(f"Folder tidak ditemukan: {d}")


def periksa_ekstensi(root):
    """Keras hanya membaca ekstensi di IMG_EXT dan mengabaikan sisanya
    tanpa peringatan (satu kelas bisa hilang). Cek di awal agar ketahuan."""
    n_kelas, tidak_didukung = 0, []
    for c in sorted(os.listdir(root)):
        folder = os.path.join(root, c)
        if not os.path.isdir(folder):
            continue
        n_kelas += 1
        for dp, _, names in os.walk(folder):
            for fn in names:
                if not fn.lower().endswith(IMG_EXT):
                    tidak_didukung.append(os.path.join(dp, fn))
    return n_kelas, tidak_didukung


N_DIR = {}
for d in (train_dir, valid_dir):
    N_DIR[d], bad = periksa_ekstensi(d)
    if bad:
        print(f"{len(bad)} berkas di {d} berekstensi tidak didukung, contoh:")
        for p in bad[:10]:
            print("  ", p)
        raise RuntimeError("Jalankan bersihkan_dataset.py lalu arahkan train_dir/valid_dir "
                           "ke folder hasilnya.")

# ==========================================================
# 3. DATA (tf.data, TANPA rescale=1./255)
# ==========================================================
# EfficientNet Keras sudah punya lapisan Rescaling/Normalization di dalam
# modelnya, jadi input harus piksel mentah 0-255 (float32).
AUTOTUNE = tf.data.AUTOTUNE


def load_ds(directory, shuffle):
    return tf.keras.utils.image_dataset_from_directory(
        directory,
        labels="inferred",
        label_mode="categorical",
        image_size=IMG_SIZE,
        batch_size=BATCH_SIZE,
        shuffle=shuffle,
        seed=SEED,
    )


raw_train = load_ds(train_dir, shuffle=True)
raw_valid = load_ds(valid_dir, shuffle=False)
raw_train_eval = load_ds(train_dir, shuffle=False)  # akurasi latih tanpa augmentasi

class_names = raw_train.class_names
if class_names != raw_valid.class_names:
    raise ValueError("Pemetaan kelas training dan validasi berbeda.")
NUM_CLASSES = len(class_names)
if NUM_CLASSES != N_DIR[train_dir] or NUM_CLASSES != N_DIR[valid_dir]:
    raise RuntimeError(
        f"Jumlah kelas terbaca ({NUM_CLASSES}) tidak sama dengan jumlah folder "
        f"(train {N_DIR[train_dir]}, valid {N_DIR[valid_dir]}). "
        "Ada kelas yang gambarnya tidak terbaca. Jalankan bersihkan_dataset.py."
    )

xb, _ = next(iter(raw_train))
print(f"Rentang piksel batch: {float(tf.reduce_min(xb)):.1f} - {float(tf.reduce_max(xb)):.1f}")
if float(tf.reduce_max(xb)) <= 1.5:
    raise RuntimeError("Piksel terlihat sudah diskalakan ke 0-1. Hapus rescale/pembagian 255.")

with open(CLASS_INDEX_PATH, "w", encoding="utf-8") as f:
    json.dump({n: i for i, n in enumerate(class_names)}, f, indent=4, ensure_ascii=False)

# bobot kelas (balanced) dari jumlah berkas per folder
counts = np.array([
    len([f for f in os.listdir(os.path.join(train_dir, c)) if f.lower().endswith(IMG_EXT)])
    for c in class_names
], dtype=np.float64)
cw = counts.sum() / (NUM_CLASSES * counts)
class_weight = {i: float(w) for i, w in enumerate(cw)}
n_train = int(counts.sum())
n_valid = sum(
    len([f for f in os.listdir(os.path.join(valid_dir, c)) if f.lower().endswith(IMG_EXT)])
    for c in class_names
)

print("\n==========================================")
print("Backbone          :", f"EfficientNet{BACKBONE} {IMG_SIZE}")
print("Jumlah kelas      :", NUM_CLASSES)
print("Gambar training   :", n_train)
print("Gambar validasi   :", n_valid)
print(f"Gambar/kelas      : min {int(counts.min())}, maks {int(counts.max())}")
print("rescale 1./255    : tidak digunakan")
print("==========================================\n")


# ----------------------------------------------------------
# Cek duplikat valid vs train (perceptual hash)
# ----------------------------------------------------------
def cek_kebocoran(ambang=4):
    import imagehash
    from PIL import Image

    def hash_dir(root):
        paths, hashes = [], []
        for c in class_names:
            folder = os.path.join(root, c)
            for fn in sorted(os.listdir(folder)):
                if not fn.lower().endswith(IMG_EXT):
                    continue
                p = os.path.join(folder, fn)
                try:
                    with Image.open(p) as im:
                        h = imagehash.phash(im.convert("RGB"))
                    paths.append(p)
                    hashes.append(h.hash.flatten().astype(np.float32))
                except Exception:
                    continue
        return paths, np.array(hashes)

    print("Mengecek duplikat valid vs train (beberapa menit)...")
    tp, th = hash_dir(train_dir)
    vp, vh = hash_dir(valid_dir)
    ham = vh @ (1.0 - th).T + (1.0 - vh) @ th.T  # jarak Hamming
    nearest = ham.min(axis=1)
    idx = ham.argmin(axis=1)
    dup = np.where(nearest <= ambang)[0]
    with open(DUP_PATH, "w", encoding="utf-8") as f:
        for i in dup:
            f.write(f"{vp[i]}  <->  {tp[idx[i]]}  (jarak {int(nearest[i])})\n")
    persen = 100.0 * len(dup) / max(len(vp), 1)
    print(f"Gambar valid yang mirip gambar latih: {len(dup)} dari {len(vp)} ({persen:.1f}%)")
    if len(dup) > 0:
        print(f"  Daftar: {DUP_PATH}")
        print("  Gambar ini membuat akurasi validasi tidak murni. Pindahkan/hapus dari valid.")
    print()


if CEK_DUPLIKAT:
    try:
        cek_kebocoran()
    except ImportError:
        print("Paket imagehash tidak ada, cek duplikat dilewati.\n")

# ----------------------------------------------------------
# Augmentasi + MixUp / CutMix (hanya untuk data latih)
# ----------------------------------------------------------
augment = tf.keras.Sequential([
    layers.RandomFlip("horizontal"),
    layers.RandomRotation(0.08, fill_mode="reflect"),
    layers.RandomZoom(0.25, fill_mode="reflect"),
    layers.RandomTranslation(0.12, 0.12, fill_mode="reflect"),
    layers.RandomContrast(0.25),
    layers.RandomBrightness(0.2, value_range=(0.0, 255.0)),
], name="augmentasi")


def sample_beta(alpha, shape):
    g1 = tf.random.gamma(shape, alpha)
    g2 = tf.random.gamma(shape, alpha)
    return g1 / (g1 + g2 + 1e-8)


def mixup(images, labels):
    b = tf.shape(images)[0]
    lam = sample_beta(MIXUP_ALPHA, [b])
    lam_x = tf.reshape(lam, [-1, 1, 1, 1])
    lam_y = tf.reshape(lam, [-1, 1])
    images = lam_x * images + (1.0 - lam_x) * tf.reverse(images, [0])
    labels = lam_y * labels + (1.0 - lam_y) * tf.reverse(labels, [0])
    return images, labels


def cutmix(images, labels):
    h = tf.shape(images)[1]
    w = tf.shape(images)[2]
    lam = tf.random.uniform([], 0.0, 1.0)
    ratio = tf.sqrt(1.0 - lam)
    cut_h = tf.cast(tf.cast(h, tf.float32) * ratio, tf.int32)
    cut_w = tf.cast(tf.cast(w, tf.float32) * ratio, tf.int32)
    cy = tf.random.uniform([], 0, h, dtype=tf.int32)
    cx = tf.random.uniform([], 0, w, dtype=tf.int32)
    y1 = tf.clip_by_value(cy - cut_h // 2, 0, h)
    y2 = tf.clip_by_value(cy + cut_h // 2, 0, h)
    x1 = tf.clip_by_value(cx - cut_w // 2, 0, w)
    x2 = tf.clip_by_value(cx + cut_w // 2, 0, w)
    ys = tf.range(h)[:, None]
    xs = tf.range(w)[None, :]
    mask = (ys >= y1) & (ys < y2) & (xs >= x1) & (xs < x2)
    mask = tf.cast(mask[None, :, :, None], images.dtype)
    images = images * (1.0 - mask) + tf.reverse(images, [0]) * mask
    area = tf.cast((y2 - y1) * (x2 - x1), tf.float32)
    lam_adj = 1.0 - area / tf.cast(h * w, tf.float32)
    labels = lam_adj * labels + (1.0 - lam_adj) * tf.reverse(labels, [0])
    return images, labels


def augment_and_mix(images, labels):
    images = augment(images, training=True)
    p = tf.random.uniform([])
    return tf.cond(
        p < CUTMIX_PROB,
        lambda: cutmix(images, labels),
        lambda: tf.cond(
            p < CUTMIX_PROB + MIXUP_PROB,
            lambda: mixup(images, labels),
            lambda: (images, labels),
        ),
    )


train_ds = raw_train.map(augment_and_mix, num_parallel_calls=AUTOTUNE).prefetch(AUTOTUNE)
valid_ds = raw_valid.prefetch(AUTOTUNE)
train_eval_ds = raw_train_eval.prefetch(AUTOTUNE)

# ==========================================================
# 4. MODEL
# ==========================================================
base_model = BACKBONE_CLS(
    include_top=False,
    weights="imagenet",
    input_shape=IMG_SIZE + (3,),
)
base_model.trainable = False

inputs = tf.keras.Input(shape=IMG_SIZE + (3,))
x = base_model(inputs, training=False)  # BatchNorm backbone tetap mode inferensi
x = layers.GlobalAveragePooling2D()(x)
x = layers.Dropout(0.4)(x)
x = layers.Dense(128, activation="relu", kernel_regularizer=l2(1e-3))(x)
x = layers.Dropout(0.5)(x)
outputs = layers.Dense(NUM_CLASSES, activation="softmax", kernel_regularizer=l2(1e-3))(x)
model = Model(inputs=inputs, outputs=outputs)

loss_fn = tf.keras.losses.CategoricalCrossentropy(label_smoothing=LABEL_SMOOTHING)


def make_callbacks(best_path, csv_path, min_lr, es_patience, lr_patience):
    return [
        ModelCheckpoint(best_path, monitor="val_loss", mode="min",
                        save_best_only=True, verbose=1),
        EarlyStopping(monitor="val_loss", mode="min", patience=es_patience,
                      restore_best_weights=True, verbose=1),
        ReduceLROnPlateau(monitor="val_loss", mode="min", factor=0.5,
                          patience=lr_patience, min_lr=min_lr, verbose=1),
        CSVLogger(csv_path),
    ]


# ==========================================================
# 5. TAHAP 1: FEATURE EXTRACTION
# ==========================================================
model.compile(optimizer=Adam(learning_rate=LR_STAGE1), loss=loss_fn, metrics=["accuracy"])

print("\n=== TAHAP 1: FEATURE EXTRACTION ===\n")
history1 = model.fit(
    train_ds,
    epochs=EPOCHS_STAGE1,
    validation_data=valid_ds,
    class_weight=class_weight,
    callbacks=make_callbacks(STAGE1_BEST, "model/riwayat_norescale_stage1.csv",
                             min_lr=1e-6, es_patience=4, lr_patience=2),
)
# EarlyStopping(restore_best_weights=True) sudah mengembalikan bobot terbaik di memori.

# ==========================================================
# 6. TAHAP 2: FINE-TUNING TERBATAS
# ==========================================================
print("\n=== TAHAP 2: FINE-TUNING TERBATAS ===\n")
base_model.trainable = True
for layer in base_model.layers:
    layer.trainable = False
for layer in base_model.layers[-UNFREEZE_LAST_LAYERS:]:
    if not isinstance(layer, tf.keras.layers.BatchNormalization):
        layer.trainable = True

print("Total layer backbone     :", len(base_model.layers))
print("Layer backbone dilatih   :", sum(1 for l in base_model.layers if l.trainable))

model.compile(optimizer=Adam(learning_rate=LR_STAGE2), loss=loss_fn, metrics=["accuracy"])

history2 = model.fit(
    train_ds,
    epochs=EPOCHS_STAGE2,
    validation_data=valid_ds,
    class_weight=class_weight,
    callbacks=make_callbacks(STAGE2_BEST, "model/riwayat_norescale_stage2.csv",
                             min_lr=1e-7, es_patience=7, lr_patience=3),
)

model.save(MODEL_FINAL)

# ==========================================================
# 7. LAPORAN OVERFITTING
# ==========================================================
# Catatan: "accuracy" selama training dihitung pada gambar yang sudah di-mix
# (MixUp/CutMix), jadi sengaja lebih rendah dan tidak sebanding dengan
# validasi. Perbandingan yang adil ada di bawah ini.
train_loss, train_acc = model.evaluate(train_eval_ds, verbose=0)
val_loss, val_acc = model.evaluate(valid_ds, verbose=0)
gap = train_acc - val_acc

print("\n==========================================")
print("TRAINING SELESAI")
print("==========================================")
print(f"Akurasi latih (tanpa augmentasi): {train_acc * 100:.2f}%")
print(f"Akurasi validasi                : {val_acc * 100:.2f}%")
print(f"Selisih latih - validasi        : {gap * 100:.2f} poin")
if gap > MAX_GAP:
    print("PERINGATAN: selisih besar, indikasi overfitting. Periksa laporan per kelas, "
          "pakai gambar asli (tanpa augmentasi offline), atau tambah data.")
else:
    print("Selisih masih wajar.")
print("Model final     :", MODEL_FINAL)
print("Pemetaan kelas  :", CLASS_INDEX_PATH)

# ==========================================================
# 8. ANALISIS PER KELAS
# ==========================================================
y_true = np.concatenate([np.argmax(y.numpy(), axis=1) for _, y in raw_valid])
y_prob = model.predict(valid_ds, verbose=0)
y_pred = np.argmax(y_prob, axis=1)

report = classification_report(y_true, y_pred, target_names=class_names, digits=3)
with open(REPORT_PATH, "w", encoding="utf-8") as f:
    f.write(report)
print("\n" + report)
print("Laporan klasifikasi:", REPORT_PATH)

cm = confusion_matrix(y_true, y_pred)
fig, ax = plt.subplots(figsize=(14, 12))
im = ax.imshow(cm, cmap="Blues")
ax.set_xticks(range(NUM_CLASSES))
ax.set_yticks(range(NUM_CLASSES))
ax.set_xticklabels(class_names, rotation=90, fontsize=7)
ax.set_yticklabels(class_names, fontsize=7)
ax.set_xlabel("Prediksi")
ax.set_ylabel("Sebenarnya")
ax.set_title("Confusion Matrix (validasi)")
fig.colorbar(im)
plt.tight_layout()
plt.savefig(CM_PATH, dpi=150)
plt.close(fig)
print("Confusion matrix   :", CM_PATH)

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

# ==========================================================
# 9. KURVA PELATIHAN
# ==========================================================
acc = history1.history["accuracy"] + history2.history["accuracy"]
vacc = history1.history["val_accuracy"] + history2.history["val_accuracy"]
ls = history1.history["loss"] + history2.history["loss"]
vls = history1.history["val_loss"] + history2.history["val_loss"]
split = len(history1.history["loss"])

fig, axes = plt.subplots(1, 2, figsize=(11, 4))
for ax, a, b, title in ((axes[0], acc, vacc, "Akurasi"), (axes[1], ls, vls, "Loss")):
    ax.plot(a, label="latih (di-mix)")
    ax.plot(b, label="validasi")
    ax.axvline(split - 0.5, color="gray", linestyle="--", label="awal tahap 2")
    ax.set_title(title)
    ax.set_xlabel("Epoch")
    ax.legend()
plt.tight_layout()
plt.savefig(CURVE_PATH, dpi=150)
print("Kurva pelatihan :", CURVE_PATH)