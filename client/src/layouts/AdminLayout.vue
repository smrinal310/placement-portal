<template>
  <div class="admin-layout">

    <!-- Mobile Overlay -->
    <div v-if="isSidebarOpen" class="admin-layout__overlay" @click="isSidebarOpen = false"></div>

    <!-- Sidebar -->
    <aside class="admin-layout__sidebar" :class="{ 'admin-layout__sidebar--open': isSidebarOpen }">
      <div class="admin-layout__logo">
        <div class="admin-layout__logo-icon">P</div>
        <span class="admin-layout__logo-text">PlacementPortal</span>
      </div>

      <nav class="admin-layout__nav">
        <RouterLink to="/admin/dashboard" class="admin-layout__nav-item" active-class="nav-item--active"
          @click="isSidebarOpen = false">
          <i class="bi bi-grid-fill"></i>
          <span>Dashboard</span>
        </RouterLink>

        <RouterLink to="/admin/companies" class="admin-layout__nav-item" active-class="nav-item--active"
          @click="isSidebarOpen = false">
          <i class="bi bi-buildings"></i>
          <span>Companies</span>
        </RouterLink>

        <RouterLink to="/admin/students" class="admin-layout__nav-item" active-class="nav-item--active"
          @click="isSidebarOpen = false">
          <i class="bi bi-person-lines-fill"></i>
          <span>Students</span>
        </RouterLink>

        <RouterLink to="/admin/drives" class="admin-layout__nav-item" active-class="nav-item--active"
          @click="isSidebarOpen = false">
          <i class="bi bi-briefcase-fill"></i>
          <span>Placement Drives</span>
        </RouterLink>

        <RouterLink to="/admin/applications" class="admin-layout__nav-item" active-class="nav-item--active"
          @click="isSidebarOpen = false">
          <i class="bi bi-file-text-fill"></i>
          <span>All Applications</span>
        </RouterLink>

        <RouterLink to="/admin/settings" class="admin-layout__nav-item" active-class="nav-item--active"
          @click="isSidebarOpen = false">
          <i class="bi bi-gear-fill"></i>
          <span>Settings</span>
        </RouterLink>
      </nav>

      <div class="admin-layout__profile">
        <div class="admin-layout__profile-info">
          <AppAvatar size="sm" :name="authStore.user?.name || 'User'" />
          <div class="admin-layout__profile-text">
            <span class="admin-layout__profile-name">{{ authStore.user?.name || 'User' }}</span>
            <span class="admin-layout__profile-role">{{ authStore.user?.role || 'Admin' }}</span>
          </div>
        </div>
        <button class="admin-layout__logout" @click="handleLogout" aria-label="Logout">
          <i class="bi bi-box-arrow-right"></i>
        </button>
      </div>
    </aside>

    <!-- Main Content Wrapper -->
    <div class="admin-layout__main">
      <!-- Navbar -->
      <header class="admin-layout__navbar">
        <div class="admin-layout__navbar-left">
          <button class="admin-layout__mobile-toggle" @click="isSidebarOpen = true" aria-label="Open Request">
            <i class="bi bi-list"></i>
          </button>

          <div class="admin-layout__search">
            <i class="bi bi-search admin-layout__search-icon"></i>
            <input type="text" class="admin-layout__search-input" placeholder="Search for students, companies..." />
          </div>
        </div>

        <div class="admin-layout__navbar-right">
          <button class="admin-layout__notification" aria-label="Notifications">
            <i class="bi bi-bell-fill"></i>
            <span v-if="authStore.unreadNotifications > 0" class="admin-layout__notification-badge"></span>
          </button>

          <button class="admin-layout__help" aria-label="Help">
            <span>Help</span>
            <i class="bi bi-question-circle"></i>
          </button>
        </div>
      </header>

      <!-- Page Content -->
      <main class="admin-layout__content">
        <RouterView />
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter, RouterLink } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import AppAvatar from '../components/common/AppAvatar.vue'

const router = useRouter()
const authStore = useAuthStore()

const isSidebarOpen = ref(false)

const handleLogout = async () => {
  await authStore.logout()
  router.push('/login')
}
</script>

<style scoped>
.admin-layout {
  display: flex;
  min-height: 100vh;
  background-color: var(--color-content-bg);
}

.admin-layout__overlay {
  position: fixed;
  inset: 0;
  background-color: rgba(0, 0, 0, 0.3);
  z-index: 40;
  /* Between content and sidebar */
}

