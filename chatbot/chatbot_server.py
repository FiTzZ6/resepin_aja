from flask import Flask, request, jsonify
from tensorflow.keras.models import load_model
import nltk, numpy as np, json, pickle, random
import sys,os


# Tambahkan path vision_model supaya bisa diimport
sys.path.append(os.path.join(os.path.dirname(__file__), "../vision_model"))

from predict_image import predict_food_image
from nltk.stem import WordNetLemmatizer
import mysql.connector
import re
import datetime


app = Flask(__name__)
lemmatizer = WordNetLemmatizer()

# --- Load model dan data NLP ---
MODEL_PATH = os.path.join(os.path.dirname(__file__), "model", "model.h5")
try:
    model = load_model(MODEL_PATH)
    print("Model berhasil dimuat!")
except Exception as e:
    model = None
    print(f"Error saat load model: {e}")
intents = json.loads(open("dataset/intents.json", encoding="utf-8").read())
words = pickle.load(open("model/words.pkl", "rb"))
classes = pickle.load(open("model/classes.pkl", "rb"))

# --- Koneksi MySQL ---
db = mysql.connector.connect(
    host="localhost", user="root", password="", database="resepin_aja"
)
cursor = db.cursor(dictionary=True)


# ---------------------
# Fungsi Bantu NLP
# ---------------------
def clean_up_sentence(sentence):
    sentence_words = nltk.word_tokenize(sentence)
    sentence_words = [lemmatizer.lemmatize(word.lower()) for word in sentence_words]
    return sentence_words


def bag_of_words(sentence, words):
    sentence_words = clean_up_sentence(sentence)
    bag = [0] * len(words)
    for s in sentence_words:
        for i, w in enumerate(words):
            if w == s:
                bag[i] = 1
    return np.array(bag)


def predict_class(sentence):
    bow = bag_of_words(sentence, words)
    res = model.predict(np.array([bow]))[0]
    ERROR_THRESHOLD = 0.25
    results = [[i, r] for i, r in enumerate(res) if r > ERROR_THRESHOLD]
    results.sort(key=lambda x: x[1], reverse=True)
    return [{"intent": classes[r[0]], "probability": str(r[1])} for r in results]


# ---------------------
# Ekstraksi bahan dari kalimat
# ---------------------
def extract_ingredients_from_message(msg):
    # Contoh input: "aku punya telur, bawang putih dan ayam"
    msg = msg.lower()

    # Pisah dulu berdasarkan koma
    parts = re.split(r"[,\n]", msg)

    bahan_list = []
    stopwords = [
        "aku",
        "saya",
        "punya",
        "bahan",
        "ada",
        "pakai",
        "gunakan",
        "menggunakan",
        "dan",
        "dengan",
        "yang",
        "nih",
        "ini",
    ]

    for part in parts:
        words = re.findall(r"[a-zA-Z0-9]+", part)
        words = [w for w in words if w not in stopwords]

        if len(words) > 0:
            bahan_list.append(" ".join(words))  # contoh: "bawang putih"

    return bahan_list


# ---------------------
# Cari resep dari bahan (lebih akurat + partial)
# ---------------------
def cari_resep_dari_bahan(bahan_list):
    bahan_list = [b.strip().lower() for b in bahan_list if b.strip()]
    if not bahan_list:
        return "http://localhost:8000/resepcari"

    exists_clauses = []
    params = []

    for bahan in bahan_list:
        # Ambil kata pertama sebagai bahan utama, contoh: 'telur ayam' -> 'telur'
        kata_utama = bahan.split()[0]

        exists_clauses.append(
            """
            EXISTS (
                SELECT 1 FROM bahan_resep br
                WHERE br.id_resep = r.id_resep
                AND (
                    LOWER(br.nama_bahan) = %s
                    OR LOWER(br.nama_bahan) LIKE %s
                )
            )
        """
        )
        params.append(kata_utama)  # exact match (telur)
        params.append(f"{kata_utama} %")  # like match (telur ayam, telur bebek, dsb)

    where_clause = " AND ".join(exists_clauses)
    query = f"""
        SELECT r.id_resep, r.judul
        FROM resep r
        WHERE {where_clause}
    """

    cursor.execute(query, params)
    results = cursor.fetchall()

    if results:
        resep_ids = [str(r["id_resep"]) for r in results]
        return f"http://localhost:8000/resepcari?ids={','.join(resep_ids)}"

    return "http://localhost:8000/resepcari?bahan_not_found=1"


