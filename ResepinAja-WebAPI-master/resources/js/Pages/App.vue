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
onUnmounted(() => clearInterval(timeInterval))

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
  chats.value.push({ user: `📷 ${imageFiles.value.length} foto dikirim`, bot: null })
  scrollToBottom()
  const fd = new FormData()
  imageFiles.value.forEach(f => fd.append('files[]', f))
  try {
    loading.value = true
    const res = await axios.post('/chatbot/images', fd)
    if (res.data.status === 'success') {
      const ing = res.data.data.map(d => d.predicted_label)
      chats.value[chats.value.length - 1].bot = `Terdeteksi: ${ing.join(', ')}`
      setTimeout(() => { window.location.href = `/resepcari?cari_bahan=${encodeURIComponent(ing.join(','))}` }, 1500)
    }
  } catch { chats.value[chats.value.length - 1].bot = 'Gagal memproses.' }
  finally { loading.value = false; imageFiles.value = []; scrollToBottom() }
}

const handleFileChange = (e) => { imageFiles.value = Array.from(e.target.files) }
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

          <!-- Theme toggle -->
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
              <div class="bubble bubble-you">{{ c.user }}</div>
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
            <label class="cb-imgrow">
              <i class="bi bi-image"></i>
              <span>{{ imageFiles.length ? imageFiles.length + ' foto dipilih' : 'Kirim foto bahan' }}</span>
              <input type="file" multiple accept="image/*" @change="handleFileChange" class="d-none" />
              <button v-if="imageFiles.length" @click.prevent="sendImage" class="cb-imgbtn" :disabled="loading">
                Cari <i class="bi bi-arrow-right"></i>
              </button>
            </label>
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

/* ── DARK THEME (default) ── */
:root, [data-theme="dark"] {
  --bg:         #1c1c1c;
  --bg2:        #242424;
  --bg3:        #2c2c2c;
  --bg4:        #343434;
  --border:     rgba(255,255,255,0.10);
  --border2:    rgba(255,255,255,0.16);
  --text:       #f0ece4;
  --text2:      rgba(240,236,228,0.70);
  --text3:      rgba(240,236,228,0.40);
  --text4:      rgba(240,236,228,0.24);
  --gold:       #d4a853;
  --gold-light: #e8c068;
  --gold-bg:    rgba(212,168,83,0.12);
  --gold-bd:    rgba(212,168,83,0.28);
  --danger:     #e57373;
  --danger-bg:  rgba(229,115,115,0.12);
  --success:    #66bb6a;
  --nav-bg:     rgba(28,28,28,0.70);
  --nav-raised: rgba(28,28,28,0.96);
  --footer-bg:  #161616;
  --shadow:     0 4px 24px rgba(0,0,0,0.35);
  --shadow-lg:  0 12px 48px rgba(0,0,0,0.50);
  --radius:     14px;
  --radius-lg:  20px;
  --radius-xl:  28px;
}

/* ── LIGHT THEME ── */
[data-theme="light"] {
  --bg:         #f5f2ed;
  --bg2:        #ffffff;
  --bg3:        #ede9e3;
  --bg4:        #e5e0d8;
  --border:     rgba(0,0,0,0.09);
  --border2:    rgba(0,0,0,0.15);
  --text:       #1e1a14;
  --text2:      rgba(30,26,20,0.65);
  --text3:      rgba(30,26,20,0.42);
  --text4:      rgba(30,26,20,0.22);
  --gold:       #b8892a;
  --gold-light: #c9973a;
  --gold-bg:    rgba(184,137,42,0.10);
  --gold-bd:    rgba(184,137,42,0.28);
  --danger:     #c0392b;
  --danger-bg:  rgba(192,57,43,0.10);
  --success:    #2e7d32;
  --nav-bg:     rgba(245,242,237,0.80);
  --nav-raised: rgba(245,242,237,0.98);
  --footer-bg:  #ebe7e0;
  --shadow:     0 4px 24px rgba(0,0,0,0.10);
  --shadow-lg:  0 12px 48px rgba(0,0,0,0.16);
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
.tag-fire { background: rgba(212,94,50,0.12); color: #d45e32; border: 1px solid rgba(212,94,50,0.25); }

.btn-primary {
  display: inline-flex; align-items: center; gap: 7px;
  font-size: 14px; font-weight: 600; background: var(--gold); color: #0e0e0e;
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
  background: var(--danger-bg); border: 1px solid rgba(229,115,115,0.2);
  color: var(--danger); cursor: pointer; transition: all 0.15s;
  display: flex; align-items: center; justify-content: center; font-size: 15px;
}
.del-btn:hover { background: rgba(229,115,115,0.22); }
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
.nav-search { flex: 1; max-width: 500px; }
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
.mob-item--cta { background: var(--gold); color: #0e0e0e; border-radius: 50px; justify-content: center; margin-top: 8px; font-weight: 600; }
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
  background: var(--gold); border: none; color: #0e0e0e;
  font-size: 22px; cursor: pointer; display: flex; align-items: center; justify-content: center;
  box-shadow: 0 8px 28px rgba(212,168,83,0.4); transition: all 0.2s;
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
  color: #0e0e0e; font-size: 14px; cursor: pointer; flex-shrink: 0;
  display: flex; align-items: center; justify-content: center; transition: background 0.15s;
}
.cb-send:hover { background: var(--gold-light); }
.cb-send:disabled { opacity: 0.4; cursor: not-allowed; }
.cb-imgrow {
  display: flex; align-items: center; gap: 8px; cursor: pointer;
  font-size: 12px; color: var(--text3); background: var(--bg3);
  border: 1.5px dashed var(--border2); border-radius: 10px; padding: 8px 12px; transition: all 0.15s;
}
.cb-imgrow:hover { border-color: var(--gold); color: var(--text2); }
.cb-imgrow i { font-size: 15px; color: var(--gold); }
.cb-imgbtn {
  margin-left: auto; background: var(--gold); border: none;
  color: #0e0e0e; font-size: 12px; font-weight: 600;
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