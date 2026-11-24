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
  position: relative;
  margin: 0 -24px 48px;
  padding: 60px 24px 40px;
  overflow: hidden;
  background: var(--bg2, #343434);
  border-bottom: 1px solid var(--border, rgba(255,255,255,.12));
  color: var(--text, #f7f7f7);
}
.profile-hero-bg {
  position: absolute;
  inset: 0;
  background: radial-gradient(ellipse at 60% 0%, var(--gold-bg, rgba(255,255,255,.08)) 0%, transparent 70%);
  pointer-events: none;
}
.profile-hero-content {
  position: relative;
  z-index: 2;
  max-width: 1400px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  gap: 32px;
}
.profile-avatar-wrap { flex-shrink: 0; }
.profile-avatar {
  width: 110px;
  height: 110px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--bg4, #505050), var(--bg2, #343434));
  border: 2px solid var(--border2, rgba(255,255,255,.22));
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: var(--shadow, 0 4px 24px rgba(0,0,0,.2));
}
.profile-avatar-letter {
  font-family: 'Playfair Display', serif;
  font-size: 3rem;
  font-weight: 700;
  color: var(--text, #f7f7f7);
}
.profile-meta { flex: 1; min-width: 0; }
.profile-username {
  font-family: 'Playfair Display', serif;
  font-size: 2.5rem;
  font-weight: 700;
  color: var(--text, #f7f7f7);
  margin: 0 0 8px;
  overflow-wrap: anywhere;
}
.profile-bio {
  font-size: 15px;
  color: var(--text3, rgba(255,255,255,.62));
  margin: 0 0 20px;
  line-height: 1.65;
  max-width: 480px;
  overflow-wrap: anywhere;
}
.profile-stats { display: flex; gap: 28px; }
.pstat { display: flex; flex-direction: column; }
.pstat-val {
  font-family: 'Playfair Display', serif;
  font-size: 1.8rem;
  font-weight: 700;
  color: var(--gold, #dedede);
  line-height: 1;
}
.pstat-lbl {
  font-size: 12px;
  color: var(--text3, rgba(255,255,255,.62));
  font-weight: 500;
  margin-top: 4px;
}
.profile-resep { padding-bottom: 80px; color: var(--text, #f7f7f7); }
.section-header { margin-bottom: 28px; }
.section-h2 {
  font-family: 'Playfair Display', serif;
  font-size: 2rem;
  font-weight: 700;
  color: var(--text, #f7f7f7);
  margin: 0;
}
.section-h2 em { color: var(--gold, #dedede); font-style: italic; }
.resep-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px,1fr));
  gap: 20px;
}
.empty-profile {
  text-align: center;
  padding: 64px 24px;
  color: var(--text3, rgba(255,255,255,.62));
  background: var(--bg2, #343434);
  border: 1px solid var(--border, rgba(255,255,255,.12));
  border-radius: var(--radius-lg, 20px);
}
.empty-profile i {
  font-size: 48px;
  display: block;
  margin-bottom: 12px;
  color: var(--text4, rgba(255,255,255,.42));
}
.empty-profile p { margin: 0; color: var(--text2, rgba(255,255,255,.82)); }

/* Pastikan tampilan mengikuti pilihan tema dari App.vue. */
:global(html[data-theme="light"]) .profile-hero {
  background: var(--bg2, #e4e4e4);
}
:global(html[data-theme="light"]) .profile-avatar {
  background: linear-gradient(135deg, var(--bg3, #d8d8d8), var(--bg2, #e4e4e4));
}
:global(html[data-theme="light"]) .empty-profile {
  background: var(--bg2, #e4e4e4);
}

@media (max-width: 640px) {
  .profile-hero { margin-left: -16px; margin-right: -16px; padding: 40px 16px 32px; }
  .profile-hero-content { flex-direction: column; text-align: center; gap: 20px; }
  .profile-bio { margin-left: auto; margin-right: auto; }
  .profile-stats { justify-content: center; }
  .profile-username { font-size: 2rem; }
  .section-h2 { font-size: 1.6rem; }
}
</style>