<!-- ════════════════════════════════════
  TambahResep.vue
════════════════════════════════════ -->
<script setup>
import { ref } from 'vue';
import App from './App.vue';
import { usePage, router } from '@inertiajs/vue3'
 
const userData = usePage().props.auth_user;
document.title = "Tambah Resep – Resepin Aja";
 
const resep = ref({
  judul:'', gambar:null, deskripsi:'', waktu_masak:'', porsi_masak:'',
  kategori_masak:'Makanan Ringan', id_user: userData.id_user,
  alat:[{nama_alat:''}],
  bahan:[{nama_bahan:'', jumlah_bahan:'', satuan_bahan:'Buah'}],
  langkah:[{cara_langkah:''}],
});
const previewUrl = ref(null);
const isSubmitting = ref(false);
const activeStep = ref(0); // 0=info, 1=alat+bahan, 2=langkah
 
const handleGambar = (e) => { resep.value.gambar = e.target.files[0]; previewUrl.value = URL.createObjectURL(e.target.files[0]); };
const tambahAlat = () => resep.value.alat.push({nama_alat:''});
const hapusAlat = (i) => resep.value.alat.splice(i,1);
const tambahBahan = () => resep.value.bahan.push({nama_bahan:'', jumlah_bahan:'', satuan_bahan:'Buah'});
const hapusBahan = (i) => resep.value.bahan.splice(i,1);
const tambahLangkah = () => resep.value.langkah.push({urutan:resep.value.langkah.length+1, cara_langkah:''});
const hapusLangkah = (i) => { resep.value.langkah.splice(i,1); resep.value.langkah.forEach((l,idx)=>l.urutan=idx+1); };
 
const submitResep = async () => {
  isSubmitting.value = true;
  const fd = new FormData();
  fd.append('judul',resep.value.judul); fd.append('deskripsi',resep.value.deskripsi);
  fd.append('gambar',resep.value.gambar); fd.append('id_user',resep.value.id_user);
  fd.append('wkt_masak',resep.value.waktu_masak); fd.append('prs_masak',resep.value.porsi_masak);
  fd.append('ktg_masak',resep.value.kategori_masak);
  fd.append('bahan',JSON.stringify(resep.value.bahan.map(b=>b.nama_bahan)));
  fd.append('jumlah',JSON.stringify(resep.value.bahan.map(b=>b.jumlah_bahan)));
  fd.append('satuan',JSON.stringify(resep.value.bahan.map(b=>b.satuan_bahan)));
  fd.append('alat',JSON.stringify(resep.value.alat.map(a=>a.nama_alat)));
  fd.append('langkah',JSON.stringify(resep.value.langkah.map(l=>l.cara_langkah)));
  try {
    const response = await fetch('/addresep', { method:'POST', body:fd,
      headers:{'X-CSRF-TOKEN':document.querySelector('meta[name="csrf-token"]').content,'Accept':'application/json'}, credentials:'include' });
    const data = await response.json();
    alert(data.message); router.visit('/');
  } catch(e) { alert('Gagal menyimpan'); console.error(e); }
  finally { isSubmitting.value = false; }
};
</script>
 
