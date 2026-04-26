"""
Evaluasi Chatbot NLP - Confusion Matrix (Enhanced)
====================================================
Evaluasi menggunakan DATA UJI BARU yang tidak ada di intents.json
agar hasil lebih valid dan realistis.

Jalankan: python evaluate_chatbot.py
Output  : confusion_matrix.png + laporan di terminal
"""

import json
import pickle
import random
import numpy as np
import matplotlib
matplotlib.use("Agg")           # non-GUI backend agar bisa simpan tanpa display
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
import os

warnings.filterwarnings("ignore")

from nltk.stem import WordNetLemmatizer
from tensorflow.keras.models import load_model
from sklearn.metrics import (
    confusion_matrix,
    classification_report,
    accuracy_score,
)
import nltk

# ─────────────────────────────────────────────
# 1. Load model & artefak
# ─────────────────────────────────────────────
lemmatizer = WordNetLemmatizer()

MODEL_PATH   = "model/model.h5"
INTENTS_PATH = "dataset/intents.json"
WORDS_PATH   = "model/words.pkl"
CLASSES_PATH = "model/classes.pkl"

model   = load_model(MODEL_PATH)
intents = json.loads(open(INTENTS_PATH, encoding="utf-8").read())
words   = pickle.load(open(WORDS_PATH, "rb"))
classes = pickle.load(open(CLASSES_PATH, "rb"))

print(f"[OK] Model dimuat  : {MODEL_PATH}")
print(f"[OK] Jumlah kelas  : {len(classes)}")
print(f"[OK] Jumlah kata   : {len(words)}")

# ─────────────────────────────────────────────
# 2. Fungsi NLP (sama persis dengan chatbot)
# ─────────────────────────────────────────────
def clean_up_sentence(sentence):
    tokens = nltk.word_tokenize(sentence)
    return [lemmatizer.lemmatize(w.lower()) for w in tokens]

def bag_of_words(sentence):
    sentence_words = clean_up_sentence(sentence)
    bag = [0] * len(words)
    for s in sentence_words:
        for i, w in enumerate(words):
            if w == s:
                bag[i] = 1
    return np.array(bag)

def predict_class(sentence):
    bow = bag_of_words(sentence)
    res = model.predict(np.array([bow]), verbose=0)[0]
    ERROR_THRESHOLD = 0.25
    results = [[i, r] for i, r in enumerate(res) if r > ERROR_THRESHOLD]
    results.sort(key=lambda x: x[1], reverse=True)
    if not results:
        top_i = int(np.argmax(res))
        return classes[top_i]
    return classes[results[0][0]]

