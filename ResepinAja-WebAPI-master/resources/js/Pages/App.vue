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
const loading = ref(false)

const toggleChat = () => {
  isOpen.value = !isOpen.value
  if (isOpen.value) scrollToBottom()
}

const scrollToBottom = () => {
  nextTick(() => {
    const container = document.querySelector('.chatbot-body')
    if (container) container.scrollTop = container.scrollHeight
  })
}

const sendMessage = async () => {
  if (!message.value.trim()) return
  const msg = message.value
  message.value = ''
  await sendToChatbot(msg)
}

const sendImage = async () => {
  if (!imageFiles.value.length) { alert('Pilih minimal satu gambar!'); return }
  chats.value.push({ user: `📷 Mengirim ${imageFiles.value.length} gambar...`, bot: 'Memproses...' })
  scrollToBottom()
  const formData = new FormData()
  imageFiles.value.forEach(file => formData.append('files[]', file))
  try {
    loading.value = true
    const res = await axios.post('/chatbot/images', formData, { headers: { 'Content-Type': 'multipart/form-data' } })
    if (res.data.status === 'success') {
      const ingredients = res.data.data.map(d => d.predicted_label)
      detectedIngredients.value.push(...ingredients)
      chats.value[chats.value.length - 1].bot = `🧠 Terdeteksi bahan: ${ingredients.join(', ')}`
      setTimeout(() => { window.location.href = `/resepcari?cari_bahan=${encodeURIComponent(ingredients.join(','))}` }, 1500)
    }
  } catch (err) {
    chats.value[chats.value.length - 1].bot = '⚠️ Gagal memproses gambar.'
  } finally {
    loading.value = false; imageFiles.value = []; scrollToBottom()
  }
}

const sendToChatbot = async (msg) => {
  chats.value.push({ user: msg, bot: '...' })
  scrollToBottom()
  try {
    loading.value = true
    const res = await axios.post('/chatbot', { message: msg })
    const data = res.data?.data || {}
    if (data.type === "redirect" && data.url) {
      chats.value[chats.value.length - 1].bot = data.message || "Mengarahkan ke halaman terkait..."
      setTimeout(() => { window.location.href = data.url }, 1500)
    } else {
      chats.value[chats.value.length - 1].bot = data.message || data.bot_response || "Chatbot tidak merespon."
    }
  } catch {
    chats.value[chats.value.length - 1].bot = '⚠️ Terjadi kesalahan saat menghubungi chatbot.'
  } finally {
    loading.value = false; scrollToBottom()
  }
}

const handleFileChange = (e) => { imageFiles.value = Array.from(e.target.files) }
</script>

