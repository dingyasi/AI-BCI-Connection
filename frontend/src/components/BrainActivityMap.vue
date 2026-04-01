<template>
  <div class="bci-signal-viewer">
    <!-- 头部 -->
    <div class="viewer-header">
      <span class="header-title">BCI信号分析</span>
      <span class="status-badge" :class="{ active: isActive }">
        {{ isActive ? '采集中' : '待机' }}
      </span>
    </div>
    
    <!-- 主要显示区 -->
    <div class="main-display">
      <!-- 左侧：脑地形图 -->
      <div class="topo-section">
        <div class="section-label">脑电地形图</div>
        <canvas ref="topoCanvas" class="topo-canvas"></canvas>
        
        <!-- 激活指示 -->
        <div v-if="isActive" class="activation-badge" :class="activationSide">
          <span class="badge-icon">⚡</span>
          <span class="badge-text">{{ activationArea }} ERD {{ erdPercent }}%</span>
        </div>
      </div>
      
      <!-- 右侧：频谱分析 -->
      <div class="spectrum-section">
        <div class="section-label">功率谱密度</div>
        <canvas ref="spectrumCanvas" class="spectrum-canvas"></canvas>
        
        <!-- 频段信息 -->
        <div class="band-info">
          <div class="band-item" :class="{ active: activeBand === 'mu' }">
            <span class="band-name">Mu</span>
            <span class="band-freq">8-13Hz</span>
          </div>
          <div class="band-item" :class="{ active: activeBand === 'beta' }">
            <span class="band-name">Beta</span>
            <span class="band-freq">13-30Hz</span>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 对侧激活说明 - 实用教育功能 -->
    <div class="education-panel">
      <div class="edu-header">
        <span class="edu-icon">💡</span>
        <span class="edu-title">BCI原理学习</span>
      </div>
      <div class="edu-content" v-if="!isActive">
        <p class="edu-hint">👆 选择运动想象任务，观察脑电信号变化</p>
        <div class="edu-preview">
          <div class="preview-item">
            <span class="preview-icon">🧠</span>
            <span>ERD = 能量下降</span>
          </div>
          <div class="preview-item">
            <span class="preview-icon">⚡</span>
            <span>ERS = 能量上升</span>
          </div>
        </div>
      </div>
      <div class="edu-content active" v-else>
        <div class="edu-row">
          <span class="edu-label">任务</span>
          <span class="edu-value highlight">{{ currentTaskName }}</span>
        </div>
        <div class="edu-row">
          <span class="edu-label">ERD区域</span>
          <span class="edu-value erd">{{ activationArea }}</span>
        </div>
        <div class="edu-row">
          <span class="edu-label">ERS区域</span>
          <span class="edu-value ers">{{ ersArea }}</span>
        </div>
        <div class="edu-note">
          {{ explanation }}
        </div>
      </div>
    </div>
    
    <!-- 运动想象按钮 -->
    <div class="mi-controls">
      <div class="control-label">运动想象任务</div>
      <div class="task-buttons">
        <button 
          v-for="task in tasks" 
          :key="task.id"
          class="task-btn"
          :class="{ active: currentTask === task.id, [task.color]: true }"
          @click="selectTask(task.id)"
        >
          <span class="task-icon">{{ task.icon }}</span>
          <span class="task-name">{{ task.name }}</span>
        </button>
      </div>
    </div>
    
    <!-- 分类结果 -->
    <div class="classification-section">
      <div class="class-header">分类结果</div>
      <div class="class-bars">
        <div v-for="result in classResults" :key="result.label" class="class-bar-row">
          <span class="bar-label">{{ result.label }}</span>
          <div class="bar-track">
            <div class="bar-fill" :style="{ width: result.value + '%', background: result.color }"></div>
          </div>
          <span class="bar-value" :style="{ color: result.color }">{{ result.value }}%</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount, watch, computed } from 'vue'

const props = defineProps<{
  motorImagery?: 'left' | 'right' | 'foot' | null
}>()

