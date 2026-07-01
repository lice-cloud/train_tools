<template>
  <div class="bar">
    <span class="ver">v{{ info.current || "?" }}</span>
    <span v-if="info.state === 'checking'" class="msg">Checking...</span>
    <span v-else-if="info.state === 'error'" class="msg warn">
      Check failed: {{ info.error }}
    </span>
    <span v-else-if="info.state === 'ok' && info.has_update" class="msg new">
      v{{ info.latest }} available
    </span>
    <span v-else-if="info.state === 'ok' && !info.has_update" class="msg">
      Up to date
    </span>
    <button v-if="info.state !== 'checking'" class="btn" @click="doCheck">
      Check Updates
    </button>
    <button
      v-if="info.state === 'ok' && info.has_update && info.download_url"
      class="btn dl"
      :disabled="downloading"
      @click="doDownload"
    >
      {{ downloading ? "Downloading..." : "Download" }}
    </button>
  </div>
</template>

<script setup>
import { reactive, onMounted, ref } from "vue"

const info = reactive({ state: "idle", current: null, latest: null, has_update: false, download_url: "", error: "" })
const downloading = ref(false)

onMounted(doCheck)

async function doCheck() {
  info.state = "checking"
  try {
    const res = await fetch("/api/check-update")
    const data = await res.json()
    info.current = data.current_version
    info.latest = data.latest_version
    if (data.has_update) {
      info.has_update = true
      info.download_url = data.download_url || ""
      info.state = "ok"
    } else if (data.error) {
      info.state = "error"
      info.error = data.error
    } else {
      info.state = "ok"
      info.has_update = false
    }
  } catch (e) {
    info.state = "error"
    info.error = e.message
  }
}

async function doDownload() {
  downloading.value = true
  try {
    await fetch("/api/update", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ download_url: info.download_url }),
    })
  } catch {
    info.error = "Download failed"
    downloading.value = false
  }
}
</script>

<style scoped>
.bar {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 4px 12px;
  background: #f0f0f0;
  border-top: 1px solid #ddd;
  font-size: 12px;
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  z-index: 100;
}
.ver { font-weight: 600; color: #555; }
.msg { color: #666; flex: 1; }
.msg.new { color: #1a73e8; font-weight: 600; }
.msg.warn { color: #d32f2f; }
.btn {
  background: #e0e0e0;
  border: none;
  padding: 2px 10px;
  border-radius: 3px;
  cursor: pointer;
  font-size: 12px;
}
.btn.dl { background: #1a73e8; color: #fff; font-weight: 600; }
.btn:disabled { opacity: 0.6; cursor: not-allowed; }
</style>