<template>
  <div class="main-wrapper">
    <!-- ===== NAVBAR ===== -->
    <nav class="ra-navbar">
      <div class="nav-inner">
        <!-- Logo -->
        <Link class="nav-logo" href="/">
          <img src="../../../public/assets/Logo.png" alt="Resepin Aja" width="56" height="56" />
          <span class="nav-brand-text">Resepin Aja</span>
        </Link>

        <!-- Searchbar center -->
        <div class="nav-search">
          <Searchbar />
        </div>

        <!-- Nav links -->
        <ul class="nav-links">
          <li>
            <Link class="nav-link-item" href="/">Beranda</Link>
          </li>
          <li>
            <Link class="nav-link-item" href="/resepcari">Resep</Link>
          </li>

          <!-- Logged in -->
          <li v-if="userData" class="nav-user-wrap dropdown">
            <a class="nav-user-btn dropdown-toggle" href="#" role="button" data-bs-toggle="dropdown">
              <img src="../../../public/assets/muehe.png" class="nav-avatar" width="34" height="34" />
              <span class="nav-username">{{ userData.username }}</span>
              <i class="bi bi-chevron-down nav-chevron"></i>
            </a>
            <div class="dropdown-menu dropdown-menu-end nav-dropdown-menu p-0">
              <div class="nav-dropdown-inner">
                <div class="nav-dropdown-col">
                  <Link href="/tambahresep" class="nav-dd-item">
                    <span class="nav-dd-icon nav-dd-icon--green"><i class="bi bi-plus-circle-fill"></i></span>
                    <span>
                      <strong>Tambah Resep</strong>
                      <small>Bagikan kreasi masakan</small>
                    </span>
                  </Link>
                  <Link :href="`/tersimpanresep/${userData.id_user}`" class="nav-dd-item">
                    <span class="nav-dd-icon nav-dd-icon--gold"><i class="bi bi-bookmark-star-fill"></i></span>
                    <span>
                      <strong>Resep Tersimpan</strong>
                      <small>Koleksi favorit kamu</small>
                    </span>
                  </Link>
                </div>
                <div class="nav-dropdown-divider"></div>
                <div class="nav-dropdown-col nav-dropdown-col--sm">
                  <Link :href="`/profil/${userData.id_user}`" class="nav-dd-link">
                    <i class="bi bi-person-circle me-2"></i>Profil Saya
                  </Link>
                  <button class="nav-dd-link nav-dd-link--danger" data-bs-toggle="modal" data-bs-target="#LogoutPanel">
                    <i class="bi bi-box-arrow-right me-2"></i>Keluar
                  </button>
                </div>
              </div>
            </div>
          </li>

          <!-- Guest -->
          <li v-else>
            <button class="nav-login-btn" data-bs-toggle="modal" data-bs-target="#LoginPanel">
              <i class="bi bi-person me-1"></i> Masuk
            </button>
          </li>
        </ul>
      </div>
    </nav>

    <!-- ===== PAGE CONTENT ===== -->
    <div class="page-container">
      <slot />
    </div>

    <!-- Modals -->
    <div v-if="userData">
      <Logout />
    </div>
    <div v-else>
      <Login />
      <Register />
    </div>

    <!-- ===== CHATBOT ===== -->
    <div class="chatbot-wrap">
      <transition name="chat-slide">
        <div v-if="isOpen" class="chatbot-panel">
          <div class="chatbot-head">
            <div class="chatbot-head-info">
              <div class="chatbot-avatar"><i class="bi bi-stars"></i></div>
              <div>
                <div class="chatbot-head-title">Asisten Resepin</div>
                <div class="chatbot-head-sub">Tanya resep apa saja</div>
              </div>
            </div>
            <button @click="toggleChat" class="chatbot-close"><i class="bi bi-x-lg"></i></button>
          </div>

          <div class="chatbot-body" style="height: 280px; overflow-y: auto;">
            <div class="chatbot-empty" v-if="!chats.length">
              <i class="bi bi-chat-dots"></i>
              <p>Halo! Tanya resep apa hari ini? 🍳</p>
            </div>
            <div v-for="(chat, index) in chats" :key="index" class="chat-row">
              <div class="bubble bubble-user">{{ chat.user }}</div>
              <div class="bubble bubble-bot">{{ chat.bot }}</div>
            </div>
          </div>

          <div class="chatbot-footer">
            <div class="chat-input-row">
              <input v-model="message" @keyup.enter="sendMessage" placeholder="Tanya resep..." class="chat-input" />
              <button @click="sendMessage" class="chat-send-btn" :disabled="loading">
                <i class="bi bi-send-fill"></i>
              </button>
            </div>
            <div class="chat-img-row">
              <label class="chat-file-label">
                <i class="bi bi-image me-1"></i>
                <span>{{ imageFiles.length ? imageFiles.length + ' foto dipilih' : 'Kirim foto bahan' }}</span>
                <input type="file" multiple @change="handleFileChange" class="d-none" />
              </label>
              <button @click="sendImage" class="chat-img-btn" :disabled="loading || !imageFiles.length">
                <i class="bi bi-search me-1"></i> Cari
              </button>
            </div>
          </div>
        </div>
      </transition>

      <button v-if="!isOpen" class="chatbot-fab" @click="toggleChat">
        <i class="bi bi-stars"></i>
      </button>
    </div>

    <!-- ===== FOOTER ===== -->
    <footer class="ra-footer">
      <div class="footer-inner">
        <div class="footer-brand">
          <img src="../../../public/assets/Logo.png" alt="" width="40" height="40" />
          <div>
            <div class="footer-brand-name">Resepin Aja</div>
            <div class="footer-brand-copy">© 2025 Ger Ger Jeger. Inc</div>
          </div>
        </div>
        <div class="footer-links">
          <Link href="/" class="footer-link">Beranda</Link>
          <Link href="/resepcari" class="footer-link">Resep</Link>
          <Link href="/tambahresep" class="footer-link">Tambah Resep</Link>
        </div>
        <div class="footer-socials">
          <a href="#" class="footer-social-btn" aria-label="Instagram"><i class="bi bi-instagram"></i></a>
          <a href="#" class="footer-social-btn" aria-label="Facebook"><i class="bi bi-facebook"></i></a>
          <a href="#" class="footer-social-btn" aria-label="TikTok"><i class="bi bi-tiktok"></i></a>
        </div>
      </div>
    </footer>
  </div>