const emit = defineEmits<{
  brainPulse: [region: 'left' | 'center' | 'right', intensity: number]
}>()

const topoCanvas = ref<HTMLCanvasElement>()
const spectrumCanvas = ref<HTMLCanvasElement>()
const isActive = ref(false)
const currentTask = ref<string | null>(null)
const animationId = ref<number>()
const topoPhase = ref(0)
const activeBand = ref('mu')

const tasks = [
  { id: 'left', name: '左手', icon: '◀', color: 'blue', region: '右脑C4', side: 'right' },
  { id: 'right', name: '右手', icon: '▶', color: 'orange', region: '左脑C3', side: 'left' },
  { id: 'foot', name: '双脚', icon: '▼', color: 'green', region: '中央Cz', side: 'center' }
]

const classResults = ref([
  { label: '左手', value: 10, color: '#00aaff' },
  { label: '右手', value: 10, color: '#ff6b00' },
  { label: '双脚', value: 10, color: '#00ff88' }
])

const currentTaskName = computed(() => {
  const task = tasks.find(t => t.id === currentTask.value)
  return task ? task.name : '--'
})

const activationArea = computed(() => {
  const task = tasks.find(t => t.id === currentTask.value)
  return task ? task.region : '--'
})

const activationSide = computed(() => {
  const task = tasks.find(t => t.id === currentTask.value)
  return task ? task.side : ''
})

const ersArea = computed(() => {
  switch (currentTask.value) {
    case 'left': return '左脑C3区'
    case 'right': return '右脑C4区'
    case 'foot': return '双侧感觉区'
    default: return '--'
  }
})

const erdPercent = computed(() => {
  return isActive.value ? Math.floor(35 + Math.random() * 20) : 0
})

const principle = computed(() => {
  switch (currentTask.value) {
    case 'left': return '右手运动皮层ERD'
    case 'right': return '左手运动皮层ERD'
    case 'foot': return '双侧运动皮层ERD'
    default: return '--'
  }
})

const explanation = computed(() => {
  switch (currentTask.value) {
    case 'left': return '想象左手运动时，右脑C4区域的Mu/Beta节律能量下降（ERD），因为运动皮层控制对侧身体。'
    case 'right': return '想象右手运动时，左脑C3区域的Mu/Beta节律能量下降（ERD），这是对侧控制原理。'
    case 'foot': return '想象双脚运动时，中央Cz区域（控制下肢的皮层区域）出现ERD现象。'
    default: return ''
  }
})

