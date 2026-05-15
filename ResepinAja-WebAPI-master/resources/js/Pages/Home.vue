<script setup>
import { Link } from '@inertiajs/vue3'
import App from './App.vue';
import ResepCard from './components/ResepCard.vue';
import StarRating from './components/StarRating.vue';
import { ref, onMounted } from 'vue'
import axios from 'axios'

document.title = "Beranda – Resepin Aja";
const data = defineProps({ resepbest: Array, resepbaru: Array })

const waktuSekarang = ref('')
const kategoriWaktu = ref('')
const resepRekomendasi = ref([])
const activeSlide = ref(0)
let slideTimer = null

const fetchRekomendasi = async () => {
  try {
    const res = await axios.get('/rekomendasi-waktu')
    resepRekomendasi.value = res.data.data
    kategoriWaktu.value = res.data.waktu
    waktuSekarang.value = res.data.jam
  } catch (e) { console.error(e) }
}

const nextSlide = () => {
  if (data.resepbest?.length) activeSlide.value = (activeSlide.value + 1) % data.resepbest.length
}
const goSlide = (i) => { activeSlide.value = i; resetTimer() }
const resetTimer = () => { clearInterval(slideTimer); slideTimer = setInterval(nextSlide, 5000) }

onMounted(() => {
  fetchRekomendasi()
  setInterval(fetchRekomendasi, 60000)
  slideTimer = setInterval(nextSlide, 5000)
})
</script>