</template>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@600;700&family=DM+Sans:wght@400;500;600&display=swap');

/* ===== CSS VARIABLES ===== */
:global(:root) {
  --ra-green: #1a3a2e;
  --ra-green-mid: #2d5a47;
  --ra-green-soft: #3d7a60;
  --ra-cream: #faf6f0;
  --ra-cream-dk: #f0e8db;
  --ra-gold: #c9973a;
  --ra-gold-light: #e8c068;
  --ra-text: #1c1c1c;
  --ra-muted: #6b6b6b;
  --ra-white: #ffffff;
  --ra-radius: 14px;
  --ra-shadow: 0 4px 24px rgba(26, 58, 46, 0.10);
  --ra-shadow-lg: 0 8px 40px rgba(26, 58, 46, 0.18);
}

* {
  font-family: 'DM Sans', sans-serif;
  box-sizing: border-box;
}

html,
body,
#app {
  height: 100%;
  margin: 0;
}

/* ===== NAVBAR ===== */
.ra-navbar {
  background: var(--ra-green);
  position: sticky;
  top: 0;
  z-index: 1000;
  border-bottom: 1px solid rgba(201, 151, 58, 0.2);
  box-shadow: 0 2px 20px rgba(0, 0, 0, 0.2);
}

.nav-inner {
  max-width: 1300px;
  margin: 0 auto;
  padding: 0 24px;
  height: 72px;
  display: flex;
  align-items: center;
  gap: 20px;
}

.nav-logo {
  display: flex;
  align-items: center;
  gap: 10px;
  text-decoration: none;
  flex-shrink: 0;
}

.nav-brand-text {
  font-family: 'Cormorant Garamond', serif;
  font-size: 22px;
  font-weight: 700;
  color: var(--ra-gold-light);
  letter-spacing: 0.01em;
  white-space: nowrap;
}

.nav-search {
  flex: 1;
  max-width: 480px;
}

.nav-links {
  display: flex;
  align-items: center;
  gap: 6px;
  list-style: none;
  margin: 0;
  padding: 0;
  flex-shrink: 0;
}

.nav-link-item {
  font-size: 14px;
  font-weight: 500;
  color: rgba(255, 255, 255, 0.75);
  text-decoration: none;
  padding: 8px 14px;
  border-radius: 8px;
  transition: all 0.18s;
}

.nav-link-item:hover {
  color: #fff;
  background: rgba(255, 255, 255, 0.08);
}

/* User dropdown trigger */
.nav-user-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 50px;
  padding: 5px 14px 5px 5px;
  color: #fff;
  text-decoration: none;
  font-size: 14px;
  font-weight: 500;
  transition: background 0.18s;
  cursor: pointer;
}

.nav-user-btn:hover {
  background: rgba(255, 255, 255, 0.14);
}

.nav-avatar {
  border-radius: 50%;
  object-fit: cover;
  border: 2px solid var(--ra-gold);
}

.nav-chevron {
  font-size: 11px;
  opacity: 0.6;
}

/* Dropdown */
.nav-dropdown-menu {
  border: 1px solid var(--ra-cream-dk);
  border-radius: var(--ra-radius);
  box-shadow: var(--ra-shadow-lg);
  min-width: 320px;
  overflow: hidden;
  margin-top: 8px;
}

.nav-dropdown-inner {
  display: flex;
  gap: 0;
  background: var(--ra-white);
}

