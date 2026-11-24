<script setup>
import "bootstrap-icons/font/bootstrap-icons.css";
import { Link, usePage } from '@inertiajs/vue3'
import Login from './Login.vue';
import Logout from './Logout.vue';
import Register from './Register.vue';
import Searchbar from './components/Searchbar.vue';
import { ref, nextTick, onMounted, onUnmounted } from 'vue'
import axios from 'axios'

const userData = usePage().props.auth_user;
const message = ref('')
const chats = ref([])
const isOpen = ref(false)
const imageFiles = ref([])
const imagePreviews = ref([])
const allPreviewUrls = ref([])
const loading = ref(false)
const currentTime = ref('')
const scrolled = ref(false)
const mobileMenuOpen = ref(false)
const isDark = ref(true)

let timeInterval = null

const updateTime = () => {
  currentTime.value = new Date().toLocaleString('id-ID', {
    timeZone: 'Asia/Jakarta', hour: '2-digit', minute: '2-digit',
    day: '2-digit', month: 'short', year: 'numeric'
  })
}

const applyTheme = (dark) => {
  document.documentElement.setAttribute('data-theme', dark ? 'dark' : 'light')
  localStorage.setItem('ra-theme', dark ? 'dark' : 'light')
}

const toggleTheme = () => {
  isDark.value = !isDark.value
  applyTheme(isDark.value)
}

onMounted(() => {
  const saved = localStorage.getItem('ra-theme')
  isDark.value = saved ? saved === 'dark' : true
  applyTheme(isDark.value)
  updateTime()
  timeInterval = setInterval(updateTime, 1000)
  window.addEventListener('scroll', () => { scrolled.value = window.scrollY > 24 })
})
onUnmounted(() => {
  clearInterval(timeInterval)
  allPreviewUrls.value.forEach(url => URL.revokeObjectURL(url))
})

const scrollToBottom = () => nextTick(() => {
  const el = document.querySelector('.cb-messages')
  if (el) el.scrollTop = el.scrollHeight
})

const toggleChat = () => { isOpen.value = !isOpen.value; if (isOpen.value) scrollToBottom() }

const sendMessage = async () => {
  if (!message.value.trim()) return
  const msg = message.value; message.value = ''
  chats.value.push({ user: msg, bot: null })
  scrollToBottom()
  try {
    loading.value = true
    const res = await axios.post('/chatbot', { message: msg })
    const d = res.data?.data || {}
    chats.value[chats.value.length - 1].bot = d.message || d.bot_response || 'Tidak ada respon.'
    if (d.type === 'redirect' && d.url) setTimeout(() => { window.location.href = d.url }, 1200)
  } catch { chats.value[chats.value.length - 1].bot = 'Gagal terhubung.' }
  finally { loading.value = false; scrollToBottom() }
}

const sendImage = async () => {
  if (!imageFiles.value.length) return

  chats.value.push({
    user: '',
    userImages: [...imagePreviews.value],
    bot: null
  })

  scrollToBottom()

  const fd = new FormData()
  imageFiles.value.forEach(f => fd.append('files[]', f))

  try {
    loading.value = true

    const res = await axios.post('/chatbot/images', fd)

    if (res.data.status === 'success') {
      const predictions = res.data.data || []

      // Ambil hanya prediksi dengan confidence >= 45%
      const accepted = predictions.filter(
        item => item.is_accepted === true
      )

      const rejected = predictions.filter(
        item => item.is_accepted === false
      )

      // Jika tidak ada foto yang lolos
      if (accepted.length === 0) {
        const highestConfidence = predictions.length
          ? Math.max(...predictions.map(item => item.confidence))
          : 0

        chats.value[chats.value.length - 1].bot =
          `Maaf, bahan makanan belum dapat dikenali dengan yakin. ` +
          `Confidence tertinggi ${highestConfidence}%. ` +
          `Silakan unggah foto yang lebih jelas.`

        return
      }

      // Ambil nama bahan yang lolos
      const ingredients = accepted.map(
        item => item.predicted_label
      )

      let response = `Bahan berhasil dikenali: ${ingredients.join(', ')}.`

      if (rejected.length > 0) {
        response += ` ${rejected.length} foto tidak digunakan karena confidence di bawah 45%.`
      }

      chats.value[chats.value.length - 1].bot = response

      // Kirim hanya bahan yang lolos ke pencarian resep
      setTimeout(() => {
        window.location.href =
          `/resepcari?cari_bahan=${encodeURIComponent(ingredients.join(','))}`
      }, 1500)
    } else {
      chats.value[chats.value.length - 1].bot =
        'Gagal memproses gambar. Silakan coba kembali.'
    }

  } catch (error) {
    chats.value[chats.value.length - 1].bot =
      'Gagal memproses gambar. Periksa koneksi ke server.'

  } finally {
    loading.value = false
    imageFiles.value = []
    imagePreviews.value = []
    scrollToBottom()
  }
}

