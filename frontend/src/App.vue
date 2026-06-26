<template>
  <div class="app">
    <h1>Train Tools</h1>
    <p>{{ message }}</p>
    <button @click="fetchHealth">Check API</button>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const message = ref('Welcome to Train Tools')

async function fetchHealth() {
  const res = await fetch('/api/health')
  const data = await res.json()
  message.value = JSON.stringify(data)
}
</script>

<style>
body {
  margin: 0;
  font-family: sans-serif;
}
.app {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100vh;
}
</style>