.nav-dropdown-col {
  flex: 1;
  padding: 12px;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.nav-dropdown-col--sm {
  flex: 0 0 auto;
  min-width: 140px;
  background: var(--ra-cream);
  border-left: 1px solid var(--ra-cream-dk);
}

.nav-dropdown-divider {
  display: none;
}

.nav-dd-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 12px;
  border-radius: 10px;
  text-decoration: none;
  color: var(--ra-text);
  transition: background 0.15s;
}

.nav-dd-item:hover {
  background: var(--ra-cream);
}

.nav-dd-item strong {
  display: block;
  font-size: 14px;
  font-weight: 600;
}

.nav-dd-item small {
  font-size: 12px;
  color: var(--ra-muted);
}

.nav-dd-icon {
  width: 38px;
  height: 38px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  flex-shrink: 0;
}

.nav-dd-icon--green {
  background: #e6f4ed;
  color: #2d7a50;
}

.nav-dd-icon--gold {
  background: #fdf3e1;
  color: var(--ra-gold);
}

.nav-dd-link {
  display: flex;
  align-items: center;
  width: 100%;
  padding: 9px 12px;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 500;
  text-decoration: none;
  color: var(--ra-text);
  background: none;
  border: none;
  cursor: pointer;
  transition: background 0.15s;
}

.nav-dd-link:hover {
  background: var(--ra-cream-dk);
}

.nav-dd-link--danger {
  color: #c0392b;
}

.nav-dd-link--danger:hover {
  background: #fdecea;
}

/* Login button */
.nav-login-btn {
  font-size: 14px;
  font-weight: 600;
  color: var(--ra-green);
  background: var(--ra-gold-light);
  border: none;
  border-radius: 50px;
  padding: 9px 20px;
  cursor: pointer;
  transition: background 0.18s, transform 0.15s;
}

.nav-login-btn:hover {
  background: var(--ra-gold);
  color: #fff;
  transform: translateY(-1px);
}

/* ===== PAGE CONTENT ===== */
.page-container {
  max-width: 1300px;
  margin: 0 auto;
  padding: 0 24px;
  background: transparent;
  min-height: 60vh;
}

/* ===== CHATBOT ===== */
.chatbot-wrap {
  position: fixed;
  bottom: 24px;
  right: 24px;
  z-index: 9999;
  display: flex;
  flex-direction: column;
  align-items: flex-end;
}

.chatbot-fab {
  width: 58px;
  height: 58px;
  border-radius: 50%;
  background: var(--ra-green);
  border: 2px solid var(--ra-gold);
  color: var(--ra-gold-light);
  font-size: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  box-shadow: var(--ra-shadow-lg);
  transition: transform 0.2s, background 0.2s;
}

.chatbot-fab:hover {
  background: var(--ra-green-mid);
  transform: scale(1.08);
}

.chatbot-panel {
  width: 360px;
  border-radius: 20px;
  overflow: hidden;
  box-shadow: var(--ra-shadow-lg);
  background: var(--ra-white);
  border: 1px solid var(--ra-cream-dk);
  margin-bottom: 12px;
}

.chatbot-head {
  background: var(--ra-green);
  padding: 14px 16px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.chatbot-head-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.chatbot-avatar {
  width: 38px;
  height: 38px;
  border-radius: 50%;
  background: rgba(201, 151, 58, 0.2);
  border: 1.5px solid var(--ra-gold);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--ra-gold-light);
  font-size: 18px;
}

.chatbot-head-title {
  font-size: 14px;
  font-weight: 600;
  color: #fff;
}

.chatbot-head-sub {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.55);
}

.chatbot-close {
  background: rgba(255, 255, 255, 0.1);
  border: none;
  border-radius: 8px;
  color: #fff;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  font-size: 14px;
  transition: background 0.15s;
}

.chatbot-close:hover {
  background: rgba(255, 255, 255, 0.2);
}

