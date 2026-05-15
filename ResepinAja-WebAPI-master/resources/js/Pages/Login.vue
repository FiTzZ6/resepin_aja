<!-- Login.vue -->
<script setup>
import { ref } from 'vue'
import axios from 'axios'
 
const username = ref('')
const password = ref('')
const isLoading = ref(false)
const error = ref('')
 
const submit = async () => {
  error.value = ''
  isLoading.value = true
  try {
    await axios.get('http://localhost:8000/sanctum/csrf-cookie', { withCredentials: true });
    await axios.post('http://localhost:8000/login', { username: username.value, password: password.value }, { withCredentials: true });
    const el = document.getElementById('LoginPanel')
    if (el) bootstrap.Modal.getOrCreateInstance(el).hide()
    username.value = ''; password.value = ''
    location.reload()
  } catch (err) {
    error.value = err.response?.data?.message || Object.values(err.response?.data || {}).flat().join(' ') || 'Login gagal.'
  } finally { isLoading.value = false }
}
</script>
 
<template>
  <div class="modal fade" id="LoginPanel" tabindex="-1">
    <div class="modal-dialog modal-dialog-centered">
      <div class="modal-content ra-modal">
        <div class="ra-modal-head">
          <div>
            <h2 class="ra-modal-title">Selamat Datang Kembali</h2>
            <p class="ra-modal-sub">Masuk ke akun Resepin Aja kamu</p>
          </div>
          <button class="ra-modal-close" data-bs-dismiss="modal"><i class="bi bi-x-lg"></i></button>
        </div>
        <div class="ra-modal-body">
          <div v-if="error" class="ra-error"><i class="bi bi-exclamation-circle"></i> {{ error }}</div>
          <form @submit.prevent="submit" class="ra-form">
            <div class="fgroup">
              <label class="field-label">Username</label>
              <div class="input-icon-wrap">
                <i class="bi bi-person input-icon"></i>
                <input v-model="username" type="text" class="field-input input-with-icon" placeholder="Username kamu" required />
              </div>
            </div>
            <div class="fgroup">
              <label class="field-label">Password</label>
              <div class="input-icon-wrap">
                <i class="bi bi-lock input-icon"></i>
                <input v-model="password" type="password" class="field-input input-with-icon" placeholder="Password" required />
              </div>
            </div>
            <button type="submit" class="ra-submit-btn" :disabled="isLoading">
              <span v-if="!isLoading"><i class="bi bi-box-arrow-in-right"></i> Masuk</span>
              <span v-else><span class="spinner-border spinner-border-sm"></span> Memproses...</span>
            </button>
          </form>
          <p class="ra-switch">Belum punya akun? <a href="#" data-bs-toggle="modal" data-bs-target="#RegisterPanel" data-bs-dismiss="modal">Daftar di sini</a></p>
        </div>
      </div>
    </div>
  </div>
</template>
 
<style scoped>
.ra-modal {
  background: var(--bg2); border: 1px solid var(--border2);
  border-radius: 20px; overflow: hidden;
  box-shadow: var(--shadow-lg);
}
.ra-modal-head {
  display: flex; align-items: flex-start; justify-content: space-between;
  padding: 28px 28px 0;
}
.ra-modal-title {
  font-family: 'Playfair Display', serif; font-size: 1.6rem; font-weight: 700;
  color: var(--text); margin: 0 0 4px;
}
.ra-modal-sub { font-size: 13px; color: var(--text3); margin: 0; }
.ra-modal-close {
  width: 32px; height: 32px; border-radius: 9px;
  background: var(--bg3); border: none; color: var(--text2);
  font-size: 14px; cursor: pointer; display: flex; align-items: center; justify-content: center;
  transition: all 0.15s; flex-shrink: 0;
}
.ra-modal-close:hover { background: var(--bg4); color: var(--text); }
.ra-modal-body { padding: 24px 28px 28px; }
 
.ra-error {
  display: flex; align-items: center; gap: 8px;
  font-size: 13px; color: var(--danger); background: var(--danger-bg);
  border: 1px solid rgba(229,115,115,0.2); border-radius: 10px;
  padding: 10px 14px; margin-bottom: 16px;
}
.ra-form { display: flex; flex-direction: column; gap: 16px; }
.fgroup { display: flex; flex-direction: column; gap: 7px; }
.input-icon-wrap { position: relative; }
.input-icon { position: absolute; left: 14px; top: 50%; transform: translateY(-50%); color: var(--text3); font-size: 16px; pointer-events: none; }
.input-with-icon { padding-left: 40px; }
 
.ra-submit-btn {
  width: 100%; padding: 13px; border-radius: 50px;
  background: var(--gold); color: #0e0e0e; border: none;
  font-size: 15px; font-weight: 600; cursor: pointer;
  display: flex; align-items: center; justify-content: center; gap: 8px;
  transition: all 0.2s; margin-top: 4px;
}
.ra-submit-btn:hover { background: var(--gold-light); }
.ra-submit-btn:disabled { opacity: 0.55; cursor: not-allowed; }
 
.ra-switch { text-align: center; font-size: 13px; color: var(--text3); margin: 16px 0 0; }
.ra-switch a { color: var(--gold); font-weight: 600; }
.ra-switch a:hover { color: var(--gold-light); }
</style>