// 绘制脑地形图
const drawTopography = () => {
  const canvas = topoCanvas.value
  if (!canvas) return
  
  const ctx = canvas.getContext('2d')
  if (!ctx) return
  
  const w = canvas.width
  const h = canvas.height
  const cx = w / 2
  const cy = h / 2
  const r = w * 0.4
  
  ctx.clearRect(0, 0, w, h)
  topoPhase.value += 0.02
  
  // 头部轮廓
  ctx.beginPath()
  ctx.arc(cx, cy, r, 0, Math.PI * 2)
  ctx.fillStyle = 'rgba(0, 30, 50, 0.8)'
  ctx.fill()
  ctx.strokeStyle = 'rgba(0, 255, 255, 0.4)'
  ctx.lineWidth = 2
  ctx.stroke()
  
  // 鼻子
  ctx.beginPath()
  ctx.moveTo(cx - 6, cy - r)
  ctx.lineTo(cx, cy - r - 10)
  ctx.lineTo(cx + 6, cy - r)
  ctx.fillStyle = 'rgba(0, 255, 255, 0.3)'
  ctx.fill()
  
  // 绘制激活热力图
  if (isActive.value && currentTask.value) {
    drawActivationHeatmap(ctx, cx, cy, r)
  } else {
    // 基线活动
    const baseGrad = ctx.createRadialGradient(cx, cy, 0, cx, cy, r * 0.6)
    baseGrad.addColorStop(0, 'rgba(0, 255, 255, 0.1)')
    baseGrad.addColorStop(1, 'transparent')
    ctx.fillStyle = baseGrad
    ctx.beginPath()
    ctx.arc(cx, cy, r * 0.6, 0, Math.PI * 2)
    ctx.fill()
  }
  
  // 电极点
  const electrodes = [
    { name: 'F3', x: 0.3, y: 0.25, isLeft: true },
    { name: 'F4', x: 0.7, y: 0.25, isLeft: false },
    { name: 'C3', x: 0.25, y: 0.5, isLeft: true },
    { name: 'Cz', x: 0.5, y: 0.45, isLeft: null },
    { name: 'C4', x: 0.75, y: 0.5, isLeft: false },
    { name: 'P3', x: 0.3, y: 0.75, isLeft: true },
    { name: 'P4', x: 0.7, y: 0.75, isLeft: false },
  ]
  
  electrodes.forEach(elec => {
    const ex = cx + (elec.x - 0.5) * r * 1.6
    const ey = cy + (elec.y - 0.5) * r * 1.6
    
    let isActive_elec = false
    if (currentTask.value === 'left' && elec.isLeft === false) isActive_elec = true
    if (currentTask.value === 'right' && elec.isLeft === true) isActive_elec = true
    if (currentTask.value === 'foot' && elec.name === 'Cz') isActive_elec = true
    
    ctx.beginPath()
    ctx.arc(ex, ey, isActive_elec ? 6 : 4, 0, Math.PI * 2)
    ctx.fillStyle = isActive_elec ? '#00ffff' : 'rgba(255, 255, 255, 0.4)'
    ctx.fill()
    
    if (isActive_elec) {
      ctx.shadowColor = '#00ffff'
      ctx.shadowBlur = 10
      ctx.fill()
      ctx.shadowBlur = 0
    }
    
    ctx.font = '9px monospace'
    ctx.fillStyle = isActive_elec ? '#fff' : 'rgba(255, 255, 255, 0.5)'
    ctx.textAlign = 'center'
    ctx.fillText(elec.name, ex, ey + 14)
  })
}

const drawActivationHeatmap = (ctx: CanvasRenderingContext2D, cx: number, cy: number, r: number) => {
  const pulse = Math.sin(topoPhase.value * 3) * 0.2 + 0.8
  let hotspotX = cx, hotspotY = cy
  let color = '0, 255, 136'
  let ersColor = '255, 180, 0'
  
  switch (currentTask.value) {
    case 'left':
      // 右脑C4区域ERD
      hotspotX = cx + r * 0.45
      hotspotY = cy
      color = '0, 170, 255'  // 蓝色表示ERD
      break
    case 'right':
      // 左脑C3区域ERD
      hotspotX = cx - r * 0.45
      hotspotY = cy
      color = '255, 107, 0'  // 橙色表示ERD
      break
    case 'foot':
      // 中央Cz区域ERD
      hotspotX = cx
      hotspotY = cy - r * 0.15
      color = '0, 255, 136'  // 绿色表示ERD
      break
  }
  
  // ERD区域（能量下降）- 强烈显示
  const erdSize = r * 0.55
  const grad = ctx.createRadialGradient(hotspotX, hotspotY, 0, hotspotX, hotspotY, erdSize)
  grad.addColorStop(0, `rgba(${color}, ${0.9 * pulse})`)
  grad.addColorStop(0.4, `rgba(${color}, ${0.6 * pulse})`)
  grad.addColorStop(0.7, `rgba(${color}, ${0.3 * pulse})`)
  grad.addColorStop(1, 'transparent')
  ctx.fillStyle = grad
  ctx.beginPath()
  ctx.arc(hotspotX, hotspotY, erdSize, 0, Math.PI * 2)
  ctx.fill()
  
  // 对侧ERS区域（能量上升）- 对比显示
  const ersX = currentTask.value === 'foot' ? hotspotX : (currentTask.value === 'left' ? cx - r * 0.45 : cx + r * 0.45)
  const ersY = currentTask.value === 'foot' ? cy + r * 0.3 : cy
  const ersGrad = ctx.createRadialGradient(ersX, ersY, 0, ersX, ersY, r * 0.35)
  ersGrad.addColorStop(0, `rgba(${ersColor}, ${0.5 * pulse})`)
  ersGrad.addColorStop(0.6, `rgba(${ersColor}, ${0.2 * pulse})`)
  ersGrad.addColorStop(1, 'transparent')
  ctx.fillStyle = ersGrad
  ctx.beginPath()
  ctx.arc(ersX, ersY, r * 0.35, 0, Math.PI * 2)
  ctx.fill()
  
  // 添加ERD/ERS文字标签
  ctx.font = 'bold 9px monospace'
  ctx.textAlign = 'center'
  
  // ERD标签
  ctx.fillStyle = `rgba(255, 255, 255, ${0.9 * pulse})`
  ctx.fillText('ERD', hotspotX, hotspotY - erdSize - 5)
  
  // ERS标签
  ctx.fillStyle = `rgba(255, 200, 100, ${0.7 * pulse})`
  ctx.fillText('ERS', ersX, ersY + r * 0.35 + 12)
  
  // 能量流动箭头
  ctx.strokeStyle = `rgba(255, 255, 255, ${0.4 * pulse})`
  ctx.lineWidth = 1
  ctx.setLineDash([3, 3])
  ctx.beginPath()
  ctx.moveTo(hotspotX, hotspotY)
  ctx.lineTo(ersX, ersY)
  ctx.stroke()
  ctx.setLineDash([])
}

