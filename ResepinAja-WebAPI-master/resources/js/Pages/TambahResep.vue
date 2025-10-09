<script setup>
import { ref } from 'vue';
import App from './App.vue';
import { usePage, router } from '@inertiajs/vue3'

const userData = usePage().props.auth_user;

document.title = "Tambah Resep";
const resep = ref({
  judul: '',
  gambar: null,
  deskripsi: '',
  waktu_masak: '',
  porsi_masak: '',
  kategori_masak: 'Makanan Ringan',
  id_user: userData.id_user, 
  alat: [{ nama_alat: '' }],
  bahan: [{ nama_bahan: '', jumlah_bahan: '', satuan_bahan: 'Buah' }],
  langkah: [{ cara_langkah: '' }],
});

const handleGambar = (e) => {
  resep.value.gambar = e.target.files[0];
};

const tambahAlat = () => {
  resep.value.alat.push({ nama_alat: '' });
};

const hapusAlat = (i) => {
  resep.value.alat.splice(i, 1);
};

const tambahBahan = () => {
  resep.value.bahan.push({ nama_bahan: '', jumlah_bahan: '', satuan_bahan: '' });
};

const hapusBahan = (i) => {
  resep.value.bahan.splice(i, 1);
};

const tambahLangkah = () => {
  resep.value.langkah.push({ urutan: resep.value.langkah.length + 1, cara_langkah: '' });
};

const hapusLangkah = (i) => {
  resep.value.langkah.splice(i, 1);
};

const submitResep = async () => {
  const formData = new FormData();
  formData.append('judul', resep.value.judul);
  formData.append('deskripsi', resep.value.deskripsi);
  formData.append('gambar', resep.value.gambar);
  formData.append('id_user', resep.value.id_user);
  formData.append('wkt_masak', resep.value.waktu_masak);
  formData.append('prs_masak', resep.value.porsi_masak);
  formData.append('ktg_masak', resep.value.kategori_masak);
  formData.append('bahan', JSON.stringify(resep.value.bahan.map(b => b.nama_bahan)));
  formData.append('jumlah', JSON.stringify(resep.value.bahan.map(b => b.jumlah_bahan)));
  formData.append('satuan', JSON.stringify(resep.value.bahan.map(b => b.satuan_bahan)));
  formData.append('alat', JSON.stringify(resep.value.alat.map(a => a.nama_alat)));
  formData.append('langkah', JSON.stringify(resep.value.langkah.map(l => l.cara_langkah)));

  try {
    const response = await fetch('/addresep', {
      method: 'POST',
      body: formData,
      headers: {
        'X-CSRF-TOKEN': document.querySelector('meta[name="csrf-token"]').content,
        'Accept': 'application/json',
      },
      credentials: 'include'
    });

    const data = await response.json();
    alert(data.message);
    router.visit('/');
  } catch (error) {
    alert('Terjadi kesalahan saat menyimpan resep');
    console.error(error);
  }
};

</script>

<template>
  <App>
    <div class="container my-3">
      <form @submit.prevent="submitResep" enctype='multipart/form-data'>
        <div class="row">
          <div class="col-12 col-md-5">
            <label class="form-label h5">Gambar Resep</label>
            <div class="input-group mb-3">
              <input type="file" @change="handleGambar" accept="image/*" />
            </div>
            <label class="form-label h5">Judul Resep</label>
            <div class="input-group mb-3">
              <input v-model="resep.judul" type="text" class="form-control" placeholder="Air Segar" required />
            </div>
            <label class="form-label h5">Deskripsi</label>
            <div class="input-group mb-3">
              <textarea v-model="resep.deskripsi" class="form-control" required placeholder="Air Segar Merupakan..."
                rows="5"></textarea>
            </div>
          </div>
          <div class="col-12 col-md-7">
            <div class="row">
              <div class="col-6">
                <label class="form-label h6">Waktu Masak</label>
                <div class="input-group mb-3">
                  <input v-model="resep.waktu_masak" type="number" min="1" max="360" class="form-control" placeholder="10 Menit"
                    required />
                </div>
              </div>
              <div class="col-6">
                <label class="form-label h6">Porsi Masak</label>
                <div class="input-group mb-3">
                  <input v-model="resep.porsi_masak" type="number" min="1" max="35" class="form-control" placeholder="5 Orang"
                    required />
                </div>
              </div>
            </div>
            <!-- Alat -->
            <label class="form-label h6">Kategori</label><br>
            <div class="input-group mb-3">
              <select v-model="resep.kategori_masak" class="form-select" placeholder="Satuan">
                <option value="Makanan Ringan" selected>Makanan Ringan</option>
                <option value="Makanan Berat">Makanan Berat</option>
                <option value="Minuman">Minuman</option>
                <option value="Dessert">Dessert</option>
                <option value="Snack">Snack</option>
              </select>
            </div>

            <div class="d-flex justify-content-between">
              <label class="form-label h5">Alat</label>
              <button type="button" @click="tambahAlat" class="btn p-1">+ Tambah Alat</button>
            </div>
            <div class="input-group mb-3" v-for="(alat, index) in resep.alat" :key="index">
              <input v-model="alat.nama_alat" type="text" class="form-control" placeholder="Nama Alat" />
              <button type="button" @click="hapusAlat(index)" class="btn btn-danger"><i
                  class="bi bi-x-circle-fill"></i></button>
            </div>
            <!-- Bahan -->
            <div class="d-flex justify-content-between">
              <label class="form-label h5">Bahan</label>
              <button type="button" @click="tambahBahan" class="btn p-1">+ Tambah Bahan</button>
            </div>
            <div class="input-group mb-3" v-for="(bahan, index) in resep.bahan" :key="index">
              <input v-model="bahan.nama_bahan" type="text" class="form-control" placeholder="Nama Bahan" />
              <input v-model="bahan.jumlah_bahan" type="text" class="form-control" placeholder="Jumlah" />
              <select v-model="bahan.satuan_bahan" class="form-select" placeholder="Satuan">
                <option value="Buah" selected>Buah</option>
                <option value="gr">Gram</option>
                <option value="ml">Mililiter</option>
              </select>
              <button type="button" @click="hapusBahan(index)" class="btn btn-danger"><i
                  class="bi bi-x-circle-fill"></i></button>
            </div>
            <!-- Langkah -->
            <div class="d-flex justify-content-between">
              <label class="form-label h5">Langkah</label>
              <button type="button" @click="tambahLangkah" class="btn p-1">+ Tambah Langkah</button>
            </div>
            <div class="input-group mb-3" v-for="(langkah, index) in resep.langkah" :key="index">
              <span class="input-group-text" id="basic-addon1">Langkah {{ index + 1 }}</span>
              <textarea v-model="langkah.cara_langkah" class="form-control" placeholder="Masukan Air"></textarea>
              <button type="button" @click="hapusLangkah(index)" class="btn btn-danger"><i
                  class="bi bi-x-circle-fill"></i></button>
            </div>
            <!-- Submit -->
          </div>
        </div>
        <br>
        <p>Simpan jika dirasa sudah benar.</p>
        <button type="submit" class="btn btn-success">Simpan Resep</button>
      </form>
    </div>
  </App>
</template>