<template>
  <App>

    <!-- ═══════ HERO — full bleed ═══════ -->
    <section class="hero">
      <!-- blurred ambient bg -->
      <transition name="bg-swap" mode="out-in">
        <div class="hero-ambient" :key="activeSlide"
          :style="`background-image:url('http://localhost:8000/storage/${data.resepbest?.[activeSlide]?.gambar}')`">
        </div>
      </transition>
      <div class="hero-scrim"></div>

      <div class="hero-body">
        <!-- Info column -->
        <div class="hero-info">
          <span class="tag tag-fire"><i class="bi bi-fire"></i> Terpopuler</span>

          <transition name="fade-up" mode="out-in">
            <div :key="activeSlide" class="hero-text-block">
              <h1 class="hero-title">{{ data.resepbest?.[activeSlide]?.judul }}</h1>
              <p class="hero-desc">{{ data.resepbest?.[activeSlide]?.deskripsi }}</p>
              <div class="hero-meta">
                <span class="meta-chip"><i class="bi bi-clock"></i> {{ data.resepbest?.[activeSlide]?.wkt_masak }} menit</span>
                <span class="meta-chip"><i class="bi bi-egg-fried"></i> {{ data.resepbest?.[activeSlide]?.jumlah_bahan }} bahan</span>
                <span class="meta-chip star-chip"><i class="bi bi-star-fill"></i> {{ data.resepbest?.[activeSlide]?.bintang || '–' }}</span>
              </div>
              <Link :href="`/detailresep/${data.resepbest?.[activeSlide]?.id_resep}`" class="btn-primary">
                Lihat Resep <i class="bi bi-arrow-right ms-1"></i>
              </Link>
            </div>
          </transition>

          <!-- Dots -->
          <div class="hero-dots">
            <button v-for="(r,i) in data.resepbest" :key="r.id_resep"
              class="dot" :class="{ 'dot-on': i === activeSlide }"
              @click="goSlide(i)">
            </button>
          </div>
        </div>

        <!-- Thumbnail stack -->
        <div class="hero-stack">
          <div v-for="(r,i) in data.resepbest?.slice(0,5)" :key="r.id_resep"
            class="stack-item" :class="{ 'stack-item--on': i === activeSlide }"
            @click="goSlide(i)">
            <img :src="`http://localhost:8000/storage/${r.gambar}`" class="stack-img" />
            <div class="stack-text">
              <span class="stack-n">{{ String(i+1).padStart(2,'0') }}</span>
              <span class="stack-name">{{ r.judul }}</span>
              <span class="stack-time"><i class="bi bi-clock"></i> {{ r.wkt_masak }} mnt</span>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- ═══════ STAT BAR ═══════ -->
    <div class="stat-bar">
      <div class="stat-bar-inner">
        <div class="stat-item">
          <span class="stat-n">{{ data.resepbest?.length || 0 }}</span>
          <span class="stat-l">Resep Unggulan</span>
        </div>
        <div class="stat-div"></div>
        <div class="stat-item">
          <span class="stat-n">{{ data.resepbaru?.length || 0 }}+</span>
          <span class="stat-l">Resep Terbaru</span>
        </div>
        <div class="stat-div"></div>
        <div class="stat-item">
          <span class="stat-n">{{ resepRekomendasi.length }}</span>
          <span class="stat-l">Rekomendasi Sekarang</span>
        </div>
        <div class="stat-div"></div>
        <div class="stat-item">
          <span class="stat-n">100%</span>
          <span class="stat-l">Gratis Selamanya</span>
        </div>
      </div>
    </div>

    <!-- ═══════ REKOMENDASI WAKTU ═══════ -->
    <section class="content-section">
      <div class="content-inner">
        <div class="sec-header">
          <div>
            <span class="tag tag-gold"><i class="bi bi-clock-history"></i> {{ kategoriWaktu }}</span>
            <h2 class="section-title" style="margin-top:10px">Cocok dimasak pukul {{ waktuSekarang }}</h2>
          </div>
        </div>
        <div v-if="resepRekomendasi.length" class="resep-grid">
          <ResepCard v-for="r in resepRekomendasi" :key="r.id_resep" :resepData="r" />
        </div>
        <div v-else class="empty-state">
          <i class="bi bi-hourglass-split"></i>
          <h3>Memuat rekomendasi...</h3>
        </div>
      </div>
    </section>

    <!-- ═══════ FEATURE CALLOUT ═══════ -->
    <div class="callout-band">
      <div class="callout-inner">
        <div class="callout-item">
          <i class="bi bi-stars callout-icon"></i>
          <div>
            <h4 class="callout-h">Rekomendasi Cerdas</h4>
            <p class="callout-p">Resep disesuaikan dengan waktu makan kamu</p>
          </div>
        </div>
        <div class="callout-item">
          <i class="bi bi-camera callout-icon"></i>
          <div>
            <h4 class="callout-h">Deteksi Bahan</h4>
            <p class="callout-p">Foto bahan di dapur, cari resep otomatis</p>
          </div>
        </div>
        <div class="callout-item">
          <i class="bi bi-bookmark-heart callout-icon"></i>
          <div>
            <h4 class="callout-h">Simpan Favorit</h4>
            <p class="callout-p">Kumpulkan resep terbaik dalam satu koleksi</p>
          </div>
        </div>
        <div class="callout-item">
          <i class="bi bi-pencil-square callout-icon"></i>
          <div>
            <h4 class="callout-h">Bagikan Resepmu</h4>
            <p class="callout-p">Upload kreasi masakan sendiri ke komunitas</p>
          </div>
        </div>
      </div>
    </div>

    <!-- ═══════ RESEP TERBARU ═══════ -->
    <section class="content-section">
      <div class="content-inner">
        <div class="sec-header">
          <div>
            <span class="tag tag-gold"><i class="bi bi-stars"></i> Minggu Ini</span>
            <h2 class="section-title" style="margin-top:10px">Resep Pilihan Terbaru</h2>
          </div>
          <Link href="/resepcari" class="see-all">
            Lihat Semua <i class="bi bi-arrow-right"></i>
          </Link>
        </div>
        <div class="resep-grid">
          <ResepCard v-for="r in data.resepbaru" :key="r.id_resep" :resepData="r" />
        </div>
      </div>
    </section>

    <div style="height:60px"></div>
  </App>
</template>