/* Sidebar Styles */
.admin-layout__sidebar {
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

.admin-layout__logo {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  height: var(--navbar-height);
  padding-block: 0;
  padding-inline: var(--space-6);
  flex-shrink: 0;
}

.admin-layout__logo-icon {
  width: var(--space-8);
  height: var(--space-8);
  background-color: var(--color-primary);
  color: var(--color-white);
  border-radius: var(--border-radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: var(--font-weight-bold);
}

.admin-layout__logo-text {
  font-size: var(--font-size-md);
  font-weight: var(--font-weight-bold);
  color: var(--color-text-primary);
}

.admin-layout__nav {
  flex-grow: 1;
  overflow-y: auto;
  padding: var(--space-4);
  display: flex;
  flex-direction: column;
  gap: var(--space-1);
}

.admin-layout__nav-item {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding-block: var(--space-3);
  padding-inline: var(--space-4);
  border-radius: var(--border-radius-md);
  color: var(--color-text-secondary);
  text-decoration: none;
  transition: all var(--transition-fast);
  font-size: var(--font-size-sm);
}

.admin-layout__nav-item i {
  font-size: var(--font-size-md);
}

.admin-layout__nav-item:hover {
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

.admin-layout__profile {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--space-4);
  border-top: var(--border-width) solid var(--color-border);
  flex-shrink: 0;
}

.admin-layout__profile-info {
  display: flex;
  align-items: center;
  gap: var(--space-3);
}

.admin-layout__profile-text {
  display: flex;
  flex-direction: column;
}

.admin-layout__profile-name {
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-bold);
  color: var(--color-text-primary);
  line-height: var(--line-height-tight);
}

.admin-layout__profile-role {
  font-size: var(--font-size-xs);
  color: var(--color-text-muted);
}

.admin-layout__logout {
  background: none;
  border: none;
  color: var(--color-text-muted);
  font-size: var(--font-size-md);
  cursor: pointer;
  padding: var(--space-1);
  border-radius: var(--border-radius-sm);
  transition: color var(--transition-fast);
  display: flex;
  align-items: center;
  justify-content: center;
  outline: none;
}

.admin-layout__logout:hover {
  color: var(--color-danger);
}

/* Main Content Area */
.admin-layout__main {
  flex-grow: 1;
  display: flex;
  flex-direction: column;
  margin-left: var(--sidebar-width);
  min-height: 100vh;
}

/* Navbar Styles */
.admin-layout__navbar {
  position: fixed;
  top: 0;
  right: 0;
  left: var(--sidebar-width);
  height: var(--navbar-height);
  background-color: var(--color-white);
  border-bottom: var(--border-width) solid var(--color-border);
  z-index: var(--z-navbar);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-block: 0;
  padding-inline: var(--space-6);
}

.admin-layout__navbar-left {
  display: flex;
  align-items: center;
  gap: var(--space-4);
  flex-grow: 1;
}

.admin-layout__mobile-toggle {
  display: none;
  background: none;
  border: none;
  font-size: var(--font-size-xl);
  color: var(--color-text-secondary);
  cursor: pointer;
  padding: var(--space-1);
}

.admin-layout__search {
  position: relative;
  width: 100%;
  max-width: 280px;
}

.admin-layout__search-icon {
  position: absolute;
  left: var(--space-3);
  top: 50%;
  transform: translateY(-50%);
  color: var(--color-text-muted);
  pointer-events: none;
}

.admin-layout__search-input {
  width: 100%;
  padding-top: var(--space-2);
  padding-right: var(--space-3);
  padding-bottom: var(--space-2);
  padding-left: var(--space-8);
  border: var(--border-width) solid var(--color-border);
  border-radius: var(--border-radius-md);
  font-size: var(--font-size-sm);
  color: var(--color-text-primary);
  background-color: var(--color-white);
  transition: border-color var(--transition-fast);
  outline: none;
}

.admin-layout__search-input::placeholder {
  color: var(--color-text-muted);
}

.admin-layout__search-input:focus {
  border-color: var(--color-primary);
}

.admin-layout__navbar-right {
  display: flex;
  align-items: center;
  gap: var(--space-4);
}

.admin-layout__notification {
  position: relative;
  background: none;
  border: none;
  color: var(--color-text-secondary);
  font-size: var(--font-size-lg);
  cursor: pointer;
  padding: var(--space-1);
  display: flex;
  align-items: center;
  justify-content: center;
  transition: color var(--transition-fast);
}

.admin-layout__notification:hover {
  color: var(--color-text-primary);
}

.admin-layout__notification-badge {
  position: absolute;
  top: 2px;
  right: 4px;
  width: 8px;
  height: 8px;
  background-color: var(--color-danger);
  border-radius: var(--border-radius-pill);
  border: 2px solid var(--color-white);
}

.admin-layout__help {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  background: none;
  border: none;
  color: var(--color-text-secondary);
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
  cursor: pointer;
  transition: color var(--transition-fast);
}

.admin-layout__help:hover {
  color: var(--color-text-primary);
}

/* Content Styles */
.admin-layout__content {
  margin-top: var(--navbar-height);
  padding: var(--content-padding);
  flex-grow: 1;
}

/* Mobile Breakpoint */
@media (max-width: 768px) {
  .admin-layout__sidebar {
    transform: translateX(-100%);
  }

  .admin-layout__sidebar--open {
    transform: translateX(0);
  }

  .admin-layout__main {
    margin-left: 0;
  }

  .admin-layout__navbar {
    left: 0;
    padding-block: 0;
    padding-inline: var(--space-4);
  }

  .admin-layout__mobile-toggle {
    display: flex;
  }

  .admin-layout__search {
    display: none;
  }
}
</style>
