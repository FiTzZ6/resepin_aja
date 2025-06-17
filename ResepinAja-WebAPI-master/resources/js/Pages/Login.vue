<script setup>
import { useForm, usePage } from '@inertiajs/vue3'

const form = useForm({
  username: '',
  password: '',
})

function submit() {
  form.post('/login', {
    onSuccess: () => {
      const loginModal = new bootstrap.Modal(document.getElementById('LoginPanel'))
      loginModal.hide()
      form.reset()
      location.reload()
    }
  })
}
</script>

<template><!-- LOGIN -->
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
              <input type="text" class="form-control rounded-3" id="floatingInput" placeholder="Gatonanju" v-model="form.username" required/>
              <label for="floatingInput">Username</label>
            </div>
            <div class="form-floating mb-3">
              <input type="password" class="form-control rounded-3" id="floatingPassword" placeholder="Pass****" v-model="form.password" required/>
              <label for="floatingPassword">Password</label>
            </div>
            <button class="w-100 mb-3 btn btn-lg rounded-3 btn-dark" type="submit">Sign up</button>
          </form>
          <small class="text-body-secondary">
            <a href="#" data-bs-toggle="modal" data-bs-target="#RegisterPanel">Daftar disini</a>, jika belum mempunyai akun</small>
        </div>
      </div>
    </div>
  </div>
</template>