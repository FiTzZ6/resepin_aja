<script setup>
import "bootstrap-icons/font/bootstrap-icons.css";
import { Link, usePage } from '@inertiajs/vue3'
import Login from './Login.vue';
import Logout from './Logout.vue';
import Register from './Register.vue';
import Searchbar from './components/Searchbar.vue';
import { ref, nextTick } from 'vue'
import axios from 'axios'

const userData = usePage().props.auth_user;

const message = ref('')
const chats = ref([])
const isOpen = ref(false)
const imageFiles = ref([])
const detectedIngredients = ref([])
const loading = ref(false) // status loading

// ✅ Toggle chatbot
const toggleChat = () => {
  isOpen.value = !isOpen.value
  if (isOpen.value) scrollToBottom()
}

// ✅ Scroll otomatis
const scrollToBottom = () => {
  nextTick(() => {
    const container = document.querySelector('.chatbot-body')
    if (container) {
      container.scrollTop = container.scrollHeight
    }
  })
}

// ✅ Kirim pesan teks
const sendMessage = async () => {
  if (!message.value.trim()) return
  const msg = message.value
  message.value = ''
  await sendToChatbot(msg)
}

// ✅ Kirim gambar ke backend
const sendImage = async () => {
  if (!imageFiles.value.length) {
    alert('Pilih minimal satu gambar!')
    return
  }

  chats.value.push({
    user: `📷 Mengirim ${imageFiles.value.length} gambar...`,
    bot: 'Memproses...'
  })
  scrollToBottom()

  const formData = new FormData()
  imageFiles.value.forEach((file, i) => {
    formData.append('files[]', file)
  })

  try {
    loading.value = true
    const res = await axios.post('/chatbot/images', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })

    if (res.data.status === 'success') {
      const ingredients = res.data.data.map(d => d.predicted_label)

      detectedIngredients.value.push(...ingredients)

      chats.value[chats.value.length - 1].bot =
        `🧠 Terdeteksi bahan: ${ingredients.join(', ')}`

      // redirect ke search
      setTimeout(() => {
        window.location.href =
          `/resepcari?cari_bahan=${encodeURIComponent(ingredients.join(','))}`
      }, 1500)
    }

  } catch (err) {
    console.error(err)
    chats.value[chats.value.length - 1].bot =
      '⚠️ Gagal memproses gambar.'
  } finally {
    loading.value = false
    imageFiles.value = []
    scrollToBottom()
  }
}


// ✅ Kirim pesan teks ke chatbot Flask via Laravel
const sendToChatbot = async (msg) => {
  chats.value.push({ user: msg, bot: '...' })
  scrollToBottom()

  try {
    loading.value = true
    const res = await axios.post('/chatbot', { message: msg })
    const data = res.data?.data || {}

    // ✅ Deteksi respon redirect dari chatbot
    if (data.type === "redirect" && data.url) {
      chats.value[chats.value.length - 1].bot = data.message || "Mengarahkan ke halaman terkait..."
      setTimeout(() => {
        window.location.href = data.url
      }, 1500)
    } else {
      chats.value[chats.value.length - 1].bot = data.message || data.bot_response || "Chatbot tidak merespon."
    }

  } catch (error) {
    console.error(error)
    chats.value[chats.value.length - 1].bot = '⚠️ Terjadi kesalahan saat menghubungi chatbot.'
  } finally {
    loading.value = false
    scrollToBottom()
  }
}

// ✅ Event saat file dipilih
const handleFileChange = (e) => {
  imageFiles.value = Array.from(e.target.files)
  console.log('File dipilih:', imageFiles.value.map(f => f.name))
}
</script>

