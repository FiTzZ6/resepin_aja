
import os
import json
import random
import pickle
import re
import numpy as np
import tensorflow as tf

from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout, Input
from tensorflow.keras.optimizers import SGD
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint

# ==================================================
# 1. KONFIGURASI
# ==================================================

#Seed Acak
SEED = 42

INTENTS_PATH = "dataset/intents.json"
MODEL_DIR = "model"

MODEL_PATH = os.path.join(MODEL_DIR, "model.keras")
WORDS_PATH = os.path.join(MODEL_DIR, "words.pkl")
CLASSES_PATH = os.path.join(MODEL_DIR, "classes.pkl")
HISTORY_PATH = os.path.join(MODEL_DIR, "training_history.pkl")

#Epoch Maksimum dan Batch Size
EPOCHS = 200
BATCH_SIZE = 5

#Data Validasi
VALIDATION_SPLIT = 0.15

random.seed(SEED)
np.random.seed(SEED)
tf.random.set_seed(SEED)

os.makedirs(MODEL_DIR, exist_ok=True)

# ==================================================
# 2. STEMMER SASTRAWI DAN NORMALISASI
# ==================================================

#Normalisasi
factory = StemmerFactory()
stemmer = factory.create_stemmer()

# Normalisasi kata informal ke bentuk yang lebih konsisten.
SLANG_MAP = {
    "gak": "tidak",
    "gk": "tidak",
    "ga": "tidak",
    "nggak": "tidak",
    "enggak": "tidak",
    "ndak": "tidak",
    "kagak": "tidak",
    "udah": "sudah",
    "dah": "sudah",
    "aja": "saja",
    "doang": "saja",
    "yg": "yang",
    "dgn": "dengan",
    "utk": "untuk",
    "gimana": "bagaimana",
    "gmna": "bagaimana",
    "knp": "kenapa",
    "kenapa": "kenapa",
    "apaan": "apa",
    "brp": "berapa",
    "makasih": "terima kasih",
    "makasi": "terima kasih",
    "trimakasih": "terima kasih",
    "terimakasih": "terima kasih",
    "pengen": "ingin",
    "pingin": "ingin",
    "bikinin": "buatkan",
    "buatin": "buatkan",
    "nyari": "cari",
    "nyariin": "carikan"
}

def clean_up_sentence(sentence):
    """
    Normalisasi teks bahasa Indonesia, tokenisasi sederhana,
    dan stemming menggunakan Sastrawi.
    Fungsi ini wajib digunakan juga saat inferensi.
    """
    sentence = str(sentence).lower().strip()

    # Hilangkan karakter selain huruf dan spasi.
    sentence = re.sub(r"[^a-zA-ZÀ-ÿ\s]", " ", sentence)

    # Pisahkan frasa hasil normalisasi menjadi kata-kata.
    tokens = sentence.split()
    normalized_tokens = []

    for token in tokens:
        token = SLANG_MAP.get(token, token)

        # Beberapa normalisasi menghasilkan lebih dari satu kata.
        for word in token.split():
            if not word:
                continue

            # Ubah kata berimbuhan menjadi kata dasar.
            word = stemmer.stem(word)

            if word:
                normalized_tokens.append(word)

    return normalized_tokens


# ==================================================
# 3. MEMBACA DATASET
# ==================================================
with open(INTENTS_PATH, "r", encoding="utf-8") as f:
    intents = json.load(f)

if "intents" not in intents or not intents["intents"]:
    raise ValueError("Dataset intents.json kosong atau tidak valid.")

words = []
classes = []
documents = []
seen_tags = set()

for intent in intents["intents"]:
    tag = intent.get("tag")
    patterns = intent.get("patterns", [])

    if not tag or not patterns:
        raise ValueError(f"Intent tidak lengkap: {intent}")

    if tag in seen_tags:
        raise ValueError(f"Tag intent duplikat: {tag}")

    seen_tags.add(tag)

    valid_pattern_count = 0

    for pattern in patterns:
        if not isinstance(pattern, str) or not pattern.strip():
            continue

        normalized = clean_up_sentence(pattern)

        if not normalized:
            continue

        words.extend(normalized)
        documents.append((normalized, tag))
        valid_pattern_count += 1

    if valid_pattern_count == 0:
        raise ValueError(
            f"Intent '{tag}' tidak memiliki pola kalimat valid."
        )

    classes.append(tag)

words = sorted(set(words))
classes = sorted(set(classes))

if not words or not documents:
    raise ValueError("Tidak ada pola kalimat valid untuk pelatihan.")

print(f"Jumlah intent       : {len(classes)}")
print(f"Jumlah pola kalimat : {len(documents)}")
print(f"Jumlah kosakata     : {len(words)}")

# ==================================================
# 4. MEMBENTUK BAG-OF-WORDS DAN LABEL ONE-HOT
# ==================================================
training = []

#Representasi Teks
for tokens, tag in documents:
    token_set = set(tokens)

    bag = [
        1 if word in token_set else 0
        for word in words
    ]

    output = [0] * len(classes)
    output[classes.index(tag)] = 1

    training.append((bag, output))

random.shuffle(training)

train_x = np.asarray(
    [item[0] for item in training],
    dtype=np.float32
)

train_y = np.asarray(
    [item[1] for item in training],
    dtype=np.float32
)

if len(train_x) < 2:
    raise ValueError(
        "Data terlalu sedikit untuk pelatihan dan validasi."
    )

# ==================================================
# 5. MEMBANGUN MODEL ANN
# ==================================================

#Arsitektur
model = Sequential([
    Input(shape=(len(words),)),
    Dense(128, activation="relu"),
    Dropout(0.5),
    Dense(64, activation="relu"),
    Dropout(0.5),
    Dense(len(classes), activation="softmax")
])

#Optimizer
optimizer = SGD(
    learning_rate=0.01,
    momentum=0.9,
    nesterov=True
)

#Loss Function
model.compile(
    optimizer=optimizer,
    loss="categorical_crossentropy",
    metrics=["accuracy"]
)

model.summary()

# ==================================================
# 6. CALLBACK DAN VALIDASI
# ==================================================
callbacks = [
    EarlyStopping(
        monitor="val_loss",
        patience=20,
        restore_best_weights=True,
        verbose=1
    ),
    ModelCheckpoint(
        filepath=MODEL_PATH,
        monitor="val_loss",
        save_best_only=True,
        verbose=1
    )
]

# ==================================================
# 7. PELATIHAN
# ==================================================

#Epoch Maksimum dan Batch Size
# dan Data Validasi
history = model.fit(
    train_x,
    train_y,
    epochs=EPOCHS,
    batch_size=BATCH_SIZE,
    validation_split=VALIDATION_SPLIT,
    shuffle=True,
    callbacks=callbacks,
    verbose=1
)

# Simpan bobot terbaik hasil pelatihan.
model.save(MODEL_PATH)

with open(WORDS_PATH, "wb") as f:
    pickle.dump(words, f)

with open(CLASSES_PATH, "wb") as f:
    pickle.dump(classes, f)

with open(HISTORY_PATH, "wb") as f:
    pickle.dump(history.history, f)

print("\nPelatihan chatbot selesai.")
print(f"Model       : {MODEL_PATH}")
print(f"Vocabulary  : {WORDS_PATH}")
print(f"Classes     : {CLASSES_PATH}")
print(f"History     : {HISTORY_PATH}")
print(f"Epoch aktual: {len(history.history['loss'])}")
print("\nContoh preprocessing:")
print("Input  : Saya ingin memasak makanan")
print("Output :", clean_up_sentence(
    "Saya ingin memasak makanan"
))