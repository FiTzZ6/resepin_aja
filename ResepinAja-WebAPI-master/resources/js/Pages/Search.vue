<script setup>
import { onMounted, ref } from 'vue'
import App from './App.vue';
import ResepCard from './components/ResepCard.vue';
 
document.title = "Temukan Resep – Resepin Aja";
const dataResep = ref([]);
const filterOpen = ref(false);
const isLoading = ref(false);
 
const form = ref({
  cari_resep: '', user_resep: '', ktg_masak: [], tgl_masak: [],
  cari_bahan: '', sort: '', rating: [], ids: null
});
 
const kategoriResep = ["Makanan Ringan","Makanan Berat","Minuman","Snack","Dessert"];
const ratingOptions = [5,4,3,2,1,0];
const sortOptions = [{val:'',label:'Relevansi'},{val:'terbaru',label:'Terbaru'},{val:'rating',label:'Rating Tertinggi'},{val:'tercepat',label:'Tercepat'}];
 
const getArr = (p,k) => p.getAll(k).length ? p.getAll(k) : (p.get(k) ? [p.get(k)] : []);
 
const updateFromURL = () => {
  const u = new URLSearchParams(window.location.search);
  form.value = {
    cari_resep: u.get('cari_resep')||'', user_resep: getArr(u,'user_resep[]').join(',')||u.get('user_resep')||'',
    ktg_masak: getArr(u,'ktg_masak[]'), tgl_masak: getArr(u,'tgl_masak[]'),
    cari_bahan: u.get('cari_bahan')||'', sort: u.get('sort')||'',
    rating: getArr(u,'rating[]').map(Number), ids: u.get('ids')||null
  };
};
 
const fetchResep = async () => {
  isLoading.value = true; filterOpen.value = false;
  const p = new URLSearchParams();
  const app = (k,arr) => arr.forEach(v => p.append(k,v));
  if (form.value.ids) p.append('ids',form.value.ids);
  if (form.value.cari_resep) p.append('cari_resep',form.value.cari_resep);
  const users = typeof form.value.user_resep==='string' ? form.value.user_resep.split(',').map(u=>u.trim()).filter(u=>u) : form.value.user_resep;
  app('user_resep[]',users); app('ktg_masak[]',form.value.ktg_masak); app('tgl_masak[]',form.value.tgl_masak); app('rating[]',form.value.rating);
  if (form.value.cari_bahan) p.append('cari_bahan',form.value.cari_bahan);
  if (form.value.sort) p.append('sort',form.value.sort);
  window.history.pushState({},'',' /resepcari?'+p.toString());
  try {
    const res = await fetch('/api/resepcari?'+p.toString());
    const json = await res.json();
    dataResep.value = json.data;
  } catch(e) { console.error(e); }
  finally { isLoading.value = false; }
};
 
const resetFilters = () => {
  form.value = { cari_resep:'', user_resep:'', ktg_masak:[], tgl_masak:[], cari_bahan:'', sort:'', rating:[], ids:null };
  fetchResep();
};
 
const activeCount = () => {
  let n=0;
  if(form.value.cari_resep) n++;
  if(form.value.user_resep) n++;
  if(form.value.cari_bahan) n++;
  n += form.value.ktg_masak.length + form.value.tgl_masak.length + form.value.rating.length;
  return n;
};
 
onMounted(() => { updateFromURL(); fetchResep(); });
window.addEventListener('popstate', () => { updateFromURL(); fetchResep(); });
</script>
 
