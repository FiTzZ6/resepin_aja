import random
import json
import pickle
import numpy as np
from tensorflow.keras.models import load_model
from nltk.stem import WordNetLemmatizer
import nltk

lemmatizer = WordNetLemmatizer()

model = load_model('model/model.h5')
intents = json.loads(open('dataset/intents.json', encoding='utf-8').read())
words = pickle.load(open('model/words.pkl', 'rb'))
classes = pickle.load(open('model/classes.pkl', 'rb'))

def clean_up_sentence(sentence):
    sentence_words = nltk.word_tokenize(sentence)
    sentence_words = [lemmatizer.lemmatize(word.lower()) for word in sentence_words]
    return sentence_words

def bag_of_words(sentence, words):
    sentence_words = clean_up_sentence(sentence)
    bag = [0]*len(words)
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
    return_list = []
    for r in results:
        return_list.append({"intent": classes[r[0]], "probability": str(r[1])})
    return return_list

def get_response(ints, intents_json):
    tag = ints[0]['intent']
    list_of_intents = intents_json['intents']
    for i in list_of_intents:
        if i['tag'] == tag:
            result = random.choice(i['responses'])
            break
    return result

print("Chatbot siap! (ketik 'keluar' untuk berhenti)")

while True:
    message = input("Kamu: ")
    if message.lower() == "keluar":
        break
    ints = predict_class(message)
    res = get_response(ints, intents)
    print("Bot:", res)
