
import csv
import os
import pickle
import re
import warnings
from collections import Counter
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from tensorflow.keras.models import load_model

warnings.filterwarnings("ignore")

# ============================================================
# 1. KONFIGURASI DAN PEMUATAN MODEL
# ============================================================
BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / "model" / "model.keras"
WORDS_PATH = BASE_DIR / "model" / "words.pkl"
CLASSES_PATH = BASE_DIR / "model" / "classes.pkl"

CM_PATH = BASE_DIR / "confusion_matrix.png"
REPORT_PATH = BASE_DIR / "classification_report.csv"
WRONG_PATH = BASE_DIR / "prediksi_salah.csv"

for path in (MODEL_PATH, WORDS_PATH, CLASSES_PATH):
    if not path.is_file():
        raise FileNotFoundError(
            f"File tidak ditemukan: {path}\n"
            "Pastikan file berada di folder chatbot/model dan jalankan program dari project yang benar."
        )

stemmer = StemmerFactory().create_stemmer()
model = load_model(str(MODEL_PATH))
with open(WORDS_PATH, "rb") as file:
    words = list(pickle.load(file))
with open(CLASSES_PATH, "rb") as file:
    classes = list(pickle.load(file))

print(f"[OK] Model dimuat   : {MODEL_PATH}")
print(f"[OK] Jumlah kelas   : {len(classes)}")
print(f"[OK] Jumlah kosakata: {len(words)}")

# ============================================================
# 2. PREPROCESSING HARUS SAMA DENGAN train.py
# ============================================================
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
    "nyariin": "carikan",
}


def clean_up_sentence(sentence):
    """Normalisasi dan stemming Bahasa Indonesia, identik dengan train.py."""
    sentence = str(sentence).lower().strip()
    sentence = re.sub(r"[^a-zA-ZÀ-ÿ\s]", " ", sentence)
    tokens = sentence.split()
    normalized_tokens = []

    for token in tokens:
        token = SLANG_MAP.get(token, token)
        for word in token.split():
            if not word:
                continue
            word = stemmer.stem(word)
            if word:
                normalized_tokens.append(word)

    return normalized_tokens


def bag_of_words(sentence):
    """Membentuk vektor biner sesuai urutan words.pkl."""
    sentence_words = set(clean_up_sentence(sentence))
    return np.asarray(
        [1.0 if word in sentence_words else 0.0 for word in words],
        dtype=np.float32,
    )


def predict_intent(sentence):
    """Mengembalikan intent dengan probabilitas softmax tertinggi dan confidence-nya."""
    vector = bag_of_words(sentence)
    probabilities = model.predict(vector.reshape(1, -1), verbose=0)[0]
    index = int(np.argmax(probabilities))
    return classes[index], float(probabilities[index])