const handleFileChange = (e) => {
  const files = Array.from(e.target.files || [])
  imageFiles.value = files

  // Buat URL preview agar gambar langsung terlihat sebelum dikirim.
  imagePreviews.value = files.map(file => {
    const url = URL.createObjectURL(file)
    allPreviewUrls.value.push(url)
    return url
  })
}
</script>

<template>
  <div class="shell">

    <!-- ═══ NAVBAR ═══ -->
    <nav class="navbar" :class="{ 'navbar--raised': scrolled }">
      <div class="nav-inner">

        <Link href="/" class="nav-logo">
          <div class="logo-icon">
            <img src="../../../public/assets/Logo.png" width="30" height="30" alt="" />
          </div>
          <span class="logo-text">Resepin<em>Aja</em></span>
        </Link>

        <div class="nav-search"><Searchbar /></div>

        <div class="nav-right">
          <Link href="/" class="nav-link">Beranda</Link>
          <Link href="/resepcari" class="nav-link">Resep</Link>

          <template v-if="userData">
            <Link href="/tambahresep" class="btn-primary btn-sm">
              <i class="bi bi-plus-lg"></i> Tambah
            </Link>
            <div class="dropdown">
              <button class="nav-user dropdown-toggle" data-bs-toggle="dropdown">
                <div class="user-ava">{{ userData.username?.charAt(0)?.toUpperCase() }}</div>
                <span class="user-name">{{ userData.username }}</span>
                <i class="bi bi-chevron-down"></i>
              </button>
              <div class="dropdown-menu dropdown-menu-end ra-dropdown">
                <Link :href="`/profil/${userData.id_user}`" class="dd-item">
                  <i class="bi bi-person-circle dd-ic"></i> Profil Saya
                </Link>
                <Link :href="`/tersimpanresep/${userData.id_user}`" class="dd-item">
                  <i class="bi bi-bookmark-heart dd-ic"></i> Tersimpan
                </Link>
                <Link href="/tambahresep" class="dd-item">
                  <i class="bi bi-plus-circle dd-ic"></i> Tambah Resep
                </Link>
                <div class="dd-sep"></div>
                <button class="dd-item dd-item--danger" data-bs-toggle="modal" data-bs-target="#LogoutPanel">
                  <i class="bi bi-box-arrow-right dd-ic"></i> Keluar
                </button>
              </div>
            </div>
          </template>
          <template v-else>
            <button class="btn-primary btn-sm" data-bs-toggle="modal" data-bs-target="#LoginPanel">
              <i class="bi bi-person"></i> Masuk
            </button>
          </template>

          <button class="theme-toggle desktop-theme-toggle" @click="toggleTheme" :aria-label="isDark ? 'Aktifkan tema putih' : 'Aktifkan tema hitam'" :title="isDark ? 'Tema putih' : 'Tema hitam'">
            <i class="bi" :class="isDark ? 'bi-sun-fill' : 'bi-moon-fill'"></i>
          </button>
        </div>

        <!-- Hamburger -->
        <button class="hamburger" @click="mobileMenuOpen = !mobileMenuOpen">
          <i class="bi" :class="mobileMenuOpen ? 'bi-x-lg' : 'bi-list'"></i>
        </button>
      </div>

      <!-- Mobile Menu -->
      <transition name="slide-down">
        <div v-if="mobileMenuOpen" class="mobile-menu">
          <div class="mobile-search"><Searchbar /></div>
          <Link href="/" class="mob-item" @click="mobileMenuOpen=false">Beranda</Link>
          <Link href="/resepcari" class="mob-item" @click="mobileMenuOpen=false">Resep</Link>
          <template v-if="userData">
            <Link href="/tambahresep" class="mob-item" @click="mobileMenuOpen=false"><i class="bi bi-plus-lg"></i> Tambah Resep</Link>
            <Link :href="`/profil/${userData.id_user}`" class="mob-item" @click="mobileMenuOpen=false"><i class="bi bi-person-circle"></i> Profil</Link>
            <Link :href="`/tersimpanresep/${userData.id_user}`" class="mob-item" @click="mobileMenuOpen=false"><i class="bi bi-bookmark-heart"></i> Tersimpan</Link>
            <button class="mob-item mob-item--danger" data-bs-toggle="modal" data-bs-target="#LogoutPanel" @click="mobileMenuOpen=false"><i class="bi bi-box-arrow-right"></i> Keluar</button>
          </template>
          <template v-else>
            <button class="mob-item mob-item--cta" data-bs-toggle="modal" data-bs-target="#LoginPanel" @click="mobileMenuOpen=false">Masuk / Daftar</button>
          </template>
          <div class="mob-theme-row">
            <span class="mob-theme-label">Mode Tampilan</span>
            <button class="theme-toggle" @click="toggleTheme">
              <i class="bi" :class="isDark ? 'bi-sun-fill' : 'bi-moon-fill'"></i>
              {{ isDark ? 'Light Mode' : 'Dark Mode' }}
            </button>
          </div>
        </div>
      </transition>
    </nav>

    <!-- ═══ CONTENT ═══ -->
    <main class="page-main"><slot /></main>

    <!-- Modals -->
    <Logout v-if="userData" />
    <template v-else><Login /><Register /></template>

    <!-- ═══ CHATBOT ═══ -->
    <div class="cb-wrap">
      <transition name="cb-pop">
        <div v-if="isOpen" class="cb-panel">
          <div class="cb-head">
            <div class="cb-head-info">
              <div class="cb-orb"><i class="bi bi-stars"></i></div>
              <div>
                <p class="cb-title">Asisten Resepin</p>
                <p class="cb-sub">Tanya resep apa saja</p>
              </div>
            </div>
            <button @click="toggleChat" class="cb-x"><i class="bi bi-x-lg"></i></button>
          </div>

          <div class="cb-messages">
            <div v-if="!chats.length" class="cb-empty">
              <i class="bi bi-chat-heart"></i>
              <p>Halo! Mau masak apa hari ini? 🍳</p>
            </div>
            <div v-for="(c,i) in chats" :key="i" class="cb-pair">
              <div v-if="c.user || c.userImages?.length" class="bubble bubble-you">
                <span v-if="c.user">{{ c.user }}</span>
                <div v-if="c.userImages?.length" class="cb-chat-images">
                  <img
                    v-for="(image, imageIndex) in c.userImages"
                    :key="imageIndex"
                    :src="image"
                    :alt="`Foto bahan ${imageIndex + 1}`"
                    class="cb-chat-image"
                  />
                </div>
              </div>
              <div class="bubble bubble-bot">
                <span v-if="c.bot === null" class="typing"><span></span><span></span><span></span></span>
                <span v-else>{{ c.bot }}</span>
              </div>
            </div>
          </div>

          <div class="cb-foot">
            <div class="cb-input-row">
              <input v-model="message" @keyup.enter="sendMessage" placeholder="Tanya resep..." class="cb-input" />
              <button @click="sendMessage" :disabled="loading" class="cb-send">
                <i class="bi bi-send-fill"></i>
              </button>
            </div>
            <div v-if="imagePreviews.length" class="cb-selected-images">
              <div class="cb-selected-heading">
                <span>{{ imagePreviews.length }} foto siap dikirim</span>
                <button type="button" class="cb-clear-images" @click="imageFiles = []; imagePreviews = []">Hapus pilihan</button>
              </div>
              <div class="cb-preview-list">
                <img
                  v-for="(image, index) in imagePreviews"
                  :key="index"
                  :src="image"
                  :alt="`Preview foto ${index + 1}`"
                  class="cb-preview-image"
                />
              </div>
            </div>
            <div class="cb-imgrow">
              <label class="cb-imglabel">
                <i class="bi bi-image"></i>
                <span>{{ imageFiles.length ? imageFiles.length + ' foto dipilih' : 'Kirim foto bahan' }}</span>
                <input type="file" multiple accept="image/*" @change="handleFileChange" class="d-none" />
              </label>
              <button v-if="imageFiles.length" @click="sendImage" class="cb-imgbtn" :disabled="loading">
                {{ loading ? 'Memproses...' : 'Kirim foto' }} <i class="bi bi-arrow-right"></i>
              </button>
            </div>
          </div>
        </div>
      </transition>

      <button class="cb-fab" @click="toggleChat" :class="{ 'is-open': isOpen }">
        <i class="bi" :class="isOpen ? 'bi-x-lg' : 'bi-stars'"></i>
      </button>
    </div>

    <!-- ═══ FOOTER ═══ -->
    <footer class="site-footer">
      <div class="footer-inner">
        <div class="footer-brand">
          <img src="../../../public/assets/Logo.png" width="38" height="38" alt="" />
          <div>
            <div class="footer-name">Resepin<em>Aja</em></div>
            <div class="footer-time">{{ currentTime }} WIB</div>
            <div class="footer-copy">© 2025 Ger Ger Jeger. Inc</div>
          </div>
        </div>
        <div class="footer-links">
          <Link href="/" class="footer-link">Beranda</Link>
          <Link href="/resepcari" class="footer-link">Resep</Link>
          <Link href="/tambahresep" class="footer-link">Tambah Resep</Link>
        </div>
        <div class="footer-socials">
          <a href="#" class="soc-btn"><i class="bi bi-instagram"></i></a>
          <a href="#" class="soc-btn"><i class="bi bi-facebook"></i></a>
          <a href="#" class="soc-btn"><i class="bi bi-tiktok"></i></a>
        </div>
      </div>
    </footer>
  </div>
