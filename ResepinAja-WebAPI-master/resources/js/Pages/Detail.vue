<script setup>
import { onMounted, ref } from 'vue'
import { Link, usePage, router } from '@inertiajs/vue3'
import StarRating from './components/StarRating.vue';
import SaveButton from './components/SaveButton.vue';
import App from './App.vue';

document.title = "Detail Resep – Resepin Aja";
const data = defineProps({ resepDetail: Array })
const userData = usePage().props.auth_user;

const dataRating = ref([])
const rating = ref(0)
const comment = ref('')
const existingRating = ref(null)
const isLoading = ref(false)
const isFetching = ref(false)
const activeTab = ref('bahan')
const checkedSteps = ref(new Set())

onMounted(async () => {
  isFetching.value = true
  await fetchAllRating()
})

const fetchAllRating = async () => {
  try {
    if (userData) await fetchUserRating()
    const res = await fetch(`/api/ratingresep/${data.resepDetail["resep"].id_resep}`)
    const json = await res.json()
    dataRating.value = json.data || []
  } catch (e) { console.error(e) }
  finally { isFetching.value = false }
}

const fetchUserRating = async () => {
  try {
    const res = await fetch(`/api/user-rating/${data.resepDetail["resep"].id_resep}/${data.resepDetail["resep"].id_user}`)
    const d = await res.json()
    if (d.exists && d.rating) {
      existingRating.value = d.rating
      rating.value = d.rating.bintang
      comment.value = d.rating.komentar || ''
    } else { existingRating.value = null; rating.value = 0; comment.value = '' }
  } catch (e) { console.error(e) }
}

const submitRating = async () => {
  isLoading.value = true
  try {
    const res = await fetch('/api/submit-rating', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'X-CSRF-TOKEN': document.querySelector('meta[name="csrf-token"]').content },
      body: JSON.stringify({ id_resep: data.resepDetail["resep"].id_resep, id_user: data.resepDetail["resep"].id_user, bintang: rating.value, komentar: comment.value })
    })
    const d = await res.json()
    if (d.success) { await fetchAllRating(); await fetchUserRating() }
  } catch (e) { console.error(e) }
  finally { isLoading.value = false }
}

const deleteRating = async () => {
  if (!confirm('Hapus ulasan?')) return
  isLoading.value = true
  try {
    const res = await fetch('/api/del-rating', {
      method: 'DELETE',
      headers: { 'Content-Type': 'application/json', 'X-CSRF-TOKEN': document.querySelector('meta[name="csrf-token"]').content },
      body: JSON.stringify({ id_resep: data.resepDetail["resep"].id_resep, id_user: data.resepDetail["resep"].id_user })
    })
    const d = await res.json()
    if (d.success) { existingRating.value = null; rating.value = 0; comment.value = ''; await fetchAllRating() }
  } catch (e) { console.error(e) }
  finally { isLoading.value = false }
}

const deleteResep = async (id_resep) => {
  if (!confirm('Hapus resep ini?')) return
  try {
    const res = await fetch('/api/deleteresep', {
      method: 'DELETE',
      headers: { 'Content-Type': 'application/json', 'X-CSRF-TOKEN': document.querySelector('meta[name="csrf-token"]').content },
      body: JSON.stringify({ id_resep })
    })
    const d = await res.json()
    if (!res.ok) throw new Error(d.message || 'Gagal')
    alert(d.message); router.visit('/')
  } catch (e) { alert(e.message); console.error(e) }
}

const toggleStep = (id) => {
  const s = new Set(checkedSteps.value)
  s.has(id) ? s.delete(id) : s.add(id)
  checkedSteps.value = s
}
</script>

