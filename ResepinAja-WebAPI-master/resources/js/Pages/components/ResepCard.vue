<script setup>
import { Link, usePage } from '@inertiajs/vue3'
import StarRating from './StarRating.vue';
import SaveButton from './SaveButton.vue';

const props = defineProps({
    resepData: Object,
});

const user = usePage().props.auth_user;

</script>


<template>
    <Link :href="`/detailresep/${resepData.id_resep}`" class="text-decoration-none">
    <div class="card">
        <div class="row">
            <div class="col-5 pe-0">
                <div class="position-relative">
                    <div class="ratio ratio-1x1">
                        <img :src="`http://127.0.0.1:8000/storage/${resepData.gambar}`"
                            class="card-img-top object-fit-cover border rounded-start-2" alt="Recipe image" />
                    </div>
                    <div class="position-absolute top-0 end-0">
                        <SaveButton :resepData="props.resepData"/>
                    </div>
                </div>
            </div>
            <div class="col-7 p-2">
                <h5 class="d-block text-truncate fw-bold">{{ resepData.judul }}</h5>
                <p class="text-truncate truncate-mod">
                    {{ resepData.jumlah_bahan }} Bahan | {{ resepData.wkt_masak }} menit <br>
                    {{ resepData.prs_resep }} Porsi
                </p>
                <h6 class="text-warning fw-bold align-bottom">
                    <StarRating :rating="resepData.bintang" />
                    {{ !resepData.bintang ? 0 : resepData.bintang }}/5 ({{ !resepData.jml_bintang ? 0 :
                    resepData.jml_bintang }})
                </h6>
            </div>
        </div>
    </div>
    </Link>
</template>