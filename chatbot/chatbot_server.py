from flask import Flask, request, jsonify
from tensorflow.keras.models import load_model
import nltk, numpy as np, json, pickle, random
from nltk.stem import WordNetLemmatizer
import mysql.connector
import re
import datetime

app = Flask(__name__)
lemmatizer = WordNetLemmatizer()

# --- Load model dan data NLP ---
model = load_model("model/model.h5")
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

    # 1) Cek kombinasi kompleks lebih dulu
    combo = parse_combination_filters(msg_lower)
    if combo["users"] or combo["bahan"] or combo["min_rating"] or combo["max_rating"]:
        # bangun query params
        params = []
        # users
        if combo["users"]:
            # kirim sebagai user_resep[] untuk mendukung multi-user
            for u in combo["users"]:
                params.append(("user_resep[]", u))
        # bahan
        if combo["bahan"]:
            # gabungkan menjadi satu param cari_bahan (backend menerima comma-separated)
            params.append(("cari_bahan", ",".join(combo["bahan"])))
        # rating min/max
        if combo["min_rating"] is not None and combo["max_rating"] is not None:
            params.append(("min_rating", str(combo["min_rating"])))
            params.append(("max_rating", str(combo["max_rating"])))
        elif combo["min_rating"] is not None:
            params.append(("min_rating", str(combo["min_rating"])))
        elif combo["max_rating"] is not None:
            params.append(("max_rating", str(combo["max_rating"])))

        # sort
        if combo["sort"]:
            params.append(("sort", combo["sort"]))

        # buat query string manual
        query_parts = []
        for k, v in params:
            encoded_value = re.sub(r'\s+', '%20', v)
            query_parts.append(f"{k}={encoded_value}")
        query = "&".join(query_parts)
        # jika tidak ada params (edge-case), fallback
        if not query:
            return {
                "type": "text",
                "message": "Maaf, saya tidak menemukan filter yang valid.",
            }

        return {
            "type": "redirect",
            "message": "Menampilkan resep sesuai kombinasi filter kamu... 🍽️",
            "url": f"http://localhost:8000/resepcari?{query}",
        }
        
        
    # Daftar kategori yang ada
    kategori_keywords = {
        "makanan ringan": "Makanan Ringan",
        "makanan berat": "Makanan Berat",
        "minuman": "Minuman",
        "snack": "Snack",
        "dessert": "Dessert",
    }

    # 🔹 Cek kategori di pesan user
    for kw, ktg in kategori_keywords.items():
        if kw in msg_lower:
            return {
                "type": "redirect",
                "message": f"Menampilkan resep kategori {ktg} 🍽️",
                "url": f"http://localhost:8000/resepcari?ktg_masak[]={ktg}",
            }
            # 🔹 Filter berdasarkan waktu memasak
    if any(
        kw in msg_lower for kw in ["tercepat", "waktu cepat", "masak cepat", "cepat"]
    ):
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

    # ✅ Blok rekomendasi aman tanpa error
    if any(
        kw in msg_lower
        for kw in [
            "rekomendasi",
            "saran",
            "makan apa",
            "dimakan",
            "siang",
            "malam",
            "pagi",
        ]
    ):
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
            if 5 <= current_hour < 11:
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
            cursor.execute(
                """
                SELECT id_resep, judul
                FROM resep
                ORDER BY RAND()
                LIMIT 3
            """
            )

        results = cursor.fetchall()  # ✅ DI LUAR IF SUPAYA SELALU ADA

        if results:
            resep_ids = ",".join([str(r["id_resep"]) for r in results])
        else:
            # fallback ke random supaya tidak kosong
            cursor.execute("SELECT id_resep FROM resep ORDER BY RAND() LIMIT 3")
            fallback = cursor.fetchall()
            resep_ids = ",".join([str(r["id_resep"]) for r in fallback])

        return {
            "type": "redirect",
            "message": f"Berikut rekomendasi resep {waktu} 🍳",
            "url": f"http://localhost:8000/resepcari?ids={resep_ids}",
        }

    # 🔹 Urutkan by rating tertinggi
    if any(
        kw in msg_lower
        for kw in [
            "rating tinggi",
            "terbaik",
            "bintang tinggi",
            "paling bagus",
            "terfavorit",
        ]
    ):
        return {
            "type": "redirect",
            "message": "Menampilkan resep dengan rating tinggi (3-5) 🌟",
            "url": "http://localhost:8000/resepcari?sort=rating_desc&min_rating=3&max_rating=5",
        }

    # 🔹 Urutkan by rating terendah (0-5)
    rating_range_match = re.search(r"rating\s*(\d+)\s*-\s*(\d+)", msg_lower)
    if rating_range_match:
        start, end = int(rating_range_match.group(1)), int(rating_range_match.group(2))
        rating_list = list(range(start, end + 1))
        rating_query = "&".join([f"rating[]={r}" for r in rating_list])
        return {
            "type": "redirect",
            "message": f"Menampilkan resep dengan rating {start}-{end} ⭐",
            "url": f"http://localhost:8000/resepcari?{rating_query}",
        }
    if "rating terendah" in msg_lower:
        return {
            "type": "redirect",
            "message": "Menampilkan resep dengan rating terendah (0-2) 🌟",
            "url": "http://localhost:8000/resepcari?rating_lowest=1",
        }

    # ✅ Kombinasi: "resep dari {username} yang ratingnya {angka}"
    combo_match = re.search(
        r"(?:resep(?:nya)?|punya resep|resep buatan|resep dari|cari resep)\s*(?:dari|oleh|milik)?\s*([a-zA-Z0-9_\-\s]+)\s*(?:yang|dengan)?\s*rating(?:nya)?\s*(\d+)",
        msg_lower,
    )
    if combo_match:
        username = combo_match.group(1).strip()
        rating = combo_match.group(2).strip()

        cursor.execute(
            "SELECT id_user FROM users WHERE LOWER(username) = %s", (username.lower(),)
        )
        user_data = cursor.fetchone()

        if user_data:
            return {
                "type": "redirect",
                "message": f"Menampilkan resep dari {username} dengan rating {rating} ⭐",
                "url": f"http://localhost:8000/resepcari?user_resep={username}&rating[]={rating}",
            }
        else:
            return {
                "type": "text",
                "message": f"Pengguna '{username}' tidak ditemukan.",
            }

    # 🔹 Tangani banyak user sekaligus: "resep dari user1 dan user2"
    multi_user_match = re.search(
        r"(?:resep(?:nya)?|punya resep|resep buatan|tampilkan resep)\s*(?:dari|oleh|milik)?\s*([a-zA-Z0-9_\-\s,dan]+)",
        msg_lower,
    )

    if multi_user_match:
        raw_users = multi_user_match.group(1)

        # Pisahkan berdasarkan "dan" atau koma
        usernames = re.split(r"\s*(?:dan|,|&)\s*", raw_users)
        usernames = [u.strip() for u in usernames if u.strip()]

        valid_users = []
        for username in usernames:
            cursor.execute(
                "SELECT id_user FROM users WHERE LOWER(username) = %s",
                (username.lower(),),
            )
            user_data = cursor.fetchone()
            if user_data:
                valid_users.append(username)

        if valid_users:
            url_query = "&".join([f"user_resep[]={u}" for u in valid_users])
            return {
                "type": "redirect",
                "message": f"Menampilkan resep dari {', '.join(valid_users)} 👨‍🍳",
                "url": f"http://localhost:8000/resepcari?{url_query}",
            }
        else:
            return {
                "type": "text",
                "message": f"Maaf, tidak ditemukan pengguna yang disebutkan.",
            }

    user_match = re.search(
        r"(?:resep(?:nya)?|punya resep|resep buatan)\s*(?:dari|oleh|milik)\s*([a-zA-Z0-9_\-\s]+)",
        msg_lower,
    )
    if user_match:
        username = re.sub(r"\s+", " ", user_match.group(1).strip())
        cursor.execute(
            "SELECT id_user FROM users WHERE LOWER(username) = %s", (username.lower(),)
        )
        user_data = cursor.fetchone()

        if user_data:
            return {
                "type": "redirect",
                "message": f"Menampilkan resep dari {username} 👨‍🍳",
                "url": f"http://localhost:8000/resepcari?user_resep={username}",
            }
        else:
            return {
                "type": "text",
                "message": f"Maaf, tidak ditemukan pengguna dengan nama '{username}'.",
            }

    # ---------------------
    # Jika hanya 'resep ...' tanpa 'dari/oleh/milik' → Nama resep
    # ---------------------
    resep_match = re.search(
        r"(?:aku mau resep|resep|punya resep|resep buatan)\s+(.+)", msg_lower
    )
    if resep_match:
        nama_resep = resep_match.group(1).strip()
        return {
            "type": "redirect",
            "message": f"Menampilkan resep '{nama_resep}'...",
            "url": f"http://localhost:8000/resepcari?cari_resep={nama_resep}",
        }

    # 🔹 Jika menyebut bahan (pakai, punya, menggunakan)
    if any(kw in msg_lower for kw in ["punya", "bahan", "ada", "pakai", "menggunakan"]):
        bahan = extract_ingredients_from_message(msg_lower)
        if bahan:
            # Buat URL yang memuat query cari_bahan
            query_bahan = ",".join(bahan)
            return {
                "type": "redirect",
                "message": f"Mencarikan resep dengan bahan: {', '.join(bahan)}...",
                "url": f"http://localhost:8000/resepcari?cari_bahan={query_bahan}",
            }

    # 🔹 Tambahkan ini sebelum cek intents.json
    rating_range_match = re.search(r"rating\s*(\d+)\s*-\s*(\d+)", msg_lower)
    if rating_range_match:
        start = int(rating_range_match.group(1))
        end = int(rating_range_match.group(2))
        # Buat list rating dari start ke end
        rating_list = list(range(start, end + 1))
        rating_query = "&".join([f"rating[]={r}" for r in rating_list])
        return {
            "type": "redirect",
            "message": f"Menampilkan resep dengan rating {start}-{end} ⭐",
            "url": f"http://localhost:8000/resepcari?{rating_query}",  # <-- ganti ke /resepcari
        }

    # 🔹 Jika cocok ke NLP intents.json
    if ints:
        tag = ints[0]["intent"]
        for i in intents_json["intents"]:
            if i["tag"] == tag:
                return {"type": "text", "message": random.choice(i["responses"])}

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


if __name__ == "__main__":
    app.run(port=5000)