# ============================================================
# 3. DATA UJI TERPISAH - 16 INTENT x 10 KALIMAT = 160
# ============================================================
TEST_DATA_UNSEEN = [
    # salam (10 kalimat)
    ('Hei, ada yang bisa bantu?', 'salam'),
    ('Permisi, bisa minta bantuan?', 'salam'),
    ('Halo bot, lagi bisa?', 'salam'),
    ('Hai semuanya!', 'salam'),
    ('Halo, saya baru membuka aplikasi ini', 'salam'),
    ('Pagi, asisten resep!', 'salam'),
    ('Apa kabar hari ini?', 'salam'),
    ('Halo, saya mau tanya-tanya', 'salam'),
    ('Hai, boleh minta tolong?', 'salam'),
    ('Hei, masih aktif?', 'salam'),

    # nasi_goreng (10 kalimat)
    ('Tolong ajarin bikin nasi goreng dong', 'nasi_goreng'),
    ('Nasi goreng kampung cara buatnya?', 'nasi_goreng'),
    ('Bagaimana membuat nasi goreng spesial?', 'nasi_goreng'),
    ('Pengen buat nasi goreng, mulai dari mana?', 'nasi_goreng'),
    ('Cara masak nasi goreng yang enak?', 'nasi_goreng'),
    ('Nasi goreng rumahan resepnya apa?', 'nasi_goreng'),
    ('Bikin nasi goreng buat sarapan gimana?', 'nasi_goreng'),
    ('Tips masak nasi goreng biar gak lengket?', 'nasi_goreng'),
    ('Tutorial buat nasi goreng sederhana', 'nasi_goreng'),
    ('Nasi goreng enak bumbunya apa aja?', 'nasi_goreng'),

    # ayam_goreng (10 kalimat)
    ('Ayam goreng renyah gimana caranya?', 'ayam_goreng'),
    ('Pengen goreng ayam, bumbunya apa?', 'ayam_goreng'),
    ('Bagaimana cara menggoreng ayam biar matang merata?', 'ayam_goreng'),
    ('Resep ayam goreng rumahan enak', 'ayam_goreng'),
    ('Cara buat ayam goreng kremes?', 'ayam_goreng'),
    ('Ayam goreng tepung cara bikinnya?', 'ayam_goreng'),
    ('Masak ayam goreng yang crispy gimana?', 'ayam_goreng'),
    ('Tutorial goreng ayam biar gak gosong', 'ayam_goreng'),
    ('Bumbu marinasi ayam goreng apa saja?', 'ayam_goreng'),
    ('Cara bikin ayam goreng kalasan?', 'ayam_goreng'),

    # soto_ayam (10 kalimat)
    ('Cara buat soto bening ayam?', 'soto_ayam'),
    ('Soto ayam lamongan resepnya?', 'soto_ayam'),
    ('Bikin soto ayam buat makan siang gimana?', 'soto_ayam'),
    ('Bahan-bahan untuk soto ayam apa aja?', 'soto_ayam'),
    ('Cara masak soto kuning?', 'soto_ayam'),
    ('Soto ayam sederhana cara membuatnya?', 'soto_ayam'),
    ('Pengen bikin soto ayam yang gurih', 'soto_ayam'),
    ('Resep kuah soto ayam biar bening?', 'soto_ayam'),
    ('Cara membuat soto ayam khas Jawa?', 'soto_ayam'),
    ('Soto ayam bumbunya apa saja ya?', 'soto_ayam'),

    # rendang (10 kalimat)
    ('Cara membuat rendang daging?', 'rendang'),
    ('Rendang minang asli resepnya?', 'rendang'),
    ('Berapa lama masak rendang yang benar?', 'rendang'),
    ('Rendang kering bumbunya apa saja?', 'rendang'),
    ('Cara masak rendang biar empuk?', 'rendang'),
    ('Rendang sapi yang legit gimana bikinnya?', 'rendang'),
    ('Tutorial memasak rendang Padang', 'rendang'),
    ('Resep rendang ayam enak', 'rendang'),
    ('Cara bikin rendang biar gak berair?', 'rendang'),
    ('Rendang yang enak masaknya berapa jam?', 'rendang'),

    # bahan_pengganti (10 kalimat)
    ('Tidak punya ketumbar, bisa pakai apa?', 'bahan_pengganti'),
    ('Pengganti santan kelapa apa ya?', 'bahan_pengganti'),
    ('Kalau gak ada kemiri bisa diganti apa?', 'bahan_pengganti'),
    ('Alternatif kecap asin selain kecap?', 'bahan_pengganti'),
    ('Ganti bawang putih pakai apa?', 'bahan_pengganti'),
    ('Tidak ada daun salam, bisa pakai daun apa?', 'bahan_pengganti'),
    ('Pengganti gula aren untuk masak apa?', 'bahan_pengganti'),
    ('Bisa gak pakai susu evaporasi ganti santan?', 'bahan_pengganti'),
    ('Alternatif tepung terigu untuk gorengan?', 'bahan_pengganti'),
    ('Kalau gak punya jahe, gantinya apa?', 'bahan_pengganti'),

    # makanan_ringan (10 kalimat)
    ('Cemilan mudah buat anak-anak apa ya?', 'makanan_ringan'),
    ('Bikin snack sehat di rumah gimana?', 'makanan_ringan'),
    ('Resep keripik singkong homemade', 'makanan_ringan'),
    ('Cara buat donat kentang yang empuk?', 'makanan_ringan'),
    ('Makanan ringan buat tamu mendadak?', 'makanan_ringan'),
    ('Resep cireng isi yang enak?', 'makanan_ringan'),
    ('Cara bikin bakwan sayur renyah?', 'makanan_ringan'),
    ('Camilan dari pisang selain pisang goreng?', 'makanan_ringan'),
    ('Bikin tahu bulat crispy gimana?', 'makanan_ringan'),
    ('Bagaimana meracik camilan berisi kacang hijau?', 'makanan_ringan'),

    # cari_resep (10 kalimat)
    ('Temukan resep dengan bahan ayam', 'cari_resep'),
    ('Cari masakan pakai daging sapi', 'cari_resep'),
    ('Ada resep yang pakai tahu tempe?', 'cari_resep'),
    ('Resep masakan Jawa apa saja?', 'cari_resep'),
    ('Cari resep yang gampang dibuat', 'cari_resep'),
    ('Tampilkan resep makanan Padang', 'cari_resep'),
    ('Resep apa yang cocok buat pemula?', 'cari_resep'),
    ('Cari resep masakan berkuah', 'cari_resep'),
    ('Ada resep yang pakai cabai?', 'cari_resep'),
    ('Cari resep masakan sederhana', 'cari_resep'),

    # cari_bahan (10 kalimat)
    ('Di kulkasku ada telur dan wortel', 'cari_bahan'),
    ('Aku cuma punya tempe sama bawang', 'cari_bahan'),
    ('Bisa masak apa dari tahu dan cabai?', 'cari_bahan'),
    ('Aku punya daging cincang dan tomat', 'cari_bahan'),
    ('Ada resep pakai kentang sama keju?', 'cari_bahan'),
    ('Masak apa kalau cuma ada mie dan telur?', 'cari_bahan'),
    ('Resep dari bahan ikan dan santan', 'cari_bahan'),
    ('Pakai bayam aja bisa masak apa?', 'cari_bahan'),
    ('Aku punya sisa nasi dan sayuran', 'cari_bahan'),
    ('Bahan di kulkas ada kentang dan wortel', 'cari_bahan'),

    # terimakasih (10 kalimat)
    ('Wah, makasih banyak ya!', 'terimakasih'),
    ('Terima kasih banyak infonya', 'terimakasih'),
    ('Trims ya, sangat membantu!', 'terimakasih'),
    ('Makasih, resepnya mantap!', 'terimakasih'),
    ('Terima kasih atas bantuannya', 'terimakasih'),
    ('Thanks a lot!', 'terimakasih'),
    ('Makasih udah kasih resepnya', 'terimakasih'),
    ('Terimakasih sudah membantu saya', 'terimakasih'),
    ('Makasih infonya berguna banget', 'terimakasih'),
    ('Thx banyak ya bot!', 'terimakasih'),

    # perpisahan (10 kalimat)
    ('Yaudah, pamit dulu ya', 'perpisahan'),
    ('Oke, sampai nanti!', 'perpisahan'),
    ('See you later!', 'perpisahan'),
    ('Bye bye!', 'perpisahan'),
    ('Aku pergi dulu ya', 'perpisahan'),
    ('Dah, makasih sudah bantu!', 'perpisahan'),
    ('Kita lanjut ngobrol di lain kesempatan ya', 'perpisahan'),
    ('Good bye!', 'perpisahan'),
    ('Oke, selamat tinggal', 'perpisahan'),
    ('Pamit ya, sampai jumpa lagi', 'perpisahan'),

    # rekomendasi_resep (10 kalimat)
    ('Masakan apa yang cocok untuk makan malam?', 'rekomendasi_resep'),
    ('Kasih ide menu buat keluarga hari ini', 'rekomendasi_resep'),
    ('Aku bingung mau masak apa', 'rekomendasi_resep'),
    ('Menu apa yang enak untuk akhir pekan?', 'rekomendasi_resep'),
    ('Sarankan hidangan untuk makan siang', 'rekomendasi_resep'),
    ('Ada ide masakan yang lezat?', 'rekomendasi_resep'),
    ('Beri saya pilihan masakan untuk hari ini', 'rekomendasi_resep'),
    ('Masakan apa yang sebaiknya aku coba?', 'rekomendasi_resep'),
    ('Tolong pilihkan menu buat besok', 'rekomendasi_resep'),
    ('Enaknya masak apa untuk keluarga?', 'rekomendasi_resep'),

    # resep_mudah (10 kalimat)
    ('Aku baru belajar memasak, mulai dari mana?', 'resep_mudah'),
    ('Ada menu yang tidak ribet dibuat?', 'resep_mudah'),
    ('Resep praktis untuk orang sibuk dong', 'resep_mudah'),
    ('Masakan sederhana dengan sedikit langkah apa?', 'resep_mudah'),
    ('Aku mau masak tanpa banyak persiapan', 'resep_mudah'),
    ('Hidangan apa yang gampang dibuat pemula?', 'resep_mudah'),
    ('Bisa kasih resep yang simpel?', 'resep_mudah'),
    ('Menu rumahan yang tidak merepotkan apa?', 'resep_mudah'),
    ('Aku ingin masak cepat dengan cara sederhana', 'resep_mudah'),
    ('Resep apa yang mudah diikuti?', 'resep_mudah'),

    # waktu_memasak (10 kalimat)
    ('Berapa menit untuk menyiapkan hidangan ini?', 'waktu_memasak'),
    ('Biasanya masakan itu matang berapa lama?', 'waktu_memasak'),
    ('Berapa lama waktu yang dibutuhkan untuk memasak?', 'waktu_memasak'),
    ('Kalau direbus perlu berapa menit?', 'waktu_memasak'),
    ('Kira-kira kapan makanan ini siap disajikan?', 'waktu_memasak'),
    ('Waktu memasak totalnya berapa lama?', 'waktu_memasak'),
    ('Berapa lama harus menggorengnya?', 'waktu_memasak'),
    ('Apa masakan ini bisa selesai dalam setengah jam?', 'waktu_memasak'),
    ('Berapa menit sampai dagingnya empuk?', 'waktu_memasak'),
    ('Berapa lama proses masak dari awal sampai selesai?', 'waktu_memasak'),

    # bantuan (10 kalimat)
    ('Bisakah kamu memaparkan kemampuanmu?', 'bantuan'),
    ('Bisa jelaskan cara menggunakan chatbot ini?', 'bantuan'),
    ('Fitur apa yang tersedia di sini?', 'bantuan'),
    ('Aku harus mengetik apa supaya bisa mulai?', 'bantuan'),
    ('Tolong pandu aku menggunakan aplikasi ini', 'bantuan'),
    ('Bagaimana cara mencari menu lewat chatbot?', 'bantuan'),
    ('Apa kegunaan asisten resep ini?', 'bantuan'),
    ('Bisa bantu aku memahami fitur-fiturnya?', 'bantuan'),
    ('Jelaskan hal yang dapat kamu bantu', 'bantuan'),
    ('Bagaimana memulai pencarian resep?', 'bantuan'),

    # tidak_paham (10 kalimat)
    ('Maksud jawabanmu itu apa?', 'tidak_paham'),
    ('Aku kurang mengerti penjelasan tadi', 'tidak_paham'),
    ('Jawaban itu membingungkan buatku', 'tidak_paham'),
    ('Bisa jelaskan dengan kata-kata lain?', 'tidak_paham'),
    ('Aku belum menangkap maksudnya', 'tidak_paham'),
    ('Apa maksud dari pesan tersebut?', 'tidak_paham'),
    ('Penjelasanmu masih kurang jelas', 'tidak_paham'),
    ('Aku tidak memahami yang kamu katakan', 'tidak_paham'),
    ('Boleh ulangi dengan lebih sederhana?', 'tidak_paham'),
    ('Aku masih bingung dengan jawaban itu', 'tidak_paham'),
]


