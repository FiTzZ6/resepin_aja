<script setup>
import { usePage } from '@inertiajs/vue3'
import { ref, onMounted } from 'vue';

const props = defineProps({
    resepData: Object,
});

const user = usePage().props.auth_user;
const isSaved = ref(false);

onMounted(() => {
    checkSavedStatus();
});

const checkSavedStatus = async () => {
    try {
        const response = await fetch(`/api/check-saved/${user.id_user}/${props.resepData.id_resep}`);
        const data = await response.json();
        isSaved.value = data.is_saved;
    } catch (error) {
        console.error('Error checking saved status:', error);
    }
};

const toggleSave = async (e) => {
    e.preventDefault();
    e.stopPropagation();
    try {
        if (isSaved.value) {
            await unsaveRecipe();
        } else {
            await saveRecipe();
        }
    } finally {
        await checkSavedStatus();
    }
};

const saveRecipe = async () => {
    try {
        const response = await fetch('/api/save-recipe', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRF-TOKEN': document.querySelector('meta[name="csrf-token"]').content
            },
            body: JSON.stringify({
                id_user: user.id_user,
                id_resep: props.resepData.id_resep
            })
        });
        const data = await response.json();
        if (response.ok) {
            isSaved.value = true;
        } else {
            throw new Error(data.message || 'Failed to save recipe');
        }
    } catch (error) {
        console.error('Error saving recipe:', error);
    }
};

const unsaveRecipe = async () => {
    try {
        const response = await fetch('/api/unsave-recipe', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRF-TOKEN': document.querySelector('meta[name="csrf-token"]').content
            },
            body: JSON.stringify({
                id_user: user.id_user,
                id_resep: props.resepData.id_resep
            })
        });

        const data = await response.json();
        if (response.ok) {
            isSaved.value = false;
        } else {
            throw new Error(data.message || 'Failed to unsave recipe');
        }
    } catch (error) {
        console.error('Error unsaving recipe:', error);
    }
};
</script>


<template>
    <button @click="toggleSave" class="btn m-2 p-2 border border-dark"
        :class="isSaved ? 'btn-success' : 'btn-warning', user ? '' : 'd-none'">
        <i :class="isSaved ? 'bi bi-bookmark-check-fill h5 text-white' : 'bi h5 bi-bookmark-plus-fill text-dark'"></i>
    </button>

</template>