<template>
  <App>

    <!-- ═══ HERO ═══ -->
    <section class="hero">
      <div class="hero-bg"
        :style="`background-image:url('http://localhost:8000/storage/${resepDetail['resep'].gambar}')`">
      </div>
      <div class="hero-overlay"></div>

      <div class="hero-body">
        <!-- Gambar resep -->
        <div class="hero-img-wrap">
          <img
            :src="`http://localhost:8000/storage/${resepDetail['resep'].gambar}`"
            :alt="resepDetail['resep'].judul"
            class="hero-img"
          />
        </div>

        <!-- Info -->
        <div class="hero-info">
          <span class="badge-unggulan">
            <i class="bi bi-award-fill"></i> Resep Unggulan
          </span>

          <h1 class="hero-title">{{ resepDetail['resep'].judul }}</h1>

          <div class="hero-author">
            <i class="bi bi-person-circle"></i>
            Oleh&nbsp;
            <Link :href="`/profil/${resepDetail['resep'].id_user}`" class="author-link">
              {{ resepDetail['resep'].username }}
            </Link>
          </div>

          <div class="hero-chips">
            <span class="chip"><i class="bi bi-fork-knife"></i> {{ resepDetail['resep'].ktg_masak }}</span>
            <span class="chip"><i class="bi bi-clock"></i> {{ resepDetail['resep'].wkt_masak }} Menit</span>
            <span class="chip"><i class="bi bi-people-fill"></i> {{ resepDetail['resep'].prs_masak }} Porsi</span>
            <span class="chip"><i class="bi bi-egg-fried"></i> {{ resepDetail['resep'].jumlah_bahan }} Bahan</span>
          </div>

          <div class="hero-rating">
            <StarRating :rating="resepDetail['resep'].bintang" />
            <span class="rating-num">{{ resepDetail['resep'].bintang || '0' }}</span>
            <span class="rating-count">({{ resepDetail['resep'].jml_bintang }} ulasan)</span>
          </div>

          <div class="hero-actions">
            <SaveButton :resepData="resepDetail['resep']" class="btn-save" />
            <button class="btn-icon" onclick="window.print()" title="Cetak">
              <i class="bi bi-printer"></i>
            </button>
            <template v-if="userData && resepDetail['resep'].id_user == userData.id_user">
              <Link :href="`/editresep/${resepDetail['resep'].id_resep}`" class="btn-icon" title="Edit">
                <i class="bi bi-pencil"></i>
              </Link>
              <button @click="deleteResep(resepDetail['resep'].id_resep)" class="btn-icon btn-icon--danger" title="Hapus">
                <i class="bi bi-trash"></i>
              </button>
            </template>
          </div>
        </div>
      </div>
    </section>

    <!-- ═══ BODY ═══ -->
    <div class="page-body">
      <div class="body-layout">

        <!-- ── KIRI ── -->
        <div class="col-left">

          <!-- Deskripsi -->
          <div class="desc-card">
            <i class="bi bi-quote desc-icon"></i>
            <p class="desc-text">"{{ resepDetail['resep'].deskripsi }}"</p>
          </div>

          <!-- Quick stats (mobile) -->
          <div class="quick-stats">
            <div class="qs-col">
              <i class="bi bi-clock qs-icon"></i>
              <span class="qs-val">{{ resepDetail['resep'].wkt_masak }}</span>
              <span class="qs-lbl">Menit</span>
            </div>
            <div class="qs-sep"></div>
            <div class="qs-col">
              <i class="bi bi-people qs-icon"></i>
              <span class="qs-val">{{ resepDetail['resep'].prs_masak }}</span>
              <span class="qs-lbl">Porsi</span>
            </div>
            <div class="qs-sep"></div>
            <div class="qs-col">
              <i class="bi bi-egg-fried qs-icon"></i>
              <span class="qs-val">{{ resepDetail['resep'].jumlah_bahan }}</span>
              <span class="qs-lbl">Bahan</span>
            </div>
          </div>

          <!-- TABS -->
          <div class="tab-block">
            <div class="tab-nav">
              <button class="tab-btn" :class="{ active: activeTab==='bahan' }" @click="activeTab='bahan'">
                <i class="bi bi-basket2-fill"></i> Bahan
              </button>
              <button class="tab-btn" :class="{ active: activeTab==='alat' }" @click="activeTab='alat'">
                <i class="bi bi-tools"></i> Alat
              </button>
              <button class="tab-btn" :class="{ active: activeTab==='cara' }" @click="activeTab='cara'">
                <i class="bi bi-fire"></i> Cara Masak
              </button>
            </div>

            <div class="tab-body">

              <!-- Bahan -->
              <div v-show="activeTab==='bahan'">
                <h3 class="tab-title"><i class="bi bi-basket2-fill"></i> Bahan-Bahan</h3>
                <div class="list-items">
                  <div class="list-row" v-for="(b,i) in resepDetail['bahan']" :key="b.id_bahan">
                    <span class="row-num">{{ i+1 }}</span>
                    <span class="row-name">{{ b.nama_bahan }}</span>
                    <span class="row-amount">{{ b.jml_bahan }} {{ b.stn_bahan }}</span>
                  </div>
                </div>
              </div>

              <!-- Alat -->
              <div v-show="activeTab==='alat'">
                <h3 class="tab-title"><i class="bi bi-tools"></i> Alat-Alat</h3>
                <div class="list-items">
                  <div class="list-row" v-for="(a,i) in resepDetail['alat']" :key="a.id_alat">
                    <span class="row-num">{{ i+1 }}</span>
                    <span class="row-name">{{ a.nama_alat }}</span>
                  </div>
                </div>
              </div>

              <!-- Cara Masak -->
              <div v-show="activeTab==='cara'">
                <h3 class="tab-title"><i class="bi bi-fire"></i> Cara Memasak</h3>
                <div class="steps-list">
                  <div
                    v-for="l in resepDetail['langkah']" :key="l.id_langkah"
                    class="step-row"
                    :class="{ 'step-done': checkedSteps.has(l.id_langkah) }"
                    @click="toggleStep(l.id_langkah)"
                  >
                    <div class="step-num">
                      <i v-if="checkedSteps.has(l.id_langkah)" class="bi bi-check-lg"></i>
                      <span v-else>{{ l.urutan }}</span>
                    </div>
                    <p class="step-text">{{ l.cara_langkah }}</p>
                  </div>
                </div>
                <p class="step-hint"><i class="bi bi-hand-index"></i> Ketuk langkah untuk menandai selesai</p>
              </div>

            </div>
          </div>

          <!-- Rating form -->
          <div class="section-card" v-if="userData">
            <h3 class="card-title"><i class="bi bi-pencil-square"></i> Berikan Ulasanmu</h3>
            <div class="star-row">
              <i
                v-for="s in 5" :key="s"
                class="bi bi-star-fill star-btn"
                :class="{ 'star-on': s <= rating }"
                :style="existingRating ? 'pointer-events:none' : ''"
                @click="rating = s"
              ></i>
            </div>
            <p class="star-label">{{ rating }}/5</p>
            <textarea
              v-model="comment" rows="4" class="field-textarea"
              placeholder="Bagikan pengalamanmu memasak resep ini..."
              :disabled="!!existingRating"
            ></textarea>
            <div style="display:flex;gap:10px">
              <button v-if="!existingRating" @click="submitRating" class="btn-gold" :disabled="isLoading || rating===0">
                <span v-if="!isLoading"><i class="bi bi-send-fill"></i> Kirim Ulasan</span>
                <span v-else class="spinner-border spinner-border-sm"></span>
              </button>
              <button v-else @click="deleteRating" class="btn-danger" :disabled="isLoading">
                <span v-if="!isLoading"><i class="bi bi-trash-fill"></i> Hapus Ulasan</span>
                <span v-else class="spinner-border spinner-border-sm"></span>
              </button>
            </div>
          </div>

          <!-- Reviews -->
          <div class="section-card">
            <h3 class="card-title"><i class="bi bi-chat-square-text"></i> Ulasan ({{ dataRating.length }})</h3>
            <div v-if="dataRating.length" class="reviews-list">
              <div class="review-item" v-for="r in dataRating" :key="r.id_rating">
                <div class="review-top">
                  <div class="review-user">
                    <div class="review-ava">{{ r.username?.charAt(0)?.toUpperCase() }}</div>
                    <Link :href="`/profil/${r.id_user}`" class="review-uname">{{ r.username }}</Link>
                  </div>
                  <StarRating :rating="r.bintang" />
                </div>
                <p class="review-text">{{ r.komentar }}</p>
              </div>
            </div>
            <div v-else class="reviews-empty">
              <i class="bi bi-chat-dots"></i>
              <p>Belum ada ulasan. Jadilah yang pertama!</p>
            </div>
          </div>

        </div>

        <!-- ── SIDEBAR ── -->
        <aside class="col-sidebar">

          <div class="widget">
            <h4 class="widget-title"><i class="bi bi-info-circle-fill"></i> Info Resep</h4>
            <div class="widget-grid">
              <div class="wstat">
                <i class="bi bi-clock wstat-icon"></i>
                <span class="wstat-val">{{ resepDetail['resep'].wkt_masak }}</span>
                <span class="wstat-lbl">Menit</span>
              </div>
              <div class="wstat">
                <i class="bi bi-people-fill wstat-icon"></i>
                <span class="wstat-val">{{ resepDetail['resep'].prs_masak }}</span>
                <span class="wstat-lbl">Porsi</span>
              </div>
              <div class="wstat">
                <i class="bi bi-egg-fried wstat-icon"></i>
                <span class="wstat-val">{{ resepDetail['resep'].jumlah_bahan }}</span>
                <span class="wstat-lbl">Bahan</span>
              </div>
              <div class="wstat">
                <i class="bi bi-star-fill wstat-icon wstat-gold"></i>
                <span class="wstat-val">{{ resepDetail['resep'].bintang || '–' }}</span>
                <span class="wstat-lbl">Rating</span>
              </div>
            </div>
          </div>

          <div class="widget" v-if="resepDetail['langkah']?.length">
            <h4 class="widget-title"><i class="bi bi-check2-all"></i> Progress Memasak</h4>
            <div class="progress-track">
              <div class="progress-fill"
                :style="`width:${Math.round(checkedSteps.size / resepDetail['langkah'].length * 100)}%`">
              </div>
            </div>
            <p class="progress-lbl">{{ checkedSteps.size }}/{{ resepDetail['langkah'].length }} langkah selesai</p>
          </div>

          <div class="widget">
            <h4 class="widget-title"><i class="bi bi-tag-fill"></i> Kategori</h4>
            <span class="kat-pill">{{ resepDetail['resep'].ktg_masak }}</span>
          </div>

        </aside>

      </div>
    </div>

  </App>
