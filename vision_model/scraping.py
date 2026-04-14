import os
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
import json
import time

# ========================
# CONFIG
# ========================
queries = [
    "jahe",
    "ginger root",
    "fresh ginger",
    "jahe segar",
    "ginger indonesia"
]

save_folder = r"C:\xampp\htdocs\resepin_aja\vision_model\dataset\dataset_blmjadi\jahe"
max_images = 300

if not os.path.exists(save_folder):
    os.makedirs(save_folder)

headers = {
    "User-Agent": "Mozilla/5.0"
}

image_urls = set()

# ========================
# SCRAPING
# ========================
for query in queries:
    print(f"\n🔍 Scraping: {query}")

    for page in range(0, 5):
        url = f"https://www.bing.com/images/search?q={query}&first={page*35}&form=HDRSC2"

        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")

        image_elements = soup.find_all("a", class_="iusc")

        for element in image_elements:
            try:
                m = element.get("m")
                if m:
                    data = json.loads(m)
                    image_urls.add(data["murl"])
            except:
                continue

        print(f"Page {page+1} → total: {len(image_urls)}")

        if len(image_urls) >= max_images:
            break

        time.sleep(1)

    if len(image_urls) >= max_images:
        break

print(f"\nTotal unik ditemukan: {len(image_urls)} gambar")

# ========================
# DOWNLOAD
# ========================
for i, url in enumerate(tqdm(list(image_urls)[:max_images])):
    try:
        img_data = requests.get(url, headers=headers, timeout=10).content
        with open(os.path.join(save_folder, f"jahe{i}.jpg"), "wb") as f:
            f.write(img_data)
    except:
        continue

print("Download selesai!")