<template>
  <App>
    <div class="browse-wrap">
 
      <!-- Sidebar + Grid layout -->
      <div class="browse-layout">
 
        <!-- ── LEFT SIDEBAR FILTER ── -->
        <aside class="filter-sidebar">
          <div class="filter-sidebar-head">
            <h3 class="filter-title"><i class="bi bi-sliders2"></i> Filter</h3>
            <button v-if="activeCount()" @click="resetFilters" class="reset-link">Reset</button>
          </div>
 
          <div class="filter-section">
            <label class="filter-label">Nama Resep</label>
            <div class="search-field">
              <i class="bi bi-search sf-icon"></i>
              <input v-model="form.cari_resep" @keyup.enter="fetchResep" type="text" class="sf-input" placeholder="Cari resep..." />
            </div>
          </div>
 
          <div class="filter-section">
            <label class="filter-label">Pembuat</label>
            <input v-model="form.user_resep" type="text" class="field-input" placeholder="Nama pengguna..." />
          </div>
 
          <div class="filter-section">
            <label class="filter-label">Bahan</label>
            <input v-model="form.cari_bahan" type="text" class="field-input" placeholder="Telur, ayam..." />
          </div>
 
          <div class="filter-section">
            <label class="filter-label">Urutkan</label>
            <select v-model="form.sort" class="field-input field-select">
              <option v-for="s in sortOptions" :key="s.val" :value="s.val">{{ s.label }}</option>
            </select>
          </div>
 
          <div class="filter-section">
            <label class="filter-label">Kategori</label>
            <div class="pill-group">
              <label v-for="k in kategoriResep" :key="k" class="pill" :class="{'pill--on': form.ktg_masak.includes(k)}">
                <input type="checkbox" v-model="form.ktg_masak" :value="k" class="d-none" />
                {{ k }}
              </label>
            </div>
          </div>
 
          <div class="filter-section">
            <label class="filter-label">Waktu Masak</label>
            <div class="pill-group">
              <label class="pill" :class="{'pill--on': form.tgl_masak.includes('cepat')}">
                <input type="checkbox" v-model="form.tgl_masak" value="cepat" class="d-none" />
                <i class="bi bi-lightning-charge"></i> Cepat ≤15 mnt
              </label>
              <label class="pill" :class="{'pill--on': form.tgl_masak.includes('lama')}">
                <input type="checkbox" v-model="form.tgl_masak" value="lama" class="d-none" />
                <i class="bi bi-hourglass-split"></i> Lama >15 mnt
              </label>
            </div>
          </div>
 
          <div class="filter-section">
            <label class="filter-label">Rating</label>
            <div class="pill-group">
              <label v-for="r in ratingOptions" :key="r" class="pill" :class="{'pill--on': form.rating.includes(r)}">
                <input type="checkbox" v-model="form.rating" :value="r" class="d-none" />
                {{ r }} ★
              </label>
            </div>
          </div>
 
          <button @click="fetchResep" class="btn-primary" style="width:100%; justify-content:center; margin-top:8px">
            <i class="bi bi-check-lg"></i> Terapkan Filter
          </button>
        </aside>
 
        <!-- ── MAIN CONTENT ── -->
        <div class="browse-main">
          <div class="browse-topbar">
            <div>
              <h1 class="section-title">Temukan <em>Resep</em></h1>
              <p class="browse-count">{{ isLoading ? 'Mencari...' : `${dataResep.length} resep ditemukan` }}</p>
            </div>
            <!-- Active chips -->
            <div class="active-chips" v-if="activeCount()">
              <span v-if="form.cari_resep" class="achip">{{ form.cari_resep }} <i class="bi bi-x" @click="form.cari_resep=''; fetchResep()"></i></span>
              <span v-if="form.cari_bahan" class="achip">Bahan: {{ form.cari_bahan }} <i class="bi bi-x" @click="form.cari_bahan=''; fetchResep()"></i></span>
              <span v-for="k in form.ktg_masak" :key="k" class="achip">{{ k }} <i class="bi bi-x" @click="form.ktg_masak=form.ktg_masak.filter(x=>x!==k); fetchResep()"></i></span>
            </div>
          </div>
 
          <!-- Skeleton loading -->
          <div v-if="isLoading" class="resep-grid">
            <div class="skeleton" v-for="i in 9" :key="i"></div>
          </div>
          <div v-else-if="dataResep.length" class="resep-grid browse-grid">
            <ResepCard v-for="r in dataResep" :key="r.id_resep" :resepData="r" />
          </div>
          <div v-else class="empty-state">
            <i class="bi bi-search-heart"></i>
            <h3>Resep tidak ditemukan</h3>
            <p>Coba ubah filter atau kata kunci pencarian</p>
            <button @click="resetFilters" class="btn-primary" style="margin: 16px auto 0; display:inline-flex">Reset Filter</button>
          </div>
        </div>
      </div>
 
    </div>
  </App>