# ─────────────────────────────────────────────
# 3. Dataset uji BARU (kalimat yang TIDAK ADA di intents.json)
#    Setiap intent punya ~10 kalimat variasi baru
# ─────────────────────────────────────────────
TEST_DATA_UNSEEN = [
    # ── salam ──────────────────────────────────────────────────────────
    ("Hei, ada yang bisa bantu?",                "salam"),
    ("Permisi, bisa minta bantuan?",              "salam"),
    ("Halo bot, lagi bisa?",                      "salam"),
    ("Hai semuanya!",                             "salam"),
    ("Selamat malam",                             "salam"),
    ("Selamat sore",                              "salam"),
    ("Apa kabar hari ini?",                       "salam"),
    ("Halo, saya mau tanya-tanya",                "salam"),
    ("Hai, boleh minta tolong?",                  "salam"),
    ("Hei, masih aktif?",                         "salam"),

    # ── nasi_goreng ───────────────────────────────────────────────────
    ("Tolong ajarin bikin nasi goreng dong",      "nasi_goreng"),
    ("Nasi goreng kampung cara buatnya?",         "nasi_goreng"),
    ("Bagaimana membuat nasi goreng spesial?",    "nasi_goreng"),
    ("Pengen buat nasi goreng, mulai dari mana?", "nasi_goreng"),
    ("Cara masak nasi goreng yang enak?",         "nasi_goreng"),
    ("Nasi goreng rumahan resepnya apa?",         "nasi_goreng"),
    ("Bikin nasi goreng buat sarapan gimana?",    "nasi_goreng"),
    ("Tips masak nasi goreng biar gak lengket?",  "nasi_goreng"),
    ("Tutorial buat nasi goreng sederhana",       "nasi_goreng"),
    ("Nasi goreng enak bumbunya apa aja?",        "nasi_goreng"),

    # ── ayam_goreng ───────────────────────────────────────────────────
    ("Ayam goreng renyah gimana caranya?",        "ayam_goreng"),
    ("Pengen goreng ayam, bumbunya apa?",         "ayam_goreng"),
    ("Bagaimana cara menggoreng ayam biar matang merata?", "ayam_goreng"),
    ("Resep ayam goreng rumahan enak",            "ayam_goreng"),
    ("Cara buat ayam goreng kremes?",             "ayam_goreng"),
    ("Ayam goreng tepung cara bikinnya?",         "ayam_goreng"),
    ("Masak ayam goreng yang crispy gimana?",     "ayam_goreng"),
    ("Tutorial goreng ayam biar gak gosong",      "ayam_goreng"),
    ("Bumbu marinasi ayam goreng apa saja?",      "ayam_goreng"),
    ("Cara bikin ayam goreng kalasan?",           "ayam_goreng"),

    # ── soto_ayam ─────────────────────────────────────────────────────
    ("Cara buat soto bening ayam?",               "soto_ayam"),
    ("Soto ayam lamongan resepnya?",              "soto_ayam"),
    ("Bikin soto ayam buat makan siang gimana?",  "soto_ayam"),
    ("Bahan-bahan untuk soto ayam apa aja?",      "soto_ayam"),
    ("Cara masak soto kuning?",                   "soto_ayam"),
    ("Soto ayam sederhana cara membuatnya?",      "soto_ayam"),
    ("Pengen bikin soto ayam yang gurih",         "soto_ayam"),
    ("Resep kuah soto ayam biar bening?",         "soto_ayam"),
    ("Cara membuat soto ayam khas Jawa?",         "soto_ayam"),
    ("Soto ayam bumbunya apa saja ya?",           "soto_ayam"),

    # ── rendang ───────────────────────────────────────────────────────
    ("Cara membuat rendang daging?",              "rendang"),
    ("Rendang minang asli resepnya?",             "rendang"),
    ("Berapa lama masak rendang yang benar?",     "rendang"),
    ("Rendang kering bumbunya apa saja?",         "rendang"),
    ("Cara masak rendang biar empuk?",            "rendang"),
    ("Rendang sapi yang legit gimana bikinnya?",  "rendang"),
    ("Tutorial memasak rendang Padang",           "rendang"),
    ("Resep rendang ayam enak",                   "rendang"),
    ("Cara bikin rendang biar gak berair?",       "rendang"),
    ("Rendang yang enak masaknya berapa jam?",    "rendang"),

    # ── bahan_pengganti ───────────────────────────────────────────────
    ("Tidak punya ketumbar, bisa pakai apa?",     "bahan_pengganti"),
    ("Pengganti santan kelapa apa ya?",           "bahan_pengganti"),
    ("Kalau gak ada kemiri bisa diganti apa?",    "bahan_pengganti"),
    ("Alternatif kecap asin selain kecap?",       "bahan_pengganti"),
    ("Ganti bawang putih pakai apa?",             "bahan_pengganti"),
    ("Tidak ada daun salam, bisa pakai daun apa?","bahan_pengganti"),
    ("Pengganti gula aren untuk masak apa?",      "bahan_pengganti"),
    ("Bisa gak pakai susu evaporasi ganti santan?","bahan_pengganti"),
    ("Alternatif tepung terigu untuk gorengan?",  "bahan_pengganti"),
    ("Kalau gak punya jahe, gantinya apa?",       "bahan_pengganti"),

    # ── makanan_ringan ────────────────────────────────────────────────
    ("Cemilan mudah buat anak-anak apa ya?",      "makanan_ringan"),
    ("Bikin snack sehat di rumah gimana?",        "makanan_ringan"),
    ("Resep keripik singkong homemade",           "makanan_ringan"),
    ("Cara buat donat kentang yang empuk?",       "makanan_ringan"),
    ("Makanan ringan buat tamu mendadak?",        "makanan_ringan"),
    ("Resep cireng isi yang enak?",               "makanan_ringan"),
    ("Cara bikin bakwan sayur renyah?",           "makanan_ringan"),
    ("Camilan dari pisang selain pisang goreng?", "makanan_ringan"),
    ("Bikin tahu bulat crispy gimana?",           "makanan_ringan"),
    ("Resep onde-onde isi kacang hijau?",         "makanan_ringan"),

    # ── cari_resep ────────────────────────────────────────────────────
    ("Temukan resep dengan bahan ayam",           "cari_resep"),
    ("Cari masakan pakai daging sapi",            "cari_resep"),
    ("Ada resep yang pakai tahu tempe?",          "cari_resep"),
    ("Resep masakan Jawa apa saja?",              "cari_resep"),
    ("Cari resep yang gampang dibuat",            "cari_resep"),
    ("Tampilkan resep makanan Padang",            "cari_resep"),
    ("Resep apa yang cocok buat pemula?",         "cari_resep"),
    ("Cari resep masakan berkuah",                "cari_resep"),
    ("Ada resep yang pakai cabai?",               "cari_resep"),
    ("Cari resep masakan sederhana",              "cari_resep"),

    # ── cari_bahan ────────────────────────────────────────────────────
    ("Di kulkasku ada telur dan wortel",          "cari_bahan"),
    ("Aku cuma punya tempe sama bawang",          "cari_bahan"),
    ("Bisa masak apa dari tahu dan cabai?",       "cari_bahan"),
    ("Aku punya daging cincang dan tomat",        "cari_bahan"),
    ("Ada resep pakai kentang sama keju?",        "cari_bahan"),
    ("Masak apa kalau cuma ada mie dan telur?",   "cari_bahan"),
    ("Resep dari bahan ikan dan santan",          "cari_bahan"),
    ("Pakai bayam aja bisa masak apa?",           "cari_bahan"),
    ("Aku punya sisa nasi dan sayuran",           "cari_bahan"),
    ("Bahan di kulkas ada kentang dan wortel",    "cari_bahan"),

    # ── terimakasih ───────────────────────────────────────────────────
    ("Wah, makasih banyak ya!",                   "terimakasih"),
    ("Terima kasih banyak infonya",               "terimakasih"),
    ("Trims ya, sangat membantu!",                "terimakasih"),
    ("Makasih, resepnya mantap!",                 "terimakasih"),
    ("Terima kasih atas bantuannya",              "terimakasih"),
    ("Thanks a lot!",                             "terimakasih"),
    ("Makasih udah kasih resepnya",               "terimakasih"),
    ("Terimakasih sudah membantu saya",           "terimakasih"),
    ("Makasih infonya berguna banget",            "terimakasih"),
    ("Thx banyak ya bot!",                        "terimakasih"),

    # ── perpisahan ────────────────────────────────────────────────────
    ("Yaudah, pamit dulu ya",                     "perpisahan"),
    ("Oke, sampai nanti!",                        "perpisahan"),
    ("See you later!",                            "perpisahan"),
    ("Bye bye!",                                  "perpisahan"),
    ("Aku pergi dulu ya",                         "perpisahan"),
    ("Dah, makasih sudah bantu!",                 "perpisahan"),
    ("Sampai ketemu lagi",                        "perpisahan"),
    ("Good bye!",                                 "perpisahan"),
    ("Oke, selamat tinggal",                      "perpisahan"),
    ("Pamit ya, sampai jumpa lagi",               "perpisahan"),
]

