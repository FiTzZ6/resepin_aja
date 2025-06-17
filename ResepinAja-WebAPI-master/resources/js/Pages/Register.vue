<script setup>
import { useForm, usePage } from '@inertiajs/vue3'

const form = useForm({
  username: '',
  no_hp: '',
  password: '',
  password_confirmation: ''
})

function submit() {
  form.post('/register', {
    onSuccess: () => {
      const registerModal = bootstrap.Modal.getInstance(document.getElementById('RegisterPanel'))
      registerModal?.hide()
      const loginModal = new bootstrap.Modal(document.getElementById('LoginPanel'))
      loginModal.show()
      form.reset()
    }
  })
}
// const page = usePage().props.value.auth_user;

// watchEffect(() => {
//   if (page.success) {
//     const modal = new bootstrap.Modal(document.getElementById('RegisterPanel'));
//     modal.hide();
//     form.reset();
//   }
// })
</script>

<template><!-- REG -->
  <div class="modal fade" id="RegisterPanel" tabindex="-1">
    <div class="modal-dialog">
      <div class="modal-content rounded-4 shadow">
        <div class="modal-header p-5 pb-4 border-bottom-0">
          <div>
            <h1 class="fw-bold mb-0 fs-2">Mending Resepin Aja</h1>
            <small>Buat Akun disini</small>
          </div>
          <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
        </div>
        <div class="modal-body p-5 pt-0">
          <form @submit.prevent="submit">
            <div class="form-floating mb-3">
              <input type="text" class="form-control rounded-3" id="floatingInput" placeholder="" v-model="form.username" required/>
              <label for="floatingInput">Username</label>
            </div>
            <div class="form-floating mb-3">
              <input type="text" class="form-control rounded-3" placeholder="" v-model="form.no_hp" required/>
              <label for="floatingInput">No HP</label>
            </div>
            <div class="form-floating mb-3">
              <input type="password" class="form-control rounded-3" placeholder="" v-model="form.password" required/>
              <label for="floatingPassword">Password</label>
            </div>
            <div class="form-floating mb-3">
              <input type="password" class="form-control rounded-3" placeholder="" v-model="form.password_confirmation" required/>
              <label for="floatingPassword">Konfirmasi Password</label>
            </div>
            <button class="w-100 mb-3 btn btn-lg rounded-3 btn-dark" type="submit" :disabled="form.processing">Sign up</button>
          </form>
          <small class="text-body-secondary">
            <a href="#" data-bs-toggle="modal" data-bs-target="#LoginPanel">Masuk disini</a>, jika sudah mempunyai akun</small>
        </div>
      </div>
    </div>
  </div>
</template>