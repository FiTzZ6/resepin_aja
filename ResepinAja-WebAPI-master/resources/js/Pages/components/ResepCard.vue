<!-- components/ResepCard.vue -->
<!-- Drop-in replacement dengan full theme support, hover animations, dan layout yang konsisten -->
<script setup>
import { Link, usePage } from '@inertiajs/vue3'
import { ref } from 'vue'
import axios from 'axios'

const props = defineProps({ resepData: Object })
const userData = usePage().props.auth_user

const isSaved = ref(props.resepData?.is_saved || false)
const isSaving = ref(false)

const toggleSave = async (e) => {
  e.preventDefault(); e.stopPropagation()
  if (!userData) { alert('Login dulu untuk menyimpan resep!'); return }
  if (isSaving.value) return
  isSaving.value = true
  try {
    const res = await axios.post('/api/save-resep', {
      id_resep: props.resepData.id_resep,
      id_user: userData.id_user
    })
    isSaved.value = res.data.saved
  } catch(e) { console.error(e) }
  finally { isSaving.value = false }
}

const rating = props.resepData?.bintang ? Math.round(props.resepData.bintang) : 0
</script>

<template>
  <Link :href="`/detailresep/${resepData.id_resep}`" class="recipe-card">
    <div class="rc-img-wrap">
      <img :src="`http://localhost:8000/storage/${resepData.gambar}`" class="rc-img" :alt="resepData.judul" loading="lazy" />
      <div class="rc-img-overlay"></div>

      <!-- Bookmark button -->
      <button class="rc-save" :class="{'rc-save--saved': isSaved}" @click="toggleSave" :disabled="isSaving">
        <i class="bi" :class="isSaved ? 'bi-bookmark-fill' : 'bi-bookmark'"></i>
      </button>

      <!-- Category badge -->
      <span class="rc-cat">{{ resepData.ktg_masak }}</span>
    </div>

    <div class="rc-body">
      <h3 class="rc-title">{{ resepData.judul }}</h3>
      <p class="rc-desc">{{ resepData.deskripsi }}</p>

      <div class="rc-meta">
        <span class="rc-meta-item"><i class="bi bi-clock"></i> {{ resepData.wkt_masak }} mnt</span>
        <span class="rc-meta-item"><i class="bi bi-egg-fried"></i> {{ resepData.jumlah_bahan }} bahan</span>
        <span class="rc-meta-item rc-meta-item--people"><i class="bi bi-people"></i> {{ resepData.prs_masak }} porsi</span>
      </div>

      <div class="rc-footer">
        <div class="rc-stars">
          <span v-for="s in 5" :key="s" class="rc-star" :class="{'rc-star--on': s <= rating}">★</span>
          <span class="rc-rating-num">{{ resepData.bintang ? Number(resepData.bintang).toFixed(1) : '0' }}</span>
          <span class="rc-review-count">({{ resepData.jml_bintang || 0 }})</span>
        </div>
        <span class="rc-author">
          <i class="bi bi-person-circle"></i> {{ resepData.username }}
        </span>
      </div>
    </div>
  </Link>
</template>

<style scoped>
.recipe-card {
  display: flex; flex-direction: column;
  background: var(--bg2); border: 1px solid var(--border);
  border-radius: var(--radius-lg); overflow: hidden;
  text-decoration: none; color: inherit;
  transition: all 0.24s cubic-bezier(0.2,0,0,1);
  cursor: pointer;
}
.recipe-card:hover {
  border-color: var(--gold-bd);
  box-shadow: var(--shadow);
  transform: translateY(-3px);
}

.rc-img-wrap { position: relative; overflow: hidden; aspect-ratio: 16/10; }
.rc-img { width: 100%; height: 100%; object-fit: cover; transition: transform 0.4s ease; }
.recipe-card:hover .rc-img { transform: scale(1.04); }
.rc-img-overlay {
  position: absolute; inset: 0;
  background: linear-gradient(0deg, rgba(0,0,0,0.45) 0%, transparent 60%);
}

.rc-save {
  position: absolute; top: 10px; right: 10px;
  width: 34px; height: 34px; border-radius: 50%;
  background: rgba(255,255,255,0.15); backdrop-filter: blur(8px);
  border: 1px solid rgba(255,255,255,0.25); color: rgba(255,255,255,0.85);
  font-size: 15px; cursor: pointer;
  display: flex; align-items: center; justify-content: center;
  transition: all 0.18s; z-index: 2;
}
.rc-save:hover { background: rgba(255,255,255,0.28); color: #fff; }
.rc-save--saved { background: var(--gold) !important; border-color: var(--gold) !important; color: #0e0e0e !important; }

.rc-cat {
  position: absolute; bottom: 10px; left: 10px;
  font-size: 10px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.07em;
  background: rgba(0,0,0,0.55); backdrop-filter: blur(6px); color: #fff;
  padding: 4px 10px; border-radius: 50px; z-index: 2;
}

.rc-body { padding: 16px 18px; display: flex; flex-direction: column; gap: 8px; flex: 1; }
.rc-title {
  font-family: 'Playfair Display', serif; font-size: 1.05rem; font-weight: 700;
  color: var(--text); line-height: 1.3; margin: 0;
  display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden;
}
.rc-desc {
  font-size: 12px; color: var(--text3); line-height: 1.6; margin: 0;
  display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden;
}
.rc-meta { display: flex; flex-wrap: wrap; gap: 6px; margin-top: 4px; }
.rc-meta-item {
  display: inline-flex; align-items: center; gap: 5px;
  font-size: 11px; font-weight: 500; color: var(--text3);
  background: var(--bg3); padding: 4px 10px; border-radius: 50px;
}
.rc-meta-item i { font-size: 12px; color: var(--gold); }

.rc-footer { display: flex; align-items: center; justify-content: space-between; margin-top: auto; padding-top: 10px; border-top: 1px solid var(--border); }
.rc-stars { display: flex; align-items: center; gap: 2px; }
.rc-star { font-size: 12px; color: var(--border2); transition: color 0.1s; }
.rc-star--on { color: var(--gold); }
.rc-rating-num { font-size: 12px; font-weight: 700; color: var(--gold); margin-left: 5px; }
.rc-review-count { font-size: 11px; color: var(--text3); margin-left: 2px; }
.rc-author { font-size: 11px; color: var(--text3); display: flex; align-items: center; gap: 5px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 45%; }
.rc-author i { color: var(--gold); flex-shrink: 0; }
</style>