.chatbot-body {
  padding: 16px;
  background: var(--ra-cream);
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.chatbot-empty {
  text-align: center;
  color: var(--ra-muted);
  padding: 30px 0;
  font-size: 13px;
}

.chatbot-empty i {
  font-size: 32px;
  display: block;
  margin-bottom: 8px;
  color: var(--ra-green-soft);
}

.chat-row {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.bubble {
  max-width: 85%;
  padding: 9px 13px;
  border-radius: 14px;
  font-size: 13px;
  line-height: 1.5;
}

.bubble-user {
  align-self: flex-end;
  background: var(--ra-green);
  color: #fff;
  border-bottom-right-radius: 4px;
}

.bubble-bot {
  align-self: flex-start;
  background: var(--ra-white);
  color: var(--ra-text);
  border: 1px solid var(--ra-cream-dk);
  border-bottom-left-radius: 4px;
}

.chatbot-footer {
  padding: 12px 16px;
  display: flex;
  flex-direction: column;
  gap: 8px;
  border-top: 1px solid var(--ra-cream-dk);
}

.chat-input-row {
  display: flex;
  gap: 8px;
}

.chat-input {
  flex: 1;
  border: 1.5px solid var(--ra-cream-dk);
  border-radius: 50px;
  padding: 9px 16px;
  font-size: 13px;
  background: var(--ra-cream);
  outline: none;
  transition: border-color 0.15s;
}

.chat-input:focus {
  border-color: var(--ra-green-soft);
}

.chat-send-btn {
  width: 38px;
  height: 38px;
  border-radius: 50%;
  background: var(--ra-green);
  border: none;
  color: #fff;
  font-size: 15px;
  cursor: pointer;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.15s;
}

.chat-send-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.chat-send-btn:hover:not(:disabled) {
  background: var(--ra-green-mid);
}

.chat-img-row {
  display: flex;
  gap: 8px;
  align-items: center;
}

.chat-file-label {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: var(--ra-muted);
  cursor: pointer;
  background: var(--ra-cream);
  border: 1.5px dashed var(--ra-cream-dk);
  border-radius: 10px;
  padding: 8px 12px;
  transition: border-color 0.15s;
}

.chat-file-label:hover {
  border-color: var(--ra-green-soft);
  color: var(--ra-green);
}

.chat-img-btn {
  background: var(--ra-gold);
  border: none;
  color: var(--ra-green);
  font-size: 12px;
  font-weight: 600;
  padding: 8px 14px;
  border-radius: 10px;
  cursor: pointer;
  transition: background 0.15s;
  flex-shrink: 0;
}

.chat-img-btn:disabled {
  opacity: 0.45;
  cursor: not-allowed;
}

.chat-img-btn:hover:not(:disabled) {
  background: var(--ra-gold-light);
}

/* Chat animation */
.chat-slide-enter-active,
.chat-slide-leave-active {
  transition: opacity 0.22s, transform 0.22s;
}

.chat-slide-enter-from,
.chat-slide-leave-to {
  opacity: 0;
  transform: translateY(16px) scale(0.97);
}

/* ===== FOOTER ===== */
.ra-footer {
  background: var(--ra-green);
  border-top: 1px solid rgba(201, 151, 58, 0.2);
  padding: 32px 24px;
  margin-top: 48px;
}

.footer-inner {
  max-width: 1300px;
  margin: 0 auto;
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: 20px;
}

.footer-brand {
  display: flex;
  align-items: center;
  gap: 12px;
}

.footer-brand-name {
  font-family: 'Cormorant Garamond', serif;
  font-size: 20px;
  font-weight: 700;
  color: var(--ra-gold-light);
}

.footer-brand-copy {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.4);
  margin-top: 2px;
}

.footer-links {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}

.footer-link {
  font-size: 13px;
  font-weight: 500;
  color: rgba(255, 255, 255, 0.6);
  text-decoration: none;
  padding: 6px 14px;
  border-radius: 50px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  transition: all 0.18s;
}

.footer-link:hover {
  color: var(--ra-gold-light);
  border-color: rgba(201, 151, 58, 0.4);
}

.footer-socials {
  display: flex;
  gap: 10px;
}

.footer-social-btn {
  width: 38px;
  height: 38px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1px solid rgba(255, 255, 255, 0.15);
  color: rgba(255, 255, 255, 0.6);
  text-decoration: none;
  font-size: 16px;
  transition: all 0.18s;
}

.footer-social-btn:hover {
  background: rgba(201, 151, 58, 0.2);
  color: var(--ra-gold-light);
  border-color: var(--ra-gold);
}
</style>