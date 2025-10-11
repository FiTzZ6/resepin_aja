<script setup>
import "bootstrap-icons/font/bootstrap-icons.css";
import { Link, usePage } from '@inertiajs/vue3'
import Login from './Login.vue';
import Logout from './Logout.vue';
import Register from './Register.vue';
import Searchbar from './components/Searchbar.vue';
import { ref } from 'vue'
import axios from 'axios'

const userData = usePage().props.auth_user;

const message = ref('')
const chats = ref([])
const isOpen = ref(false)

const toggleChat = () => {
  isOpen.value = !isOpen.value
}

const sendMessage = async () => {
  if (!message.value.trim()) return

  const userMsg = message.value
  message.value = ''

  chats.value.push({ user: userMsg, bot: '...' })

  try {
    const res = await axios.post('/api/chatbot', { message: userMsg })
    const data = res.data.data

    // ← ganti bagian ini
    // Jika chatbot merespon dengan redirect
    if (data.type === "redirect" && data.url) {
      chats.value[chats.value.length - 1].bot = data.message || "Mengarahkan ke halaman terkait..."

      // Tunggu sebentar biar pesannya muncul dulu, lalu redirect
      setTimeout(() => {
        window.location.href = data.url
      }, 1500)  // redirect setelah 1.5 detik
    } else {
      // Jika hanya pesan biasa
      chats.value[chats.value.length - 1].bot = data.message || data.bot_response
    }

  } catch (error) {
    console.error(error)
    chats.value[chats.value.length - 1].bot = '⚠️ Terjadi kesalahan saat menghubungi chatbot.'
  }
}


</script>

<template>
  <nav class="navbar navbar-expand-md" style="background-color: rgb(255, 110, 85)">
    <div class="container-fluid">
      <Link class="navbar-brand p-0" href="/"><img src="../../../public/assets/Logo.png" alt="" width="75" height="75">
      </Link>
      <button class="navbar-toggler bg-warning" type="button" data-bs-toggle="collapse"
        data-bs-target="#navbarSupportedContent" aria-controls="navbarSupportedContent" aria-expanded="false"
        aria-label="Toggle navigation">
        <span class="navbar-toggler-icon"></span>
      </button>
      <div class="collapse navbar-collapse" id="navbarSupportedContent">
        <Searchbar />
        <ul class="navbar-nav mb-2 mb-md-0">
          <li class="nav-item me-2">
            <Link class="nav-link active" aria-current="page" href="/">Beranda</Link>
          </li>
          <li class="nav-item me-2">
            <Link class="nav-link" href="/resepcari">Resep</Link>
          </li>
          <!-- User Info -->
          <li class="nav-item" v-if="userData">
            <a class="nav-link dropdown-toggle" href="#" role="button" data-bs-toggle="dropdown" aria-expanded="false">
              <img src="../../../public/assets/muehe.png" class="me-1 rounded-5" alt="..." width="30" height="30" />
              <span class="fw-bold text-dark">{{ userData.username }}</span>
            </a>
            <div class="dropdown-menu dropdown-menu-end me-2 p-0">
              <div
                class="d-flex flex-column flex-lg-row align-items-stretch justify-content-start p-3 rounded-3 shadow-lg"
                data-bs-theme="light">
                <nav class="col-lg-8">
                  <ul class="list-unstyled d-flex flex-column gap-2">
                    <li>
                      <Link href="/tambahresep"
                        class="btn btn-hover-light rounded-2 d-flex align-items-start gap-2 py-2 px-3 lh-sm text-start">
                      <i class="bi bi-database-fill-add text-success" style="font-size: 24px;"></i>
                      <div><strong class="d-block">Tambah Resep</strong> <small class="text-secondary">Tambahkan resep
                          tersendiri</small></div>
                      </Link>
                    </li>
                    <li>
                      <Link :href="`/tersimpanresep/${userData.id_user}`"
                        class="btn btn-hover-light rounded-2 d-flex align-items-start gap-2 py-2 px-3 lh-sm text-start">
                      <i class="bi bi-bookmark-star-fill text-primary" style="font-size: 24px;"></i>
                      <div><strong class="d-block">Resep Tersimpan</strong> <small class="text-secondary">Resep
                          simpanan pengguna</small></div>
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
                          class="dropdown-item text-dark fw-bold btn btn-light">
                        Profil
                        </Link>
                      </li>
                      <li>
                        <button type="button" class="dropdown-item text-danger fw-bold btn btn-warning"
                          data-bs-toggle="modal" data-bs-target="#LogoutPanel">
                          Logout
                        </button>
                      </li>

                    </ul>
                  </nav>
                </div>
              </div>
            </div>
          </li>
          <li class="nav-item" v-else>
            <button type="button" class="fw-bold btn btn-outline-dark" data-bs-toggle="modal"
              data-bs-target="#LoginPanel">
              Login
            </button>
          </li>
        </ul>
      </div>
    </div>
  </nav>

  <!-- KONTEN -->
  <div class="container position-relative">
    <slot />
  </div>
  <div v-if="userData">
    <Logout></Logout>
  </div>
  <div v-else>
    <Login></Login>
    <Register></Register>
  </div>

  <!-- 🧠 Chatbot Widget -->
  <div class="chatbot-container fixed-bottom end-0 p-3">
    <div v-if="isOpen" class="card shadow-lg" style="width: 350px;">
      <div class="card-header bg-danger text-white d-flex justify-content-between align-items-center">
        <span>Asisten Resepin Aja 🍳</span>
        <button @click="toggleChat" class="btn btn-sm btn-light">×</button>
      </div>

      <div class="card-body" style="height: 300px; overflow-y: auto;">
        <div v-for="(chat, index) in chats" :key="index" class="mb-3">
          <div class="text-primary fw-bold">Kamu:</div>
          <div class="bg-light p-2 rounded">{{ chat.user }}</div>
          <div class="text-success fw-bold mt-1">Chatbot:</div>
          <div class="bg-warning-subtle p-2 rounded">{{ chat.bot }}</div>
        </div>
      </div>

      <div class="card-footer d-flex">
        <input v-model="message" @keyup.enter="sendMessage" placeholder="Tanya resep apa hari ini..."
          class="form-control me-2" />
        <button @click="sendMessage" class="btn btn-danger">Kirim</button>
      </div>
    </div>

    <!-- Tombol untuk buka chatbot -->
    <button v-else class="btn btn-danger rounded-circle shadow-lg" style="width: 60px; height: 60px;"
      @click="toggleChat">
      💬
    </button>
  </div>


  <!-- FOOTER -->
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
        <li class="ms-3">
          <a class="text-body-secondary" href="#" aria-label="Instagram">
            <svg class="bi" width="24" height="24" aria-hidden="true">
              <use xlink:href="#instagram"></use>
            </svg></a>
        </li>
        <li class="ms-3">
          <a class="text-body-secondary" href="#" aria-label="Facebook">
            <svg class="bi" width="24" height="24">
              <use xlink:href="#facebook"></use>
            </svg></a>
        </li>
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
  /* biar muncul di atas elemen lain */
}
</style>
