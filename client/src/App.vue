<script setup>
import { onMounted } from 'vue'
import { RouterView } from 'vue-router'
import { useAuthStore } from './stores/auth'

const authStore = useAuthStore()

onMounted(async () => {
  await authStore.initAuth()
})
</script>

<template>
  <RouterView />
</template>