# ---------------------
# Parser kombinasi kompleks: users, bahan, rating, kata khusus (terenak)
# ---------------------
def parse_combination_filters(msg):
    """
    Mengembalikan dict dengan kunci opsional:
      - users: list of usernames (strings)
      - bahan: list of bahan (strings)
      - min_rating: int
      - max_rating: int
      - sort: 'rating_desc' atau lainnya
    """
    out = {
        "users": [],
        "bahan": [],
        "min_rating": None,
        "max_rating": None,
        "sort": None,
    }

    text = msg.lower()

    # 1) Cari frasa user: "dari fikri dan athar", "dari fikri, athar"
    user_match = re.search(r"(?:dari|oleh|milik)\s+([a-z0-9_\-\s, dan&]+)", text)
    if user_match:
        raw = user_match.group(1)
        # split by 'dan', ',', '&'
        users = re.split(r"\s*(?:dan|,|&)\s*", raw)
        users = [u.strip() for u in users if u.strip()]
        out["users"] = users

    # 2) Cari bahan: patterns after 'yang bahannya', 'yang bahannya ayam', 'pakai', 'punya'
    bahan_match = re.search(
        r"(?:yang\s+bahannya|yang\s+pakai|yang\s+menggunakan|pakai|punya|dengan)\s+([a-z0-9_\-\s, dan&]+)",
        text,
    )
    if bahan_match:
        raw_bahan = bahan_match.group(1)
        bahan_list = re.split(r"\s*(?:dan|,|&)\s*", raw_bahan)
        bahan_list = [b.strip() for b in bahan_list if b.strip()]
        out["bahan"] = bahan_list
    else:
        # fallback: cek ada kata 'ayam', 'telur' langsung disebutkan tanpa kata kunci
        # gunakan extract_ingredients_from_message sebagai fallback
        if any(
            k in text
            for k in ["ayam", "telur", "bawang", "tahu", "tempe", "daging", "ikan"]
        ):
            ext = extract_ingredients_from_message(text)
            if ext:
                out["bahan"] = ext

    # 3) Rating: "rating 4 ke atas", "rating minimal 3", "rating 3-5", "rating 4+"
    # pola range
    range_match = re.search(r"rating\s*(\d+)\s*[-–]\s*(\d+)", text)
    if range_match:
        out["min_rating"] = int(range_match.group(1))
        out["max_rating"] = int(range_match.group(2))
    else:
        # pola 'rating X ke atas' / 'rating minimal X' / 'rating X+'
        up_match = re.search(
            r"rating\s*(\d+)\s*(?:ke\s*atas|keatas|minimal|minimalnya|lebih\s*dari|>)|\brating\s*(\d+)\s*\+",
            text,
        )
        if up_match:
            # group may have None
            val = up_match.group(1) or up_match.group(2)
            if val:
                out["min_rating"] = int(val)
                out["max_rating"] = 5

        # pola 'rating di atas X' (strict greater than)
        above_match = re.search(r"rating\s*di\s*atas\s*(\d+)", text)
        if above_match:
            out["min_rating"] = int(above_match.group(1)) + 1
            out["max_rating"] = 5

    # 4) Kata kunci 'terenak' atau 'terbaik' -> prioritaskan rating tinggi
    if "terenak" in text or "terbaik" in text or "paling enak" in text:
        # set minimal rating 4 sebagai default jika belum ada rating
        if not out["min_rating"]:
            out["min_rating"] = 4
        out["sort"] = "rating_desc"

    return out


