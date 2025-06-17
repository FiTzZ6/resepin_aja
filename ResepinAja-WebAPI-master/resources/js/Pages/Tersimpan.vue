<script setup>
import { onMounted, ref, computed, watch } from 'vue';
import App from './App.vue';
import ResepCard from './components/ResepCard.vue';

document.title = "Resep Tersimpan";
const searchQuery = ref('');
const dataFilter = ref([]);
const data = defineProps({
    resepSaved: Array,
});

onMounted(() => {
    dataFilter.value = data.resepSaved;
});

const filteredResep = computed(() => {
    if (!searchQuery.value) {
        return dataFilter.value; 
    }

    const query = searchQuery.value.toLowerCase();
    return dataFilter.value.filter(resep =>
        resep.judul.toLowerCase().includes(query) ||
        (resep.deskripsi && resep.deskripsi.toLowerCase().includes(query))
    );
});

watch(() => data.resepSaved, (newVal) => {
    dataFilter.value = newVal;
});
</script>

<template>
    <App>
        <div class="mb-3">
            <label for="searchInput" class="form-label fw-bold ms-1 mt-2">Cari Resep</label>
            <input v-model="searchQuery" type="text" class="form-control" id="searchInput"
                placeholder="Resep makanan yang disimpan..." @input="searchQuery = $event.target.value">
        </div>
        <div class="container-lg">
            <div v-if="filteredResep.length === 0" class="text-center py-4">
                <p class="text-muted">Tidak ada resep yang ditemukan</p>
            </div>
            <div class="row" v-else>
                <div class="col-12 col-md-6 col-lg-4 p-2" v-for="resep in filteredResep" :key="resep.id_resep">
                    <ResepCard :resepData="resep" />
                </div>
            </div>
        </div>
    </App>
</template>