# ─────────────────────────────────────────────
# 4. Dataset pola asli dari intents.json
# ─────────────────────────────────────────────
def build_training_data():
    X, y = [], []
    for intent in intents["intents"]:
        for pattern in intent["patterns"]:
            X.append(pattern)
            y.append(intent["tag"])
    return X, y

X_train, y_train = build_training_data()
X_unseen = [d[0] for d in TEST_DATA_UNSEEN]
y_unseen = [d[1] for d in TEST_DATA_UNSEEN]

print(f"\n[OK] Pola latih (intents.json) : {len(X_train)} sampel")
print(f"[OK] Data uji baru (unseen)    : {len(X_unseen)} sampel")

# ─────────────────────────────────────────────
# 5. Prediksi untuk dua set data
# ─────────────────────────────────────────────
def run_predictions(X):
    print(f"[..] Prediksi {len(X)} sampel...", end="", flush=True)
    preds = [predict_class(s) for s in X]
    print(" selesai.")
    return preds

y_pred_train  = run_predictions(X_train)
y_pred_unseen = run_predictions(X_unseen)

# ─────────────────────────────────────────────
# 6. Cetak laporan terminal
# ─────────────────────────────────────────────
def print_report(y_true, y_pred, label):
    acc = accuracy_score(y_true, y_pred)
    benar = sum(t == p for t, p in zip(y_true, y_pred))
    print("\n" + "=" * 65)
    print(f"  {label}")
    print("=" * 65)
    print(f"  Accuracy : {acc * 100:.2f}%   ({benar}/{len(y_true)} benar)")
    print("-" * 65)
    print(classification_report(y_true, y_pred, labels=classes, zero_division=0))

