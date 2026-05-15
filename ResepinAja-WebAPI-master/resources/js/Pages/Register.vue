<!-- Register.vue -->
<script setup>
import { useForm } from '@inertiajs/vue3'
 
const form = useForm({ username:'', no_hp:'', password:'', password_confirmation:'' })
 
function submit() {
  form.post('/register', {
    onSuccess: () => {
      bootstrap.Modal.getInstance(document.getElementById('RegisterPanel'))?.hide()
      new bootstrap.Modal(document.getElementById('LoginPanel')).show()
      form.reset()
    }
  })
}
</script>
 
<template>
  <div class="modal fade" id="RegisterPanel" tabindex="-1">
    <div class="modal-dialog modal-dialog-centered">
      <div class="modal-content ra-modal">
        <div class="ra-modal-head">
          <div>
            <h2 class="ra-modal-title">Buat Akun Baru</h2>
            <p class="ra-modal-sub">Bergabung dengan komunitas Resepin Aja</p>
          </div>
          <button class="ra-modal-close" data-bs-dismiss="modal"><i class="bi bi-x-lg"></i></button>
        </div>
        <div class="ra-modal-body">
          <form @submit.prevent="submit" class="ra-form">
            <div class="fgroup">
              <label class="field-label">Username</label>
              <div class="input-icon-wrap">
                <i class="bi bi-person input-icon"></i>
                <input v-model="form.username" type="text" class="field-input input-with-icon" placeholder="Username unik kamu" required />
              </div>
              <p v-if="form.errors.username" class="field-err">{{ form.errors.username }}</p>
            </div>
            <div class="fgroup">
              <label class="field-label">No. HP</label>
              <div class="input-icon-wrap">
                <i class="bi bi-phone input-icon"></i>
                <input v-model="form.no_hp" type="text" class="field-input input-with-icon" placeholder="08xxxxxxxxxx" required />
              </div>
            </div>
            <div class="frow">
              <div class="fgroup">
                <label class="field-label">Password</label>
                <input v-model="form.password" type="password" class="field-input" placeholder="Min. 8 karakter" required />
              </div>
              <div class="fgroup">
                <label class="field-label">Konfirmasi</label>
                <input v-model="form.password_confirmation" type="password" class="field-input" placeholder="Ulangi password" required />
              </div>
            </div>
            <button type="submit" class="ra-submit-btn" :disabled="form.processing">
              <span v-if="!form.processing"><i class="bi bi-person-plus-fill"></i> Daftar Sekarang</span>
              <span v-else><span class="spinner-border spinner-border-sm"></span> Mendaftar...</span>
            </button>
          </form>
          <p class="ra-switch">Sudah punya akun? <a href="#" data-bs-toggle="modal" data-bs-target="#LoginPanel" data-bs-dismiss="modal">Masuk di sini</a></p>
        </div>
      </div>
    </div>
  </div>
</template>
 
<style scoped>
.ra-modal { background: var(--bg2); border: 1px solid var(--border2); border-radius: 20px; overflow: hidden; box-shadow: var(--shadow-lg); }
.ra-modal-head { display: flex; align-items: flex-start; justify-content: space-between; padding: 28px 28px 0; }
.ra-modal-title { font-family: 'Playfair Display', serif; font-size: 1.6rem; font-weight: 700; color: var(--text); margin: 0 0 4px; }
.ra-modal-sub { font-size: 13px; color: var(--text3); margin: 0; }
.ra-modal-close { width: 32px; height: 32px; border-radius: 9px; background: var(--bg3); border: none; color: var(--text2); font-size: 14px; cursor: pointer; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.ra-modal-body { padding: 24px 28px 28px; }
.ra-form { display: flex; flex-direction: column; gap: 14px; }
.fgroup { display: flex; flex-direction: column; gap: 7px; }
.frow { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
.input-icon-wrap { position: relative; }
.input-icon { position: absolute; left: 14px; top: 50%; transform: translateY(-50%); color: var(--text3); font-size: 16px; pointer-events: none; }
.input-with-icon { padding-left: 40px; }
.field-err { font-size: 12px; color: var(--danger); margin: 2px 0 0; }
.ra-submit-btn { width: 100%; padding: 13px; border-radius: 50px; background: var(--gold); color: #0e0e0e; border: none; font-size: 15px; font-weight: 600; cursor: pointer; display: flex; align-items: center; justify-content: center; gap: 8px; transition: all 0.2s; margin-top: 4px; }
.ra-submit-btn:hover { background: var(--gold-light); }
.ra-submit-btn:disabled { opacity: 0.55; cursor: not-allowed; }
.ra-switch { text-align: center; font-size: 13px; color: var(--text3); margin: 16px 0 0; }
.ra-switch a { color: var(--gold); font-weight: 600; }
</style>