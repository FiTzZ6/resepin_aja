<script setup>
import { Link } from '@inertiajs/vue3'
import { onMounted, ref } from 'vue'
import "bootstrap-icons/font/bootstrap-icons.css";
import App from './App.vue';
import ResepCard from './components/ResepCard.vue';

const data = defineProps({
    userProfile: Array,
    resepProfile: Array
})
document.title = data.userProfile.username;
</script>
<template>
    <App>
        <div class="row mt-3">
            <div class="col-12 col-md-2">
                <img src="../../../public/assets/muehe.png" class="pic-width rounded-5">
            </div>
            <div class="col-12 col-md-10 py-3">
                <h3 class="fw-bold">{{ userProfile.username }}</h3>
                <p>{{ userProfile.deskripsi_user }}</p>
            </div>
        </div>
        <hr>
        <div class="row">
            <div class="col-12 col-md-6 col-lg-4 p-2" v-for="resep in resepProfile" :key="resep.id_resep">
                <ResepCard :resepData="resep" />
            </div>
        </div>
    </App>
</template>

<style scoped>
.pic-width {
    width: 25%;
}

@media (min-width: 768px) {
    .pic-width {
        width: 100%;
    }
}
</style>