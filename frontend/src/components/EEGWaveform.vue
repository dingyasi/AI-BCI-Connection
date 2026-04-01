<template>
  <div class="eeg-container">
    <div class="eeg-header">
      <span class="eeg-title">📡 实时EEG信号</span>
      <div class="eeg-meta">
        <span class="eeg-fs">160Hz</span>
        <span class="eeg-status" :class="{ active: isSimulating }">
          {{ isSimulating ? '采集中' : '待机' }}
        </span>
      </div>
    </div>
    
    <div class="preprocess-info">
      <span class="pp-item">陷波50Hz</span>
      <span class="pp-item">带通8-30Hz</span>
      <span class="pp-item">64通道</span>
    </div>
    
    <div class="eeg-channels">
      <div v-for="(channel, idx) in channels" :key="idx" class="channel-row">
        <span class="channel-label">{{ channel.name }}</span>
        <canvas 
          :ref="el => canvasRefs[idx] = el as HTMLCanvasElement"
          class="channel-canvas"
          :style="{ borderColor: channel.color }"
        ></canvas>
        <span class="channel-freq" :style="{ color: channel.color }">
          {{ channel.freq }}Hz
        </span>
      </div>
    </div>
    
    <div class="eeg-controls">
      <button 
        class="eeg-btn" 
        :class="{ active: isSimulating }"
        @click="toggleSimulation"
      >
        {{ isSimulating ? '⏸ 暂停' : '▶ 开始' }}
      </button>
      <div class="eeg-legend">
        <span class="legend-item"><span class="dot" style="background:#00ffff"></span>Mu节律</span>
        <span class="legend-item"><span class="dot" style="background:#ff6b00"></span>Beta节律</span>
        <span class="legend-item"><span class="dot" style="background:#00ff88"></span>Theta波</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount, watch } from 'vue'

interface EEGChannel {
  name: string
  color: string
  freq: number
  phase: number
  amplitude: number
}

const props = defineProps<{
  motorImagery?: 'left' | 'right' | 'foot' | null
}>()

const canvasRefs = ref<(HTMLCanvasElement | null)[]>([])
const isSimulating = ref(true)
const animationId = ref<number>()

const channels = ref<EEGChannel[]>([
  { name: 'C3', color: '#00ffff', freq: 10, phase: 0, amplitude: 50 },
  { name: 'Cz', color: '#ff6b00', freq: 12, phase: 0.5, amplitude: 45 },
  { name: 'C4', color: '#00ff88', freq: 11, phase: 1, amplitude: 48 },
  { name: 'P3', color: '#ffaa00', freq: 9, phase: 1.5, amplitude: 40 },
  { name: 'Pz', color: '#00aaff', freq: 10, phase: 2, amplitude: 42 },
  { name: 'P4', color: '#ff55aa', freq: 8, phase: 2.5, amplitude: 38 },
])

const time = ref(0)
const dataPoints = 200

// Update frequencies based on motor imagery
watch(() => props.motorImagery, (val) => {
  if (val === 'left') {
    // Left hand imagery: ERD in C4 (right hemisphere)
    channels.value[2].amplitude = 25  // C4 suppressed
    channels.value[0].amplitude = 55  // C3 enhanced
    channels.value[2].freq = 9
  } else if (val === 'right') {
    // Right hand imagery: ERD in C3 (left hemisphere)
    channels.value[0].amplitude = 25  // C3 suppressed
    channels.value[2].amplitude = 55  // C4 enhanced
    channels.value[0].freq = 9
  } else if (val === 'foot') {
    // Foot imagery: ERD in Cz (central)
    channels.value[1].amplitude = 20  // Cz suppressed
    channels.value[0].amplitude = 50
    channels.value[2].amplitude = 50
  } else {
    // Rest state
    channels.value.forEach(ch => {
      ch.amplitude = 40 + Math.random() * 15
      ch.freq = 8 + Math.random() * 5
    })
  }
})

const drawWaveform = (canvas: HTMLCanvasElement, channel: EEGChannel, timeOffset: number) => {
  const ctx = canvas.getContext('2d')
  if (!ctx) return
  
  const width = canvas.width
  const height = canvas.height
  
  ctx.clearRect(0, 0, width, height)
  
  // Background grid
  ctx.strokeStyle = 'rgba(0, 255, 255, 0.1)'
  ctx.lineWidth = 0.5
  for (let i = 0; i < width; i += 20) {
    ctx.beginPath()
    ctx.moveTo(i, 0)
    ctx.lineTo(i, height)
    ctx.stroke()
  }
  for (let i = 0; i < height; i += 10) {
    ctx.beginPath()
    ctx.moveTo(0, i)
    ctx.lineTo(width, i)
    ctx.stroke()
  }
  
  // Draw waveform
  ctx.beginPath()
  ctx.strokeStyle = channel.color
  ctx.lineWidth = 2
  ctx.shadowColor = channel.color
  ctx.shadowBlur = 5
  
  const centerY = height / 2
  
  for (let i = 0; i < width; i++) {
    const t = (i / width) * 4 + timeOffset + channel.phase
    
    // Mix multiple frequencies for realistic EEG
    const mu = Math.sin(t * channel.freq * 0.1) * channel.amplitude * 0.6
    const beta = Math.sin(t * channel.freq * 0.2 + 0.5) * channel.amplitude * 0.25
    const noise = (Math.random() - 0.5) * 10
    
    const y = centerY + mu + beta + noise
    
    if (i === 0) {
      ctx.moveTo(i, y)
    } else {
      ctx.lineTo(i, y)
    }
  }
  
  ctx.stroke()
  ctx.shadowBlur = 0
  
  // Draw center line
  ctx.strokeStyle = 'rgba(255, 255, 255, 0.2)'
  ctx.lineWidth = 1
  ctx.setLineDash([5, 5])
  ctx.beginPath()
  ctx.moveTo(0, centerY)
  ctx.lineTo(width, centerY)
  ctx.stroke()
  ctx.setLineDash([])
}