</template>

<style>
/* ════════════════════════════════
   GLOBAL THEME VARIABLES
════════════════════════════════ */
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,700;0,900;1,600&family=Outfit:wght@300;400;500;600;700&display=swap');

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

/* ── BLACK & WHITE THEME ── */
:root, [data-theme="dark"] {
  color-scheme: dark;
  --bg:         #090909;
  --bg2:        #141414;
  --bg3:        #202020;
  --bg4:        #2b2b2b;
  --border:     rgba(255,255,255,0.10);
  --border2:    rgba(255,255,255,0.18);
  --text:       #f5f5f5;
  --text2:      rgba(255,255,255,0.72);
  --text3:      rgba(255,255,255,0.46);
  --text4:      rgba(255,255,255,0.28);
  --gold:       #f2f2f2;
  --accent-text: #090909;
  --gold-light: #ffffff;
  --gold-bg:    rgba(255,255,255,0.09);
  --gold-bd:    rgba(255,255,255,0.24);
  --danger:     #d0d0d0;
  --danger-bg:  rgba(255,255,255,0.08);
  --success:    #eeeeee;
  --nav-bg:     rgba(9,9,9,0.78);
  --nav-raised: rgba(9,9,9,0.97);
  --footer-bg:  #050505;
  --shadow:     0 4px 24px rgba(0,0,0,0.40);
  --shadow-lg:  0 12px 48px rgba(0,0,0,0.58);
  --radius:     14px;
  --radius-lg:  20px;
  --radius-xl:  28px;
}

