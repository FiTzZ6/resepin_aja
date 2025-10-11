<script setup>
import { onMounted, ref } from 'vue'
import { Link, usePage, router} from '@inertiajs/vue3'
import StarRating from './components/StarRating.vue';
import SaveButton from './components/SaveButton.vue';
import App from './App.vue';

document.title = "Detail Resep";
const data = defineProps({
    resepDetail: Array
})

const userData = usePage().props.auth_user;

const dataRating = ref([])
const rating = ref(0);
const comment = ref('');
const existingRating = ref(null);
const isLoading = ref(false);
const isFetching = ref(false);

onMounted(async () => {
    isFetching.value = true;
    await fetchAllRating()
})

const fetchAllRating = async () =>{
    try {
        if (userData){
            await fetchUserRating();
        }
        const res = await fetch(`/api/ratingresep/${data.resepDetail["resep"].id_resep}`)
        if (!res.ok) throw new Error('Failed to fetch ratings');
        const json = await res.json()
        dataRating.value = json.data || [];
    } catch (error) {
        console.error('Error loading data:', error);
    } finally {
        isFetching.value = false;
    }
}

const fetchUserRating = async () => {
    try {
        const response = await fetch(`/api/user-rating/${data.resepDetail["resep"].id_resep}/${data.resepDetail["resep"].id_user}`);
        if (!response.ok) throw new Error('Failed to fetch user rating');
        
        const dataRes = await response.json();
        if (dataRes.exists && dataRes.rating) {
            existingRating.value = dataRes.rating;
            rating.value = dataRes.rating.bintang;
            comment.value = dataRes.rating.komentar || '';
        } else {
            existingRating.value = null;
            rating.value = 0;
            comment.value = '';
        }
    } catch (error) {
        console.error('Error fetching rating:', error);
        existingRating.value = null;
    }
};

const setRating = (stars) => {
    rating.value = stars;
};

const submitRating = async () => {
    isLoading.value = true;
    try {
        const response = await fetch('/api/submit-rating', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRF-TOKEN': document.querySelector('meta[name="csrf-token"]').content
            },
            body: JSON.stringify({
                id_resep: data.resepDetail["resep"].id_resep,
                id_user: data.resepDetail["resep"].id_user,
                bintang: rating.value,
                komentar: comment.value
            })
        });
        console.log(response)
        const dataRes = await response.json();

        if (dataRes.success) {
            await fetchAllRating()
            await fetchUserRating(); // Refresh the rating display
        }
    } catch (error) {
        console.error('Error submitting rating:', error);
    } finally {
        isLoading.value = false;
    }
};

// Delete rating
const deleteRating = async () => {
    if (!confirm('Are you sure you want to delete your rating?')) return;

    isLoading.value = true;

    try {
        const response = await fetch('/api/del-rating', {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRF-TOKEN': document.querySelector('meta[name="csrf-token"]').content
            },
            body: JSON.stringify({
                id_resep: data.resepDetail["resep"].id_resep,
                id_user: data.resepDetail["resep"].id_user
            })
        });

        const dataRes = await response.json();

        if (dataRes.success) {
            existingRating.value = null;
            rating.value = 0;
            comment.value = '';
            await fetchAllRating()
        }
    } catch (error) {
        console.error('Error deleting rating:', error);
    } finally {
        isLoading.value = false;
    }
};