# ============================================================
# 4. VALIDASI DATA UJI
# ============================================================
def validate_test_data():
    if len(TEST_DATA_UNSEEN) != 160:
        raise ValueError(
            f"Data uji harus 160 kalimat (16 intent x 10), ditemukan {len(TEST_DATA_UNSEEN)}."
        )

    labels = {tag for _, tag in TEST_DATA_UNSEEN}
    if len(labels) != 16:
        raise ValueError(f"Data uji harus mencakup 16 intent, ditemukan {len(labels)}.")

    counts = Counter(tag for _, tag in TEST_DATA_UNSEEN)
    wrong_counts = {tag: count for tag, count in counts.items() if count != 10}
    if wrong_counts:
        raise ValueError(f"Setiap intent harus punya 10 kalimat. Jumlah saat ini: {dict(counts)}")

    class_set = set(classes)
    if labels != class_set:
        raise ValueError(
            "Tag data uji tidak cocok dengan classes.pkl. "
            f"Tidak diuji: {sorted(class_set - labels)}; "
            f"tag tidak dikenal: {sorted(labels - class_set)}"
        )

    texts = [text.strip().casefold() for text, _ in TEST_DATA_UNSEEN]
    if len(texts) != len(set(texts)):
        duplicates = [text for text, n in Counter(texts).items() if n > 1]
        raise ValueError(f"Ada kalimat duplikat di data uji: {duplicates}")

    if model.output_shape[-1] != len(classes):
        raise ValueError(
            f"Output model ({model.output_shape[-1]}) tidak cocok dengan classes.pkl ({len(classes)})."
        )
    if model.input_shape[-1] != len(words):
        raise ValueError(
            f"Input model ({model.input_shape[-1]}) tidak cocok dengan words.pkl ({len(words)})."
        )

    print(f"[OK] Jumlah intent diuji : {len(labels)}")
    print(f"[OK] Jumlah data uji    : {len(TEST_DATA_UNSEEN)}")
    print("[OK] Data uji            : 10 kalimat untuk setiap intent")
    print("[CATATAN] Program tidak membaca intents.json; pastikan dataset uji tetap terpisah dari pola training.")


