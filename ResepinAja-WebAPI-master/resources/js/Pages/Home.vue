<script setup>
import { Link } from '@inertiajs/vue3'
import "bootstrap-icons/font/bootstrap-icons.css";
import App from './App.vue';
import ResepCard from './components/ResepCard.vue';
import StarRating from './components/StarRating.vue';

document.title = "Beranda ";
const data = defineProps({
  resepbest: Array,
  resepbaru: Array
})
</script>

<template>
  <App>
    <h3 class="mt-2"><b>Populer</b></h3>
    <div id="carouselExampleInterval" class="carousel slide" data-bs-ride="carousel">
      <div class="carousel-inner">
        <div class="carousel-item px-1" data-bs-interval="4000" :class="index == 0 ? 'active' : ''"
          v-for="(resep, index) in data.resepbest" :key="resep.id_resep">
          <div class="bg-dark rounded-4">
            <Link :href='`/detailresep/${resep.id_resep}`' class="text-light">
              <div class="row">
                <div class="col-6 d-none d-md-inline-block col-md-4 col-lg-3">
                  <img :src='`http://127.0.0.1:8000/storage/${resep.gambar}`' class="d-block w-100 rounded-start-4" style="height: 225px;" alt="..." />
                </div>
                <div class="col-12 col-md-8 col-lg-9">
                  <div class="p-3 ps-md-0">
                    <h3 class="text-truncate"><b>{{ resep.judul }}</b></h3>
                    <p class="text-truncate truncate-mod">
                      {{ resep.deskripsi }}
                    </p>
                    <p class="text-truncate truncate-mod">
                      {{resep.jumlah_bahan}} Bahan | {{resep.wkt_masak}} menit | {{resep.prs_masak}} Porsi
                    </p>
                    <h5 class="text-warning fw-bold">
                      <StarRating :rating="resep.bintang" />
                      {{ resep.bintang == null ? 0 : resep.bintang}}/5 ({{resep.jml_bintang}})</h5>
                  </div>
                </div>
              </div>
            </Link>
          </div>
        </div>
      </div>
      <button class="carousel-control-prev" type="button" data-bs-target="#carouselExampleInterval"
        data-bs-slide="prev">
        <span class="carousel-control-prev-icon" aria-hidden="true"></span>
        <span class="visually-hidden">Previous</span>
      </button>
      <button class="carousel-control-next" type="button" data-bs-target="#carouselExampleInterval"
        data-bs-slide="next">
        <span class="carousel-control-next-icon" aria-hidden="true"></span>
        <span class="visually-hidden">Next</span>
      </button>
    </div>
    <h3 class="mt-2"><b>Terbaru</b></h3>
    <div class="row">
      <div class="col-12 col-md-6 col-lg-4 p-2" v-for="resep in data.resepbaru" :key="resep.id_resep">
        <ResepCard :resepData="resep"/>
      </div>
    </div>
  </App>
</template>