const animate = () => {
  if (!isSimulating.value) return
  
  time.value += 0.05
  
  channels.value.forEach((channel, idx) => {
    const canvas = canvasRefs.value[idx]
    if (canvas) {
      drawWaveform(canvas, channel, time.value)
    }
  })
  
  // Update frequency display with some variation
  channels.value.forEach(ch => {
    ch.freq = ch.freq + (Math.random() - 0.5) * 0.2
  })
  
  animationId.value = requestAnimationFrame(animate)
}

const toggleSimulation = () => {
  isSimulating.value = !isSimulating.value
  if (isSimulating.value) {
    animate()
  }
}

const resizeCanvases = () => {
  canvasRefs.value.forEach(canvas => {
    if (canvas) {
      canvas.width = canvas.offsetWidth * 2
      canvas.height = canvas.offsetHeight * 2
    }
  })
}

onMounted(() => {
  resizeCanvases()
  window.addEventListener('resize', resizeCanvases)
  if (isSimulating.value) {
    animate()
  }
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', resizeCanvases)
  if (animationId.value) {
    cancelAnimationFrame(animationId.value)
  }
})
</script>

<style scoped>
.eeg-container {
  background: rgba(0, 10, 20, 0.8);
  border: 1px solid rgba(0, 255, 255, 0.3);
  border-radius: 12px;
  padding: 12px;
  backdrop-filter: blur(10px);
}

.eeg-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 6px;
  padding-bottom: 6px;
  border-bottom: 1px solid rgba(0, 255, 255, 0.2);
}

.eeg-title {
  color: #00ffff;
  font-size: 0.75rem;
  font-weight: bold;
  letter-spacing: 1px;
}

.eeg-meta {
  display: flex;
  align-items: center;
  gap: 8px;
}

.eeg-fs {
  font-size: 0.55rem;
  color: #ff6b00;
  background: rgba(255, 107, 0, 0.1);
  padding: 1px 5px;
  border-radius: 3px;
}

.eeg-status {
  font-size: 0.6rem;
  color: #888;
  padding: 2px 6px;
  background: rgba(0, 0, 0, 0.3);
  border-radius: 10px;
}

.eeg-status.active {
  color: #00ff88;
  animation: blink 1s infinite;
}

.preprocess-info {
  display: flex;
  gap: 6px;
  margin-bottom: 8px;
  flex-wrap: wrap;
}

.pp-item {
  font-size: 0.5rem;
  color: #888;
  background: rgba(0, 255, 255, 0.05);
  padding: 1px 4px;
  border-radius: 3px;
  border: 1px solid rgba(0, 255, 255, 0.1);
}

@keyframes blink {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

.eeg-channels {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.channel-row {
  display: flex;
  align-items: center;
  gap: 8px;
}

.channel-label {
  width: 30px;
  font-size: 0.65rem;
  color: #aaa;
  text-align: right;
}

.channel-canvas {
  flex: 1;
  height: 35px;
  background: rgba(0, 0, 0, 0.3);
  border: 1px solid rgba(0, 255, 255, 0.2);
  border-radius: 4px;
}

.channel-freq {
  width: 40px;
  font-size: 0.65rem;
  font-weight: bold;
  text-align: right;
}

.eeg-controls {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 10px;
  padding-top: 8px;
  border-top: 1px solid rgba(0, 255, 255, 0.2);
}

.eeg-btn {
  padding: 6px 16px;
  background: rgba(0, 255, 255, 0.1);
  border: 1px solid rgba(0, 255, 255, 0.3);
  border-radius: 6px;
  color: #00ffff;
  font-size: 0.75rem;
  cursor: pointer;
  transition: all 0.2s;
}

.eeg-btn:hover {
  background: rgba(0, 255, 255, 0.2);
}

.eeg-btn.active {
  background: rgba(0, 255, 255, 0.3);
  border-color: #00ffff;
}

.eeg-legend {
  display: flex;
  gap: 12px;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 0.6rem;
  color: #888;
}

.legend-item .dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
}
</style>