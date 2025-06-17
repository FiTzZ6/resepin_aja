import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'
import Detail from '../views/Detail.vue'
import TambahResep from '../views/TambahResep.vue'
import Tersimpan from '../views/Tersimpan.vue'
import Profil from '../views/Profil.vue'

export default createRouter({
  history: createWebHistory(),
  routes: [
    { 
      path: '/',
      children:[
        {path: '', component: Home},
        {path: 'detail', component: Detail},
        {path: 'tambah', component: TambahResep},
        {path: 'tersimpan', component: Tersimpan},
        {path: 'profil', component: Profil},
        {path: 'percarian', component: Detail},
      ]
    }
  ]
})
