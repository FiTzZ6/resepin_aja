<script setup>
import { Link } from '@inertiajs/vue3'
import "bootstrap-icons/font/bootstrap-icons.css";
import App from './App.vue';
import ResepCard from './components/ResepCard.vue';
import StarRating from './components/StarRating.vue';
import { ref, onMounted } from 'vue'
import axios from 'axios'

// state
const waktuSekarang = ref('')
const kategoriWaktu = ref('')
const resepRekomendasi = ref([])

// ambil dari backend (INI KUNCI UTAMA 🔥)
const fetchRekomendasi = async () => {
  try {
    const res = await axios.get('/rekomendasi-waktu')

    resepRekomendasi.value = res.data.data
    kategoriWaktu.value = res.data.waktu
    waktuSekarang.value = res.data.jam
  } catch (err) {
    console.error('Gagal ambil rekomendasi:', err)
  }
}

// lifecycle
onMounted(() => {
  fetchRekomendasi()

  // auto update tiap menit
  setInterval(() => {
    fetchRekomendasi()
  }, 60000)
})

document.title = "Beranda – Resepin Aja";
const data = defineProps({
  resepbest: Array,
  resepbaru: Array
})
</script>

<template>
  <App>

    <!-- ========== HERO BANNER ========== -->
    <section class="hero-section">

      <!-- Eyebrow -->
      <div class="section-eyebrow">
        <span class="eyebrow-pill">
          <i class="bi bi-fire"></i> Terpopuler
        </span>
      </div>

      <!-- Carousel -->
      <div id="heroCarousel" class="carousel slide" data-bs-ride="carousel">

        <!-- Indicators -->
        <div class="carousel-indicators hero-indicators">
          <button v-for="(r, i) in data.resepbest" :key="r.id_resep" type="button" data-bs-target="#heroCarousel"
            :data-bs-slide-to="i" :class="i === 0 ? 'active' : ''">
          </button>
        </div>

        <div class="carousel-inner hero-inner">
          <div v-for="(resep, index) in data.resepbest" :key="resep.id_resep" class="carousel-item"
            :class="index === 0 ? 'active' : ''">

            <!-- ❗ FIX: Link tidak membungkus semua -->
            <div class="hero-card">

              <div class="hero-ambient"
                :style="`background-image:url('http://localhost:8000/storage/${resep.gambar}')`">
              </div>

              <div class="hero-body">

                <div class="hero-photo-wrap">
                  <img :src="`http://localhost:8000/storage/${resep.gambar}`" class="hero-photo" />
                </div>

                <div class="hero-info">

                  <span class="hero-tag">
                    <i class="bi bi-award-fill me-1"></i>Resep Unggulan
                  </span>

                  <h1 class="hero-title">{{ resep.judul }}</h1>
                  <p class="hero-desc">{{ resep.deskripsi }}</p>

                  <div class="hero-chips">
                    <span class="hero-chip">
                      <i class="bi bi-egg-fried"></i>{{ resep.jumlah_bahan }} Bahan
                    </span>
                    <span class="hero-chip">
                      <i class="bi bi-clock"></i>{{ resep.wkt_masak }} menit
                    </span>
                  </div>

                  <!-- ✅ Link dipindah ke tombol -->
                  <Link :href="`/detailresep/${resep.id_resep}`" class="hero-cta">
                    Lihat Resep Lengkap
                    <i class="bi bi-arrow-right ms-2"></i>
                  </Link>

                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- ✅ FIX: tombol pakai class bootstrap + custom -->
        <button class="carousel-control-prev hero-ctrl hero-ctrl-prev" type="button" data-bs-target="#heroCarousel"
          data-bs-slide="prev">

          <i class="bi bi-chevron-left"></i>
        </button>

        <button class="carousel-control-next hero-ctrl hero-ctrl-next" type="button" data-bs-target="#heroCarousel"
          data-bs-slide="next">

          <i class="bi bi-chevron-right"></i>
        </button>

      </div>
    </section>

    <!-- ========== DIVIDER ========== -->
    <div class="section-divider">
      <div class="divider-line"></div>
      <span class="divider-icon"><i class="bi bi-flower1"></i></span>
      <div class="divider-line"></div>
    </div>


    <!-- ========== REKOMENDASI WAKTU ========== -->
    <section class="terbaru-section">
      <div class="section-head">
        <div>
          <span class="eyebrow-pill eyebrow-pill--gold">
            <i class="bi bi-clock"></i> Rekomendasi {{ kategoriWaktu }}
          </span>
          <h2 class="section-title">
            Cocok dimasak sekarang ({{ waktuSekarang }})
          </h2>
        </div>
      </div>

      <!-- kalau ada data -->
      <div v-if="resepRekomendasi.length" class="resep-grid">
        <div class="resep-grid-item" v-for="resep in resepRekomendasi" :key="resep.id_resep">
          <ResepCard :resepData="resep" />
        </div>
      </div>

      <!-- kalau belum ada data -->
      <div v-else style="text-align:center; padding:20px; color:#888;">
        Memuat rekomendasi...
      </div>
    </section>

    <!-- ========== RESEP TERBARU ========== -->
    <section class="terbaru-section">
      <div class="section-head">
        <div>
          <span class="eyebrow-pill eyebrow-pill--gold">
            <i class="bi bi-stars"></i> Terbaru
          </span>
          <h2 class="section-title">Resep Pilihan Minggu Ini</h2>
        </div>
        <Link href="/resepcari" class="see-all-btn">
          Lihat Semua <i class="bi bi-arrow-right ms-1"></i>
        </Link>
      </div>

      <div class="resep-grid">
        <div class="resep-grid-item" v-for="resep in data.resepbaru" :key="resep.id_resep">
          <ResepCard :resepData="resep" />
        </div>
      </div>
    </section>

    <div style="height: 48px;"></div>

  </App>
