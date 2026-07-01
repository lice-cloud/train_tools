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
    <button v-if="info.state !== 'checking' && !downloading" class="btn" @click="doCheck">
      Check Updates
    </button>
    <button
      v-if="info.state === 'ok' && info.has_update && info.download_url && !downloading"
      class="btn dl"
      @click="doDownload"
    >
      Download Update
    </button>
    <div v-if="downloading" class="progress-wrap">
      <div class="progress-bar" :style="{ width: progress + '%' }"></div>
      <span class="progress-text" v-if="dlStatus === 'downloading'">{{ progress }}%</span>
      <span class="progress-text" v-else-if="dlStatus === 'ready'">Ready, restarting...</span>
      <span class="progress-text" v-else-if="dlStatus === 'error'">Download failed</span>
    </div>
  </div>
</template>

<script setup>
import { reactive, onMounted, ref } from "vue"

const info = reactive({ state: "idle", current: null, latest: null, has_update: false, download_url: "", error: "" })
const downloading = ref(false)
const progress = ref(0)
const dlStatus = ref("")

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
  progress.value = 0
  dlStatus.value = "downloading"
  try {
    const r = await fetch("/api/update", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ download_url: info.download_url }),
    })
    if (!r.ok) throw new Error("start failed")
    pollProgress()
  } catch {
    dlStatus.value = "error"
    downloading.value = false
  }
}

async function pollProgress() {
  const interval = setInterval(async () => {
    try {
      const r = await fetch("/api/update-status")
      const s = await r.json()
      progress.value = s.progress || 0
      dlStatus.value = s.status
      if (s.status === "ready") {
        clearInterval(interval)
        await fetch("/api/update-apply", { method: "POST" })
      } else if (s.status === "error") {
        clearInterval(interval)
        setTimeout(() => { downloading.value = false }, 3000)
      }
    } catch {
      clearInterval(interval)
      dlStatus.value = "error"
    }
  }, 500)
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
.progress-wrap {
  flex: 1;
  height: 16px;
  background: #ddd;
  border-radius: 8px;
  position: relative;
  overflow: hidden;
}
.progress-bar {
  height: 100%;
  background: #1a73e8;
  border-radius: 8px;
  transition: width 0.3s;
}
.progress-text {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 11px;
  color: #333;
  font-weight: 600;
}
</style>
