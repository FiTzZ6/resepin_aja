"""
Bersihkan dataset agar semua gambar bisa dibaca TensorFlow.

TensorFlow (image_dataset_from_directory) hanya bisa men-decode JPEG, PNG,
BMP, dan GIF, dan hanya membaca berkas berekstensi .jpg/.jpeg/.png/.bmp/.gif.
Berkas yang formatnya lain (WEBP, TIFF, PPM, AVIF, dll.), meskipun
ekstensinya .jpg/.png, membuat training error. Berkas dengan ekstensi lain
diabaikan diam-diam, bahkan satu kelas bisa hilang.

Skrip ini TIDAK mengubah dataset asli. Hasilnya ditulis ke folder baru.
Jalankan sekali:  python bersihkan_dataset.py
"""
import os
import shutil
from collections import Counter

from PIL import Image
from tqdm import tqdm

SRC_ROOT = "dataset/dataset_baru_7sep"
DST_ROOT = "dataset/dataset_baru_7sep_bersih"
SPLITS = ["train_augmentasi", "valid", "test"]

# format yang bisa di-decode TensorFlow -> ekstensi yang benar
SAFE_EXT = {"JPEG": ".jpg", "PNG": ".png", "BMP": ".bmp", "GIF": ".gif"}
# mode warna yang aman dibaca TensorFlow tanpa konversi
SAFE_MODES = {"RGB", "L", "RGBA", "LA", "P"}
JPEG_QUALITY = 95


def unique_path(path):
    base, ext = os.path.splitext(path)
    cand, n = path, 1
    while os.path.exists(cand):
        n += 1
        cand = f"{base}_{n}{ext}"
    return cand


def ke_rgb(im):
    """Konversi ke RGB; transparansi diganti latar putih."""
    if im.mode in ("RGBA", "LA") or (im.mode == "P" and "transparency" in im.info):
        rgba = im.convert("RGBA")
        bg = Image.new("RGB", rgba.size, (255, 255, 255))
        bg.paste(rgba, mask=rgba.split()[-1])
        return bg
    return im.convert("RGB")


def proses(src, dst_dir):
    """Return (status, detail). status: 'salin' | 'konversi' | 'lewati'."""
    stem = os.path.splitext(os.path.basename(src))[0]
    try:
        with Image.open(src) as im:
            fmt, mode = im.format, im.mode
            im.load()  # memunculkan error kalau berkas terpotong/rusak
            if fmt in SAFE_EXT and mode in SAFE_MODES:
                action, rgb = "salin", None
            else:
                action, rgb = "konversi", ke_rgb(im)
    except Exception as e:
        return "lewati", f"{type(e).__name__}: {e}"

    os.makedirs(dst_dir, exist_ok=True)
    if action == "salin":
        dst = unique_path(os.path.join(dst_dir, stem + SAFE_EXT[fmt]))
        shutil.copy2(src, dst)
        return "salin", fmt
    dst = unique_path(os.path.join(dst_dir, stem + ".jpg"))
    rgb.save(dst, "JPEG", quality=JPEG_QUALITY)
    return "konversi", f"{fmt}/{mode}"


def ringkas(root):
    """Jumlah gambar per kelas (folder tingkat pertama)."""
    hasil = {}
    for c in sorted(os.listdir(root)):
        folder = os.path.join(root, c)
        if os.path.isdir(folder):
            hasil[c] = sum(len(f) for _, _, f in os.walk(folder))
    return hasil


def main():
    if not os.path.isdir(SRC_ROOT):
        raise FileNotFoundError(f"Folder sumber tidak ditemukan: {SRC_ROOT}")
    os.makedirs(DST_ROOT, exist_ok=True)

    log = []
    stat = Counter()
    konversi_dari = Counter()

    for split in SPLITS:
        src_split = os.path.join(SRC_ROOT, split)
        dst_split = os.path.join(DST_ROOT, split)
        if not os.path.isdir(src_split):
            raise FileNotFoundError(f"Folder tidak ditemukan: {src_split}")
        if os.path.exists(dst_split):
            print(f"{split}: sudah ada di {DST_ROOT}, dilewati "
                  "(hapus folder itu kalau ingin mengulang).")
            continue

        files = [os.path.join(r, n) for r, _, ns in os.walk(src_split) for n in ns]
        for src in tqdm(files, desc=split):
            rel_dir = os.path.relpath(os.path.dirname(src), src_split)
            if rel_dir == ".":
                log.append(f"[{split}] LEWATI (tidak berada di folder kelas): {src}")
                stat["lewati"] += 1
                continue
            status, detail = proses(src, os.path.join(dst_split, rel_dir))
            stat[status] += 1
            if status == "konversi":
                konversi_dari[detail] += 1
                log.append(f"[{split}] KONVERSI ({detail}): {src}")
            elif status == "lewati":
                log.append(f"[{split}] LEWATI ({detail}): {src}")

    laporan = os.path.join(DST_ROOT, "laporan_pembersihan.txt")
    with open(laporan, "a", encoding="utf-8") as f:
        f.write("\n".join(log) + ("\n" if log else ""))

    print("\n==========================================")
    print("HASIL PEMBERSIHAN")
    print("==========================================")
    print(f"Disalin apa adanya : {stat['salin']}")
    print(f"Dikonversi ke JPEG : {stat['konversi']}")
    print(f"Dilewati (rusak)   : {stat['lewati']}")
    if konversi_dari:
        print("Konversi dari format/mode:")
        for k, v in konversi_dari.most_common():
            print(f"  {k}: {v}")
    print(f"Detail per berkas  : {laporan}")

    ringkasan = {s: ringkas(os.path.join(DST_ROOT, s)) for s in SPLITS}
    for s, d in ringkasan.items():
        print(f"\n{s}: {len(d)} kelas, {sum(d.values())} gambar")
    kelas_train = set(ringkasan[SPLITS[0]])
    for s in SPLITS[1:]:
        kelas_s = set(ringkasan[s])
        if kelas_train != kelas_s:
            print(f"\nPERINGATAN: daftar kelas train dan {s} berbeda!")
            print("  Hanya di train:", sorted(kelas_train - kelas_s))
            print(f"  Hanya di {s}:", sorted(kelas_s - kelas_train))
    for s in SPLITS:
        src_s = os.path.join(SRC_ROOT, s)
        kelas_src = {d for d in os.listdir(src_s) if os.path.isdir(os.path.join(src_s, d))}
        hilang = sorted(kelas_src - set(ringkasan[s]))
        if hilang:
            print(f"PERINGATAN: kelas ada di sumber tapi TIDAK ada di hasil ({s}): {hilang}")
            print("  Semua gambar kelas itu gagal dibaca. Cek isi foldernya.")
    kosong = [c for s in SPLITS for c, n in ringkasan[s].items() if n == 0]
    if kosong:
        print("PERINGATAN: kelas tanpa gambar:", kosong)

    print(f"\nSelesai. Pakai folder ini di skrip training:\n  {DST_ROOT}")


if __name__ == "__main__":
    main()