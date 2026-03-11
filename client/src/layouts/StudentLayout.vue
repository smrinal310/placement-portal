<template>
  <div class="student-layout">

    <!-- Mobile Overlay -->
    <div v-if="isSidebarOpen" class="student-layout__overlay" @click="isSidebarOpen = false"></div>

    <!-- Sidebar -->
    <aside class="student-layout__sidebar" :class="{ 'student-layout__sidebar--open': isSidebarOpen }">
      <div class="student-layout__logo">
          <span class="student-layout__logo-title">PlacementPortal</span>
          <span class="student-layout__logo-sub">Student Panel</span>
      </div>

      <nav class="student-layout__nav">
        <RouterLink
          to="/student/dashboard"
          class="student-layout__nav-item"
          active-class="nav-item--active"
          @click="isSidebarOpen = false"
        >
          <i class="bi bi-grid-fill"></i>
          <span>Dashboard</span>
        </RouterLink>

        <RouterLink
          to="/student/applications"
          class="student-layout__nav-item"
          active-class="nav-item--active"
          @click="isSidebarOpen = false"
        >
          <i class="bi bi-file-earmark-text-fill"></i>
          <span>My Applications</span>
        </RouterLink>

        <RouterLink
          to="/student/profile"
          class="student-layout__nav-item"
          active-class="nav-item--active"
          @click="isSidebarOpen = false"
        >
          <i class="bi bi-person-fill"></i>
          <span>Profile</span>
        </RouterLink>
      </nav>

      <div class="student-layout__profile">
        <div class="student-layout__profile-info">
          <AppAvatar size="sm" :name="authStore.user?.name || 'Student'" />
          <div class="student-layout__profile-text">
            <span class="student-layout__profile-name">{{ authStore.user?.name || 'Student' }}</span>
            <span class="student-layout__profile-role">Student</span>
          </div>
        </div>
        <div class="student-layout__profile-actions">
          <!-- Notification Bell -->
          <div class="student-layout__notif-wrap" ref="notifWrapRef">
            <button
              class="student-layout__notif-btn"
              :class="{ 'student-layout__notif-btn--active': notifOpen }"
              aria-label="Notifications"
              @click="toggleNotif"
            >
              <i class="bi bi-bell-fill"></i>
              <span v-if="unreadCount > 0" class="student-layout__notif-badge">{{ unreadCount > 9 ? '9+' : unreadCount }}</span>
            </button>
          </div>

          <!-- Dropdown panel — teleported to body so it escapes sidebar clipping -->
          <Teleport to="body">
            <div
              v-if="notifOpen"
              class="student-layout__notif-panel"
              :style="panelStyle"
            >
              <div class="student-layout__notif-header">
                <span class="student-layout__notif-title">Notifications</span>
                <button v-if="unreadCount > 0" class="student-layout__notif-markall" @click="markAll">Mark all read</button>
              </div>
              <div class="student-layout__notif-list">
                <div v-if="notifications.length === 0" class="student-layout__notif-empty">
                  No notifications
                </div>
                <div
                  v-for="n in notifications"
                  :key="n.id"
                  class="student-layout__notif-item"
                  :class="{ 'student-layout__notif-item--unread': !n.is_read }"
                  @click="markRead(n)"
                >
                  <div class="student-layout__notif-item-title">{{ n.title }}</div>
                  <div class="student-layout__notif-item-msg">{{ n.message }}</div>
                  <div class="student-layout__notif-item-time">{{ formatRelative(n.created_at) }}</div>
                </div>
              </div>
            </div>
          </Teleport>

          <button class="student-layout__logout" @click="handleLogout" aria-label="Logout">
            <i class="bi bi-box-arrow-right"></i>
          </button>
        </div>
      </div>
    </aside>

    <!-- Mobile toggle -->
    <button class="student-layout__mobile-toggle" @click="isSidebarOpen = true" aria-label="Open menu">
      <i class="bi bi-list"></i>
    </button>

    <!-- Page Content -->
    <main class="student-layout__content">
      <RouterView />
    </main>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import AppAvatar from '@/components/common/AppAvatar.vue'
import * as studentApi from '@/api/student'