/* ── WHITE THEME ── */
[data-theme="light"] {
  color-scheme: light;
  --bg:         #ffffff;
  --bg2:        #f7f7f7;
  --bg3:        #eeeeee;
  --bg4:        #e4e4e4;
  --border:     rgba(0,0,0,0.10);
  --border2:    rgba(0,0,0,0.20);
  --text:       #101010;
  --text2:      rgba(0,0,0,0.72);
  --text3:      rgba(0,0,0,0.48);
  --text4:      rgba(0,0,0,0.28);
  --gold:       #111111;
  --accent-text: #ffffff;
  --gold-light: #333333;
  --gold-bg:    rgba(0,0,0,0.06);
  --gold-bd:    rgba(0,0,0,0.20);
  --danger:     #333333;
  --danger-bg:  rgba(0,0,0,0.06);
  --success:    #222222;
  --nav-bg:     rgba(255,255,255,0.82);
  --nav-raised: rgba(255,255,255,0.98);
  --footer-bg:  #eeeeee;
  --shadow:     0 4px 24px rgba(0,0,0,0.08);
  --shadow-lg:  0 12px 48px rgba(0,0,0,0.14);
}

html, body { height: 100%; }
body {
  background: var(--bg);
  color: var(--text);
  font-family: 'Outfit', sans-serif;
  font-size: 15px;
  line-height: 1.6;
  transition: background 0.3s, color 0.3s;
}
a { color: inherit; text-decoration: none; }