</template>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,600;0,700;1,600&family=DM+Sans:wght@400;500;600&display=swap');

:global(body) {
  background: #faf6f0;
}

.eyebrow-pill {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  padding: 5px 14px;
  border-radius: 50px;
  background: rgba(26, 58, 46, 0.08);
  color: #1a3a2e;
  border: 1px solid rgba(26, 58, 46, 0.14);
}

.eyebrow-pill--gold {
  background: rgba(201, 151, 58, 0.1);
  color: #9a6200;
  border-color: rgba(201, 151, 58, 0.25);
}

/* Hero */
.hero-section {
  padding: 36px 0 0;
}

.section-eyebrow {
  margin-bottom: 20px;
}

.hero-inner {
  border-radius: 24px;
  overflow: hidden;
}

.hero-card-link {
  text-decoration: none;
  color: inherit;
  display: block;
}

.hero-card {
  position: relative;
  border-radius: 24px;
  overflow: hidden;
  min-height: 320px;
  display: flex;
  align-items: center;
  z-index: 1;
}

@media (min-width: 768px) {
  .hero-card {
    min-height: 380px;
  }
}

.hero-ambient {
  position: absolute;
  inset: 0;
  background-size: cover;
  background-position: center;
  filter: blur(30px) brightness(0.3) saturate(0.5);
  transform: scale(1.12);
  z-index: 0;
}

.hero-body {
  position: relative;
  z-index: 2;
  display: flex;
  align-items: center;
  gap: 36px;
  padding: 32px 40px;
  width: 100%;
}

@media (max-width: 767px) {
  .hero-body {
    flex-direction: column;
    padding: 24px 20px;
  }
}

.hero-photo-wrap {
  flex-shrink: 0;
  position: relative;
  display: none;
}

@media (min-width: 640px) {
  .hero-photo-wrap {
    display: block;
  }
}

.hero-photo {
  width: 200px;
  height: 260px;
  object-fit: cover;
  border-radius: 18px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
  border: 2px solid rgba(255, 255, 255, 0.12);
  position: relative;
  z-index: 1;
}

@media (min-width: 992px) {
  .hero-photo {
    width: 240px;
    height: 300px;
  }
}

.hero-photo-glow {
  position: absolute;
  inset: 20px -10px -20px 10px;
  background: rgba(201, 151, 58, 0.25);
  border-radius: 18px;
  filter: blur(24px);
  z-index: 0;
}