print_report(y_train,  y_pred_train,  "SET 1 -- Data Latih (intents.json)")
print_report(y_unseen, y_pred_unseen, "SET 2 -- Data Uji Baru (unseen)")

# ─────────────────────────────────────────────
# 7. Visualisasi 4 confusion matrix (2x2)
#    Baris atas  : Data Latih
#    Baris bawah : Data Uji Baru
# ─────────────────────────────────────────────
def make_cm(y_true, y_pred):
    cm = confusion_matrix(y_true, y_pred, labels=classes)
    cm_norm = cm.astype(float)
    row_sums = cm_norm.sum(axis=1, keepdims=True)
    row_sums[row_sums == 0] = 1
    return cm, cm_norm / row_sums

cm_tr,   cm_tr_n  = make_cm(y_train,  y_pred_train)
cm_un,   cm_un_n  = make_cm(y_unseen, y_pred_unseen)

n  = len(classes)
cs = max(0.6, 6.5 / n)
fs = max(9, n * cs)

fig, axes = plt.subplots(2, 2, figsize=(fs * 2 + 2, fs * 2 + 2))
fig.patch.set_facecolor("#0d1117")

BG   = "#0d1117"
TC   = "#e6edf3"
LC   = "#8b949e"
MONO = "DejaVu Sans Mono"

def hm(ax, data, title, cmap, fmt, vmax=None):
    fa = max(5, 8 - n // 9)
    sns.heatmap(
        data, ax=ax, annot=True, fmt=fmt, cmap=cmap,
        xticklabels=classes, yticklabels=classes,
        linewidths=0.25, linecolor="#161b22",
        square=True, cbar=True,
        vmin=0, vmax=vmax,
        annot_kws={"size": fa, "family": MONO},
    )
    ax.set_facecolor(BG)
    ax.set_title(title, color=TC, fontsize=11, fontweight="bold", pad=10)
    ax.set_xlabel("Prediksi", color=LC, fontsize=9, labelpad=6)
    ax.set_ylabel("Aktual",   color=LC, fontsize=9, labelpad=6)
    tf = max(6, 9 - n // 10)
    ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha="right", color=LC, fontsize=tf)
    ax.set_yticklabels(ax.get_yticklabels(), rotation=0,              color=LC, fontsize=tf)
    cb = ax.collections[0].colorbar
    cb.ax.yaxis.set_tick_params(color=LC, labelsize=7)
    plt.setp(cb.ax.yaxis.get_ticklabels(), color=LC)

hm(axes[0][0], cm_tr,   "Data Latih -- Jumlah",    "Blues",   "d",   vmax=None)
hm(axes[0][1], cm_tr_n, "Data Latih -- Recall",    "YlGn",    ".2f", vmax=1.0)
hm(axes[1][0], cm_un,   "Data Uji Baru -- Jumlah", "Purples", "d",   vmax=None)
hm(axes[1][1], cm_un_n, "Data Uji Baru -- Recall", "OrRd",    ".2f", vmax=1.0)

acc_tr = accuracy_score(y_train,  y_pred_train)
acc_un = accuracy_score(y_unseen, y_pred_unseen)

fig.suptitle(
    f"Evaluasi Chatbot NLP -- Confusion Matrix\n"
    f"Acc Data Latih: {acc_tr*100:.1f}%   |   "
    f"Acc Data Uji Baru: {acc_un*100:.1f}%   |   "
    f"Kelas: {n}   |   Total sampel: {len(y_train) + len(y_unseen)}",
    color=TC, fontsize=13, fontweight="bold", y=1.005,
)

plt.tight_layout()
OUT = "confusion_matrix.png"
plt.savefig(OUT, dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
print(f"\n[OK] Gambar disimpan --> {os.path.abspath(OUT)}")

# ─────────────────────────────────────────────
# 8. Detail prediksi yang salah
# ─────────────────────────────────────────────
wrong = [(s, t, p) for s, t, p in zip(X_unseen, y_unseen, y_pred_unseen) if t != p]
if wrong:
    print(f"\n[!] {len(wrong)} prediksi SALAH pada data uji baru:")
    print("-" * 65)
    for s, t, p in wrong:
        print(f"  Kalimat  : {s}")
        print(f"  Aktual   : {t}")
        print(f"  Prediksi : {p}")
        print()
else:
    print("\n[OK] Semua prediksi data uji baru benar!")