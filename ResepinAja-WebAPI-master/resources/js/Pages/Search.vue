<script setup>
import App from './App.vue';
import { onMounted, ref } from 'vue'
import { router } from '@inertiajs/vue3';
import ResepCard from './components/ResepCard.vue';

document.title = "Kumpulan Resep";
const dataResep = ref([])
const form = ref({
	cari_resep: '',
	user_resep: '',
	ktg_masak: [],
	tgl_masak: 'desc'
});

const kategoriResep = ["Makanan Ringan", "Makanan Berat", "Minuman", "Snack", "Dessert"];

const updateFormFromURL = () => {
	const urlParams = new URLSearchParams(window.location.search);
	form.value = {
		cari_resep: urlParams.get('cari_resep') || '',
		user_resep: urlParams.get('user_resep') || '',
		ktg_masak: urlParams.getAll('ktg_masak[]') || [],
		tgl_masak: urlParams.get('tgl_masak') || 'desc'
	};
};

onMounted(() => {
	updateFormFromURL();
	fetchResep();
	// router.on('navigate', () => {
	// 	updateFormFromURL();
	// 	fetchResep();
	// });
});

const fetchResep = async () => {
	const params = new URLSearchParams();

	if (form.value.cari_resep) params.append('cari_resep', form.value.cari_resep);
	if (form.value.user_resep) params.append('user_resep', form.value.user_resep);
	form.value.ktg_masak.forEach(item => params.append('ktg_masak[]', item));
	if (form.value.tgl_masak) params.append('tgl_masak', form.value.tgl_masak);

	const queryString = params.toString();
	const newUrl = '/resepcari?' + queryString;
	window.history.pushState({}, '', newUrl);
	try {
		const res = await fetch('/api/resepcari?' + queryString);
		const json = await res.json();
		dataResep.value = json.data;
		document.getElementById('filtermenu').classList.remove('show');
	} catch (error) {
		console.error('Error fetching recipes:', error);
	}
};
</script>

<template>
	<App>
		<!-- <p>{{dataResep}}</p> -->
		<a class="btn btn-dark mt-3" data-bs-toggle="collapse" href="#filtermenu">Filter
			Spesifik</a>
		<div class="collapse" id="filtermenu">
			<div class="mt-3 p-2 bg-light border rounded-3">
				<h5><b>Filter Spesifik</b></h5>
				<form @submit.prevent="fetchResep">
					<div class="row">
						<div class="col-12 col-md-4 border-end">
							<div class="mb-2">
								<label for="exampleFormControlInput1" class="form-label">Nama Resep</label>
								<input type="text" v-model="form.cari_resep" class="form-control form-control-sm"
									value={{form.value.cari_resep}} id="exampleFormControlInput1" name="cari_resep"
									placeholder="Rendang Crispy...">
							</div>
							<div class="mb-2">
								<label for="exampleFormControlInput1" class="form-label">Nama Pembuat</label>
								<input type="text" v-model="form.user_resep" class="form-control form-control-sm"
									id="exampleFormControlInput1" name="user_resep" placeholder="Bintang Rendang...">
							</div>
							<hr class="d-md-none">
						</div>
						<div class="col-12 col-md-4 border-end">
							<div class="form-check" v-for="(kategori, index) in kategoriResep" :key="index">
								<input class="form-check-input" v-model="form.ktg_masak" type="checkbox"
									:value="kategori" name="ktg_masak" :id="`jenis${index}`">
								<label class="form-check-label" :for="`jenis${index}`">
									{{ kategori }}
								</label>
							</div>
							<hr class="d-md-none">
						</div>
						<div class="col-12 col-md-4">
							<div class="form-check">
								<input class="form-check-input" v-model="form.tgl_masak" type="radio" name="tgl_masak"
									id="tgl_masak1" value="desc" checked>
								<label class="form-check-label" for="tgl_masak1">
									Terbaru
								</label>
							</div>
							<div class="form-check">
								<input class="form-check-input" v-model="form.tgl_masak" type="radio" name="tgl_masak"
									id="tgl_masak2" value="asc">
								<label class="form-check-label" for="tgl_masak2">
									Terlama
								</label>
							</div>
							<hr>
							<button type="submit" class="btn text-white"
								style=" background-color: rgb(255, 110, 85);">Cari
								Sekarang</button>
						</div>
					</div>
				</form>
			</div>
		</div>
		<div class="container-lg">
			<div class="row">
				<div class="col-12 col-md-6 col-lg-4 p-2" v-for="resep in dataResep" :key="resep.id_resep">
					<ResepCard :resepData="resep" />
				</div>
			</div>
		</div>
	</App>
</template>