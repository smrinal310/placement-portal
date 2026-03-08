<template>
  <div style="padding: 2rem; max-width: 400px; margin: 4rem auto; border: 1px solid #ddd; border-radius: 8px;">
    <h2 style="margin-bottom: 2rem;">Welcome Back</h2>
    <form @submit.prevent="handleLogin">
      <div style="margin-bottom: 1rem;">
        <label style="display: block; margin-bottom: 0.5rem; font-weight: 500;">Email</label>
        <input v-model="email" type="email"
          style="width: 100%; padding: 0.75rem; border: 1px solid #ccc; border-radius: 4px;" required />
      </div>
      <div style="margin-bottom: 1.5rem;">
        <label style="display: block; margin-bottom: 0.5rem; font-weight: 500;">Password</label>
        <input v-model="password" type="password"
          style="width: 100%; padding: 0.75rem; border: 1px solid #ccc; border-radius: 4px;" required />
      </div>
      <div v-if="authStore.error" style="color: #dc3545; margin-bottom: 1rem; font-size: 0.875rem;">
        {{ authStore.error }}
      </div>
      <button :disabled="authStore.loading" type="submit"
        style="width: 100%; padding: 0.75rem; background-color: #0d6efd; color: white; border: none; border-radius: 4px; font-weight: 600; cursor: pointer;">
        {{ authStore.loading ? 'Logging in...' : 'Log In' }}
      </button>
    </form>

    <div style="margin-top: 2rem; padding-top: 1rem; border-top: 1px solid #eee; font-size: 0.875rem; color: #666;">
      <p style="margin-bottom: 0.5rem;"><strong>Admin Test Account:</strong></p>
      <p style="margin: 0; font-family: monospace;">admin@gmail.com / Admin@1234</p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const email = ref('admin@gmail.com')
const password = ref('Admin@1234')

const handleLogin = async () => {
  try {
    await authStore.login(email.value, password.value)

    // Navigate based on role
    if (authStore.isAdmin) router.push('/admin/dashboard')
    else if (authStore.isCompany) router.push('/company/dashboard')
    else if (authStore.isStudent) router.push('/student/dashboard')
  } catch (error) {
    // Error is handled in authStore, it simply sets authStore.error
  }
}
</script>