// 基线功率谱（静息状态）
const baselineSpectrum = [
  15, 20, 25, 30, 35, 45, 55, 65, 75, 80, 70, 55, 45, 40, 38, 36, 34, 32, 30, 28,
  26, 25, 24, 23, 22, 21, 20, 19, 18, 17, 16, 15, 14, 13, 12
]

// ERD/ERS响应系数
const getERDFactor = (freq: number): number => {
  if (!isActive.value || !currentTask.value) return 1.0
  
  // Mu节律(8-13Hz)和Beta节律(13-30Hz)会产生ERD
  const isMuBand = freq >= 8 && freq <= 13
  const isBetaBand = freq >= 13 && freq <= 30
  
  if (isMuBand || isBetaBand) {
    // ERD - 能量下降40-60%
    return 0.4 + Math.random() * 0.2
  }
  return 1.0
}

// 绘制功率谱
const drawSpectrum = () => {
  const canvas = spectrumCanvas.value
  if (!canvas) return
  
  const ctx = canvas.getContext('2d')
  if (!ctx) return
  
  const w = canvas.width
  const h = canvas.height
  
  ctx.clearRect(0, 0, w, h)
  
  // 背景网格
  ctx.strokeStyle = 'rgba(0, 255, 255, 0.1)'
  ctx.lineWidth = 0.5
  for (let i = 0; i < 5; i++) {
    const y = (i / 5) * h
    ctx.beginPath()
    ctx.moveTo(0, y)
    ctx.lineTo(w, y)
    ctx.stroke()
  }
  
  // 频段标记
  const bands = [
    { name: 'Delta', range: [1, 4], color: '#8b5cf6' },
    { name: 'Theta', range: [4, 8], color: '#06b6d4' },
    { name: 'Mu', range: [8, 13], color: '#00ff88' },
    { name: 'Beta', range: [13, 30], color: '#ff6b00' }
  ]
  
  const freqToX = (freq: number) => ((freq - 1) / 34) * w * 0.9 + w * 0.05
  const powerToY = (power: number) => h - 30 - (power / 100) * (h - 50)
  
  // 绘制频段区域
  bands.forEach(band => {
    const x1 = freqToX(band.range[0])
    const x2 = freqToX(band.range[1])
    
    // 高亮当前活跃的频段
    const isHighlight = (isActive.value && (band.name === 'Mu' || band.name === 'Beta'))
    
    ctx.fillStyle = isHighlight ? band.color + '30' : band.color + '10'
    ctx.fillRect(x1, 0, x2 - x1, h - 20)
    
    ctx.fillStyle = isHighlight ? band.color : band.color + '80'
    ctx.font = isHighlight ? 'bold 9px monospace' : '8px monospace'
    ctx.textAlign = 'center'
    ctx.fillText(band.name, (x1 + x2) / 2, h - 5)
  })
  
  // 绘制基线功率谱（虚线）
  ctx.beginPath()
  ctx.setLineDash([4, 4])
  ctx.strokeStyle = 'rgba(100, 100, 100, 0.5)'
  ctx.lineWidth = 1
  
  for (let i = 0; i < 35; i++) {
    const x = freqToX(i + 1)
    const y = powerToY(baselineSpectrum[i] || 20)
    if (i === 0) ctx.moveTo(x, y)
    else ctx.lineTo(x, y)
  }
  ctx.stroke()
  ctx.setLineDash([])
  
  // 绘制当前功率谱（实线）
  ctx.beginPath()
  ctx.strokeStyle = isActive.value ? '#00ffff' : '#00aaff'
  ctx.lineWidth = 2.5
  
  for (let i = 0; i < 35; i++) {
    const freq = i + 1
    const x = freqToX(freq)
    
    // 基础功率 + 少量噪声
    let power = baselineSpectrum[i] + (Math.random() - 0.5) * 5
    
    // 应用ERD
    const erdFactor = getERDFactor(freq)
    power *= erdFactor
    
    const y = powerToY(power)
    if (i === 0) ctx.moveTo(x, y)
    else ctx.lineTo(x, y)
  }
  ctx.stroke()
  
  // 填充曲线下方
  ctx.lineTo(freqToX(35), h - 30)
  ctx.lineTo(freqToX(1), h - 30)
  ctx.closePath()
  ctx.fillStyle = isActive.value ? 'rgba(0, 255, 255, 0.15)' : 'rgba(0, 170, 255, 0.1)'
  ctx.fill()
  
  // 绘制ERD标注
  if (isActive.value) {
    // Mu频段ERD标注
    const muX = (freqToX(8) + freqToX(13)) / 2
    const muY = powerToY(50)
    
    ctx.fillStyle = '#ff6b00'
    ctx.font = 'bold 10px monospace'
    ctx.textAlign = 'center'
    ctx.fillText('ERD', muX, muY - 5)
    ctx.font = '8px monospace'
    ctx.fillText('能量↓', muX, muY + 8)
    
    // 箭头指示下降
    ctx.beginPath()
    ctx.strokeStyle = '#ff6b00'
    ctx.lineWidth = 2
    ctx.moveTo(muX, muY - 15)
    ctx.lineTo(muX, muY - 5)
    ctx.lineTo(muX - 4, muY - 10)
    ctx.moveTo(muX, muY - 5)
    ctx.lineTo(muX + 4, muY - 10)
    ctx.stroke()
  }
  
  // 频率轴标签
  ctx.fillStyle = '#666'
  ctx.font = '8px monospace'
  ctx.textAlign = 'center'
  for (let freq = 5; freq <= 30; freq += 5) {
    ctx.fillText(freq + '', freqToX(freq), h - 15)
  }
  ctx.fillText('Hz', freqToX(32), h - 15)
  
  // 功率轴标签
  ctx.save()
  ctx.translate(8, h / 2)
  ctx.rotate(-Math.PI / 2)
  ctx.fillStyle = '#666'
  ctx.font = '8px monospace'
  ctx.textAlign = 'center'
  ctx.fillText('功率', 0, 0)
  ctx.restore()
}