</template>
 
<style scoped>
.browse-wrap { width: 100%; padding: 32px 0 80px; }
.browse-layout { display: grid; grid-template-columns: 280px 1fr; gap: 0; align-items: start; min-height: 70vh; }
 
/* Sidebar */
.filter-sidebar {
  position: sticky; top: 80px; padding: 24px;
  background: var(--bg2); border-right: 1px solid var(--border);
  height: calc(100vh - 80px); overflow-y: auto;
  display: flex; flex-direction: column; gap: 0;
}
.filter-sidebar-head { display: flex; align-items: center; justify-content: space-between; margin-bottom: 20px; }
.filter-title { font-family: 'Playfair Display', serif; font-size: 1.2rem; font-weight: 700; color: var(--text); display: flex; align-items: center; gap: 8px; }
.filter-title i { color: var(--gold); }
.reset-link { font-size: 12px; color: var(--danger); background: none; border: none; cursor: pointer; padding: 4px 8px; border-radius: 6px; transition: background 0.15s; }
.reset-link:hover { background: var(--danger-bg); }
 
.filter-section { margin-bottom: 20px; }
.filter-label { display: block; font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.07em; color: var(--text3); margin-bottom: 8px; }
.search-field { display: flex; align-items: center; gap: 10px; background: var(--bg3); border: 1px solid var(--border); border-radius: 10px; padding: 0 12px; transition: border-color 0.15s; }
.search-field:focus-within { border-color: var(--gold); }
.sf-icon { color: var(--text3); font-size: 15px; flex-shrink: 0; }
.sf-input { flex: 1; background: none; border: none; outline: none; padding: 10px 0; font-size: 13px; color: var(--text); font-family: 'Outfit', sans-serif; }
.sf-input::placeholder { color: var(--text4); }
.field-select { appearance: none; cursor: pointer; }
 
.pill-group { display: flex; flex-wrap: wrap; gap: 6px; }
.pill {
  font-size: 12px; font-weight: 500; padding: 5px 12px; border-radius: 50px;
  background: var(--bg3); border: 1px solid var(--border);
  color: var(--text2); cursor: pointer; transition: all 0.15s;
  display: inline-flex; align-items: center; gap: 5px; user-select: none;
}
.pill:hover { border-color: var(--gold-bd); color: var(--text); }
.pill--on { background: var(--gold-bg) !important; border-color: var(--gold) !important; color: var(--gold) !important; }
 
/* Main */
.browse-main { padding: 0 32px; }
.browse-topbar { margin-bottom: 28px; display: flex; align-items: flex-end; justify-content: space-between; gap: 12px; flex-wrap: wrap; }
.browse-count { font-size: 13px; color: var(--text3); margin-top: 4px; }
.active-chips { display: flex; flex-wrap: wrap; gap: 8px; }
.achip {
  display: inline-flex; align-items: center; gap: 7px;
  font-size: 12px; font-weight: 500; background: var(--gold-bg); border: 1px solid var(--gold-bd);
  color: var(--gold); padding: 4px 11px; border-radius: 50px;
}
.achip i { cursor: pointer; font-size: 11px; opacity: 0.7; }
.achip i:hover { opacity: 1; }
 
.browse-grid { grid-template-columns: repeat(auto-fill, minmax(240px, 1fr)); }
 
.skeleton { height: 310px; border-radius: 16px; background: var(--bg3); animation: shimmer 1.6s infinite; background-size: 200% 100%; background-image: linear-gradient(90deg, var(--bg3) 0%, var(--bg4) 50%, var(--bg3) 100%); }
@keyframes shimmer { 0%{background-position:-200% 0} 100%{background-position:200% 0} }
 
@media (max-width: 900px) {
  .browse-layout { grid-template-columns: 1fr; }
  .filter-sidebar { position: static; height: auto; border-right: none; border-bottom: 1px solid var(--border); }
  .browse-main { padding: 24px 20px; }
}
</style>