.hero-info {
  flex: 1;
  color: #fff;
}

.hero-tag {
  display: inline-flex;
  align-items: center;
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 0.07em;
  text-transform: uppercase;
  background: rgba(201, 151, 58, 0.2);
  color: #e8c068;
  border: 1px solid rgba(201, 151, 58, 0.3);
  padding: 4px 12px;
  border-radius: 50px;
  margin-bottom: 14px;
}

.hero-title {
  font-family: 'Cormorant Garamond', serif;
  font-size: 2.6rem;
  font-weight: 700;
  color: #fff;
  line-height: 1.1;
  text-transform: capitalize;
  margin-bottom: 10px;
  text-shadow: 0 2px 12px rgba(0, 0, 0, 0.3);
}

@media (min-width: 992px) {
  .hero-title {
    font-size: 3.2rem;
  }
}

.hero-desc {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.6);
  margin-bottom: 16px;
  line-height: 1.6;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.hero-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 16px;
}

.hero-chip {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  font-weight: 500;
  color: rgba(255, 255, 255, 0.8);
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.1);
  padding: 5px 12px;
  border-radius: 50px;
}

.hero-rating {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 20px;
}

.hero-rating-score {
  font-size: 14px;
  font-weight: 600;
  color: #e8c068;
}

.hero-rating-count {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.45);
}

.hero-cta {
  display: inline-flex;
  align-items: center;
  font-size: 14px;
  font-weight: 600;
  color: #1a3a2e;
  background: #e8c068;
  padding: 12px 24px;
  border-radius: 50px;
  box-shadow: 0 4px 20px rgba(201, 151, 58, 0.4);
  transition: background 0.2s, transform 0.2s, box-shadow 0.2s;
}

.hero-card-link:hover .hero-cta {
  background: #c9973a;
  color: #fff;
  transform: translateX(4px);
  box-shadow: 0 6px 28px rgba(201, 151, 58, 0.5);
}

.hero-indicators {
  bottom: 16px;
  gap: 6px;
}

.hero-indicators [data-bs-target] {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.3);
  border: none;
  margin: 0 3px;
  transition: width 0.3s, background 0.3s;
}

.hero-indicators .active {
  width: 26px;
  border-radius: 10px;
  background: #e8c068;
}

.hero-ctrl {
  width: 44px;
  height: 44px;
  border-radius: 50%;
  background: rgba(26, 58, 46, 0.5);
  border: 1px solid rgba(255, 255, 255, 0.12);
  color: #fff;
  font-size: 17px;
  display: flex;
  align-items: center;
  justify-content: center;
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  backdrop-filter: blur(6px);
  opacity: 1;
  transition: background 0.18s;
  z-index: 50;
  pointer-events: auto;
}

.hero-ctrl:hover {
  background: rgba(201, 151, 58, 0.55);
}

.hero-ctrl-prev {
  left: 16px;
}

.hero-ctrl-next {
  right: 16px;
}

/* Divider */
.section-divider {
  display: flex;
  align-items: center;
  gap: 16px;
  margin: 44px 0;
}

.divider-line {
  flex: 1;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(26, 58, 46, 0.15), transparent);
}

.divider-icon {
  color: #c9973a;
  font-size: 20px;
  opacity: 0.65;
}

/* Terbaru */
.section-head {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  margin-bottom: 28px;
  flex-wrap: wrap;
  gap: 12px;
}

.section-title {
  font-family: 'Cormorant Garamond', serif;
  font-size: 1.9rem;
  font-weight: 700;
  color: #1a3a2e;
  margin: 8px 0 0;
  line-height: 1.2;
}

.see-all-btn {
  display: inline-flex;
  align-items: center;
  font-size: 13px;
  font-weight: 600;
  color: #1a3a2e;
  text-decoration: none;
  border-bottom: 2px solid transparent;
  padding-bottom: 2px;
  transition: border-color 0.18s, color 0.18s;
}

.see-all-btn:hover {
  color: #c9973a;
  border-bottom-color: #c9973a;
}

/* Grid */
.resep-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 22px;
}

@media (min-width: 576px) {
  .resep-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (min-width: 992px) {
  .resep-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}
</style>