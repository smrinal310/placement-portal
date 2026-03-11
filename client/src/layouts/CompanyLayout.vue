<template>
  <div class="company-layout">

    <!-- Mobile Overlay -->
    <div v-if="isSidebarOpen" class="company-layout__overlay" @click="isSidebarOpen = false"></div>

    <!-- Sidebar -->
    <aside class="company-layout__sidebar" :class="{ 'company-layout__sidebar--open': isSidebarOpen }">
      <div class="company-layout__logo">
        <span class="company-layout__logo-title">PlacementPortal</span>
        <span class="company-layout__logo-sub">Company Panel</span>
      </div>

      <nav class="company-layout__nav">
        <RouterLink to="/company/dashboard" class="company-layout__nav-item" active-class="nav-item--active"
          @click="isSidebarOpen = false">
          <i class="bi bi-grid-fill"></i>
          <span>Dashboard</span>
        </RouterLink>

        <RouterLink to="/company/drives" class="company-layout__nav-item" active-class="nav-item--active"
          :class="{ 'nav-item--active': isDrivesActive }"
          @click="isSidebarOpen = false">
          <i class="bi bi-briefcase-fill"></i>
          <span>My Drives</span>
        </RouterLink>

        <RouterLink to="/company/profile" class="company-layout__nav-item" active-class="nav-item--active"
          @click="isSidebarOpen = false">
          <i class="bi bi-building"></i>
          <span>Company Profile</span>
        </RouterLink>


      </nav>

      <div class="company-layout__profile">
        <div class="company-layout__profile-info">
          <AppAvatar size="sm" :name="authStore.user?.name || 'Company'" />
          <div class="company-layout__profile-text">
            <span class="company-layout__profile-name">{{ authStore.user?.name || 'Company' }}</span>
            <span class="company-layout__profile-role">company</span>
          </div>
        </div>
        <button class="company-layout__logout" @click="handleLogout" aria-label="Logout">
          <i class="bi bi-box-arrow-right"></i>
        </button>
      </div>
    </aside>

    <!-- Mobile toggle (visible only on small screens) -->
    <button class="company-layout__mobile-toggle" @click="isSidebarOpen = true" aria-label="Open menu">
      <i class="bi bi-list"></i>
    </button>

    <!-- Page Content -->
    <main class="company-layout__content">
      <RouterView />
    </main>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter, useRoute, RouterLink } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import AppAvatar from '@/components/common/AppAvatar.vue'

const router = useRouter()
const route = useRoute()

const isDrivesActive = computed(() => route.path.startsWith('/company/drives'))
const authStore = useAuthStore()

const isSidebarOpen = ref(false)

const handleLogout = async () => {
  await authStore.logout()
  router.push('/login')
}
</script>

<style scoped>
.company-layout {
  display: flex;
  min-height: 100vh;
  background-color: var(--color-content-bg);
}

.company-layout__overlay {
  position: fixed;
  inset: 0;
  background-color: rgba(0, 0, 0, 0.3);
  z-index: 40;
}

/* ── Sidebar ── */
.company-layout__sidebar {
  position: fixed;
  top: 0;
  left: 0;
  bottom: 0;
  width: var(--sidebar-width);
  background-color: var(--color-sidebar-bg);
  border-right: var(--border-width) solid var(--color-border);
  z-index: 50;
  display: flex;
  flex-direction: column;
  transition: transform var(--transition-base);
}

.company-layout__logo {
  display: flex;
  flex-direction: column;
  justify-content: center;
  gap: 3px;
  height: var(--navbar-height);
  padding-inline: var(--space-5);
  flex-shrink: 0;
  border-bottom: var(--border-width) solid var(--color-border);
}

.company-layout__logo-title {
  font-size: var(--font-size-lg);
  font-weight: var(--font-weight-bold);
  color: var(--color-text-primary);
  line-height: 1;
  letter-spacing: -0.02em;
}

.company-layout__logo-sub {
  font-size: var(--font-size-sm);
  color: var(--color-text-muted);
  line-height: 1;
}

.company-layout__nav {
  flex-grow: 1;
  overflow-y: auto;
  padding: var(--space-3);
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.company-layout__nav-item {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding-block: 10px;
  padding-inline: var(--space-3);
  border-radius: var(--border-radius-lg);
  color: var(--color-text-secondary);
  text-decoration: none;
  transition: background-color var(--transition-fast), color var(--transition-fast);
  font-size: var(--font-size-base);
  font-weight: var(--font-weight-medium);
}

.company-layout__nav-item i {
  font-size: var(--font-size-md);
  width: 20px;
  text-align: center;
  flex-shrink: 0;
}

.company-layout__nav-item:hover {
  background-color: var(--color-gray-100);
  color: var(--color-text-primary);
}

.nav-item--active {
  background-color: var(--color-primary-light);
  color: var(--color-primary);
  font-weight: var(--font-weight-semibold);
}

.nav-item--active:hover {
  background-color: var(--color-primary-light);
  color: var(--color-primary);
}

.company-layout__profile {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--space-3);
  border-top: var(--border-width) solid var(--color-border);
  background-color: var(--color-gray-50);
  flex-shrink: 0;
}

.company-layout__profile-info {
  display: flex;
  align-items: center;
  gap: var(--space-3);
}

.company-layout__profile-text {
  display: flex;
  flex-direction: column;
}

.company-layout__profile-name {
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-bold);
  color: var(--color-text-primary);
  line-height: var(--line-height-tight);
}

.company-layout__profile-role {
  font-size: var(--font-size-xs);
  color: var(--color-text-muted);
  text-transform: capitalize;
}

.company-layout__logout {
  background: none;
  border: none;
  color: var(--color-text-muted);
  font-size: var(--font-size-md);
  cursor: pointer;
  padding: 0;
  border-radius: var(--border-radius-md);
  transition: background-color var(--transition-fast), color var(--transition-fast);
  display: flex;
  align-items: center;
  justify-content: center;
  outline: none;
  width: 32px;
  height: 32px;
}

.company-layout__logout:hover {
  background-color: var(--color-danger-light);
  color: var(--color-danger);
}

/* ── Main Content ── */
.company-layout__content {
  flex-grow: 1;
  margin-left: var(--sidebar-width);
  min-height: 100vh;
  padding: var(--content-padding);
}

/* Mobile toggle */
.company-layout__mobile-toggle {
  display: none;
  position: fixed;
  top: var(--space-3);
  left: var(--space-3);
  z-index: 45;
  background: var(--color-white);
  border: var(--border-width) solid var(--color-border);
  border-radius: var(--border-radius-md);
  width: 36px;
  height: 36px;
  font-size: var(--font-size-xl);
  color: var(--color-text-secondary);
  cursor: pointer;
  align-items: center;
  justify-content: center;
  box-shadow: var(--shadow-sm);
}

/* ── Mobile ── */
@media (max-width: 768px) {
  .company-layout__sidebar {
    transform: translateX(-100%);
  }

  .company-layout__sidebar--open {
    transform: translateX(0);
  }

  .company-layout__content {
    margin-left: 0;
    padding-top: calc(var(--space-3) + 36px + var(--space-3));
  }

  .company-layout__mobile-toggle {
    display: flex;
  }
}
</style>
