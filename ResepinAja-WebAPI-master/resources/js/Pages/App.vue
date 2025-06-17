<script setup>
import "bootstrap-icons/font/bootstrap-icons.css";
import { Link, usePage } from '@inertiajs/vue3'
import Login from './Login.vue';
import Logout from './Logout.vue';
import Register from './Register.vue';
import Searchbar from './components/Searchbar.vue';

const userData = usePage().props.auth_user;

</script>

<template>
  <nav class="navbar navbar-expand-md" style="background-color: rgb(255, 110, 85)">
    <div class="container-fluid">
      <Link class="navbar-brand p-0" href="/"><img src="../../../public/assets/Logo.png" alt="" width="75" height="75"></Link>
      <button class="navbar-toggler bg-warning" type="button" data-bs-toggle="collapse"
        data-bs-target="#navbarSupportedContent" aria-controls="navbarSupportedContent" aria-expanded="false"
        aria-label="Toggle navigation">
        <span class="navbar-toggler-icon"></span>
      </button>
      <div class="collapse navbar-collapse" id="navbarSupportedContent">
        <Searchbar/>
        <ul class="navbar-nav mb-2 mb-md-0">
          <li class="nav-item me-2">
            <Link class="nav-link active" aria-current="page" href="/">Beranda</Link>
          </li>
          <li class="nav-item me-2">
            <Link class="nav-link" href="/resepcari">Resep</Link>
          </li>
          <!-- User Info -->
          <li class="nav-item" v-if="userData">
            <a class="nav-link dropdown-toggle" href="#" role="button" data-bs-toggle="dropdown" aria-expanded="false">
              <img src="../../../public/assets/muehe.png" class="me-1 rounded-5" alt="..." width="30" height="30" />
              <span class="fw-bold text-dark">{{userData.username}}</span>
            </a>
            <div class="dropdown-menu dropdown-menu-end me-2 p-0">
              <div
                class="d-flex flex-column flex-lg-row align-items-stretch justify-content-start p-3 rounded-3 shadow-lg"
                data-bs-theme="light">
                <nav class="col-lg-8">
                  <ul class="list-unstyled d-flex flex-column gap-2">
                    <li>
                      <Link href="/tambahresep"
                        class="btn btn-hover-light rounded-2 d-flex align-items-start gap-2 py-2 px-3 lh-sm text-start">
                        <i class="bi bi-database-fill-add text-success" style="font-size: 24px;"></i>
                        <div><strong class="d-block">Tambah Resep</strong> <small class="text-secondary">Tambahkan resep
                            tersendiri</small></div>
                      </Link>
                    </li>
                    <li>
                      <Link :href="`/tersimpanresep/${userData.id_user}`"
                        class="btn btn-hover-light rounded-2 d-flex align-items-start gap-2 py-2 px-3 lh-sm text-start">
                        <i class="bi bi-bookmark-star-fill text-primary" style="font-size: 24px;"></i>
                        <div><strong class="d-block">Resep Tersimpan</strong> <small class="text-secondary">Resep
                            simpanan pengguna</small></div>
                      </Link>
                    </li>
                  </ul>
                </nav>
                <div class="d-none d-lg-block vr mx-4 opacity-10">&nbsp;</div>
                <hr class="d-lg-none" />
                <div class="col-lg-auto">
                  <nav>
                    <ul class="d-flex flex-column gap-2 list-unstyled small">
                      <li>
                        <Link :href='`/profil/${userData.id_user}`' class="dropdown-item text-dark fw-bold btn btn-light">
                          Profil
                        </Link>
                      </li>
                      <li>
                        <button type="button" class="dropdown-item text-danger fw-bold btn btn-warning"
                          data-bs-toggle="modal" data-bs-target="#LogoutPanel">
                          Logout
                        </button>
                      </li>
                      
                    </ul>
                  </nav>
                </div>
              </div>
            </div>
          </li>
          <li class="nav-item" v-else>
            <li>
              <button type="button" class="fw-bold btn btn-outline-dark"
                data-bs-toggle="modal" data-bs-target="#LoginPanel">
                Login
              </button>
            </li>
          </li>
        </ul>
      </div>
    </div>
  </nav>

  <!-- KONTEN -->
  <div class="container position-relative">
    <slot/>
  </div>
  <div v-if="userData">
    <Logout></Logout>
  </div>
  <div v-else>
    <Login></Login>
    <Register></Register>
  </div>

  <!-- FOOTER -->
  <div class="container">
    <footer class="d-flex flex-wrap justify-content-between align-items-center py-3 my-4 border-top">
      <div class="col-md-4 d-flex align-items-center">
        <a href="/" class="mb-3 me-2 mb-md-0 text-body-secondary text-decoration-none lh-1" aria-label="Bootstrap">
          <svg class="bi" width="30" height="24" aria-hidden="true">
            <use xlink:href="#bootstrap"></use>
          </svg>
        </a>
        <span class="mb-3 mb-md-0 text-body-secondary">© 2025 Ger Ger Jeger. Inc</span>
      </div>
      <ul class="nav col-md-4 justify-content-end list-unstyled d-flex">
        <li class="ms-3">
          <a class="text-body-secondary" href="#" aria-label="Instagram">
            <svg class="bi" width="24" height="24" aria-hidden="true">
              <use xlink:href="#instagram"></use>
            </svg></a>
        </li>
        <li class="ms-3">
          <a class="text-body-secondary" href="#" aria-label="Facebook">
            <svg class="bi" width="24" height="24">
              <use xlink:href="#facebook"></use>
            </svg></a>
        </li>
      </ul>
    </footer>
  </div>
</template>

