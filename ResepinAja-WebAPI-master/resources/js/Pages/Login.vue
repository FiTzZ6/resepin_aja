<script setup>
import { ref } from 'vue'
import axios from 'axios'

// Ref untuk form login
const username = ref('')
const password = ref('')

// Submit login
const submit = async () => {
  try {
    // Ambil CSRF cookie dulu
    await axios.get('http://localhost:8000/sanctum/csrf-cookie', { withCredentials: true });
    const res = await axios.post('http://localhost:8000/login', {
      username: username.value,
      password: password.value
    }, { withCredentials: true });
    console.log('Login berhasil', res.data)

    // Tutup modal
    const loginModalEl = document.getElementById('LoginPanel')
    if (loginModalEl) {
      const loginModal = bootstrap.Modal.getOrCreateInstance(loginModalEl)
      loginModal.hide()
    }

    // Reset form
    username.value = ''
    password.value = ''

    // Reload halaman untuk update status login
    location.reload()

  } catch (err) {
    console.error(err)
    if (err.response?.data) {
      alert(Object.values(err.response.data).flat().join('\n'))
    } else {
      alert('Login gagal. Cek console.')
    }
  }
}
</script>

<template>
  <!-- LOGIN MODAL -->
  <div class="modal fade" id="LoginPanel" tabindex="-1">
    <div class="modal-dialog">
      <div class="modal-content rounded-4 shadow">
        <div class="modal-header p-5 pb-4 border-bottom-0">
          <h1 class="fw-bold mb-0 fs-2">Masuk Resepin Aja</h1>
          <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
        </div>
        <div class="modal-body p-5 pt-0">
          <form @submit.prevent="submit">
            <div class="form-floating mb-3">
              <input type="text" class="form-control rounded-3" id="floatingUsername" placeholder="Username"
                v-model="username" required />
              <label for="floatingUsername">Username</label>
            </div>
            <div class="form-floating mb-3">
              <input type="password" class="form-control rounded-3" id="floatingPassword" placeholder="Password"
                v-model="password" required />
              <label for="floatingPassword">Password</label>
            </div>
            <button class="w-100 mb-3 btn btn-lg rounded-3 btn-dark" type="submit">
              Masuk
            </button>
          </form>
          <small class="text-body-secondary">
            <a href="#" data-bs-toggle="modal" data-bs-target="#RegisterPanel">Daftar disini</a>, jika belum mempunyai
            akun
          </small>
        </div>
      </div>
    </div>
  </div>
</template>
