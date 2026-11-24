import os
import csv
from collections import OrderedDict

from PIL import Image

# ==========================================================
# KONFIGURASI
# ==========================================================
# Arahkan ke folder yang benar-benar dipakai untuk latihan dan evaluasi.
base_dir = os.path.join(os.getcwd(), "dataset", "dataset_baru_7sep_bersih")
PARTS = OrderedDict([
    ("train", os.path.join(base_dir, "train_augmentasi")),
    ("valid", os.path.join(base_dir, "valid")),
    ("test", os.path.join(base_dir, "test")),
])

# Ekstensi yang dibaca Keras. Berkas lain (mis. .webp, .jfif) DIABAIKAN tanpa peringatan.
IMG_EXT = (".jpg", ".jpeg", ".png", ".bmp", ".gif")
VERIFIKASI_GAMBAR = True    # buka tiap gambar untuk mendeteksi berkas rusak (lebih lama)
OUT_CSV = "dataset_ringkasan.csv"

IGNORED = {"thumbs.db", "desktop.ini", ".ds_store"}


def scan_part(root):
    """Return: {kelas: {"ok": [...], "tidak_didukung": [...]}} untuk satu bagian."""
    result = {}
    for cls in sorted(os.listdir(root)):
        folder = os.path.join(root, cls)
        if not os.path.isdir(folder):
            continue
        ok, bad = [], []
        for dp, _, names in os.walk(folder):
            for fn in names:
                if fn.lower() in IGNORED:
                    continue
                p = os.path.join(dp, fn)
                (ok if fn.lower().endswith(IMG_EXT) else bad).append(p)
        result[cls] = {"ok": ok, "tidak_didukung": bad}
    return result


for name, root in PARTS.items():
    if not os.path.isdir(root):
        raise FileNotFoundError(f"Folder {name} tidak ditemukan: {root}")

scan = {name: scan_part(root) for name, root in PARTS.items()}
masalah = []

# ----------------------------------------------------------
# 1. Konsistensi kelas antar bagian
# ----------------------------------------------------------
all_classes = sorted(set().union(*[set(s) for s in scan.values()]))
for name in PARTS:
    missing = [c for c in all_classes if c not in scan[name]]
    if missing:
        masalah.append(f"[{name}] folder kelas tidak ada: {missing}")

# kelas yang foldernya ada tetapi tidak punya gambar terbaca
# (tf.data menghilangkan kelas seperti ini secara diam-diam)
for name in PARTS:
    for c, d in scan[name].items():
        if len(d["ok"]) == 0:
            masalah.append(f"[{name}] kelas '{c}' tidak punya gambar terbaca "
                           f"({len(d['tidak_didukung'])} berkas berekstensi lain)")

# ----------------------------------------------------------
# 2. Berkas berekstensi tidak didukung
# ----------------------------------------------------------
for name in PARTS:
    bad = [p for d in scan[name].values() for p in d["tidak_didukung"]]
    if bad:
        masalah.append(f"[{name}] {len(bad)} berkas berekstensi tidak didukung Keras, contoh: "
                       + ", ".join(os.path.basename(p) for p in bad[:5]))

# ----------------------------------------------------------
# 3. Berkas gambar rusak
# ----------------------------------------------------------
if VERIFIKASI_GAMBAR:
    print("Memeriksa keterbacaan gambar...")
    for name in PARTS:
        rusak = []
        for d in scan[name].values():
            for p in d["ok"]:
                try:
                    with Image.open(p) as im:
                        im.verify()
                except Exception:
                    rusak.append(p)
        if rusak:
            masalah.append(f"[{name}] {len(rusak)} gambar rusak/tidak terbaca, contoh: "
                           + ", ".join(os.path.basename(p) for p in rusak[:5]))

# ----------------------------------------------------------
# 4. Tabel per kelas (dapat dipakai untuk Tabel 3.1 / 4.1)
# ----------------------------------------------------------
rows = []
for c in all_classes:
    n = {name: len(scan[name].get(c, {"ok": []})["ok"]) for name in PARTS}
    rows.append((c, n["train"], n["valid"], n["test"], sum(n.values())))

tot = {name: sum(r[i] for r in rows) for i, name in enumerate(PARTS, start=1)}
total_all = sum(tot.values())

print("\n" + "=" * 62)
print(f"{'No':>3}  {'Kelas':<16}{'Train':>7}{'Valid':>7}{'Test':>7}{'Total':>8}")
print("=" * 62)
for i, (c, a, b, t, s) in enumerate(rows, start=1):
    print(f"{i:>3}  {c:<16}{a:>7}{b:>7}{t:>7}{s:>8}")
print("-" * 62)
print(f"{'':>3}  {'TOTAL':<16}{tot['train']:>7}{tot['valid']:>7}{tot['test']:>7}{total_all:>8}")
print("=" * 62)

print(f"\nJumlah kelas : {len(all_classes)}")
for name in PARTS:
    print(f"{name:<6}: {tot[name]:>5} ({tot[name] / total_all:.1%})")
print(f"Total : {total_all}")

tr = [r[1] for r in rows if r[1] > 0]
if tr:
    print(f"\nGambar latih per kelas: min {min(tr)}, maks {max(tr)}, "
          f"rasio maks/min {max(tr) / min(tr):.2f}")

with open(OUT_CSV, "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["No", "Kelas", "Train", "Valid", "Test", "Total"])
    for i, r in enumerate(rows, start=1):
        w.writerow([i, *r])
    w.writerow(["", "TOTAL", tot["train"], tot["valid"], tot["test"], total_all])
print(f"Tabel tersimpan: {OUT_CSV}")

# ----------------------------------------------------------
# 5. Ringkasan masalah
# ----------------------------------------------------------
print("\n" + "=" * 62)
if masalah:
    print(f"DITEMUKAN {len(masalah)} MASALAH:")
    for m in masalah:
        print(" -", m)
else:
    print("Tidak ada masalah ditemukan: kelas konsisten, ekstensi didukung, gambar terbaca.")
print("=" * 62)