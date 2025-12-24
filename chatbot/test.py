import json
import numpy as np
import pickle
from nltk.stem import WordNetLemmatizer
from tensorflow.keras.models import load_model
from sklearn.metrics import accuracy_score, precision_score, classification_report

# --- Load data dan model ---
with open('dataset/intents.json', 'r', encoding='utf-8') as f:
    intents = json.load(f)

with open('model/words.pkl', 'rb') as f:
    words = pickle.load(f)

with open('model/classes.pkl', 'rb') as f:
    classes = pickle.load(f)

model = load_model('model/model.h5')

lemmatizer = WordNetLemmatizer()

# --- Siapkan data evaluasi ---
documents = []
for intent in intents['intents']:
    for pattern in intent['patterns']:
        tokenized = pattern.lower().split()
        documents.append((tokenized, intent['tag']))

# membuat bag of words
X = []
y_true = []

for (pattern_words, tag) in documents:
    bag = []
    word_patterns = [lemmatizer.lemmatize(w.lower()) for w in pattern_words]

    for w in words:
        bag.append(1 if w in word_patterns else 0)

    X.append(bag)
    y_true.append(classes.index(tag))

X = np.array(X)

# --- Prediksi menggunakan model ---
pred = model.predict(X)
y_pred = np.argmax(pred, axis=1)

# --- Hitung Accuracy & Precision ---
accuracy = accuracy_score(y_true, y_pred)
precision = precision_score(y_true, y_pred, average='macro', zero_division=0)

# --- Hasil lengkap ---
report = classification_report(y_true, y_pred, target_names=classes, zero_division=0)

print("=== HASIL EVALUASI MODEL ===")
print(f"Accuracy      : {accuracy:.4f}")
print(f"Precision     : {precision:.4f}")
print("\n=== Classification Report ===")
print(report)