<template>
  <App>
    <div class="form-page">
 
      <!-- Page header -->
      <div class="form-header">
        <div class="form-header-inner">
          <span class="tag tag-gold"><i class="bi bi-plus-circle-fill"></i> Buat Resep Baru</span>
          <h1 class="section-title" style="margin-top:10px">Bagikan Kreasi Masakanmu</h1>
        </div>
      </div>
 
      <!-- Step tabs -->
      <div class="step-nav">
        <div class="step-nav-inner">
          <button class="step-btn" :class="{active: activeStep===0}" @click="activeStep=0"><span class="step-num">1</span> Info Dasar</button>
          <div class="step-line"></div>
          <button class="step-btn" :class="{active: activeStep===1}" @click="activeStep=1"><span class="step-num">2</span> Bahan & Alat</button>
          <div class="step-line"></div>
          <button class="step-btn" :class="{active: activeStep===2}" @click="activeStep=2"><span class="step-num">3</span> Cara Memasak</button>
        </div>
      </div>
 
      <form @submit.prevent="submitResep">
        <div class="form-body">
 
          <!-- STEP 1: Info Dasar -->
          <div v-show="activeStep===0" class="step-content">
            <div class="step-cols">
              <!-- Image -->
              <div class="card-base">
                <h4 class="card-title"><i class="bi bi-image"></i> Foto Resep</h4>
                <label class="img-area" :class="{'img-area--filled': previewUrl}">
                  <img v-if="previewUrl" :src="previewUrl" class="img-preview" />
                  <div v-else class="img-ph">
                    <i class="bi bi-camera-fill"></i>
                    <span>Klik untuk upload foto</span>
                    <small>JPG, PNG, WEBP</small>
                  </div>
                  <input type="file" @change="handleGambar" accept="image/*" class="d-none" required />
                </label>
              </div>
 
              <!-- Basic fields -->
              <div class="card-base">
                <h4 class="card-title"><i class="bi bi-card-text"></i> Detail Resep</h4>
                <div class="field-stack">
                  <div class="fgroup">
                    <label class="field-label">Judul Resep</label>
                    <input v-model="resep.judul" type="text" class="field-input" placeholder="Ayam Goreng Spesial" required />
                  </div>
                  <div class="fgroup">
                    <label class="field-label">Deskripsi</label>
                    <textarea v-model="resep.deskripsi" class="field-textarea" rows="4" required placeholder="Ceritakan sedikit resep ini..."></textarea>
                  </div>
                  <div class="frow">
                    <div class="fgroup">
                      <label class="field-label"><i class="bi bi-clock"></i> Waktu (menit)</label>
                      <input v-model="resep.waktu_masak" type="number" min="1" max="360" class="field-input" placeholder="30" required />
                    </div>
                    <div class="fgroup">
                      <label class="field-label"><i class="bi bi-people"></i> Porsi</label>
                      <input v-model="resep.porsi_masak" type="number" min="1" max="35" class="field-input" placeholder="4" required />
                    </div>
                    <div class="fgroup">
                      <label class="field-label">Kategori</label>
                      <select v-model="resep.kategori_masak" class="field-input field-select">
                        <option>Makanan Ringan</option><option>Makanan Berat</option>
                        <option>Minuman</option><option>Dessert</option><option>Snack</option>
                      </select>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            <div class="step-footer">
              <button type="button" class="btn-primary" @click="activeStep=1">Lanjut ke Bahan & Alat <i class="bi bi-arrow-right"></i></button>
            </div>
          </div>
 
          <!-- STEP 2: Bahan & Alat -->
          <div v-show="activeStep===1" class="step-content">
            <div class="step-cols">
              <!-- Alat -->
              <div class="card-base">
                <div class="card-head">
                  <h4 class="card-title"><i class="bi bi-tools"></i> Alat</h4>
                  <button type="button" @click="tambahAlat" class="add-btn"><i class="bi bi-plus-lg"></i> Tambah</button>
                </div>
                <div class="list-items">
                  <div v-for="(a,i) in resep.alat" :key="i" class="list-row">
                    <span class="row-n">{{ i+1 }}</span>
                    <input v-model="a.nama_alat" type="text" class="field-input" placeholder="Nama alat..." />
                    <button type="button" @click="hapusAlat(i)" class="del-btn" :disabled="resep.alat.length===1"><i class="bi bi-trash3"></i></button>
                  </div>
                </div>
              </div>
 
              <!-- Bahan -->
              <div class="card-base">
                <div class="card-head">
                  <h4 class="card-title"><i class="bi bi-basket2"></i> Bahan-Bahan</h4>
                  <button type="button" @click="tambahBahan" class="add-btn"><i class="bi bi-plus-lg"></i> Tambah</button>
                </div>
                <div class="list-items">
                  <div v-for="(b,i) in resep.bahan" :key="i" class="list-row">
                    <span class="row-n">{{ i+1 }}</span>
                    <input v-model="b.nama_bahan" type="text" class="field-input" placeholder="Nama bahan" style="flex:1.5" />
                    <input v-model="b.jumlah_bahan" type="text" class="field-input" placeholder="Jml" style="flex:0.5;min-width:60px" />
                    <select v-model="b.satuan_bahan" class="field-input field-select" style="flex:0.6;min-width:72px">
                      <option>Buah</option><option value="gr">Gram</option><option value="ml">mL</option>
                      <option value="sdm">Sdm</option><option value="sdt">Sdt</option>
                    </select>
                    <button type="button" @click="hapusBahan(i)" class="del-btn" :disabled="resep.bahan.length===1"><i class="bi bi-trash3"></i></button>
                  </div>
                </div>
              </div>
            </div>
            <div class="step-footer">
              <button type="button" class="step-back-btn" @click="activeStep=0"><i class="bi bi-arrow-left"></i> Kembali</button>
              <button type="button" class="btn-primary" @click="activeStep=2">Lanjut ke Cara Memasak <i class="bi bi-arrow-right"></i></button>
            </div>
          </div>
 
          <!-- STEP 3: Langkah -->
          <div v-show="activeStep===2" class="step-content">
            <div class="card-base">
              <div class="card-head">
                <h4 class="card-title"><i class="bi bi-fire"></i> Langkah Memasak</h4>
                <button type="button" @click="tambahLangkah" class="add-btn"><i class="bi bi-plus-lg"></i> Tambah Langkah</button>
              </div>
              <div class="list-items">
                <div v-for="(l,i) in resep.langkah" :key="i" class="step-form-row">
                  <div class="step-form-n">{{ i+1 }}</div>
                  <textarea v-model="l.cara_langkah" class="field-textarea" rows="2" :placeholder="`Deskripsikan langkah ke-${i+1}...`"></textarea>
                  <button type="button" @click="hapusLangkah(i)" class="del-btn" :disabled="resep.langkah.length===1"><i class="bi bi-trash3"></i></button>
                </div>
              </div>
            </div>
            <div class="step-footer">
              <button type="button" class="step-back-btn" @click="activeStep=1"><i class="bi bi-arrow-left"></i> Kembali</button>
              <button type="submit" class="btn-primary btn-submit" :disabled="isSubmitting">
                <i class="bi bi-check-circle-fill"></i>
                <span v-if="!isSubmitting">Simpan Resep</span>
                <span v-else>Menyimpan...</span>
              </button>
            </div>
          </div>
 
        </div>
      </form>
    </div>
  </App>
