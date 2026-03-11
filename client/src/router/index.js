import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import AdminLayout from '@/layouts/AdminLayout.vue'
import CompanyLayout from '@/layouts/CompanyLayout.vue'
import StudentLayout from '@/layouts/StudentLayout.vue'

const GuestLayout = {
  template: '<router-view/>'
}

const PlaceholderView = {
  template: '<div style="padding:2rem"><h2>{{ $route.name || "Coming Soon" }}</h2><p>Coming soon</p></div>'
}

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      redirect: '/login'
    },
    // Guest Routing
    {
      path: '/',
      component: GuestLayout,
      meta: { requiresAuth: false },
      children: [
        {
          path: 'login',
          name: 'login',
          component: () => import('@/views/auth/LoginView.vue').catch(() => PlaceholderView)
        },
        {
          path: 'register/student',
          name: 'register-student',
          component: () => import('@/views/auth/LoginView.vue')
        },
        {
          path: 'register/company',
          name: 'register-company',
          component: () => import('@/views/auth/LoginView.vue')
        }
      ]
    },
    // Admin Routing
    {
      path: '/admin',
      component: AdminLayout,
      meta: { requiresAuth: true, role: 'admin' },
      children: [
        {
          path: '',
          redirect: '/admin/dashboard'
        },
        {
          path: 'dashboard',
          name: 'admin-dashboard',
          component: () => import('@/views/admin/DashboardView.vue')
        },
        {
          path: 'companies',
          name: 'admin-companies',
          component: () => import('@/views/admin/CompaniesView.vue')
        },
        {
          path: 'companies/:id',
          name: 'admin-company-detail',
          component: () => import('@/views/shared/CompanyDetailView.vue')
        },
        {
          path: 'students',
          name: 'admin-students',
          component: () => import('@/views/admin/StudentsView.vue')
        },
        {
          path: 'students/:id',
          name: 'admin-student-detail',
          component: () => import('@/views/shared/StudentProfileView.vue')
        },
        {
          path: 'drives',
          name: 'admin-drives',
          component: () => import('@/views/admin/DrivesView.vue')
        },
        {
          path: 'drives/:id',
          name: 'admin-drive-detail',
          component: () => import('@/views/shared/DriveDetailView.vue')
        },
        {
          path: 'applications',
          name: 'admin-applications',
          component: () => import('@/views/admin/ApplicationsView.vue')
        }
      ]
    },
    // Company Routing
    {
      path: '/company',
      component: CompanyLayout,
      meta: { requiresAuth: true, role: 'company' },
      children: [
        {
          path: '',
          redirect: '/company/dashboard'
        },
        {
          path: 'dashboard',
          name: 'company-dashboard',
          component: () => import('@/views/company/DashboardView.vue')
        },
        {
          path: 'profile',
          name: 'company-profile',
          component: () => import('@/views/shared/CompanyDetailView.vue')
        },
        {
          path: 'profile/edit',
          name: 'company-profile-edit',
          component: () => import('@/views/company/ProfileEditView.vue')
        },
        {
          path: 'drives',
          name: 'company-drives',
          component: () => import('@/views/company/DrivesView.vue')
        },
        {
          path: 'drives/create',
          name: 'company-create-drive',
          component: () => import('@/views/company/CreateDriveView.vue')
        },
        {
          path: 'drives/:id/edit',
          name: 'company-drive-edit',
          component: () => import('@/views/company/CreateDriveView.vue')
        },
        {
          path: 'drives/:id',
          name: 'company-drive-detail',
          component: () => import('@/views/shared/DriveDetailView.vue')
        },
        {
          path: 'drives/:id/applications',
          name: 'company-drive-applications',
          component: () => import('@/views/company/DriveApplicationsView.vue')
        },
        {
          path: 'students/:id',
          name: 'company-student-detail',
          component: () => import('@/views/shared/StudentProfileView.vue')
        }
      ]
    },
    // Student Routing
    {
      path: '/student',
      component: StudentLayout,
      meta: { requiresAuth: true, role: 'student' },
      children: [
        {
          path: '',
          redirect: '/student/dashboard'
        },
        {
          path: 'dashboard',
          name: 'student-dashboard',
          component: () => import('@/views/student/DashboardView.vue')
        },
        {
          path: 'profile',
          name: 'student-profile',
          component: () => import('@/views/shared/StudentProfileView.vue')
        },
        {
          path: 'profile/edit',
          name: 'student-profile-edit',
          component: () => import('@/views/student/ProfileEditView.vue')
        },
        {
          path: 'companies/:id',
          name: 'student-company-detail',
          component: () => import('@/views/shared/CompanyDetailView.vue')
        },
        {
          path: 'drives/:id',
          name: 'student-drive-detail',
          component: () => import('@/views/shared/DriveDetailView.vue')
        },
        {
          path: 'applications',
          name: 'student-applications',
          component: () => import('@/views/student/ApplicationsView.vue')
        }
      ]
    },
    // Catch-all
    {
      path: '/:pathMatch(.*)*',
      redirect: '/login'
    }
  ]
})

router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore()
  const requiresAuth = to.meta.requiresAuth
  const routeRole = to.meta.role

  // Rehydrate auth state from localStorage on hard refresh
  if (!authStore.token) {
    authStore.initAuth()
  }

  if (requiresAuth && !authStore.token) {
    next('/login')
  } else if (requiresAuth && routeRole && authStore.user?.role !== routeRole) {
    if (authStore.user?.role === 'admin') next('/admin/dashboard')
    else if (authStore.user?.role === 'company') next('/company/dashboard')
    else if (authStore.user?.role === 'student') next('/student/dashboard')
    else next('/login')
  } else if (!requiresAuth && authStore.token && (to.path === '/login' || to.path.startsWith('/register'))) {
    if (authStore.user?.role === 'admin') next('/admin/dashboard')
    else if (authStore.user?.role === 'company') next('/company/dashboard')
    else if (authStore.user?.role === 'student') next('/student/dashboard')
    else next()
  } else {
    next()
  }
})

export default router
