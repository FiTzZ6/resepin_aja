<!-- Logout.vue -->
<template>
  <div class="modal fade" id="LogoutPanel" tabindex="-1">
    <div class="modal-dialog modal-dialog-centered modal-sm">
      <div class="modal-content ra-modal">
        <div class="ra-modal-head">
          <h2 class="ra-modal-title" style="font-size:1.3rem">Keluar dari Akun?</h2>
          <button class="ra-modal-close" data-bs-dismiss="modal"><i class="bi bi-x-lg"></i></button>
        </div>
        <div class="ra-modal-body">
          <p style="font-size:14px; color:var(--text2); margin-bottom:20px; line-height:1.65">
            Beberapa fitur tidak tersedia tanpa login. Yakin ingin keluar?
          </p>
          <div style="display:flex; flex-direction:column; gap:10px">
            <a href="/logout" class="ra-submit-btn ra-submit-btn--danger">
              <i class="bi bi-box-arrow-right"></i> Ya, Keluar
            </a>
            <button data-bs-dismiss="modal" class="ra-submit-btn" style="background:var(--bg3); color:var(--text); border:1px solid var(--border)">
              Tidak Jadi
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
 
<style scoped>
.ra-modal { background: var(--bg2); border: 1px solid var(--border2); border-radius: 20px; overflow: hidden; box-shadow: var(--shadow-lg); }
.ra-modal-head { display: flex; align-items: center; justify-content: space-between; padding: 24px 24px 0; }
.ra-modal-title { font-family: 'Playfair Display', serif; font-weight: 700; color: var(--text); margin: 0; }
.ra-modal-close { width: 30px; height: 30px; border-radius: 8px; background: var(--bg3); border: none; color: var(--text2); font-size: 13px; cursor: pointer; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.ra-modal-body { padding: 20px 24px 24px; }
.ra-submit-btn { width: 100%; padding: 12px; border-radius: 50px; background: var(--gold); color: #0e0e0e; border: none; font-size: 14px; font-weight: 600; cursor: pointer; display: flex; align-items: center; justify-content: center; gap: 8px; text-decoration: none; transition: all 0.2s; }
.ra-submit-btn--danger { background: var(--danger-bg); color: var(--danger); border: 1px solid rgba(229,115,115,0.25); }
.ra-submit-btn--danger:hover { background: rgba(229,115,115,0.2); }
</style>