const animate = () => {
  drawTopography()
  drawSpectrum()
  animationId.value = requestAnimationFrame(animate)
}

const selectTask = (task: string) => {
  if (currentTask.value === task) {
    currentTask.value = null
    isActive.value = false
    resetClassResults()
    return
  }
  
  currentTask.value = task
  isActive.value = true
  
  // 更新分类结果
  updateClassResults(task)
  
  // 发送脉冲
  const region = task === 'left' ? 'right' : task === 'right' ? 'left' : 'center'
  emit('brainPulse', region, 0.9)
}

const updateClassResults = (task: string) => {
  // 基于混淆矩阵的结果
  const matrices: Record<string, number[]> = {
    left: [89, 7, 4],
    right: [8, 85, 7],
    foot: [5, 10, 85]
  }
  
  const result = matrices[task]
  if (result) {
    classResults.value = [
      { label: '左手', value: result[0], color: '#00aaff' },
      { label: '右手', value: result[1], color: '#ff6b00' },
      { label: '双脚', value: result[2], color: '#00ff88' }
    ]
  }
}

const resetClassResults = () => {
  classResults.value = [
    { label: '左手', value: 10, color: '#00aaff' },
    { label: '右手', value: 10, color: '#ff6b00' },
    { label: '双脚', value: 10, color: '#00ff88' }
  ]
}