# ============================================================
# 5. EVALUASI
# ============================================================
def main():
    validate_test_data()

    X_test = [text for text, _ in TEST_DATA_UNSEEN]
    y_true = [tag for _, tag in TEST_DATA_UNSEEN]
    y_pred = []
    confidences = []

    print(f"[..] Memproses {len(X_test)} kalimat uji...", flush=True)
    for sentence in X_test:
        predicted, confidence = predict_intent(sentence)
        y_pred.append(predicted)
        confidences.append(confidence)
    print("[OK] Prediksi selesai.")

    accuracy = accuracy_score(y_true, y_pred)
    correct = sum(actual == predicted for actual, predicted in zip(y_true, y_pred))
    report_dict = classification_report(
        y_true,
        y_pred,
        labels=classes,
        zero_division=0,
        output_dict=True,
    )

    print("\n" + "=" * 72)
    print("EVALUASI CHATBOT NLP - DATA UJI BARU (UNSEEN)")
    print("=" * 72)
    print(f"Jumlah intent       : {len(classes)}")
    print(f"Jumlah kalimat uji  : {len(X_test)}")
    print(f"Prediksi benar      : {correct}/{len(X_test)}")
    print(f"Prediksi salah      : {len(X_test) - correct}/{len(X_test)}")
    print(f"Accuracy            : {accuracy * 100:.2f}%")
    print(f"Macro precision     : {report_dict['macro avg']['precision']:.4f}")
    print(f"Macro recall        : {report_dict['macro avg']['recall']:.4f}")
    print(f"Macro F1-score      : {report_dict['macro avg']['f1-score']:.4f}")
    print("\nCLASSIFICATION REPORT")
    print(classification_report(y_true, y_pred, labels=classes, zero_division=0, digits=4))

    # Simpan classification report ke CSV.
    with open(REPORT_PATH, "w", newline="", encoding="utf-8-sig") as file:
        writer = csv.writer(file)
        writer.writerow(["label", "precision", "recall", "f1-score", "support"])
        for label, metrics in report_dict.items():
            if isinstance(metrics, dict):
                writer.writerow([
                    label,
                    metrics.get("precision", ""),
                    metrics.get("recall", ""),
                    metrics.get("f1-score", ""),
                    metrics.get("support", ""),
                ])

    # Confusion matrix: jumlah prediksi dan recall per kelas.
    cm = confusion_matrix(y_true, y_pred, labels=classes)
    row_sums = cm.sum(axis=1, keepdims=True)
    cm_recall = np.divide(
        cm,
        row_sums,
        out=np.zeros_like(cm, dtype=float),
        where=row_sums != 0,
    )

    fig, axes = plt.subplots(1, 2, figsize=(24, 10))
    fig.suptitle(
        f"Evaluasi Intent Chatbot - 160 Data Uji | Accuracy: {accuracy * 100:.2f}%",
        fontsize=15,
        fontweight="bold",
        y=1.02,
    )
    sns.heatmap(
        cm,
        annot=True,
        fmt="d",
        cmap="Blues",
        xticklabels=classes,
        yticklabels=classes,
        linewidths=0.3,
        linecolor="white",
        annot_kws={"size": 8},
        ax=axes[0],
    )
    axes[0].set_title("Confusion Matrix - Jumlah")
    axes[0].set_xlabel("Intent Prediksi")
    axes[0].set_ylabel("Intent Aktual")

    sns.heatmap(
        cm_recall,
        annot=True,
        fmt=".2f",
        cmap="YlGn",
        vmin=0,
        vmax=1,
        xticklabels=classes,
        yticklabels=classes,
        linewidths=0.3,
        linecolor="white",
        annot_kws={"size": 8},
        ax=axes[1],
    )
    axes[1].set_title("Confusion Matrix - Recall per Intent")
    axes[1].set_xlabel("Intent Prediksi")
    axes[1].set_ylabel("Intent Aktual")

    for ax in axes:
        ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha="right", fontsize=8)
        ax.set_yticklabels(ax.get_yticklabels(), rotation=0, fontsize=8)
    plt.tight_layout()
    fig.savefig(CM_PATH, dpi=180, bbox_inches="tight")
    plt.close(fig)

    # Simpan prediksi salah ke CSV.
    wrong_rows = [
        (sentence, actual, predicted, round(confidence, 6))
        for sentence, actual, predicted, confidence in zip(X_test, y_true, y_pred, confidences)
        if actual != predicted
    ]
    with open(WRONG_PATH, "w", newline="", encoding="utf-8-sig") as file:
        writer = csv.writer(file)
        writer.writerow(["kalimat_uji", "intent_aktual", "intent_prediksi", "confidence_prediksi"])
        writer.writerows(wrong_rows)

    print("\nFILE OUTPUT")
    print(f"- Confusion matrix      : {CM_PATH}")
    print(f"- Classification report : {REPORT_PATH}")
    print(f"- Prediksi salah        : {WRONG_PATH}")
    print(f"\nJumlah salah prediksi: {len(wrong_rows)}")

    if wrong_rows:
        print("\nDETAIL PREDIKSI SALAH")
        print("-" * 72)
        for sentence, actual, predicted, confidence in wrong_rows:
            print(f"Kalimat  : {sentence}")
            print(f"Aktual   : {actual}")
            print(f"Prediksi : {predicted}")
            print(f"Confidence: {confidence:.4f}\n")
    else:
        print("[OK] Seluruh kalimat uji diprediksi dengan benar.")


if __name__ == "__main__":
    main()
