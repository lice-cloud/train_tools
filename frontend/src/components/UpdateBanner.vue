<template>
  <div v-if="update" class="banner">
    <span class="text">
      New version <strong>{{ update.latest_version }}</strong> available
      (current: {{ update.current_version }})
    </span>
    <button class="btn" :disabled="downloading" @click="download">
      {{ downloading ? "Downloading..." : "Download Update" }}
    </button>
    <button v-if="error" class="close" @click="$emit('close')">x</button>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue"

const emit = defineEmits(["close"])
const update = ref(null)
const downloading = ref(false)
const error = ref(false)

onMounted(async () => {
  try {
    const res = await fetch("/api/check-update")
    const data = await res.json()
    if (data.has_update) update.value = data
  } catch {
    // offline, ignore
  }
})

async function download() {
  downloading.value = true
  try {
    await fetch("/api/update", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ download_url: update.value.download_url }),
    })
  } catch {
    error.value = true
    downloading.value = false
  }
}
</script>

<style scoped>
.banner {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px 16px;
  background: #1a73e8;
  color: #fff;
  font-size: 14px;
}
.text { flex: 1; }
.btn {
  background: #fff;
  color: #1a73e8;
  border: none;
  padding: 4px 14px;
  border-radius: 4px;
  cursor: pointer;
  font-weight: 600;
}
.btn:disabled { opacity: 0.6; cursor: not-allowed; }
.close {
  background: none;
  border: none;
  color: #fff;
  cursor: pointer;
  font-size: 16px;
}
</style>
