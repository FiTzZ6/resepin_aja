<script setup>

</script>

<template>
      <!-- LOGOUT -->
  <div class="modal fade" id="LogoutPanel" tabindex="-1">
    <div class="modal-dialog">
      <div class="modal-content rounded-4 shadow p-3">
        <div class="modal-header border-bottom-0">
          <h1 class="modal-title fs-5 fw-bold">Logout</h1>
          <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
        </div>
        <div class="modal-body py-0">
          <p>Yakin ingin keluar? beberapa fitur pada aplikasi tidak akan dapat digunakan jika tidak dalam keadaan
            <b>Masuk / Logged In</b>.</p>
        </div>
        <div class="modal-footer flex-column align-items-stretch w-100 gap-2 pb-3 border-top-0">
          <a type="button" class="btn btn btn-danger" href="/logout">Saya Yakin</a>
          <button type="button" class="btn btn btn-secondary" data-bs-dismiss="modal">Tidak Jadi</button>
        </div>
      </div>
    </div>
  </div>
</template>