<!-- ════════════════════════════════════════════════
    Profil.vue
════════════════════════════════════════════════ -->
<script setup>
import { Link } from '@inertiajs/vue3'
import App from './App.vue';
import ResepCard from './components/ResepCard.vue';
import "bootstrap-icons/font/bootstrap-icons.css";

const data = defineProps({ userProfile: Array, resepProfile: Array })
document.title = `${data.userProfile.username} – Resepin Aja`;
</script>

<template>
  <App>
    <!-- Profile Hero -->
    <div class="profile-hero">
      <div class="profile-hero-bg"></div>
      <div class="profile-hero-content">
        <div class="profile-avatar-wrap">
          <div class="profile-avatar">
            <span class="profile-avatar-letter">{{ userProfile.username?.charAt(0)?.toUpperCase() }}</span>
          </div>
        </div>
        <div class="profile-meta">
          <h1 class="profile-username">{{ userProfile.username }}</h1>
          <p class="profile-bio">{{ userProfile.deskripsi_user || 'Belum ada deskripsi.' }}</p>
          <div class="profile-stats">
            <div class="pstat">
              <span class="pstat-val">{{ resepProfile?.length || 0 }}</span>
              <span class="pstat-lbl">Resep</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Resep Grid -->
    <div class="profile-resep">
      <div class="section-header">
        <h2 class="section-h2">Resep oleh <em>{{ userProfile.username }}</em></h2>
      </div>
      <div v-if="resepProfile?.length" class="resep-grid">
        <ResepCard v-for="r in resepProfile" :key="r.id_resep" :resepData="r" />
      </div>
      <div v-else class="empty-profile">
        <i class="bi bi-journal-x"></i>
        <p>Belum ada resep yang dibagikan.</p>
      </div>
    </div>
  </App>
</template>

<style scoped>
.profile-hero {
  position: relative; margin: 0 -24px; padding: 60px 24px 40px;
  border-bottom: 1px solid rgba(255,255,255,0.07); margin-bottom: 48px;
  overflow: hidden;
}
.profile-hero-bg {
  position: absolute; inset: 0;
  background: radial-gradient(ellipse at 60% 0%, rgba(212,168,83,0.08) 0%, transparent 70%);
}
.profile-hero-content {
  position: relative; z-index: 2; max-width: 1400px; margin: 0 auto;
  display: flex; align-items: center; gap: 32px;
}
.profile-avatar-wrap { flex-shrink: 0; }
.profile-avatar {
  width: 110px; height: 110px; border-radius: 50%;
  background: linear-gradient(135deg,rgba(212,168,83,0.2),rgba(212,168,83,0.05));
  border: 2px solid rgba(212,168,83,0.4);
  display: flex; align-items: center; justify-content: center;
}
.profile-avatar-letter { font-family: 'Playfair Display', serif; font-size: 3rem; font-weight: 700; color: #d4a853; }
.profile-meta { flex: 1; }
.profile-username { font-family: 'Playfair Display', serif; font-size: 2.5rem; font-weight: 700; color: #f0ece4; margin: 0 0 8px; }
.profile-bio { font-size: 15px; color: rgba(240,236,228,0.5); margin: 0 0 20px; line-height: 1.65; max-width: 480px; }
.profile-stats { display: flex; gap: 28px; }
.pstat { display: flex; flex-direction: column; }
.pstat-val { font-family: 'Playfair Display', serif; font-size: 1.8rem; font-weight: 700; color: #d4a853; line-height: 1; }
.pstat-lbl { font-size: 12px; color: rgba(240,236,228,0.4); font-weight: 500; margin-top: 2px; }

.profile-resep { padding-bottom: 80px; }
.section-header { margin-bottom: 28px; }
.section-h2 { font-family: 'Playfair Display', serif; font-size: 2rem; font-weight: 700; color: #f0ece4; margin: 0; }
.section-h2 em { color: #d4a853; font-style: italic; }

.resep-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px,1fr)); gap: 20px; }
.empty-profile { text-align: center; padding: 64px; color: rgba(240,236,228,0.3); }
.empty-profile i { font-size: 48px; display: block; margin-bottom: 12px; color: rgba(212,168,83,0.25); }

@media (max-width: 640px) {
  .profile-hero-content { flex-direction: column; text-align: center; }
  .profile-bio { margin-left: auto; margin-right: auto; }
  .profile-stats { justify-content: center; }
}
</style>