/* Konsistensi kontras teks dan kontrol pada kedua tema */
button, input, textarea, select { font: inherit; }
::selection { background: var(--text); color: var(--bg); }
button:focus-visible, a:focus-visible, input:focus-visible,
textarea:focus-visible, select:focus-visible {
  outline: 2px solid var(--text);
  outline-offset: 2px;
}

/* Scrollbar */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: var(--border2); border-radius: 4px; }

/* ════════════════════════════════
   SHARED UTILITIES
════════════════════════════════ */
.tag {
  display: inline-flex; align-items: center; gap: 6px;
  font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.08em;
  padding: 5px 13px; border-radius: 50px;
}
.tag-gold { background: var(--gold-bg); color: var(--gold); border: 1px solid var(--gold-bd); }
.tag-fire { background: var(--gold-bg); color: var(--text2); border: 1px solid var(--border2); }

.btn-primary {
  display: inline-flex; align-items: center; gap: 7px;
  font-size: 14px; font-weight: 600; background: var(--gold); color: var(--accent-text);
  border: none; padding: 10px 22px; border-radius: 50px; cursor: pointer;
  text-decoration: none; transition: all 0.2s; white-space: nowrap;
}
.btn-primary:hover { background: var(--gold-light); transform: translateY(-1px); }
.btn-sm { padding: 8px 18px; font-size: 13px; }

.section-title {
  font-family: 'Playfair Display', serif;
  font-size: clamp(1.7rem, 3vw, 2.6rem); font-weight: 700;
  color: var(--text); line-height: 1.2;
}
.section-title em { color: var(--gold); font-style: italic; }

.resep-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(270px, 1fr));
  gap: 20px;
}

.card-base {
  background: var(--bg2); border: 1px solid var(--border);
  border-radius: var(--radius-lg); padding: 22px;
  transition: border-color 0.2s, box-shadow 0.2s;
}
.card-base:hover { border-color: var(--border2); box-shadow: var(--shadow); }

.field-label {
  font-size: 11px; font-weight: 700; text-transform: uppercase;
  letter-spacing: 0.07em; color: var(--text3); display: flex; align-items: center; gap: 6px;
}
.field-input, .field-select, .field-textarea {
  width: 100%; background: var(--bg3); border: 1px solid var(--border);
  border-radius: 10px; padding: 11px 14px; font-size: 14px; color: var(--text);
  outline: none; transition: border-color 0.15s, background 0.15s;
  font-family: 'Outfit', sans-serif;
}
.field-input:focus, .field-select:focus, .field-textarea:focus {
  border-color: var(--gold); background: var(--bg2);
}
.field-input::placeholder, .field-textarea::placeholder { color: var(--text4); }
.field-textarea { resize: vertical; }
.field-select option { background: var(--bg2); color: var(--text); }

.del-btn {
  width: 36px; height: 36px; border-radius: 9px; flex-shrink: 0;
  background: var(--danger-bg); border: 1px solid var(--border2);
  color: var(--danger); cursor: pointer; transition: all 0.15s;
  display: flex; align-items: center; justify-content: center; font-size: 15px;
}
.del-btn:hover { background: var(--bg4); }
.del-btn:disabled { opacity: 0.3; cursor: not-allowed; }

.add-btn {
  display: inline-flex; align-items: center; gap: 6px;
  font-size: 12px; font-weight: 600;
  background: var(--gold-bg); color: var(--gold); border: 1px solid var(--gold-bd);
  padding: 7px 14px; border-radius: 8px; cursor: pointer; transition: all 0.15s;
}
.add-btn:hover { background: var(--gold-bd); }

.empty-state { text-align: center; padding: 80px 24px; color: var(--text3); }
.empty-state i { font-size: 52px; display: block; margin-bottom: 14px; color: var(--gold); opacity: 0.3; }
.empty-state h3 { font-family: 'Playfair Display', serif; font-size: 1.5rem; color: var(--text2); margin-bottom: 8px; }
.empty-state p { font-size: 14px; }
</style>

<style scoped>
/* ════════════════════════════════
   NAVBAR
════════════════════════════════ */
.shell { min-height: 100vh; display: flex; flex-direction: column; }

