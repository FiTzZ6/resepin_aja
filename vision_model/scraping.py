import os
import time
import requests

from io import BytesIO
from PIL import Image
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options


# ==========================================================
# CONFIG
# ==========================================================

queries = [
    "gula merah",
]

save_folder = r"C:\xampp\htdocs\resepin_aja\vision_model\dataset\dataset_baru_7sep\gula_merah"

# 0 = download semua yang ditemukan
# 50 = berhenti setelah 50
TARGET_IMAGES = 300
MIN_WIDTH = 100
MIN_HEIGHT = 100


# ==========================================================
# FOLDER
# ==========================================================

os.makedirs(save_folder, exist_ok=True)


# ==========================================================
# CHROME
# ==========================================================

options = Options()
options.add_argument("--start-maximized")
options.add_argument("--disable-notifications")
options.add_argument("--lang=id-ID")

driver = webdriver.Chrome(options=options)


# ==========================================================
# REQUEST
# ==========================================================

session = requests.Session()

session.headers.update({
    "User-Agent":
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 "
        "(KHTML, like Gecko) "
        "Chrome/139.0 Safari/537.36"
})


# ==========================================================
# COUNTER
# ==========================================================

saved_count = 0
failed_count = 0


# ==========================================================
# DOWNLOAD
# ==========================================================

def download_image(url, filename):

    global saved_count
    global failed_count

    try:

        if not url:
            return False

        # Download
        response = session.get(
            url,
            timeout=15
        )

        if response.status_code != 200:
            failed_count += 1
            return False

        content = response.content

        # Buka gambar
        image = Image.open(
            BytesIO(content)
        )

        image = image.convert("RGB")

        width, height = image.size

        # Filter ukuran
        if width < MIN_WIDTH or height < MIN_HEIGHT:
            failed_count += 1
            return False

        # Simpan
        image.save(
            filename,
            "JPEG",
            quality=95
        )

        saved_count += 1

        print(
            f"✅ {saved_count} "
            f"| {width}x{height} "
            f"| {os.path.basename(filename)}"
        )

        return True

    except Exception as e:

        failed_count += 1

        return False


# ==========================================================
# GOOGLE IMAGES
# ==========================================================

try:

    for query in queries:

        if TARGET_IMAGES > 0:
            if saved_count >= TARGET_IMAGES:
                break

        print("\n")
        print("=" * 60)
        print("QUERY:", query)
        print("=" * 60)

        # ------------------------------------------
        # BUKA GOOGLE IMAGES
        # ------------------------------------------

        search_url = (
            "https://www.google.com/search"
            "?udm=2&q="
            + query.replace(" ", "+")
        )

        driver.get(search_url)

        time.sleep(3)


        # ------------------------------------------
        # SCROLL
        # ------------------------------------------

        for scroll in range(10):

            driver.execute_script(
                "window.scrollTo("
                "0, document.body.scrollHeight"
                ");"
            )

            time.sleep(2)

            print(
                f"Scroll {scroll + 1}"
            )


        # ------------------------------------------
        # AMBIL SEMUA IMG
        # ------------------------------------------

        images = driver.find_elements(
            By.TAG_NAME,
            "img"
        )

        print(
            f"\nDitemukan {len(images)} elemen gambar"
        )


        # ------------------------------------------
        # DOWNLOAD SATU-SATU
        # ------------------------------------------

        query_count = 0

        for index, img in enumerate(images):

            # Kalau target sudah tercapai
            if (
                TARGET_IMAGES > 0
                and saved_count >= TARGET_IMAGES
            ):
                break

            try:

                # ----------------------------------
                # AMBIL SRC
                # ----------------------------------

                src = img.get_attribute("src")


                if not src:
                    continue


                # ----------------------------------
                # GOOGLE THUMBNAIL
                # ----------------------------------

                if (
                    "encrypted-tbn0" not in src
                    and not src.startswith("data:image")
                ):
                    continue


                # ----------------------------------
                # DOWNLOAD
                # ----------------------------------

                filename = os.path.join(
                    save_folder,
                    f"gula_merah_{saved_count:04d}.jpg"
                )

                berhasil = download_image(
                    src,
                    filename
                )

                if berhasil:
                    query_count += 1


            except Exception:
                continue


        print("\n------------------------------------------")
        print(
            f"Query selesai: {query}"
        )
        print(
            f"Berhasil dari query ini: {query_count}"
        )
        print(
            f"Total tersimpan: {saved_count}"
        )
        print("------------------------------------------")


finally:

    driver.quit()


# ==========================================================
# HASIL
# ==========================================================

print("\n")
print("=" * 60)
print("SCRAPING SELESAI")
print("=" * 60)

print(
    f"Total berhasil : {saved_count}"
)

print(
    f"Total gagal    : {failed_count}"
)

print(
    f"Folder         : {save_folder}"
)

print("=" * 60)