</template>

<style scoped>
/* Tema abu-abu monokrom untuk halaman detail resep */
:global(body) {
  background: #f1f1f1;
  color: #252525;
}

/* HERO */
.hero {
  position: relative; min-height: 70vh;
  display: flex; align-items: flex-end;
  overflow: hidden; width: 100%;
  background: #454545;
}
.hero-bg {
  position: absolute; inset: 0;
  background-size: cover; background-position: center;
  filter: blur(3px) brightness(0.28) grayscale(1);
  transform: scale(1.06);
}
.hero-overlay {
  position: absolute; inset: 0;
  background: linear-gradient(180deg, rgba(35,35,35,.12) 0%, rgba(35,35,35,.72) 48%, rgba(35,35,35,.98) 100%);
}
.hero-body {
  position: relative; z-index: 2; width: 100%;
  padding: 120px 48px 52px;
  display: flex; gap: 40px; align-items: flex-end;
}
.hero-img-wrap { flex-shrink: 0; }
.hero-img {
  width: 260px; height: 340px; object-fit: cover;
  border-radius: 18px; border: 2px solid rgba(255,255,255,.22);
  box-shadow: 0 24px 64px rgba(0,0,0,.38);
}
.hero-info { flex: 1; display: flex; flex-direction: column; gap: 14px; }
.badge-unggulan {
  display: inline-flex; align-items: center; gap: 6px; width: fit-content;
  font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: .08em;
  padding: 5px 14px; border-radius: 50px;
  background: rgba(255,255,255,.13); color: #f2f2f2;
  border: 1px solid rgba(255,255,255,.28);
}
.hero-title {
  font-family: 'Playfair Display', serif;
  font-size: clamp(2rem, 3.5vw, 3.4rem);
  font-weight: 900; color: #fff; margin: 0; line-height: 1.12;
}
.hero-author { font-size: 14px; color: rgba(255,255,255,.72); display: flex; align-items: center; gap: 7px; }
.author-link { color: #fff; font-weight: 700; transition: color .15s; }
.author-link:hover { color: #d8d8d8; }
.hero-chips { display: flex; flex-wrap: wrap; gap: 8px; }
.chip {
  display: inline-flex; align-items: center; gap: 6px;
  font-size: 12px; font-weight: 500; color: rgba(255,255,255,.88);
  background: rgba(255,255,255,.12); border: 1px solid rgba(255,255,255,.20);
  padding: 6px 14px; border-radius: 50px;
}
.chip i { color: #fff; font-size: 13px; }
.hero-rating { display: flex; align-items: center; gap: 9px; }
.rating-num { font-size: 14px; font-weight: 700; color: #fff; }
.rating-count { font-size: 13px; color: rgba(255,255,255,.58); }
.hero-actions { display: flex; align-items: center; gap: 10px; flex-wrap: wrap; }
.btn-save {
  display: inline-flex; align-items: center; gap: 8px;
  font-size: 14px; font-weight: 600; background: #f2f2f2; color: #222;
  border: 1px solid #fff; padding: 11px 24px; border-radius: 50px;
  cursor: pointer; text-decoration: none; transition: all .18s;
}
.btn-save:hover { background: #d8d8d8; transform: translateY(-1px); color: #111; }
.btn-icon {
  width: 44px; height: 44px; border-radius: 50%;
  background: rgba(255,255,255,.12); border: 1px solid rgba(255,255,255,.22);
  color: rgba(255,255,255,.88); font-size: 17px; cursor: pointer;
  display: flex; align-items: center; justify-content: center;
  text-decoration: none; transition: all .15s;
}
.btn-icon:hover { background: rgba(255,255,255,.24); color: #fff; }
.btn-icon--danger:hover { background: #555; color: #fff; border-color: #888; }

/* BODY */
.page-body { padding: 40px 48px 80px; background: #f1f1f1; }
.body-layout { display: grid; grid-template-columns: 1fr 300px; gap: 32px; align-items: start; }
.col-left { display: flex; flex-direction: column; gap: 24px; }
.desc-card {
  position: relative; background: #dedede; border: 1px solid #c9c9c9;
  border-left: 4px solid #777; border-radius: 0 14px 14px 0; padding: 22px 24px;
}
.desc-icon { position: absolute; top: -8px; left: 16px; font-size: 28px; color: #888; }
.desc-text {
  font-family: 'Playfair Display', serif; font-style: italic;
  font-size: 16px; color: #454545; line-height: 1.8; margin: 0;
}

/* QUICK STATS */
.quick-stats {
  display: none; background: #e3e3e3; border: 1px solid #ccc;
  border-radius: 14px; padding: 20px 24px; align-items: center; justify-content: space-around;
}
.qs-col { text-align: center; }
.qs-icon { font-size: 22px; color: #555; display: block; margin-bottom: 6px; }
.qs-val { display: block; font-size: 22px; font-weight: 700; color: #222; line-height: 1; }
.qs-lbl { font-size: 11px; color: #666; margin-top: 3px; display: block; }
.qs-sep { width: 1px; height: 40px; background: #c5c5c5; }

/* TABS */
.tab-block { background: #e5e5e5; border: 1px solid #c9c9c9; border-radius: 18px; overflow: hidden; }
.tab-nav { display: flex; background: #d5d5d5; border-bottom: 1px solid #c4c4c4; padding: 6px; gap: 4px; }
.tab-btn {
  flex: 1; display: flex; align-items: center; justify-content: center; gap: 8px;
  font-size: 13px; font-weight: 600; padding: 11px 16px; border-radius: 10px;
  background: transparent; border: none; color: #626262; cursor: pointer; transition: all .18s;
}
.tab-btn:hover { color: #222; background: #e7e7e7; }
.tab-btn.active { color: #fff; background: #555; box-shadow: 0 2px 10px rgba(0,0,0,.12); }
.tab-body { padding: 28px; }
.tab-title {
  font-family: 'Playfair Display', serif; font-size: 1.35rem; font-weight: 700;
  color: #292929; margin: 0 0 18px; display: flex; align-items: center; gap: 10px;
}
.tab-title i { color: #555; }

/* BAHAN & ALAT */
.list-items { display: flex; flex-direction: column; gap: 8px; }
.list-row {
  display: flex; align-items: center; gap: 14px; padding: 13px 16px;
  background: #f0f0f0; border: 1px solid #d2d2d2; border-radius: 12px; transition: all .15s;
}
.list-row:hover { background: #e7e7e7; border-color: #999; }
.row-num {
  width: 32px; height: 32px; border-radius: 50%; flex-shrink: 0;
  background: #dedede; color: #333; border: 1px solid #bdbdbd;
  display: flex; align-items: center; justify-content: center; font-size: 12px; font-weight: 700;
}
.row-name { flex: 1; font-size: 14px; font-weight: 600; color: #292929; }
.row-amount {
  font-size: 12px; font-weight: 700; color: #333; background: #e1e1e1;
  border: 1px solid #c5c5c5; padding: 4px 12px; border-radius: 50px; white-space: nowrap;
}

/* LANGKAH */
.steps-list { display: flex; flex-direction: column; gap: 10px; }
.step-row {
  display: flex; gap: 16px; padding: 18px 16px; background: #f0f0f0;
  border: 1px solid #d2d2d2; border-left: 3px solid #777;
  border-radius: 0 12px 12px 0; cursor: pointer; transition: all .2s;
}
.step-row:hover { background: #e7e7e7; }
.step-done { border-left-color: #555 !important; opacity: .68; }
.step-num {
  width: 40px; height: 40px; border-radius: 10px; flex-shrink: 0;
  background: #dedede; color: #333; border: 1px solid #bdbdbd;
  display: flex; align-items: center; justify-content: center;
  font-family: 'Playfair Display', serif; font-size: 17px; font-weight: 700;
}
.step-done .step-num { background: #555; color: #fff; border-color: #555; }
.step-text { flex: 1; font-size: 14px; line-height: 1.75; color: #414141; margin: 0; padding-top: 4px; }
.step-hint { font-size: 12px; color: #777; text-align: center; margin: 10px 0 0; }

/* FORM & ULASAN */
.section-card {
  background: #e5e5e5; border: 1px solid #c9c9c9; border-radius: 18px; padding: 24px;
  display: flex; flex-direction: column; gap: 16px;
}
.card-title {
  font-family: 'Playfair Display', serif; font-size: 1.2rem; font-weight: 700;
  color: #292929; margin: 0; display: flex; align-items: center; gap: 9px;
}
.card-title i { color: #555; }
.star-row { display: flex; gap: 8px; }
.star-btn { font-size: 26px; color: #aaa; cursor: pointer; transition: all .15s; }
.star-on { color: #333; transform: scale(1.1); }
.star-label { font-size: 13px; font-weight: 700; color: #333; margin: 0; }
.field-textarea {
  width: 100%; box-sizing: border-box; background: #f5f5f5; border: 1px solid #c8c8c8;
  border-radius: 12px; padding: 13px 15px; font-size: 14px; color: #262626;
  resize: vertical; min-height: 100px; outline: none; font-family: 'Outfit', sans-serif; transition: border-color .15s;
}
.field-textarea:focus { border-color: #555; box-shadow: 0 0 0 3px rgba(80,80,80,.12); }
.field-textarea::placeholder { color: #888; }
.field-textarea:disabled { opacity: .6; cursor: not-allowed; }
.btn-gold {
  display: inline-flex; align-items: center; gap: 8px; font-size: 14px; font-weight: 600;
  background: #555; color: #fff; border: 1px solid #555; padding: 11px 22px;
  border-radius: 50px; cursor: pointer; transition: all .18s;
}
.btn-gold:hover { background: #333; border-color: #333; }
.btn-gold:disabled { opacity: .4; cursor: not-allowed; }
.btn-danger {
  display: inline-flex; align-items: center; gap: 8px; font-size: 14px; font-weight: 600;
  background: #d5d5d5; color: #292929; border: 1px solid #aaa; padding: 11px 22px;
  border-radius: 50px; cursor: pointer; transition: all .18s;
}
.btn-danger:hover { background: #c4c4c4; }
.btn-danger:disabled { opacity: .4; cursor: not-allowed; }
.reviews-list { display: flex; flex-direction: column; gap: 12px; }
.review-item { background: #f0f0f0; border: 1px solid #d2d2d2; border-radius: 12px; padding: 16px; transition: all .15s; }
.review-item:hover { background: #e7e7e7; border-color: #aaa; }
.review-top { display: flex; align-items: center; justify-content: space-between; margin-bottom: 10px; }
.review-user { display: flex; align-items: center; gap: 10px; }
.review-ava {
  width: 34px; height: 34px; border-radius: 50%; background: #dedede;
  border: 1.5px solid #aaa; color: #333; font-size: 13px; font-weight: 700;
  display: flex; align-items: center; justify-content: center;
}
.review-uname { font-size: 13px; font-weight: 700; color: #333; text-decoration: none; }
.review-uname:hover { color: #666; }
.review-text { font-size: 13px; color: #555; line-height: 1.65; margin: 0; }
.reviews-empty { text-align: center; padding: 28px; color: #777; }
.reviews-empty i { font-size: 38px; display: block; margin-bottom: 10px; color: #999; }
.reviews-empty p { font-size: 13px; }

/* SIDEBAR */
.col-sidebar { position: sticky; top: 82px; display: flex; flex-direction: column; gap: 16px; }
.widget { background: #e2e2e2; border: 1px solid #c8c8c8; border-radius: 16px; padding: 20px; }
.widget-title {
  font-family: 'Playfair Display', serif; font-size: 1.05rem; font-weight: 700;
  color: #292929; margin: 0 0 16px; display: flex; align-items: center; gap: 8px;
}
.widget-title i { color: #555; }
.widget-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
.wstat {
  display: flex; flex-direction: column; align-items: center; text-align: center;
  padding: 14px 10px; background: #eeeeee; border-radius: 12px; border: 1px solid #d0d0d0;
}
.wstat-icon { font-size: 20px; color: #777; margin-bottom: 7px; }
.wstat-gold { color: #444 !important; }
.wstat-val { font-size: 20px; font-weight: 700; color: #292929; line-height: 1; }
.wstat-lbl { font-size: 11px; color: #777; margin-top: 3px; }
.progress-track { height: 7px; background: #c9c9c9; border-radius: 7px; overflow: hidden; margin-bottom: 8px; }
.progress-fill { height: 100%; background: linear-gradient(90deg, #555, #999); border-radius: 7px; transition: width .4s; min-width: 4px; }
.progress-lbl { font-size: 12px; color: #666; text-align: center; margin: 0; }
.kat-pill {
  display: inline-flex; font-size: 13px; font-weight: 700;
  background: #d5d5d5; color: #333; border: 1px solid #bcbcbc;
  padding: 7px 16px; border-radius: 50px;
}

/* RESPONSIVE */
@media (max-width: 1024px) {
  .body-layout { grid-template-columns: 1fr; }
  .col-sidebar { position: static; }
  .quick-stats { display: flex; }
  .widget-grid { grid-template-columns: repeat(4, 1fr); }
}
@media (max-width: 768px) {
  .hero-body { flex-direction: column; align-items: center; text-align: center; padding: 100px 20px 40px; gap: 24px; }
  .hero-img { width: 200px; height: 260px; }
  .hero-chips, .hero-rating, .hero-actions { justify-content: center; }
  .hero-author { justify-content: center; }
  .hero-title { font-size: 2rem; }
  .page-body { padding: 32px 20px 60px; }
  .tab-body { padding: 18px; }
  .tab-btn { font-size: 12px; padding: 10px 8px; }
  .tab-btn i { display: none; }
  .widget-grid { grid-template-columns: 1fr 1fr; }
}
@media (max-width: 480px) {
  .page-body { padding: 24px 16px 60px; }
  .list-row { gap: 9px; padding: 11px; }
  .row-name { font-size: 13px; }
  .row-amount { font-size: 11px; padding: 4px 8px; }
  .review-top { align-items: flex-start; gap: 8px; flex-wrap: wrap; }
}
@media print {
  .hero { min-height: auto; }
  .hero-body { padding: 24px; }
  .hero-bg, .hero-overlay, .hero-actions, .col-sidebar { display: none !important; }
  .page-body { padding: 20px; background: #fff; }
  .tab-block, .section-card, .desc-card, .widget { break-inside: avoid; }
}
</style>