<style scoped>
/* ── HERO ── */
.hero {
  position: relative; min-height: 90vh; display: flex; align-items: center;
  overflow: hidden; width: 100%;
}
.hero-ambient {
  position: absolute; inset: 0;
  background-size: cover; background-position: center;
  filter: blur(2px) brightness(0.22) saturate(0.6);
  transform: scale(1.05); transition: opacity 0.8s;
}
.bg-swap-enter-active { transition: opacity 0.8s; }
.bg-swap-enter-from { opacity: 0; }
.bg-swap-leave-active { transition: opacity 0.4s; position: absolute; }
.bg-swap-leave-to { opacity: 0; }

/* light mode: darker overlay for text readability on lighter bg */
[data-theme="light"] .hero-ambient { filter: blur(3px) brightness(0.35) saturate(0.5); }

.hero-scrim {
  position: absolute; inset: 0;
  background: linear-gradient(110deg,
    rgba(var(--hero-scrim-rgb, 20,20,20), 0.90) 30%,
    rgba(var(--hero-scrim-rgb, 20,20,20), 0.55) 65%,
    rgba(var(--hero-scrim-rgb, 20,20,20), 0.25) 100%);
}
[data-theme="light"] .hero-scrim {
  background: linear-gradient(110deg,
    rgba(245,242,237,0.88) 30%,
    rgba(245,242,237,0.55) 65%,
    rgba(245,242,237,0.20) 100%);
}

.hero-body {
  position: relative; z-index: 2; width: 100%; padding: 90px 48px 70px;
  display: grid; grid-template-columns: 1fr 400px; gap: 60px; align-items: center;
}
.hero-info { display: flex; flex-direction: column; gap: 22px; }
.hero-text-block { display: flex; flex-direction: column; gap: 16px; }
.fade-up-enter-active { transition: all 0.5s cubic-bezier(0.2,0,0,1); }
.fade-up-leave-active { transition: all 0.28s; }
.fade-up-enter-from { opacity: 0; transform: translateY(18px); }
.fade-up-leave-to { opacity: 0; }