.navbar {
  position: fixed; top: 0; left: 0; right: 0; z-index: 1000;
  background: var(--nav-bg);
  backdrop-filter: blur(20px) saturate(160%);
  border-bottom: 1px solid var(--border);
  transition: background 0.3s, border-color 0.3s;
}
.navbar--raised {
  background: var(--nav-raised);
  box-shadow: var(--shadow);
}
.nav-inner {
  max-width: 100%; padding: 0 32px; height: 66px;
  display: flex; align-items: center; gap: 16px;
}
.nav-logo { display: flex; align-items: center; gap: 10px; flex-shrink: 0; }
.logo-icon {
  width: 38px; height: 38px; border-radius: 11px;
  background: var(--gold); display: flex; align-items: center; justify-content: center;
  overflow: hidden;
}
.logo-text {
  font-family: 'Playfair Display', serif; font-size: 21px; font-weight: 700; color: var(--text);
}
.logo-text em { color: var(--gold); font-style: italic; }
.nav-search { flex: 1; max-width: 500ppx; }
.nav-right { display: flex; align-items: center; gap: 6px; flex-shrink: 0; }
.nav-link {
  font-size: 14px; font-weight: 500; color: var(--text2);
  padding: 7px 13px; border-radius: 8px; transition: all 0.15s;
}
.nav-link:hover { color: var(--text); background: var(--bg3); }

.nav-user {
  display: flex; align-items: center; gap: 8px;
  font-size: 14px; font-weight: 500; color: var(--text2);
  background: var(--bg3); border: 1px solid var(--border);
  padding: 5px 12px 5px 5px; border-radius: 50px; cursor: pointer; transition: all 0.15s;
}
.nav-user:hover { border-color: var(--border2); color: var(--text); }
.nav-user .bi-chevron-down { font-size: 11px; opacity: 0.55; }
.user-ava {
  width: 30px; height: 30px; border-radius: 50%;
  background: var(--gold-bg); border: 1.5px solid var(--gold);
  display: flex; align-items: center; justify-content: center;
  font-size: 13px; font-weight: 700; color: var(--gold);
}
.user-name { max-width: 100px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }

.ra-dropdown {
  background: var(--bg2); border: 1px solid var(--border2);
  border-radius: 14px; box-shadow: var(--shadow-lg);
  padding: 6px; min-width: 200px; margin-top: 8px;
}
.dd-item {
  display: flex; align-items: center; gap: 10px; width: 100%;
  font-size: 13px; font-weight: 500; color: var(--text2);
  padding: 9px 12px; border-radius: 9px; background: none; border: none;
  cursor: pointer; text-decoration: none; transition: all 0.15s;
}
.dd-item:hover { background: var(--bg3); color: var(--text); }
.dd-item--danger { color: var(--danger); }
.dd-item--danger:hover { background: var(--danger-bg); }
.dd-ic { font-size: 16px; color: var(--gold); }
.dd-item--danger .dd-ic { color: var(--danger); }
.dd-sep { height: 1px; background: var(--border); margin: 5px 0; }

.theme-toggle {
  display: flex; align-items: center; gap: 7px;
  width: 38px; height: 38px; border-radius: 50%;
  background: var(--bg3); border: 1px solid var(--border);
  color: var(--gold); font-size: 16px; cursor: pointer;
  justify-content: center; transition: all 0.18s; flex-shrink: 0;
}
.theme-toggle:hover { background: var(--gold-bg); border-color: var(--gold-bd); }

.hamburger {
  display: none; background: none; border: none; color: var(--text);
  font-size: 22px; cursor: pointer; padding: 4px; margin-left: auto;
}

.mobile-menu {
  background: var(--bg2); border-top: 1px solid var(--border);
  padding: 16px 24px 24px; display: flex; flex-direction: column; gap: 4px;
}
.mobile-search { margin-bottom: 12px; }
.mob-item {
  display: flex; align-items: center; gap: 10px;
  padding: 11px 14px; border-radius: 10px; font-size: 14px; font-weight: 500;
  color: var(--text2); background: none; border: none; cursor: pointer;
  text-decoration: none; transition: all 0.15s;
}
.mob-item:hover { background: var(--bg3); color: var(--text); }
.mob-item--danger { color: var(--danger); }
.mob-item--cta { background: var(--gold); color: var(--accent-text); border-radius: 50px; justify-content: center; margin-top: 8px; font-weight: 600; }
.mob-theme-row {
  display: flex; align-items: center; justify-content: space-between;
  padding: 12px 14px; border-top: 1px solid var(--border); margin-top: 8px;
}
.mob-theme-label { font-size: 13px; color: var(--text3); }
.mob-theme-row .theme-toggle { width: auto; height: auto; border-radius: 50px; padding: 7px 16px; gap: 8px; font-size: 13px; font-weight: 600; }

