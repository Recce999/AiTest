<template>
  <router-view v-if="isLogin" />
  <AppLayout v-else />
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import AppLayout from './layouts/AppLayout.vue'

const route = useRoute()
const isLogin = computed(() => route.path === '/login')
</script>

<style>
#app {
  min-height: 100vh;
}
</style>