<template>
  <!-- Navbar -->
  <nav class="navbar navbar-expand-md" style="background-color: rgb(255, 110, 85)">
    <div class="container-fluid">
      <Link class="navbar-brand p-0" href="/"><img src="../../../public/assets/Logo.png" alt="" width="75" height="75">
      </Link>
      <button class="navbar-toggler bg-warning" type="button" data-bs-toggle="collapse"
        data-bs-target="#navbarSupportedContent">
        <span class="navbar-toggler-icon"></span>
      </button>
      <div class="collapse navbar-collapse" id="navbarSupportedContent">
        <Searchbar />
        <ul class="navbar-nav mb-2 mb-md-0">
          <li class="nav-item me-2">
            <Link class="nav-link active" href="/">Beranda</Link>
          </li>
          <li class="nav-item me-2">
            <Link class="nav-link" href="/resepcari">Resep</Link>
          </li>

          <!-- ✅ Jika login -->
          <li class="nav-item" v-if="userData">
            <a class="nav-link dropdown-toggle" href="#" role="button" data-bs-toggle="dropdown">
              <img src="../../../public/assets/muehe.png" class="me-1 rounded-5" width="30" height="30" />
              <span class="fw-bold text-dark">{{ userData.username }}</span>
            </a>
            <div class="dropdown-menu dropdown-menu-end me-2 p-0">
              <div
                class="d-flex flex-column flex-lg-row align-items-stretch justify-content-start p-3 rounded-3 shadow-lg">
                <nav class="col-lg-8">
                  <ul class="list-unstyled d-flex flex-column gap-2">
                    <li>
                      <Link href="/tambahresep"
                        class="btn btn-hover-light rounded-2 d-flex align-items-start gap-2 py-2 px-3 lh-sm text-start">
                        <i class="bi bi-database-fill-add text-success" style="font-size: 24px;"></i>
                        <div><strong class="d-block">Tambah Resep</strong><small class="text-secondary">Tambahkan resep
                            sendiri</small></div>
                      </Link>
                    </li>
                    <li>
                      <Link :href="`/tersimpanresep/${userData.id_user}`"
                        class="btn btn-hover-light rounded-2 d-flex align-items-start gap-2 py-2 px-3 lh-sm text-start">
                        <i class="bi bi-bookmark-star-fill text-primary" style="font-size: 24px;"></i>
                        <div><strong class="d-block">Resep Tersimpan</strong><small class="text-secondary">Resep
                            simpanan
                            pengguna</small></div>
                      </Link>
                    </li>
                  </ul>
                </nav>
                <div class="d-none d-lg-block vr mx-4 opacity-10">&nbsp;</div>
                <hr class="d-lg-none" />
                <div class="col-lg-auto">
                  <nav>
                    <ul class="d-flex flex-column gap-2 list-unstyled small">
                      <li>
                        <Link :href='`/profil/${userData.id_user}`'
                          class="dropdown-item text-dark fw-bold btn btn-light">Profil</Link>
                      </li>
                      <li><button type="button" class="dropdown-item text-danger fw-bold btn btn-warning"
                          data-bs-toggle="modal" data-bs-target="#LogoutPanel">Logout</button></li>
                    </ul>
                  </nav>
                </div>
              </div>
            </div>
          </li>

          <!-- ✅ Jika belum login -->
          <li class="nav-item" v-else>
            <button type="button" class="fw-bold btn btn-outline-dark" data-bs-toggle="modal"
              data-bs-target="#LoginPanel">Login</button>
          </li>
        </ul>
      </div>
    </div>
  </nav>

  <!-- ✅ Slot konten halaman -->
  <div class="container position-relative">
    <slot />
  </div>

  <div v-if="userData">
    <Logout />
  </div>
  <div v-else>
    <Login />
    <Register />
  </div>

  <!-- ✅ Chatbot -->
  <div class="chatbot-container fixed-bottom end-0 p-3">
    <div v-if="isOpen" class="card shadow-lg" style="width: 350px;">
      <div class="card-header bg-danger text-white d-flex justify-content-between align-items-center">
        <span>Asisten Resepin Aja 🍳</span>
        <button @click="toggleChat" class="btn btn-sm btn-light">×</button>
      </div>

      <div class="card-body chatbot-body" style="height: 300px; overflow-y: auto;">
        <div v-for="(chat, index) in chats" :key="index" class="mb-3">
          <div class="text-primary fw-bold">Kamu:</div>
          <div class="bg-light p-2 rounded">{{ chat.user }}</div>
          <div class="text-success fw-bold mt-1">Chatbot:</div>
          <div class="bg-warning-subtle p-2 rounded">{{ chat.bot }}</div>
        </div>
      </div>

      <div class="card-footer d-flex flex-column gap-2">
        <input v-model="message" @keyup.enter="sendMessage" placeholder="Tanya resep apa hari ini..."
          class="form-control" />
        <input type="file" multiple @change="handleFileChange" class="form-control" />
        <div class="d-flex gap-2">
          <button @click="sendMessage" class="btn btn-danger flex-grow-1" :disabled="loading">Kirim</button>
          <button @click="sendImage" class="btn btn-warning flex-grow-1" :disabled="loading">Kirim Gambar</button>
        </div>
      </div>
    </div>

    <!-- Tombol buka chatbot -->
    <button v-else class="btn btn-danger rounded-circle shadow-lg" style="width: 60px; height: 60px;"
      @click="toggleChat">💬</button>
  </div>

  <!-- Footer -->
  <div class="container">
    <footer class="d-flex flex-wrap justify-content-between align-items-center py-3 my-4 border-top">
      <div class="col-md-4 d-flex align-items-center">
        <a href="/" class="mb-3 me-2 mb-md-0 text-body-secondary text-decoration-none lh-1" aria-label="Bootstrap">
          <svg class="bi" width="30" height="24" aria-hidden="true">
            <use xlink:href="#bootstrap"></use>
          </svg>
        </a>
        <span class="mb-3 mb-md-0 text-body-secondary">© 2025 Ger Ger Jeger. Inc</span>
      </div>
      <ul class="nav col-md-4 justify-content-end list-unstyled d-flex">
        <li class="ms-3"><a class="text-body-secondary" href="#"><svg class="bi" width="24" height="24">
              <use xlink:href="#instagram"></use>
            </svg></a></li>
        <li class="ms-3"><a class="text-body-secondary" href="#"><svg class="bi" width="24" height="24">
              <use xlink:href="#facebook"></use>
            </svg></a></li>
      </ul>
    </footer>
  </div>
</template>

<style scoped>
.chatbot-container {
  position: fixed;
  bottom: 20px;
  right: 20px;
  z-index: 9999;
}
</style>