.slide-down-enter-active, .slide-down-leave-active { transition: all 0.25s ease; }
.slide-down-enter-from, .slide-down-leave-to { opacity: 0; transform: translateY(-10px); }

/* ════════════════════════════════
   MAIN
════════════════════════════════ */
.page-main {
  flex: 1; padding-top: 66px;
  max-width: 100%; width: 100%;
}

/* ════════════════════════════════
   CHATBOT
════════════════════════════════ */
.cb-wrap {
  position: fixed; bottom: 24px; right: 24px; z-index: 9999;
  display: flex; flex-direction: column; align-items: flex-end; gap: 12px;
}
.cb-fab {
  width: 54px; height: 54px; border-radius: 50%;
  background: var(--gold); border: none; color: var(--accent-text);
  font-size: 22px; cursor: pointer; display: flex; align-items: center; justify-content: center;
  box-shadow: var(--shadow); transition: all 0.2s;
}
.cb-fab:hover { transform: scale(1.08); }
.cb-fab.is-open { background: var(--bg3); color: var(--text); }

.cb-panel {
  width: 358px; background: var(--bg2); border: 1px solid var(--border2);
  border-radius: 20px; overflow: hidden; box-shadow: var(--shadow-lg);
}
.cb-head {
  background: var(--bg3); padding: 13px 15px;
  display: flex; align-items: center; justify-content: space-between;
  border-bottom: 1px solid var(--border);
}
.cb-head-info { display: flex; align-items: center; gap: 11px; }
.cb-orb {
  width: 36px; height: 36px; border-radius: 50%;
  background: var(--gold-bg); border: 1.5px solid var(--gold);
  display: flex; align-items: center; justify-content: center; color: var(--gold); font-size: 17px;
}
.cb-title { font-size: 13px; font-weight: 600; color: var(--text); }
.cb-sub { font-size: 11px; color: var(--text3); }
.cb-x {
  width: 30px; height: 30px; border-radius: 8px;
  background: var(--bg4); border: none; color: var(--text2); font-size: 13px;
  cursor: pointer; display: flex; align-items: center; justify-content: center; transition: all 0.15s;
}
.cb-x:hover { background: var(--border2); color: var(--text); }

.cb-messages {
  height: 270px; overflow-y: auto; padding: 14px;
  background: var(--bg); display: flex; flex-direction: column; gap: 10px;
}
.cb-empty { text-align: center; padding: 40px 0; color: var(--text3); }
.cb-empty i { font-size: 34px; display: block; margin-bottom: 9px; color: var(--gold); opacity: 0.4; }
.cb-empty p { font-size: 13px; }
.cb-pair { display: flex; flex-direction: column; gap: 6px; }
.bubble { max-width: 87%; padding: 9px 13px; border-radius: 13px; font-size: 13px; line-height: 1.55; }
.bubble-you {
  align-self: flex-end; background: var(--gold-bg);
  border: 1px solid var(--gold-bd); color: var(--text); border-bottom-right-radius: 4px;
}
.cb-chat-images {
  display: grid; grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 6px; min-width: 150px; max-width: 230px;
}
.cb-chat-image {
  display: block; width: 100%; height: 105px; object-fit: cover;
  border-radius: 9px; border: 1px solid var(--gold-bd);
}
.cb-selected-images {
  padding: 9px; border: 1px solid var(--gold-bd);
  border-radius: 11px; background: var(--gold-bg);
}
.cb-selected-heading {
  display: flex; align-items: center; justify-content: space-between;
  gap: 8px; margin-bottom: 8px; color: var(--text2); font-size: 11px;
}
.cb-clear-images {
  border: 0; background: transparent; color: var(--danger);
  font: inherit; cursor: pointer;
}
.cb-preview-list { display: flex; gap: 7px; overflow-x: auto; padding-bottom: 2px; }
.cb-preview-image {
  width: 66px; height: 66px; flex: 0 0 66px; object-fit: cover;
  border-radius: 8px; border: 1px solid var(--border2);
}
.bubble-bot {
  align-self: flex-start; background: var(--bg3);
  border: 1px solid var(--border); color: var(--text2); border-bottom-left-radius: 4px;
}
.typing { display: inline-flex; gap: 4px; align-items: center; height: 20px; }
.typing span {
  width: 6px; height: 6px; background: var(--gold); border-radius: 50%;
  animation: bounce-dot 1.2s infinite;
}
.typing span:nth-child(2) { animation-delay: 0.2s; }
.typing span:nth-child(3) { animation-delay: 0.4s; }
@keyframes bounce-dot {
  0%, 80%, 100% { transform: scale(0.6); opacity: 0.4; }
  40% { transform: scale(1); opacity: 1; }
}