watch(() => props.motorImagery, (val) => {
  if (val) {
    selectTask(val)
  } else {
    currentTask.value = null
    isActive.value = false
    resetClassResults()
  }
})

onMounted(() => {
  if (topoCanvas.value) {
    topoCanvas.value.width = 200
    topoCanvas.value.height = 180
  }
  if (spectrumCanvas.value) {
    spectrumCanvas.value.width = 200
    spectrumCanvas.value.height = 180
  }
  animate()
})

onBeforeUnmount(() => {
  if (animationId.value) {
    cancelAnimationFrame(animationId.value)
  }
})
</script>

<style scoped>
.bci-signal-viewer {
  background: linear-gradient(180deg, #0a0f18 0%, #0d1420 100%);
  border: 1px solid rgba(0, 255, 255, 0.25);
  border-radius: 10px;
  padding: 10px;
  display: flex;
  flex-direction: column;
  gap: 8px;
  font-family: 'Segoe UI', sans-serif;
}

.viewer-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-bottom: 6px;
  border-bottom: 1px solid rgba(0, 255, 255, 0.15);
}

.header-title {
  color: #00ffff;
  font-size: 0.75rem;
  font-weight: bold;
  letter-spacing: 1px;
}

.status-badge {
  font-size: 0.6rem;
  padding: 2px 8px;
  border-radius: 10px;
  background: rgba(100, 100, 100, 0.3);
  color: #888;
  transition: all 0.3s;
}

.status-badge.active {
  background: rgba(0, 255, 136, 0.2);
  color: #00ff88;
  animation: status-pulse 1s infinite;
}

@keyframes status-pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.6; }
}

/* 主要显示区 */
.main-display {
  display: flex;
  gap: 8px;
}

