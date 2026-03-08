import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import AdminLayout from '@/layouts/AdminLayout.vue'

const GuestLayout = {
  template: '<div style="padding:2rem"><router-view/></div>'
}
const CompanyLayout = {
  template: '<div style="padding:2rem"><h2>Company Layout</h2><router-view/></div>'
}
const StudentLayout = {
  template: '<div style="padding:2rem"><h2>Student Layout</h2><router-view/></div>'
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
          component: PlaceholderView
        },
        {
          path: 'register/company',
          name: 'register-company',
          component: PlaceholderView
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
          component: PlaceholderView
        },
        {
          path: 'students',
          name: 'admin-students',
          component: () => import('@/views/admin/StudentsView.vue')
        },
        {
          path: 'students/:id',
          name: 'admin-student-detail',
          component: PlaceholderView
        },
        {
          path: 'drives',
          name: 'admin-drives',
          component: () => import('@/views/admin/DrivesView.vue')
        },
        {
          path: 'drives/:id',
          name: 'admin-drive-detail',
          component: PlaceholderView
        },
        {
          path: 'applications',
          name: 'admin-applications',
          component: () => import('@/views/admin/ApplicationsView.vue')
        },
        {
          path: 'settings',
          name: 'admin-settings',
          component: () => import('@/views/admin/SettingsView.vue')
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
          component: PlaceholderView
        },
        {
          path: 'profile',
          name: 'company-profile',
          component: PlaceholderView
        },
        {
          path: 'drives',
          name: 'company-drives',
          component: PlaceholderView
        },
        {
          path: 'drives/create',
          name: 'company-create-drive',
          component: PlaceholderView
        },
        {
          path: 'drives/:id',
          name: 'company-drive-detail',
          component: PlaceholderView
        },
        {
          path: 'applications',
          name: 'company-applications',
          component: PlaceholderView
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
          component: PlaceholderView
        },
        {
          path: 'profile',
          name: 'student-profile',
          component: PlaceholderView
        },
        {
          path: 'drives',
          name: 'student-drives',
          component: PlaceholderView
        },
        {
          path: 'drives/:id',
          name: 'student-drive-detail',
          component: PlaceholderView
        },
        {
          path: 'applications',
          name: 'student-applications',
          component: PlaceholderView
        },
        {
          path: 'export',
          name: 'student-export',
          component: PlaceholderView
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

router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()
  const requiresAuth = to.meta.requiresAuth
  const routeRole = to.meta.role

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
