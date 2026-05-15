
<!-- ════════════════════════════════════════════════
    TersimpanResep.vue
════════════════════════════════════════════════ -->
<script setup>
import { ref, onMounted, computed, watch } from 'vue';
import App from './App.vue';
import ResepCard from './components/ResepCard.vue';

document.title = "Resep Tersimpan – Resepin Aja";
const searchQuery = ref('');
const dataFilter = ref([]);
const data = defineProps({ resepSaved: Array });

onMounted(() => { dataFilter.value = data.resepSaved; });
watch(() => data.resepSaved, v => { dataFilter.value = v; });

const filteredResep = computed(() => {
  if (!searchQuery.value) return dataFilter.value;
  const q = searchQuery.value.toLowerCase();
  return dataFilter.value.filter(r => r.judul.toLowerCase().includes(q) || (r.deskripsi?.toLowerCase().includes(q)));
});
</script>

<template>
  <App>
    <div class="saved-page">
      <div class="saved-header">
        <div>
          <span class="saved-tag"><i class="bi bi-bookmark-heart-fill"></i> Koleksi Saya</span>
          <h1 class="saved-title">Resep <em>Tersimpan</em></h1>
          <p class="saved-sub">{{ filteredResep.length }} resep dalam koleksi</p>
        </div>
      </div>

      <div class="saved-search">
        <i class="bi bi-search search-icon"></i>
        <input v-model="searchQuery" type="text" class="saved-input" placeholder="Cari di koleksimu..." />
      </div>

      <div v-if="filteredResep.length" class="resep-grid">
        <ResepCard v-for="r in filteredResep" :key="r.id_resep" :resepData="r" />
      </div>
      <div v-else class="saved-empty">
        <i class="bi bi-bookmark-x"></i>
        <h3>{{ searchQuery ? 'Tidak ditemukan' : 'Belum ada resep tersimpan' }}</h3>
        <p>{{ searchQuery ? 'Coba kata kunci lain' : 'Simpan resep favoritmu dengan menekan tombol bookmark' }}</p>
      </div>
    </div>
  </App>
</template>

<style scoped>
.saved-page { padding: 40px 0 80px; }
.saved-header { margin-bottom: 28px; }
.saved-tag {
  display: inline-flex; align-items: center; gap: 6px;
  font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.08em;
  background: rgba(212,168,83,0.12); color: #d4a853; border: 1px solid rgba(212,168,83,0.25);
  padding: 5px 14px; border-radius: 50px; margin-bottom: 12px;
}
.saved-title {
  font-family: 'Playfair Display', serif; font-size: clamp(2rem,4vw,3rem);
  font-weight: 700; color: #f0ece4; margin: 0 0 6px;
}
.saved-title em { color: #d4a853; font-style: italic; }
.saved-sub { font-size: 13px; color: rgba(240,236,228,0.4); margin: 0; }

.saved-search {
  display: flex; align-items: center; gap: 12px;
  background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.1);
  border-radius: 14px; padding: 12px 18px; margin-bottom: 28px; transition: border-color 0.18s;
}
.saved-search:focus-within { border-color: rgba(212,168,83,0.45); }
.search-icon { color: rgba(240,236,228,0.35); font-size: 18px; }
.saved-input {
  flex: 1; background: none; border: none; outline: none;
  font-size: 15px; color: #f0ece4; font-family: 'Outfit', sans-serif;
}
.saved-input::placeholder { color: rgba(240,236,228,0.3); }

.resep-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px,1fr)); gap: 20px; }
.saved-empty { text-align: center; padding: 80px 32px; color: rgba(240,236,228,0.3); }
.saved-empty i { font-size: 52px; display: block; margin-bottom: 16px; color: rgba(212,168,83,0.25); }
.saved-empty h3 { font-family: 'Playfair Display', serif; font-size: 1.5rem; color: rgba(240,236,228,0.6); margin: 0 0 8px; }
.saved-empty p { font-size: 14px; }
</style>