const router = useRouter()
const authStore = useAuthStore()
const isSidebarOpen = ref(false)

const handleLogout = async () => {
  await authStore.logout()
  router.push('/login')
}

// ── Notifications ──
const notifOpen = ref(false)
const notifications = ref([])
const unreadCount = ref(0)
const notifWrapRef = ref(null)
const panelAnchor = ref({ top: 0, left: 0 })

const panelStyle = computed(() => ({
  position: 'fixed',
  bottom: `${window.innerHeight - panelAnchor.value.top + 8}px`,
  left: `${panelAnchor.value.left}px`,
  zIndex: 9999,
}))

function formatRelative(iso) {
  if (!iso) return ''
  const diff = Date.now() - new Date(iso).getTime()
  const mins = Math.floor(diff / 60000)
  if (mins < 1) return 'just now'
  if (mins < 60) return `${mins}m ago`
  const hrs = Math.floor(mins / 60)
  if (hrs < 24) return `${hrs}h ago`
  return `${Math.floor(hrs / 24)}d ago`
}

async function fetchNotifications() {
  try {
    const res = await studentApi.getNotifications()
    notifications.value = res.data?.notifications ?? []
    unreadCount.value = res.data?.unread_count ?? 0
  } catch {
    // silent
  }
}

async function markRead(n) {
  if (n.is_read) return
  try {
    await studentApi.markNotificationRead(n.id)
    n.is_read = true
    unreadCount.value = Math.max(0, unreadCount.value - 1)
  } catch {
    // silent
  }
}

async function markAll() {
  try {
    await studentApi.markAllNotificationsRead()
    notifications.value.forEach((n) => { n.is_read = true })
    unreadCount.value = 0
  } catch {
    // silent
  }
}

function toggleNotif() {
  notifOpen.value = !notifOpen.value
  if (notifOpen.value) {
    fetchNotifications()
    if (notifWrapRef.value) {
      const rect = notifWrapRef.value.getBoundingClientRect()
      panelAnchor.value = { top: rect.top, left: rect.right + 8 }
    }
  }
}

function handleOutsideClick(e) {
  const panel = document.querySelector('.student-layout__notif-panel')
  if (
    notifWrapRef.value && !notifWrapRef.value.contains(e.target) &&
    panel && !panel.contains(e.target)
  ) {
    notifOpen.value = false
  }
}

onMounted(() => {
  fetchNotifications()
  document.addEventListener('click', handleOutsideClick)
})

onUnmounted(() => {
  document.removeEventListener('click', handleOutsideClick)
})
</script>

<style scoped>
.student-layout {
  display: flex;
  min-height: 100vh;
  background-color: var(--color-content-bg);
}

.student-layout__overlay {
  position: fixed;
  inset: 0;
  background-color: rgba(0, 0, 0, 0.3);
  z-index: 40;
}