</template>
 
<style scoped>
.form-page { width: 100%; padding-bottom: 80px; }
.form-header { padding: 40px 48px 0; }
.form-header-inner { max-width: 600px; }
 
/* Step nav */
.step-nav { padding: 28px 48px 0; }
.step-nav-inner { display: flex; align-items: center; gap: 0; }
.step-btn {
  display: flex; align-items: center; gap: 10px; font-size: 14px; font-weight: 600;
  color: var(--text3); background: none; border: none; cursor: pointer;
  padding: 10px 16px; border-radius: 10px; transition: all 0.2s; white-space: nowrap;
}
.step-btn:hover { color: var(--text2); background: var(--bg3); }
.step-btn.active { color: var(--gold); background: var(--gold-bg); }
.step-num {
  width: 26px; height: 26px; border-radius: 50%; background: var(--bg3); border: 1.5px solid var(--border2);
  display: flex; align-items: center; justify-content: center; font-size: 12px; font-weight: 700;
  transition: all 0.2s;
}
.step-btn.active .step-num { background: var(--gold); border-color: var(--gold); color: #0e0e0e; }
.step-line { flex: 1; height: 1px; background: var(--border); min-width: 20px; max-width: 60px; }
 
.form-body { padding: 28px 48px 0; }
.step-content { }
.step-cols { display: grid; grid-template-columns: 1fr 1fr; gap: 24px; }
 
.card-title { font-family: 'Playfair Display', serif; font-size: 1.1rem; font-weight: 700; color: var(--text); display: flex; align-items: center; gap: 8px; margin-bottom: 18px; }
.card-title i { color: var(--gold); }
.card-head { display: flex; align-items: center; justify-content: space-between; margin-bottom: 18px; }
.card-head .card-title { margin-bottom: 0; }
 
/* Image area */
.img-area {
  border: 2px dashed var(--border2); border-radius: 14px; min-height: 220px;
  cursor: pointer; display: flex; align-items: center; justify-content: center;
  overflow: hidden; transition: border-color 0.18s;
}
.img-area:hover { border-color: var(--gold); }
.img-area--filled { border-style: solid; border-color: var(--gold-bd); }
.img-preview { width: 100%; height: 220px; object-fit: cover; }
.img-ph { text-align: center; padding: 28px; color: var(--text3); }
.img-ph i { font-size: 36px; display: block; margin-bottom: 10px; color: var(--gold); opacity: 0.5; }
.img-ph span { display: block; font-size: 14px; font-weight: 500; color: var(--text2); }
.img-ph small { font-size: 12px; margin-top: 4px; display: block; }
 
.field-stack { display: flex; flex-direction: column; gap: 14px; }
.fgroup { display: flex; flex-direction: column; gap: 7px; }
.frow { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 12px; }
 
.list-items { display: flex; flex-direction: column; gap: 10px; }
.list-row { display: flex; align-items: center; gap: 10px; }
.row-n {
  width: 28px; height: 28px; border-radius: 50%; flex-shrink: 0;
  background: var(--gold-bg); color: var(--gold); border: 1px solid var(--gold-bd);
  display: flex; align-items: center; justify-content: center; font-size: 11px; font-weight: 700;
}
.step-form-row { display: flex; align-items: flex-start; gap: 12px; }
.step-form-n {
  width: 38px; height: 38px; border-radius: 10px; flex-shrink: 0; margin-top: 2px;
  background: var(--gold-bg); color: var(--gold); border: 1px solid var(--gold-bd);
  display: flex; align-items: center; justify-content: center;
  font-family: 'Playfair Display', serif; font-size: 16px; font-weight: 700;
}
 
.step-footer { display: flex; align-items: center; justify-content: flex-end; gap: 12px; padding-top: 28px; margin-top: 28px; border-top: 1px solid var(--border); }
.step-back-btn {
  display: inline-flex; align-items: center; gap: 7px; font-size: 14px; font-weight: 600;
  color: var(--text2); background: var(--bg3); border: 1px solid var(--border);
  padding: 10px 20px; border-radius: 50px; cursor: pointer; transition: all 0.15s;
}
.step-back-btn:hover { background: var(--bg4); color: var(--text); }
.btn-submit { padding: 12px 32px; font-size: 15px; }
 
@media (max-width: 900px) {
  .form-header, .step-nav, .form-body { padding-left: 20px; padding-right: 20px; }
  .step-cols { grid-template-columns: 1fr; }
  .frow { grid-template-columns: 1fr 1fr; }
  .step-nav-inner { gap: 4px; }
  .step-line { display: none; }
}
</style>