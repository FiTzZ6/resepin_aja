<script setup>
import { ref } from 'vue'
import { router } from '@inertiajs/vue3'

const form = ref({
    cari_resep: '',
});

const searchResep = () => {
    // Only add parameters if search term exists
    const params = {};
    if (form.value.cari_resep.trim()) {
        params.cari_resep = form.value.cari_resep.trim();
    }
    
    router.visit('/resepcari', {
        data: params,
        preserveState: true,
        preserveScroll: true,
        replace: true  // Prevents adding to browser history
    });
};
</script>

<template>
    <form class="d-flex pt-2 pt-md-0 m-auto" role="search" @submit.prevent="searchResep">
        <input 
            v-model="form.cari_resep" 
            class="form-control me-2" 
            type="search" 
            placeholder="Rendang Crispy" 
            aria-label="Search" 
        />
        <button class="btn btn-success" type="submit">Cari</button>
    </form>
</template>