.hero-title {
  font-family: 'Playfair Display', serif;
  font-size: clamp(2.4rem, 4.5vw, 4.2rem);
  font-weight: 900; color: var(--text); line-height: 1.1; margin: 0;
}
[data-theme="dark"] .hero-title { color: #f0ece4; }
[data-theme="light"] .hero-title { color: #1e1a14; }

.hero-desc {
  font-size: 15px; color: var(--text2); line-height: 1.7; margin: 0;
  display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden;
}
[data-theme="dark"] .hero-desc { color: rgba(240,236,228,0.60); }
[data-theme="light"] .hero-desc { color: rgba(30,26,20,0.65); }

.hero-meta { display: flex; flex-wrap: wrap; gap: 8px; }
.meta-chip {
  display: inline-flex; align-items: center; gap: 6px;
  font-size: 12px; font-weight: 500; padding: 6px 13px; border-radius: 50px;
  background: rgba(255,255,255,0.10); border: 1px solid rgba(255,255,255,0.15);
  color: rgba(255,255,255,0.80);
}
[data-theme="light"] .meta-chip {
  background: rgba(0,0,0,0.06); border-color: rgba(0,0,0,0.12); color: rgba(30,26,20,0.75);
}
.star-chip i { color: var(--gold); }

.hero-dots { display: flex; gap: 8px; }
.dot { width: 26px; height: 4px; border-radius: 4px; border: none; cursor: pointer; background: rgba(255,255,255,0.25); transition: all 0.3s; }
.dot-on { width: 44px; background: var(--gold); }
[data-theme="light"] .dot { background: rgba(0,0,0,0.2); }

/* Stack */
.hero-stack { display: flex; flex-direction: column; gap: 10px; }
.stack-item {
  display: flex; align-items: center; gap: 12px;
  padding: 10px 12px; border-radius: 14px; cursor: pointer;
  border: 1px solid rgba(255,255,255,0.08);
  background: rgba(255,255,255,0.04);
  transition: all 0.2s;
}
[data-theme="light"] .stack-item {
  border-color: rgba(0,0,0,0.08); background: rgba(0,0,0,0.04);
}
.stack-item:hover { border-color: var(--gold-bd); background: var(--gold-bg); }
.stack-item--on { border-color: var(--gold-bd) !important; background: var(--gold-bg) !important; }
.stack-img { width: 60px; height: 60px; border-radius: 10px; object-fit: cover; flex-shrink: 0; }
.stack-text { display: flex; flex-direction: column; gap: 2px; overflow: hidden; min-width: 0; }
.stack-n { font-size: 10px; font-weight: 700; color: var(--gold); }
.stack-name { font-size: 13px; font-weight: 500; color: var(--text); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
[data-theme="dark"] .stack-name { color: rgba(240,236,228,0.85); }
.stack-time { font-size: 11px; color: var(--text3); display: flex; align-items: center; gap: 4px; }

/* ── STAT BAR ── */
.stat-bar { background: var(--gold-bg); border-top: 1px solid var(--gold-bd); border-bottom: 1px solid var(--gold-bd); padding: 28px 48px; }
.stat-bar-inner { display: flex; align-items: center; justify-content: space-around; flex-wrap: wrap; gap: 16px; }
.stat-item { text-align: center; }
.stat-n { display: block; font-family: 'Playfair Display', serif; font-size: 2.2rem; font-weight: 700; color: var(--gold); line-height: 1; }
.stat-l { font-size: 12px; color: var(--text3); font-weight: 500; margin-top: 4px; display: block; }
.stat-div { width: 1px; height: 44px; background: var(--gold-bd); flex-shrink: 0; }

/* ── CONTENT SECTION ── */
.content-section { padding: 60px 0 0; }
.content-inner { padding: 0 48px; }
.sec-header {
  display: flex; align-items: flex-end; justify-content: space-between;
  margin-bottom: 28px; flex-wrap: wrap; gap: 12px;
}
.see-all {
  display: inline-flex; align-items: center; gap: 8px;
  font-size: 13px; font-weight: 600; color: var(--gold);
  border-bottom: 1px solid var(--gold-bd); padding-bottom: 2px; transition: all 0.18s;
}
.see-all:hover { color: var(--gold-light); border-color: var(--gold-light); }

/* ── CALLOUT BAND ── */
.callout-band { background: var(--bg2); border-top: 1px solid var(--border); border-bottom: 1px solid var(--border); padding: 40px 48px; margin-top: 60px; }
.callout-inner { display: grid; grid-template-columns: repeat(4,1fr); gap: 24px; }
.callout-item { display: flex; align-items: flex-start; gap: 14px; }
.callout-icon { font-size: 28px; color: var(--gold); flex-shrink: 0; margin-top: 2px; }
.callout-h { font-size: 15px; font-weight: 600; color: var(--text); margin-bottom: 4px; }
.callout-p { font-size: 13px; color: var(--text3); line-height: 1.55; }

/* ── RESPONSIVE ── */
@media (max-width: 1100px) {
  .hero-body { grid-template-columns: 1fr; padding: 90px 32px 60px; gap: 40px; }
  .hero-stack { flex-direction: row; overflow-x: auto; padding-bottom: 4px; }
  .stack-item { flex-shrink: 0; width: 200px; }
  .callout-inner { grid-template-columns: repeat(2,1fr); }
}
@media (max-width: 768px) {
  .hero { min-height: 75vh; }
  .hero-body { padding: 80px 20px 56px; }
  .hero-stack { display: none; }
  .stat-bar { padding: 22px 20px; }
  .stat-div { display: none; }
  .content-inner { padding: 0 20px; }
  .callout-band { padding: 32px 20px; }
  .callout-inner { grid-template-columns: 1fr; gap: 16px; }
}
</style>