/* ── Sidebar ── */
.student-layout__sidebar {
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

.student-layout__logo {
  display: flex;
  flex-direction: column;
  justify-content: center;
  gap: 3px;
  height: var(--navbar-height);
  padding-inline: var(--space-5);
  flex-shrink: 0;
  border-bottom: var(--border-width) solid var(--color-border);
}

.student-layout__logo-title {
  font-size: var(--font-size-lg);
  font-weight: var(--font-weight-bold);
  color: var(--color-text-primary);
  line-height: 1;
  letter-spacing: -0.02em;
}

.student-layout__logo-sub {
  font-size: var(--font-size-sm);
  color: var(--color-text-muted);
  line-height: 1;
}

.student-layout__nav {
  flex-grow: 1;
  overflow-y: auto;
  padding: var(--space-3);
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.student-layout__nav-item {
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

.student-layout__nav-item i {
  font-size: var(--font-size-md);
  width: 20px;
  text-align: center;
  flex-shrink: 0;
}

.student-layout__nav-item:hover {
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

/* ── Profile strip ── */
.student-layout__profile {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--space-3);
  border-top: var(--border-width) solid var(--color-border);
  background-color: var(--color-gray-50);
  flex-shrink: 0;
}

.student-layout__profile-info {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  min-width: 0;
}

.student-layout__profile-text {
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.student-layout__profile-name {
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-bold);
  color: var(--color-text-primary);
  line-height: var(--line-height-tight);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.student-layout__profile-role {
  font-size: var(--font-size-xs);
  color: var(--color-text-muted);
  text-transform: capitalize;
}

.student-layout__logout {
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
  flex-shrink: 0;
  width: 32px;
  height: 32px;
}

.student-layout__logout:hover {
  background-color: var(--color-danger-light);
  color: var(--color-danger);
}

/* Profile actions row */
.student-layout__profile-actions {
  display: flex;
  align-items: center;
  gap: var(--space-1);
  flex-shrink: 0;
}

/* Notification bell */
.student-layout__notif-wrap {
  position: relative;
}

.student-layout__notif-btn {
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
  position: relative;
  outline: none;
  width: 32px;
  height: 32px;
}

.student-layout__notif-btn:hover,
.student-layout__notif-btn--active {
  background-color: var(--color-primary-light);
  color: var(--color-primary);
}

.student-layout__notif-badge {
  position: absolute;
  top: -2px;
  right: -2px;
  min-width: 16px;
  height: 16px;
  padding: 0 3px;
  background-color: var(--color-danger, #dc2626);
  color: var(--color-white);
  font-size: 10px;
  font-weight: var(--font-weight-bold);
  border-radius: 999px;
  display: flex;
  align-items: center;
  justify-content: center;
  line-height: 1;
}

/* Notification panel — fixed to viewport via Teleport */
.student-layout__notif-panel {
  width: 300px;
  background: var(--color-white);
  border: var(--border-width) solid var(--color-border);
  border-radius: var(--border-radius-lg);
  box-shadow: var(--shadow-lg);
  overflow: hidden;
}

.student-layout__notif-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--space-3) var(--space-4);
  border-bottom: var(--border-width) solid var(--color-border);
}

.student-layout__notif-title {
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
}

.student-layout__notif-markall {
  background: none;
  border: none;
  font-size: var(--font-size-xs);
  color: var(--color-primary);
  cursor: pointer;
  padding: 0;
  font-weight: var(--font-weight-medium);
}

.student-layout__notif-markall:hover {
  text-decoration: underline;
}

.student-layout__notif-list {
  max-height: 320px;
  overflow-y: auto;
}

.student-layout__notif-empty {
  padding: var(--space-6) var(--space-4);
  text-align: center;
  font-size: var(--font-size-sm);
  color: var(--color-text-muted);
}

.student-layout__notif-item {
  padding: var(--space-3) var(--space-4);
  border-bottom: var(--border-width) solid var(--color-border);
  cursor: pointer;
  transition: background-color var(--transition-fast);
}

.student-layout__notif-item:last-child {
  border-bottom: none;
}

.student-layout__notif-item:hover {
  background-color: var(--color-gray-50);
}

.student-layout__notif-item--unread {
  background-color: var(--color-primary-light);
}

.student-layout__notif-item--unread:hover {
  background-color: color-mix(in srgb, var(--color-primary-light) 80%, var(--color-primary) 20%);
}

.student-layout__notif-item-title {
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
  margin-bottom: 2px;
}

.student-layout__notif-item-msg {
  font-size: var(--font-size-xs);
  color: var(--color-text-secondary);
  line-height: var(--line-height-snug);
  margin-bottom: 4px;
}

.student-layout__notif-item-time {
  font-size: var(--font-size-xs);
  color: var(--color-text-muted);
}

/* ── Main Content ── */
.student-layout__content {
  flex-grow: 1;
  margin-left: var(--sidebar-width);
  min-height: 100vh;
  padding: var(--content-padding);
}

/* ── Mobile toggle ── */
.student-layout__mobile-toggle {
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
  .student-layout__sidebar {
    transform: translateX(-100%);
  }

  .student-layout__sidebar--open {
    transform: translateX(0);
  }

  .student-layout__content {
    margin-left: 0;
    padding-top: calc(var(--space-3) + 36px + var(--space-3));
  }

  .student-layout__mobile-toggle {
    display: flex;
  }
}
</style>