.topo-section, .spectrum-section {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.section-label {
  font-size: 0.6rem;
  color: #666;
  letter-spacing: 1px;
}

.topo-canvas, .spectrum-canvas {
  width: 100%;
  height: 160px;
  background: rgba(0, 0, 0, 0.3);
  border: 1px solid rgba(0, 255, 255, 0.1);
  border-radius: 6px;
  display: block;
}

.activation-badge {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 0.65rem;
  font-weight: bold;
}

.activation-badge.right {
  background: rgba(0, 170, 255, 0.2);
  border: 1px solid rgba(0, 170, 255, 0.4);
  color: #00aaff;
}

.activation-badge.left {
  background: rgba(255, 107, 0, 0.2);
  border: 1px solid rgba(255, 107, 0, 0.4);
  color: #ff6b00;
}

.activation-badge.center {
  background: rgba(0, 255, 136, 0.2);
  border: 1px solid rgba(0, 255, 136, 0.4);
  color: #00ff88;
}

.band-info {
  display: flex;
  gap: 6px;
}

.band-item {
  flex: 1;
  display: flex;
  justify-content: space-between;
  padding: 4px 6px;
  background: rgba(0, 0, 0, 0.3);
  border-radius: 4px;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.band-item.active {
  border-color: rgba(0, 255, 255, 0.4);
  background: rgba(0, 255, 255, 0.1);
}

.band-name {
  font-size: 0.6rem;
  color: #fff;
  font-weight: bold;
}

.band-freq {
  font-size: 0.55rem;
  color: #666;
}

/* 教育面板 - 实用功能 */
.education-panel {
  background: rgba(0, 20, 40, 0.6);
  border: 1px solid rgba(0, 255, 255, 0.15);
  border-radius: 6px;
  padding: 8px;
}

.edu-header {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 6px;
}

.edu-icon {
  font-size: 0.9rem;
}

.edu-title {
  font-size: 0.65rem;
  color: #ffaa00;
  font-weight: bold;
}

.edu-content p {
  margin: 0;
  font-size: 0.6rem;
  color: #888;
  line-height: 1.5;
}

.edu-content.active {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.edu-row {
  display: flex;
  justify-content: space-between;
  font-size: 0.6rem;
}

.edu-label {
  color: #888;
}

.edu-value {
  color: #ccc;
}

.edu-value.highlight {
  color: #00ffff;
  font-weight: bold;
}

.edu-note {
  margin-top: 4px;
  padding: 6px;
  background: rgba(255, 170, 0, 0.1);
  border-left: 2px solid #ffaa00;
  border-radius: 0 4px 4px 0;
  font-size: 0.55rem;
  color: #ccc;
  line-height: 1.4;
}

.edu-hint {
  margin: 0;
  font-size: 0.6rem;
  color: #888;
}

.edu-preview {
  display: flex;
  gap: 10px;
  margin-top: 4px;
}

.preview-item {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 0.55rem;
  color: #aaa;
  padding: 4px 6px;
  background: rgba(0, 0, 0, 0.3);
  border-radius: 4px;
}

.preview-icon {
  font-size: 0.7rem;
}

.edu-value.erd {
  color: #00aaff;
  font-weight: bold;
}

.edu-value.ers {
  color: #ff6b00;
  font-weight: bold;
}

/* 运动想象控制 */
.mi-controls {
  background: rgba(0, 0, 0, 0.3);
  border-radius: 6px;
  padding: 8px;
}

.control-label {
  font-size: 0.55rem;
  color: #666;
  letter-spacing: 1px;
  margin-bottom: 6px;
  text-align: center;
}

.task-buttons {
  display: flex;
  gap: 6px;
}

.task-btn {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 8px 4px;
  background: rgba(0, 30, 50, 0.6);
  border: 1px solid rgba(255, 255, 255, 0.15);
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.3s;
}

.task-btn:hover {
  background: rgba(0, 50, 70, 0.8);
  border-color: rgba(255, 255, 255, 0.3);
  transform: translateY(-2px);
}

.task-btn.blue.active {
  border-color: #00aaff;
  background: rgba(0, 170, 255, 0.25);
  box-shadow: 0 4px 15px rgba(0, 170, 255, 0.3);
}

.task-btn.orange.active {
  border-color: #ff6b00;
  background: rgba(255, 107, 0, 0.25);
  box-shadow: 0 4px 15px rgba(255, 107, 0, 0.3);
}

.task-btn.green.active {
  border-color: #00ff88;
  background: rgba(0, 255, 136, 0.25);
  box-shadow: 0 4px 15px rgba(0, 255, 136, 0.3);
}

.task-icon {
  font-size: 1.1rem;
  margin-bottom: 2px;
}

.task-name {
  font-size: 0.7rem;
  color: #fff;
  font-weight: bold;
}

/* 分类结果 */
.classification-section {
  background: rgba(0, 0, 0, 0.2);
  border-radius: 6px;
  padding: 8px;
}

.class-header {
  font-size: 0.6rem;
  color: #00ffff;
  margin-bottom: 6px;
  letter-spacing: 1px;
}

.class-bars {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.class-bar-row {
  display: flex;
  align-items: center;
  gap: 6px;
}

.bar-label {
  width: 32px;
  font-size: 0.55rem;
  color: #888;
}

.bar-track {
  flex: 1;
  height: 8px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 4px;
  overflow: hidden;
}

.bar-fill {
  height: 100%;
  border-radius: 4px;
  transition: width 0.5s ease-out;
}

.bar-value {
  width: 32px;
  font-size: 0.6rem;
  font-weight: bold;
  text-align: right;
}
</style>