.cb-foot {
  padding: 12px 14px; background: var(--bg2);
  border-top: 1px solid var(--border); display: flex; flex-direction: column; gap: 9px;
}
.cb-input-row { display: flex; gap: 8px; }
.cb-input {
  flex: 1; background: var(--bg3); border: 1px solid var(--border);
  border-radius: 50px; padding: 9px 16px; font-size: 13px; color: var(--text);
  outline: none; transition: border-color 0.15s; font-family: 'Outfit', sans-serif;
}
.cb-input:focus { border-color: var(--gold); }
.cb-input::placeholder { color: var(--text4); }
.cb-send {
  width: 38px; height: 38px; border-radius: 50%; background: var(--gold); border: none;
  color: var(--accent-text); font-size: 14px; cursor: pointer; flex-shrink: 0;
  display: flex; align-items: center; justify-content: center; transition: background 0.15s;
}
.cb-send:hover { background: var(--gold-light); }
.cb-send:disabled { opacity: 0.4; cursor: not-allowed; }
.cb-imgrow {
  display: flex; align-items: center; justify-content: space-between; gap: 8px;
  font-size: 12px; color: var(--text3); background: var(--bg3);
  border: 1.5px dashed var(--border2); border-radius: 10px; padding: 8px 12px; transition: all 0.15s;
}
.cb-imglabel { display: flex; align-items: center; gap: 8px; cursor: pointer; min-width: 0; }
.cb-imglabel:hover { color: var(--text2); }
.cb-imglabel i { font-size: 15px; color: var(--gold); }
.cb-imgbtn {
  margin-left: auto; background: var(--gold); border: none;
  color: var(--accent-text); font-size: 12px; font-weight: 600;
  padding: 5px 12px; border-radius: 7px; cursor: pointer; display: flex; align-items: center; gap: 4px;
}
.cb-pop-enter-active, .cb-pop-leave-active { transition: all 0.26s cubic-bezier(0.4,0,0.2,1); }
.cb-pop-enter-from, .cb-pop-leave-to { opacity: 0; transform: translateY(14px) scale(0.97); }

/* ════════════════════════════════
   FOOTER
════════════════════════════════ */
.site-footer {
  background: var(--footer-bg); border-top: 1px solid var(--border);
  padding: 32px; margin-top: auto;
}
.footer-inner {
  display: flex; flex-wrap: wrap; align-items: center;
  justify-content: space-between; gap: 20px; max-width: 100%;
}
.footer-brand { display: flex; align-items: center; gap: 13px; }
.footer-name { font-family: 'Playfair Display', serif; font-size: 20px; color: var(--text); font-weight: 700; }
.footer-name em { color: var(--gold); font-style: italic; }
.footer-time { font-size: 11px; color: var(--text4); margin-top: 2px; }
.footer-copy { font-size: 11px; color: var(--text4); }
.footer-links { display: flex; gap: 6px; flex-wrap: wrap; }
.footer-link {
  font-size: 13px; font-weight: 500; color: var(--text3);
  padding: 6px 14px; border-radius: 50px; border: 1px solid var(--border);
  transition: all 0.18s;
}
.footer-link:hover { color: var(--gold); border-color: var(--gold-bd); background: var(--gold-bg); }
.footer-socials { display: flex; gap: 10px; }
.soc-btn {
  width: 38px; height: 38px; border-radius: 50%;
  border: 1px solid var(--border); color: var(--text3); font-size: 15px;
  display: flex; align-items: center; justify-content: center; transition: all 0.18s;
}
.soc-btn:hover { background: var(--gold-bg); color: var(--gold); border-color: var(--gold-bd); }

@media (max-width: 900px) {
  .nav-right, .nav-search { display: none !important; }
  .hamburger { display: block; }
  .nav-inner { padding: 0 20px; }
}
@media (min-width: 901px) { .mobile-menu { display: none !important; } }
@media (max-width: 600px) { .footer-inner { flex-direction: column; text-align: center; } .footer-links, .footer-socials { justify-content: center; } }
</style>