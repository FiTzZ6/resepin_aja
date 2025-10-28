<script setup>
import App from './App.vue';
import { onMounted, ref } from 'vue';
import ResepCard from './components/ResepCard.vue';

document.title = "Kumpulan Resep";

const dataResep = ref([]);

const form = ref({
	cari_resep: '',
	user_resep: '',
	ktg_masak: [],
	tgl_masak: [],
	cari_bahan: '',
	sort: '',
	rating: [],
	ids: null
});

const kategoriResep = ["Makanan Ringan", "Makanan Berat", "Minuman", "Snack", "Dessert"];
const ratingOptions = [5, 4, 3, 2, 1, 0];

// ✅ Helper: ambil query param sebagai array (baik [] atau tanpa [])
const getParamArray = (urlParams, key) => {
	return urlParams.getAll(key).length
		? urlParams.getAll(key)
		: (urlParams.get(key) ? [urlParams.get(key)] : []);
};

// ✅ Update form dari URL
const updateFormFromURL = () => {
	const urlParams = new URLSearchParams(window.location.search);

	form.value = {
		cari_resep: urlParams.get('cari_resep') || '',
		user_resep: getParamArray(urlParams, 'user_resep[]').join(',') || urlParams.get('user_resep') || '',
		ktg_masak: getParamArray(urlParams, 'ktg_masak[]'),
		tgl_masak: getParamArray(urlParams, 'tgl_masak[]'),
		cari_bahan: urlParams.get('cari_bahan') || '',
		sort: urlParams.get('sort') || '',
		rating: getParamArray(urlParams, 'rating[]').map(Number),
		ids: urlParams.get('ids') || null
	};

	// ✅ Rating Range (ex: ?min_rating=2&max_rating=4)
	const minRating = urlParams.get('min_rating');
	const maxRating = urlParams.get('max_rating');
	if (minRating && maxRating) {
		form.value.rating = Array.from({ length: maxRating - minRating + 1 }, (_, i) => Number(minRating) + i);
	}

	// ✅ Quick filter (ex: ?rating_lowest)
	if (urlParams.get('rating_lowest')) {
		form.value.rating = [0, 1, 2];
	}
};

// ✅ Fetch resep dari API
const fetchResep = async () => {
	const params = new URLSearchParams();

	const appendArray = (key, arr) => arr.forEach(item => params.append(key, item));

	if (form.value.ids) params.append('ids', form.value.ids);
	if (form.value.cari_resep) params.append('cari_resep', form.value.cari_resep);

	const users = typeof form.value.user_resep === 'string'
		? form.value.user_resep.split(',').map(u => u.trim()).filter(u => u)
		: form.value.user_resep;

	appendArray('user_resep[]', users);
	appendArray('ktg_masak[]', form.value.ktg_masak);
	appendArray('tgl_masak[]', form.value.tgl_masak);
	appendArray('rating[]', form.value.rating);

	if (form.value.cari_bahan) params.append('cari_bahan', form.value.cari_bahan);
	if (form.value.sort) params.append('sort', form.value.sort);

	const queryString = params.toString();
	window.history.pushState({}, '', '/resepcari?' + queryString);

	try {
		const res = await fetch('/api/resepcari?' + queryString);
		const json = await res.json();
		dataResep.value = json.data;

		document.getElementById('filtermenu')?.classList.remove('show');
	} catch (error) {
		console.error('Error fetching recipes:', error);
	}
};

// ✅ Saat halaman dimuat
onMounted(() => {
	updateFormFromURL();
	fetchResep();
});

// ✅ Back / Forward
window.addEventListener('popstate', () => {
	updateFormFromURL();
	fetchResep();
});
</script>


<template>
	<App>
		<a class="btn btn-dark mt-3" data-bs-toggle="collapse" href="#filtermenu">Filter Spesifik</a>
		<div class="collapse" id="filtermenu">
			<div class="mt-3 p-2 bg-light border rounded-3">
				<h5><b>Filter Spesifik</b></h5>
				<form @submit.prevent="fetchResep">
					<div class="row">
						<div class="col-12 col-md-4 border-end">
							<div class="mb-2">
								<label class="form-label">Nama Resep</label>
								<input type="text" v-model="form.cari_resep" class="form-control form-control-sm"
									placeholder="Rendang Crispy...">
							</div>
							<div class="mb-2">
								<label class="form-label">Nama Pembuat</label>
								<input type="text" v-model="form.user_resep" class="form-control form-control-sm"
									placeholder="Bintang Rendang...">
							</div>
							<div class="mb-2">
								<label class="form-label">Nama Bahan</label>
								<input type="text" v-model="form.cari_bahan" class="form-control form-control-sm"
									placeholder="Telur, Ayam...">
							</div>
							<hr class="d-md-none">
						</div>
						<div class="col-12 col-md-4 border-end">
							<h6>Kategori</h6>
							<div class="form-check" v-for="(kategori, index) in kategoriResep" :key="index">
								<input class="form-check-input" type="checkbox" v-model="form.ktg_masak"
									:value="kategori" :id="`jenis${index}`">
								<label class="form-check-label" :for="`jenis${index}`">{{ kategori }}</label>
							</div>
							<hr class="d-md-none">
							<h6>Rating</h6>
							<div class="d-flex flex-wrap gap-2">
								<div class="form-check" v-for="r in ratingOptions" :key="'rating' + r">
									<input class="form-check-input" type="checkbox" v-model="form.rating" :value="r"
										:id="'rating' + r">
									<label class="form-check-label" :for="'rating' + r">{{ r }} ⭐</label>
								</div>
							</div>
						</div>
						<div class="col-12 col-md-4">
							<h6>Waktu Memasak</h6>
							<div class="form-check">
								<input class="form-check-input" type="checkbox" v-model="form.tgl_masak" value="cepat"
									id="waktu_cepat">
								<label class="form-check-label" for="waktu_cepat">Tercepat (0-15 menit)</label>
							</div>
							<div class="form-check">
								<input class="form-check-input" type="checkbox" v-model="form.tgl_masak" value="lama"
									id="waktu_lama">
								<label class="form-check-label" for="waktu_lama">Terlama (>15 menit)</label>
							</div>
							<hr>
							<button type="submit" class="btn text-white"
								style="background-color: rgb(255, 110, 85);">Cari Sekarang</button>
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