const deleteResep = async (id_resep) => {
  if (!confirm('Apakah Anda yakin ingin menghapus resep ini?')) {
    return;
  }
  try {
    const response = await fetch('/api/deleteresep', {
      method: 'DELETE',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRF-TOKEN': document.querySelector('meta[name="csrf-token"]').content,
      },
      body: JSON.stringify({ id_resep }),
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.message || 'Failed to delete recipe');
    }

    alert(data.message || 'Resep berhasil dihapus');
    router.visit('/'); 
  } catch (error) {
    alert(error.message || 'Terjadi kesalahan saat menghapus resep');
    console.error(error);
  }
};
</script>
<template>
    <App>
        <div class="row mt-3">
            <div class="col-12 col-sm-5 col-md-4">
                <img :src='`http://localhost:8000/storage/${resepDetail["resep"].gambar}`' alt=""
                    class="w-100 rounded-4">
            </div>
            <div class="col-12 col-sm-7 col-md-8 py-3">
                <div class="row">
                    <div class="col-12 col-md-8 d-flex align-items-center">
                        <h3 class="fw-bold">{{ resepDetail['resep'].judul }}</h3>
                    </div>
                    <div class="col-12 col-md-4 d-flex justify-content-end">
                        <SaveButton :resepData="resepDetail['resep']"/>
                        <div :class="userData && resepDetail['resep'].id_user == userData.id_user? 'd-inline' : 'd-none'">
                            <Link :href="`/editresep/${resepDetail['resep'].id_resep}`" class="btn btn-warning m-2 p-2 border border-dark"><i class="bi h5 bi-pencil-fill"></i></Link>
                            <button type="button" @click="deleteResep(resepDetail['resep'].id_resep)" class="btn btn-danger m-2 p-2 border border-dark"><i class="bi h5 bi-trash-fill"></i></button>
                        </div>
                    </div>
                </div>
                <h6 class="my-1">Oleh
                    <Link :href='`/profil/${resepDetail["resep"].id_user}`' class="fw-bold">{{
                        resepDetail['resep'].username }}</Link>
                </h6>
                <div class="row my-2">
                    <div class="col-12">
                        <StarRating :rating="resepDetail['resep'].bintang" :customs="'h4 me-2'" /> <span
                            class="text-warning fw-bold h5">{{ resepDetail['resep'].bintang ? resepDetail['resep'].bintang : '0' }}/5 ({{
                                resepDetail['resep'].jml_bintang }})</span>
                    </div>
                    <div class="col-4"><i class="bi bi-fork-knife"></i> {{ resepDetail['resep'].ktg_masak }}</div>
                    <div class="col-4"><i class="bi bi-stopwatch-fill"></i> {{ resepDetail['resep'].wkt_masak }} Menit
                    </div>
                    <div class="col-4"><i class="bi bi-person-fill"></i> {{ resepDetail['resep'].prs_masak }} Porsi
                    </div>
                </div>
                <p>{{ resepDetail['resep'].deskripsi }}</p>
            </div>
            <div class="col-12">
                <nav>
                    <div class="nav nav-tabs mt-2 border-dark" id="nav-tab" role="tablist">
                        <button class="nav-link active" style="width: 33.3%;" id="nav-home-tab" data-bs-toggle="tab"
                            data-bs-target="#BahanPage" type="button" role="tab" aria-selected="true">
                            Bahan
                        </button>
                        <button class="nav-link" style="width: 33.3%;" id="nav-profile-tab" data-bs-toggle="tab"
                            data-bs-target="#AlatPage" type="button" role="tab">
                            Alat
                        </button>
                        <button class="nav-link" style="width: 33.3%;" id="nav-profile-tab" data-bs-toggle="tab"
                            data-bs-target="#CaraPage" type="button" role="tab">
                            Cara Masak
                        </button>
                    </div>
                </nav>
                <div class="tab-content" id="nav-tabContent">
                    <div class="tab-pane fade show active" id="BahanPage" role="tabpanel" aria-labelledby="nav-home-tab"
                        tabindex="0">
                        <div class="my-3">
                            <h5><b>Bahan-Bahan</b></h5>
                            <div class="row my-4" v-for="(bahan, index) in resepDetail['bahan']" :key="bahan.id_bahan">
                                <div class="col-2 col-md-1 text-center"><span class="bg-warning p-2 px-3 rounded-5">{{
                                    index + 1 }}</span></div>
                                <div class="col-8-md col-7"><span class="ms-2"></span>{{ bahan.nama_bahan }}</div>
                                <div class="col-3">{{ bahan.jml_bahan }} {{ bahan.stn_bahan }}</div>
                            </div>
                        </div>
                    </div>
                    <div class="tab-pane fade" id="AlatPage" role="tabpanel" aria-labelledby="nav-profile-tab"
                        tabindex="0">
                        <div class="my-3">
                            <h5><b>Alat-Alat</b></h5>
                            <div class="row my-4" v-for="(alat, index) in resepDetail['alat']" :key="alat.id_alat">
                                <div class="col-2 col-md-1 text-center"><span class="bg-warning p-2 px-3 rounded-5">{{
                                    index + 1 }}</span></div>
                                <div class="col-8-md col-7"><span class="ms-2">{{ alat.nama_alat }}</span></div>
                            </div>
                        </div>
                    </div>
                    <div class="tab-pane fade" id="CaraPage" role="tabpanel" aria-labelledby="nav-profile-tab"
                        tabindex="0">
                        <div class="my-3">
                            <h5><b>Cara Memasak Resep</b></h5>
                            <div class="row my-4" v-for="(langkah, index) in resepDetail['langkah']"
                                :key="langkah.id_langkah">
                                <div class="col-2 col-md-1 text-center"><span class="bg-warning p-2 px-3 rounded-5">{{
                                    langkah.urutan }}</span></div>
                                <div class="col-11-md col-10">{{ langkah.cara_langkah }}</div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            <hr>

            <div class="col-12 col-md-6 mt-3" v-if="userData">
                <h5><b>Berikan Ulasanmu</b></h5>
                <form @submit.prevent="submitRating">
                    <!-- Star Rating -->
                    <div class="star-rating mb-2">
                        <i v-for="i in 5" :key="i" @click="setRating(i)" class="bi bi-star-fill h4 me-2" :class="{
                            'text-warning': i <= rating,
                            'text-secondary': i > rating,
                            'cursor-pointer': !existingRating
                        }" :style="existingRating ? 'cursor: default' : ''"></i>
                        <span class="text-warning h5 ms-3">{{ rating }}/5</span>
                        <span v-if="existingRating" class="text-muted small ms-2">
                            (Submitted on {{ new Date(existingRating.created_at).toLocaleDateString() }})
                        </span>
                    </div>

                    <!-- Comment -->
                    <div class="input-group mb-3">
                        <textarea v-model="comment" rows="5" class="form-control rounded-3" placeholder="Ulasan Anda"
                            :disabled="!!existingRating" required></textarea>
                    </div>

                    <!-- Submit/Delete Buttons -->
                    <div class="d-flex gap-2">
                        <button v-if="!existingRating" type="submit" class="btn btn-warning"
                            :disabled="isLoading || rating === 0">
                            <span v-if="!isLoading">Submit Rating</span>
                            <span v-else class="spinner-border spinner-border-sm"></span>
                        </button>

                        <button v-else type="button" @click="deleteRating" class="btn btn-outline-danger"
                            :disabled="isLoading">
                            <span v-if="!isLoading">Delete Rating</span>
                            <span v-else class="spinner-border spinner-border-sm"></span>
                        </button>
                    </div>
                </form>
            </div>
            <div class="col-12 mt-3" :class="userData ? 'col-md-6' : ''">
                <h5><b>Ulasan Resep Ini</b></h5>
                <div class="shadow-sm border p-3 rounded-3 my-2" v-for="rating in dataRating" :key="rating.id_rating"
                    v-if="dataRating.length">
                    <div class="row">
                        <div class="col-6">
                            <Link :href='`/profil/${rating.id_user}`'>
                            <img src="../../../public/assets/muehe.png" class="me-1 rounded-5" alt="..." width="30"
                                height="30" />
                            <span class="fw-bold text-dark">{{ rating.username }}</span>
                            </Link>
                        </div>
                        <div class="col-6 text-end">
                            <StarRating :rating="rating.bintang" />
                            <span class="text-warning fw-bold ms-2">{{ rating.bintang }}/5</span>
                        </div>
                        <div class="col-12 mt-2">
                            {{ rating.komentar }}
                        </div>
                    </div>
                </div>
                <p class="text-center my-3" v-else>Belum ada yang berkomentar</p>
            </div>
        </div>
    </App>
</template>

<style scoped>
.active {
    border-color: black black white black !important;
}
</style>