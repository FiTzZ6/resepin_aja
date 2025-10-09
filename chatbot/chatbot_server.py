from flask import Flask, request, jsonify
from tensorflow.keras.models import load_model
import nltk, numpy as np, json, pickle, random
from nltk.stem import WordNetLemmatizer
import mysql.connector
import re

app = Flask(__name__)
lemmatizer = WordNetLemmatizer()

# Load model dan data
model = load_model('model/model.h5')
intents = json.loads(open('dataset/intents.json', encoding='utf-8').read())
words = pickle.load(open('model/words.pkl', 'rb'))
classes = pickle.load(open('model/classes.pkl', 'rb'))


# --- Fungsi bantu ---
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


def extract_keywords(user_message):
    """Ambil kata kunci penting dari pesan user."""
    text = re.sub(r'[^a-zA-Z0-9\s]', '', user_message)
    stopwords = ['ada', 'cari', 'resep', 'dengan', 'pakai', 'apa', 'gimana', 'gini', 'yang', 'siap', 'mau']
    words_list = [word.lower() for word in text.split() if word.lower() not in stopwords]
    return ' '.join(words_list)


# --- Fungsi utama respon chatbot ---
def get_response(ints, intents_json, user_message):
    msg_lower = user_message.lower()

    # 🔹 1. Jika mengandung kata “resep”
    if "resep" in msg_lower:
        match = re.search(r"resep\s+(.*)", msg_lower)
        keywords = match.group(1).strip() if match else ""

        if not keywords:
            return {
                "type": "redirect",
                "message": "Menampilkan semua resep...",
                "url": "http://localhost:8000/resepcari"
            }

        search_url = f"http://localhost:8000/resepcari?cari_resep={keywords.replace(' ', '%20')}"
        return {
            "type": "redirect",
            "message": f"Menampilkan hasil pencarian untuk '{keywords}'...",
            "url": search_url
        }

    # 🔹 2. Jika user menyebut bahan makanan
    if any(kw in msg_lower for kw in ["punya", "bahan", "ada", "pakai", "menggunakan"]):
        # Hilangkan kata tidak penting & karakter khusus
        cleaned = re.sub(r'[^a-zA-Z0-9\s,]', '', msg_lower)
        stopwords = ['aku', 'punya', 'bahan', 'dan', 'yang', 'ada', 'pakai', 'menggunakan', 'dengan']
        tokens = [w for w in cleaned.split() if w not in stopwords]

        # Jika user tulis: "aku punya telur dan cabai" → ['telur', 'cabai']
        bahan = ','.join(tokens)

        if bahan:
            return {
                "type": "redirect",
                "url": f"http://localhost:8000/resepcari?bahan={bahan}",
                "message": f"Mencarikan resep dengan bahan: {bahan.replace(',', ', ')}..."
            }

    # 🔹 3. Intent model biasa
    if not ints:
        return {"type": "text", "message": "Maaf, saya tidak mengerti maksud Anda."}

    tag = ints[0]['intent']
    for i in intents_json['intents']:
        if i['tag'] == tag:
            return {"type": "text", "message": random.choice(i['responses'])}

    return {"type": "text", "message": "Maaf, saya belum mengerti maksud Anda."}



# --- Endpoint utama Flask ---
@app.route("/chat", methods=["POST"])
def chat():
    user_message = request.json.get("message", "").lower()

    # Jalankan prediksi intent dari model
    intents_pred = predict_class(user_message)
    response_data = get_response(intents_pred, intents, user_message)

    return jsonify(response_data)


if __name__ == "__main__":
    app.run(port=5000)