# ---------------------
# Respon utama chatbot
# ---------------------
def get_response(ints, intents_json, user_message):
    msg_lower = user_message.lower()

    # -----------------------------
    # 1) Cek kombinasi kompleks dulu (users, bahan, rating, sort)
    # -----------------------------
    combo = parse_combination_filters(msg_lower)
    if combo["users"] or combo["bahan"] or combo["min_rating"] or combo["max_rating"]:
        params = []

        # Users
        if combo["users"]:
            for u in combo["users"]:
                params.append(("user_resep[]", u))

        # Bahan (bersihkan kata 'rating' & angka)
        if combo["bahan"]:
    # Bersihkan kata-kata umum & ekstrak bahan utama
            cleaned_bahan = []
            for b in combo["bahan"]:
                extracted = extract_ingredients_from_message(b)
                if extracted:
                    cleaned_bahan.extend(extracted)
            if cleaned_bahan:
                params.append(("cari_bahan", ",".join(cleaned_bahan)))

        # Rating
        if combo["min_rating"] is not None:
            params.append(("min_rating", str(combo["min_rating"])))
        if combo["max_rating"] is not None:
            params.append(("max_rating", str(combo["max_rating"])))

        # Sort
        if combo["sort"]:
            params.append(("sort", combo["sort"]))

        # Build query
        query_parts = []
        for k, v in params:
            encoded_value = v.replace(" ", "%20")
            query_parts.append(f"{k}={encoded_value}")
        query = "&".join(query_parts)

        if not query:
            return {"type": "text", "message": "Maaf, saya tidak menemukan filter yang valid."}

        return {
            "type": "redirect",
            "message": "Menampilkan resep sesuai kombinasi filter kamu... 🍽️",
            "url": f"http://localhost:8000/resepcari?{query}",
        }

    # -----------------------------
    # 2) Cek rating range spesifik: "rating 2-4"
    # -----------------------------
    rating_range_match = re.search(r"rating\s*(\d+)\s*-\s*(\d+)", msg_lower)
    if rating_range_match:
        start, end = int(rating_range_match.group(1)), int(rating_range_match.group(2))
        rating_query = "&".join([f"rating[]={r}" for r in range(start, end + 1)])
        return {
            "type": "redirect",
            "message": f"Menampilkan resep dengan rating {start}-{end} ⭐",
            "url": f"http://localhost:8000/resepcari?{rating_query}",
        }

    # -----------------------------
    # 3) Cek rating tinggi / terendah
    # -----------------------------
    if any(kw in msg_lower for kw in ["rating tinggi", "terbaik", "bintang tinggi", "terfavorit"]):
        return {
            "type": "redirect",
            "message": "Menampilkan resep dengan rating tinggi (3-5) 🌟",
            "url": "http://localhost:8000/resepcari?sort=rating_desc&min_rating=3&max_rating=5",
        }

    if "rating terendah" in msg_lower:
        return {
            "type": "redirect",
            "message": "Menampilkan resep dengan rating terendah (0-2) 🌟",
            "url": "http://localhost:8000/resepcari?rating_lowest=1",
        }

    # -----------------------------
    # 4) Cek bahan yang disebut (pastikan bukan rating)
    # -----------------------------
    if any(kw in msg_lower for kw in ["punya", "bahan", "ada", "pakai", "menggunakan"]) and "rating" not in msg_lower:
        bahan = extract_ingredients_from_message(msg_lower)
        if bahan:
            query_bahan = ",".join(bahan)
            return {
                "type": "redirect",
                "message": f"Mencarikan resep dengan bahan: {', '.join(bahan)}...",
                "url": f"http://localhost:8000/resepcari?cari_bahan={query_bahan}",
            }

    # -----------------------------
    # 5) Cek kategori (minuman, snack, dessert, dll)
    # -----------------------------
    kategori_keywords = {
        "makanan ringan": "Makanan Ringan",
        "makanan berat": "Makanan Berat",
        "minuman": "Minuman",
        "snack": "Snack",
        "dessert": "Dessert",
    }
    for kw, ktg in kategori_keywords.items():
        if kw in msg_lower:
            return {
                "type": "redirect",
                "message": f"Menampilkan resep kategori {ktg} 🍽️",
                "url": f"http://localhost:8000/resepcari?ktg_masak[]={ktg}",
            }

    # -----------------------------
    # 6) Cek waktu memasak tercepat / terlama
    # -----------------------------
    if any(kw in msg_lower for kw in ["tercepat", "waktu cepat", "masak cepat", "cepat"]):
        return {
            "type": "redirect",
            "message": "Menampilkan resep dengan waktu memasak tercepat (0-15 menit) ⏱️",
            "url": "http://localhost:8000/resepcari?tgl_masak[]=cepat",
        }

    if any(kw in msg_lower for kw in ["terlama", "lama", "waktu lama", "masak lama"]):
        return {
            "type": "redirect",
            "message": "Menampilkan resep dengan waktu memasak terlama (>15 menit) ⏳",
            "url": "http://localhost:8000/resepcari?tgl_masak[]=lama",
        }

    # -----------------------------
    # 7) Cek rekomendasi (pagi, malam, mudah, random)
    # -----------------------------
    if any(kw in msg_lower for kw in ["rekomendasi", "saran", "makan apa", "dimakan", "siang", "malam", "pagi"]):
        current_hour = datetime.datetime.now().hour
        if "pagi" in msg_lower:
            waktu = "pagi"
        elif "siang" in msg_lower:
            waktu = "siang"
        elif "sore" in msg_lower:
            waktu = "sore"
        elif "malam" in msg_lower:
            waktu = "malam"
        else:
            if 5 <= current_hour < 7:
                waktu = "pagi"
            elif 11 <= current_hour < 15:
                waktu = "siang"
            elif 15 <= current_hour < 18:
                waktu = "sore"
            else:
                waktu = "malam"

        if "mudah" in msg_lower or "gampang" in msg_lower:
            cursor.execute(
                """
                SELECT r.id_resep, r.judul
                FROM resep r
                JOIN bahan_resep br ON r.id_resep = br.id_resep
                WHERE r.wkt_masak <= 15
                AND (r.ktg_masak LIKE %s)
                GROUP BY r.id_resep
                HAVING COUNT(br.id_bahan) <= 4
                ORDER BY RAND()
                LIMIT 3
                """,
                (f"%{waktu}%",),
            )
        else:
            cursor.execute("SELECT id_resep, judul FROM resep ORDER BY RAND() LIMIT 3")

        results = cursor.fetchall()
        if results:
            resep_ids = ",".join([str(r["id_resep"]) for r in results])
        else:
            cursor.execute("SELECT id_resep FROM resep ORDER BY RAND() LIMIT 3")
            fallback = cursor.fetchall()
            resep_ids = ",".join([str(r["id_resep"]) for r in fallback])

        return {
            "type": "redirect",
            "message": f"Berikut rekomendasi resep {waktu} 🍳",
            "url": f"http://localhost:8000/resepcari?ids={resep_ids}",
        }

    # -----------------------------
    # 8) Nama resep spesifik
    # -----------------------------
    resep_match = re.search(r"(?:aku mau resep|resep|punya resep|resep buatan)\s+(.+)", msg_lower)
    if resep_match:
        nama_resep = resep_match.group(1).strip()
        return {
            "type": "redirect",
            "message": f"Menampilkan resep '{nama_resep}'...",
            "url": f"http://localhost:8000/resepcari?cari_resep={nama_resep}",
        }

    # -----------------------------
    # 9) NLP fallback
    # -----------------------------
    if ints:
        tag = ints[0]["intent"]
        for i in intents_json["intents"]:
            if i["tag"] == tag:
                return {"type": "text", "message": random.choice(i["responses"])}

    # Default
    return {"type": "text", "message": "Maaf, saya tidak mengerti maksud Anda."}



# ---------------------
# Endpoint utama
# ---------------------
@app.route("/chat", methods=["POST"])
def chat():
    user_message = request.json.get("message", "")
    intents_pred = predict_class(user_message)
    response_data = get_response(intents_pred, intents, user_message)
    return jsonify(response_data)

# -------------------
# Endpoint prediksi gambar
# -------------------
@app.route("/predict_image", methods=["POST"])
def predict_image_endpoint():
    if 'file' not in request.files:
        return jsonify({"status": "error", "message": "Tidak ada file yang dikirim"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"status": "error", "message": "Nama file kosong"}), 400

    # Simpan sementara
    os.makedirs("temp", exist_ok=True)
    temp_path = os.path.join("temp", file.filename)
    file.save(temp_path)

    # Prediksi
    result = predict_food_image(temp_path)
    os.remove(temp_path)

    if "error" in result:
        return jsonify({"status": "error", "message": result["error"]}), 500

    return jsonify({"status": "success", "data": result})




if __name__ == "__main__":
    print("🚀 Chatbot server running on port 5001...")
    app.run(port=5000, debug=False)
