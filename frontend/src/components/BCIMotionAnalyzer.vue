<template>
  <div class="bci-analyzer">
    <!-- 头部 -->
    <div class="analyzer-header">
      <div class="header-left">
        <span class="header-icon">🧠</span>
        <span class="header-title">BCI运动想象分析</span>
      </div>
      <div class="header-right">
        <span class="subject-badge">被试: S001</span>
        <span class="status-badge" :class="{ active: isActive }">
          {{ isActive ? '● 采集中' : '○ 待机' }}
        </span>
      </div>
    </div>
    
    <!-- 信号显示区 -->
    <div class="signal-area">
      <!-- 左侧：波形 -->
      <div class="wave-section">
        <canvas ref="waveCanvas" class="wave-canvas"></canvas>
        <div class="channel-markers">
          <span v-for="(ch, idx) in channelNames" :key="ch" 
                class="channel-marker"
                :class="{ highlighted: isChannelHighlighted(idx) }">
            {{ ch }}
          </span>
        </div>
      </div>
      
      <!-- 右侧：地形图 + 频谱 -->
      <div class="analysis-side">
        <div class="topo-box">
          <div class="box-label">地形图</div>
          <canvas ref="topoCanvas" class="topo-canvas"></canvas>
          <div v-if="isActive" class="erd-indicator" :class="erdSide">
            ERD {{ erdPercent }}%
          </div>
        </div>
        
        <div class="spectrum-box">
          <div class="box-label">频谱</div>
          <canvas ref="spectrumCanvas" class="spectrum-canvas"></canvas>
        </div>
      </div>
    </div>
    
    <!-- 控制区：合并运动想象按钮 + 结果 -->
    <div class="control-area">
      <!-- 运动想象选择 -->
      <div class="task-selector">
        <div class="selector-label">运动想象任务</div>
        <div class="task-buttons">
          <button 
            v-for="task in tasks" 
            :key="task.id"
            class="task-btn"
            :class="{ active: currentTask === task.id, [task.color]: true }"
            @click="selectTask(task.id)"
          >
            <div class="btn-icon">{{ task.icon }}</div>
            <div class="btn-info">
              <span class="btn-name">{{ task.name }}</span>
              <span class="btn-region">{{ task.region }}</span>
            </div>
            <div class="btn-indicator" v-if="currentTask === task.id">
              <span class="indicator-dot"></span>
            </div>
          </button>
        </div>
      </div>
      
      <!-- 分类结果 + 教育 -->
      <div class="result-area">
        <div class="class-result">
          <div class="result-header">Hopfield分类结果</div>
          <div class="result-bars">
            <div v-for="result in classResults" :key="result.label" class="result-row">
              <span class="result-label">{{ result.label }}</span>
              <div class="result-track">
                <div class="result-fill" :style="{ width: result.value + '%', background: result.color }">
                  <span class="fill-glow"></span>
                </div>
              </div>
              <span class="result-value" :style="{ color: result.color }">{{ result.value }}%</span>
            </div>
          </div>
        </div>
        
        <div class="education-box" v-if="isActive">
          <div class="edu-icon">💡</div>
          <div class="edu-text">
            <strong>{{ eduTitle }}</strong>
            <p>{{ eduContent }}</p>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 底部状态栏 -->
    <div class="status-bar">
      <div class="status-item">
        <span class="s-label">采样率</span>
        <span class="s-value">160 Hz</span>
      </div>
      <div class="status-item">
        <span class="s-label">通道</span>
        <span class="s-value">64 CH</span>
      </div>
      <div class="status-item">
        <span class="s-label">滤波</span>
        <span class="s-value">8-30 Hz</span>
      </div>
      <div class="status-item">
        <span class="s-label">算法</span>
        <span class="s-value">Hopfield</span>
      </div>
      <div class="status-item">
        <span class="s-label">准确率</span>
        <span class="s-value highlight">85.6%</span>
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

const waveCanvas = ref<HTMLCanvasElement>()
const topoCanvas = ref<HTMLCanvasElement>()
const spectrumCanvas = ref<HTMLCanvasElement>()

const isActive = ref(false)
const currentTask = ref<string | null>(null)
const animationId = ref<number>()
const phase = ref(0)

const channelNames = ['C3', 'Cz', 'C4', 'P3', 'Pz', 'P4']

const tasks = [
  { id: 'left', name: '左手运动', icon: '👈', region: 'C4区(右脑)', color: 'blue' },
  { id: 'right', name: '右手运动', icon: '👉', region: 'C3区(左脑)', color: 'orange' },
  { id: 'foot', name: '双脚运动', icon: '🦶', region: 'Cz区(中央)', color: 'green' }
]

const classResults = ref([
  { label: '左手', value: 10, color: '#00aaff' },
  { label: '右手', value: 10, color: '#ff6b00' },
  { label: '双脚', value: 10, color: '#00ff88' }
])

const erdSide = computed(() => {
  if (currentTask.value === 'left') return 'right'
  if (currentTask.value === 'right') return 'left'
  return 'center'
})

const erdPercent = computed(() => isActive.value ? 35 + Math.floor(Math.random() * 20) : 0)

const eduTitle = computed(() => {
  const titles: Record<string, string> = {
    left: '对侧激活: 右脑C4区',
    right: '对侧激活: 左脑C3区', 
    foot: '双侧激活: 中央Cz区'
  }
  return currentTask.value ? titles[currentTask.value] : ''
})

const eduContent = computed(() => {
  const contents: Record<string, string> = {
    left: '想象左手运动时，右脑感觉运动皮层C4区的Mu/Beta节律能量下降（ERD），因为大脑控制对侧身体。',
    right: '想象右手运动时，左脑C3区出现ERD，这是运动皮层对侧控制原理的体现。',
    foot: '想象双脚运动时，中央Cz区（控制下肢的皮层位置）出现ERD现象。'
  }
  return currentTask.value ? contents[currentTask.value] : ''
})

const isChannelHighlighted = (idx: number) => {
  if (!currentTask.value) return false
  // C3(0)对应右手，C4(2)对应左手，Cz(1)对应脚
  if (currentTask.value === 'right' && idx === 0) return true
  if (currentTask.value === 'left' && idx === 2) return true
  if (currentTask.value === 'foot' && idx === 1) return true
  return false
}

// 波形数据
const waveData = Array.from({ length: 6 }, () => ({
  offset: Math.random() * Math.PI * 2,
  speed: 0.8 + Math.random() * 0.4,
  baseAmp: 12 + Math.random() * 8
}))

let wavePhase = 0

// 绘制波形
const drawWaves = () => {
  const canvas = waveCanvas.value
  if (!canvas) return
  
  const ctx = canvas.getContext('2d')
  if (!ctx) return
  
  const w = canvas.width
  const h = canvas.height
  const chH = h / 6
  
  ctx.clearRect(0, 0, w, h)
  
  // 网格
  ctx.strokeStyle = 'rgba(0, 255, 255, 0.05)'
  ctx.lineWidth = 0.5
  for (let i = 1; i < 6; i++) {
    ctx.beginPath()
    ctx.moveTo(30, i * chH)
    ctx.lineTo(w, i * chH)
    ctx.stroke()
  }
  
  // 绘制每通道波形
  const colors = ['#00ffff', '#ff6b00', '#00ff88', '#ffaa00', '#00aaff', '#ff55aa']
  
  waveData.forEach((wave, idx) => {
    const baseY = (idx + 0.5) * chH
    const isHighlighted = isChannelHighlighted(idx)
    
    // 计算ERD影响
    let ampMultiplier = 1.0
    if (isActive.value && currentTask.value) {
      if (isHighlighted) {
        ampMultiplier = 0.4  // ERD - 振幅下降
      }
    }
    
    ctx.beginPath()
    ctx.strokeStyle = isHighlighted && isActive.value ? '#ffffff' : colors[idx]
    ctx.lineWidth = isHighlighted ? 2 : 1.5
    ctx.globalAlpha = isHighlighted ? 1 : 0.8
    
    for (let x = 30; x < w; x += 2) {
      const t = (x / w) * Math.PI * 8
      let y = 0
      
      // 基础Mu节律
      y += Math.sin(wavePhase * wave.speed + t * 2 + wave.offset) * wave.baseAmp * ampMultiplier
      // Beta成分
      y += Math.sin(wavePhase * wave.speed * 2.5 + t * 4 + wave.offset) * wave.baseAmp * 0.3 * ampMultiplier
      // 慢波
      y += Math.sin(wavePhase * 0.3 + t * 0.5) * wave.baseAmp * 0.4
      // 噪声
      y += (Math.random() - 0.5) * 4
      
      const yPos = baseY + y
      
      if (x === 30) ctx.moveTo(x, yPos)
      else ctx.lineTo(x, yPos)
    }
    
    ctx.stroke()
    ctx.globalAlpha = 1
  })
  
  wavePhase += 0.15
}

// 绘制地形图
const drawTopo = () => {
  const canvas = topoCanvas.value
  if (!canvas) return
  
  const ctx = canvas.getContext('2d')
  if (!ctx) return
  
  const w = canvas.width
  const h = canvas.height
  const cx = w / 2
  const cy = h / 2
  const r = w * 0.38
  
  ctx.clearRect(0, 0, w, h)
  phase.value += 0.03
  
  // 头部
  ctx.beginPath()
  ctx.arc(cx, cy, r, 0, Math.PI * 2)
  ctx.fillStyle = 'rgba(0, 25, 40, 0.9)'
  ctx.fill()
  ctx.strokeStyle = 'rgba(0, 255, 255, 0.4)'
  ctx.lineWidth = 2
  ctx.stroke()
  
  // 鼻子
  ctx.beginPath()
  ctx.moveTo(cx - 5, cy - r)
  ctx.lineTo(cx, cy - r - 8)
  ctx.lineTo(cx + 5, cy - r)
  ctx.fillStyle = 'rgba(0, 255, 255, 0.3)'
  ctx.fill()
  
  // 激活区域
  if (isActive.value && currentTask.value) {
    drawHeatmap(ctx, cx, cy, r)
  } else {
    // 基线
    const grad = ctx.createRadialGradient(cx, cy, 0, cx, cy, r * 0.5)
    grad.addColorStop(0, 'rgba(0, 255, 255, 0.08)')
    grad.addColorStop(1, 'transparent')
    ctx.fillStyle = grad
    ctx.beginPath()
    ctx.arc(cx, cy, r * 0.5, 0, Math.PI * 2)
    ctx.fill()
  }
  
  // 电极点
  const electrodes = [
    { name: 'C3', x: 0.25, y: 0.5, isERD: currentTask.value === 'right' },
    { name: 'Cz', x: 0.5, y: 0.45, isERD: currentTask.value === 'foot' },
    { name: 'C4', x: 0.75, y: 0.5, isERD: currentTask.value === 'left' },
  ]
  
  electrodes.forEach(elec => {
    const ex = cx + (elec.x - 0.5) * r * 1.6
    const ey = cy + (elec.y - 0.5) * r * 1.6
    
    ctx.beginPath()
    ctx.arc(ex, ey, elec.isERD && isActive.value ? 8 : 5, 0, Math.PI * 2)
    ctx.fillStyle = elec.isERD && isActive.value ? '#00ffff' : 'rgba(255, 255, 255, 0.5)'
    ctx.fill()
    
    if (elec.isERD && isActive.value) {
      ctx.shadowColor = '#00ffff'
      ctx.shadowBlur = 15
      ctx.fill()
      ctx.shadowBlur = 0
    }
    
    ctx.font = elec.isERD && isActive.value ? 'bold 10px sans-serif' : '8px sans-serif'
    ctx.fillStyle = elec.isERD && isActive.value ? '#fff' : 'rgba(255, 255, 255, 0.5)'
    ctx.textAlign = 'center'
    ctx.fillText(elec.name, ex, ey + 15)
  })
}

const drawHeatmap = (ctx: CanvasRenderingContext2D, cx: number, cy: number, r: number) => {
  const pulse = Math.sin(phase.value * 3) * 0.2 + 0.8
  
  let erdX = cx, erdY = cy, ersX = cx, ersY = cy
  let erdColor = '0, 255, 136'
  
  if (currentTask.value === 'left') {
    erdX = cx + r * 0.45
    ersX = cx - r * 0.45
    erdColor = '0, 170, 255'
  } else if (currentTask.value === 'right') {
    erdX = cx - r * 0.45
    ersX = cx + r * 0.45
    erdColor = '255, 107, 0'
  } else if (currentTask.value === 'foot') {
    erdY = cy - r * 0.15
    ersY = cy + r * 0.25
  }
  
  // ERD
  const erdGrad = ctx.createRadialGradient(erdX, erdY, 0, erdX, erdY, r * 0.5)
  erdGrad.addColorStop(0, `rgba(${erdColor}, ${0.8 * pulse})`)
  erdGrad.addColorStop(0.5, `rgba(${erdColor}, ${0.4 * pulse})`)
  erdGrad.addColorStop(1, 'transparent')
  ctx.fillStyle = erdGrad
  ctx.beginPath()
  ctx.arc(erdX, erdY, r * 0.5, 0, Math.PI * 2)
  ctx.fill()
  
  // ERS
  const ersGrad = ctx.createRadialGradient(ersX, ersY, 0, ersX, ersY, r * 0.3)
  ersGrad.addColorStop(0, `rgba(255, 180, 0, ${0.4 * pulse})`)
  ersGrad.addColorStop(1, 'transparent')
  ctx.fillStyle = ersGrad
  ctx.beginPath()
  ctx.arc(ersX, ersY, r * 0.3, 0, Math.PI * 2)
  ctx.fill()
  
  // 标签
  ctx.font = 'bold 9px sans-serif'
  ctx.fillStyle = '#fff'
  ctx.textAlign = 'center'
  ctx.fillText('ERD', erdX, erdY - r * 0.5 - 5)
  ctx.fillStyle = '#ffaa00'
  ctx.fillText('ERS', ersX, ersY + r * 0.3 + 12)
}

// 绘制频谱 - 通道特定显示
const drawSpectrum = () => {
  const canvas = spectrumCanvas.value
  if (!canvas) return
  
  const ctx = canvas.getContext('2d')
  if (!ctx) return
  
  const w = canvas.width
  const h = canvas.height
  
  ctx.clearRect(0, 0, w, h)
  
  const baseSpectrum = [15, 20, 25, 30, 35, 45, 55, 65, 75, 80, 70, 55, 45, 40, 38, 36, 34, 32, 30, 28, 26, 25, 24, 23, 22, 21, 20, 19, 18, 17]
  
  const xScale = (w - 30) / 30
  const yScale = (h - 35) / 100
  
  // 根据任务确定显示的通道
  const channelInfo = {
    left: { name: 'C4', desc: '右脑', erdSide: 'right' },
    right: { name: 'C3', desc: '左脑', erdSide: 'left' },
    foot: { name: 'Cz', desc: '中央', erdSide: 'center' }
  }
  
  const currentChannel = currentTask.value ? channelInfo[currentTask.value] : null
  
  // 频段背景
  const bands = [
    { name: 'Mu (8-13Hz)', start: 8, end: 13, color: '#00ff88' },
    { name: 'Beta (13-30Hz)', start: 13, end: 30, color: '#ff6b00' }
  ]
  
  bands.forEach(band => {
    const x1 = 20 + (band.start - 1) * xScale
    const x2 = 20 + (band.end - 1) * xScale
    const isHighlighted = isActive.value
    
    ctx.fillStyle = isHighlighted ? band.color + '25' : band.color + '10'
    ctx.fillRect(x1, 5, x2 - x1, h - 35)
    
    ctx.fillStyle = isHighlighted ? band.color : band.color + '60'
    ctx.font = '7px sans-serif'
    ctx.textAlign = 'center'
    ctx.fillText(band.name.split(' ')[0], (x1 + x2) / 2, h - 8)
  })
  
  // 基线（虚线）
  ctx.beginPath()
  ctx.setLineDash([3, 3])
  ctx.strokeStyle = 'rgba(100, 100, 100, 0.4)'
  ctx.lineWidth = 1
  baseSpectrum.forEach((power, i) => {
    const x = 20 + i * xScale
    const y = 15 + (100 - power) * yScale
    if (i === 0) ctx.moveTo(x, y)
    else ctx.lineTo(x, y)
  })
  ctx.stroke()
  ctx.setLineDash([])
  
  // 动画脉冲
  const time = Date.now() / 1000
  const pulse = isActive.value ? 0.8 + Math.sin(time * 3) * 0.1 : 1
  
  // 当前谱线
  ctx.beginPath()
  ctx.strokeStyle = isActive.value ? '#00ffff' : '#00aaff'
  ctx.lineWidth = isActive.value ? 2 : 1.5
  ctx.shadowColor = isActive.value ? '#00ffff' : 'transparent'
  ctx.shadowBlur = isActive.value ? 6 : 0
  
  baseSpectrum.forEach((power, i) => {
    let adjustedPower = power + (Math.random() - 0.5) * 2
    const freq = i + 1
    
    // ERD效果 - 只在8-30Hz范围，根据任务显示
    if (isActive.value && currentTask.value) {
      if (freq >= 8 && freq <= 13) {
        // Mu频段 - 大幅下降
        adjustedPower *= 0.3 * pulse
      } else if (freq >= 13 && freq <= 30) {
        // Beta频段 - 中等下降
        adjustedPower *= 0.5 * pulse
      }
    }
    
    const x = 20 + i * xScale
    const y = 15 + (100 - adjustedPower) * yScale
    if (i === 0) ctx.moveTo(x, y)
    else ctx.lineTo(x, y)
  })
  ctx.stroke()
  ctx.shadowBlur = 0
  
  // 填充
  ctx.lineTo(20 + 29 * xScale, h - 25)
  ctx.lineTo(20, h - 25)
  ctx.closePath()
  ctx.fillStyle = isActive.value ? 'rgba(0, 255, 255, 0.15)' : 'rgba(0, 170, 255, 0.08)'
  ctx.fill()
  
  // 通道标签和ERD指示
  if (currentChannel) {
    // 通道名称
    ctx.fillStyle = '#00ffff'
    ctx.font = 'bold 10px sans-serif'
    ctx.textAlign = 'left'
    ctx.fillText(`通道: ${currentChannel.name}`, 25, 15)
    
    ctx.fillStyle = '#888'
    ctx.font = '8px sans-serif'
    ctx.fillText(`(${currentChannel.desc})`, 75, 15)
    
    // ERD标注
    ctx.fillStyle = '#ff6b00'
    ctx.font = 'bold 10px sans-serif'
    ctx.textAlign = 'center'
    
    const arrowX = 20 + 10 * xScale
    const arrowY = 32
    
    // 下降箭头
    ctx.beginPath()
    ctx.moveTo(arrowX - 6, arrowY - 3)
    ctx.lineTo(arrowX + 6, arrowY - 3)
    ctx.lineTo(arrowX, arrowY + 6)
    ctx.closePath()
    ctx.fill()
    
    ctx.fillStyle = '#ff6b00'
    ctx.font = 'bold 8px sans-serif'
    ctx.fillText('ERD', arrowX, arrowY - 8)
    
    // 下降百分比
    ctx.fillStyle = '#00ff88'
    ctx.font = 'bold 9px sans-serif'
    ctx.fillText('-70%', arrowX + 28, arrowY)
    
    // Beta频段ERD
    ctx.fillStyle = '#ff6b00'
    ctx.font = 'bold 8px sans-serif'
    const betaArrowX = 20 + 20 * xScale
    ctx.fillText('ERD', betaArrowX, arrowY - 3)
    ctx.fillText('-50%', betaArrowX + 22, arrowY + 2)
    
  } else {
    // 提示信息
    ctx.fillStyle = 'rgba(0, 255, 255, 0.5)'
    ctx.font = '9px sans-serif'
    ctx.textAlign = 'center'
    ctx.fillText('点击运动想象按钮', w/2, 20)
    ctx.fillText('查看通道频谱变化', w/2, 32)
  }
  
  // 频率轴
  ctx.fillStyle = '#555'
  ctx.font = '6px sans-serif'
  ctx.textAlign = 'center'
  for (let f = 5; f <= 30; f += 5) {
    ctx.fillText(f + '', 20 + (f - 1) * xScale, h - 2)
  }
}

const animate = () => {
  phase.value += 0.05
  drawWaves()
  drawTopo()
  drawSpectrum()
  animationId.value = requestAnimationFrame(animate)
}

const selectTask = (task: string) => {
  if (currentTask.value === task) {
    currentTask.value = null
    isActive.value = false
    resetResults()
    return
  }
  
  currentTask.value = task
  isActive.value = true
  updateResults(task)
  
  const region = task === 'left' ? 'right' : task === 'right' ? 'left' : 'center'
  emit('brainPulse', region, 0.9)
}

const updateResults = (task: string) => {
  const matrices: Record<string, number[]> = {
    left: [89, 7, 4],
    right: [8, 85, 7],
    foot: [5, 10, 85]
  }
  const result = matrices[task]
  classResults.value = [
    { label: '左手', value: result[0], color: '#00aaff' },
    { label: '右手', value: result[1], color: '#ff6b00' },
    { label: '双脚', value: result[2], color: '#00ff88' }
  ]
}

const resetResults = () => {
  classResults.value = [
    { label: '左手', value: 10, color: '#00aaff' },
    { label: '右手', value: 10, color: '#ff6b00' },
    { label: '双脚', value: 10, color: '#00ff88' }
  ]
}

watch(() => props.motorImagery, (val) => {
  if (val) selectTask(val)
  else {
    currentTask.value = null
    isActive.value = false
    resetResults()
  }
})

onMounted(() => {
  if (waveCanvas.value) { waveCanvas.value.width = 280; waveCanvas.value.height = 180 }
  if (topoCanvas.value) { topoCanvas.value.width = 140; topoCanvas.value.height = 140 }
  if (spectrumCanvas.value) { spectrumCanvas.value.width = 150; spectrumCanvas.value.height = 120 }
  animate()
})

onBeforeUnmount(() => {
  if (animationId.value) cancelAnimationFrame(animationId.value)
})
</script>

<style scoped>
.bci-analyzer {
  background: linear-gradient(180deg, #080c15 0%, #0a1018 100%);
  border: 1px solid rgba(0, 255, 255, 0.2);
  border-radius: 12px;
  padding: 10px;
  display: flex;
  flex-direction: column;
  gap: 8px;
  font-family: 'Segoe UI', sans-serif;
  height: 100%;
}

.analyzer-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-bottom: 8px;
  border-bottom: 1px solid rgba(0, 255, 255, 0.15);
}

.header-left {
  display: flex;
  align-items: center;
  gap: 8px;
}

.header-icon {
  font-size: 1.2rem;
}

.header-title {
  color: #00ffff;
  font-size: 0.8rem;
  font-weight: bold;
  letter-spacing: 1px;
}

.header-right {
  display: flex;
  gap: 10px;
  align-items: center;
}

.subject-badge {
  font-size: 0.6rem;
  color: #888;
  background: rgba(0, 0, 0, 0.3);
  padding: 2px 8px;
  border-radius: 4px;
}

.status-badge {
  font-size: 0.65rem;
  padding: 3px 10px;
  border-radius: 10px;
  background: rgba(100, 100, 100, 0.2);
  color: #888;
}

.status-badge.active {
  background: rgba(0, 255, 136, 0.15);
  color: #00ff88;
  animation: pulse-status 1.5s infinite;
}

@keyframes pulse-status {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.6; }
}

/* 信号显示区 */
.signal-area {
  display: flex;
  gap: 8px;
  flex-shrink: 0;
}

.wave-section {
  flex: 1;
  position: relative;
}

.wave-canvas {
  width: 100%;
  height: 180px;
  background: rgba(0, 0, 0, 0.4);
  border: 1px solid rgba(0, 255, 255, 0.1);
  border-radius: 6px;
  display: block;
}

.channel-markers {
  position: absolute;
  left: 5px;
  top: 0;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.channel-marker {
  flex: 1;
  display: flex;
  align-items: center;
  font-size: 0.55rem;
  color: rgba(255, 255, 255, 0.3);
  transition: all 0.3s;
}

.channel-marker.highlighted {
  color: #00ffff;
  font-weight: bold;
  text-shadow: 0 0 8px rgba(0, 255, 255, 0.8);
}

.analysis-side {
  display: flex;
  flex-direction: column;
  gap: 6px;
  width: 150px;
}

.topo-box, .spectrum-box {
  background: rgba(0, 0, 0, 0.3);
  border: 1px solid rgba(0, 255, 255, 0.1);
  border-radius: 6px;
  padding: 6px;
  position: relative;
}

.topo-canvas {
  width: 100%;
  height: 120px;
  display: block;
}

.spectrum-canvas {
  width: 100%;
  height: 90px;
  display: block;
}

.box-label {
  position: absolute;
  top: 4px;
  left: 6px;
  font-size: 0.55rem;
  color: #666;
  z-index: 1;
}

.erd-indicator {
  position: absolute;
  bottom: 6px;
  left: 50%;
  transform: translateX(-50%);
  font-size: 0.6rem;
  font-weight: bold;
  padding: 2px 8px;
  border-radius: 4px;
}

.erd-indicator.right {
  background: rgba(0, 170, 255, 0.2);
  color: #00aaff;
  border: 1px solid rgba(0, 170, 255, 0.4);
}

.erd-indicator.left {
  background: rgba(255, 107, 0, 0.2);
  color: #ff6b00;
  border: 1px solid rgba(255, 107, 0, 0.4);
}

.erd-indicator.center {
  background: rgba(0, 255, 136, 0.2);
  color: #00ff88;
  border: 1px solid rgba(0, 255, 136, 0.4);
}

/* 控制区 */
.control-area {
  display: flex;
  gap: 10px;
  flex: 1;
  min-height: 0;
}

.task-selector {
  flex: 0 0 45%;
}

.selector-label {
  font-size: 0.6rem;
  color: #666;
  letter-spacing: 1px;
  margin-bottom: 6px;
}

.task-buttons {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.task-btn {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px;
  background: rgba(0, 20, 30, 0.6);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s;
  text-align: left;
}

.task-btn:hover {
  background: rgba(0, 40, 60, 0.8);
  border-color: rgba(255, 255, 255, 0.3);
  transform: translateX(3px);
}

.task-btn.blue.active {
  border-color: #00aaff;
  background: rgba(0, 170, 255, 0.15);
  box-shadow: 0 0 20px rgba(0, 170, 255, 0.3);
}

.task-btn.orange.active {
  border-color: #ff6b00;
  background: rgba(255, 107, 0, 0.15);
  box-shadow: 0 0 20px rgba(255, 107, 0, 0.3);
}

.task-btn.green.active {
  border-color: #00ff88;
  background: rgba(0, 255, 136, 0.15);
  box-shadow: 0 0 20px rgba(0, 255, 136, 0.3);
}

.btn-icon {
  font-size: 1.5rem;
}

.btn-info {
  display: flex;
  flex-direction: column;
  flex: 1;
}

.btn-name {
  color: #fff;
  font-size: 0.8rem;
  font-weight: bold;
}

.btn-region {
  color: #888;
  font-size: 0.6rem;
}

.task-btn.active .btn-region {
  color: #fff;
}

.btn-indicator {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.indicator-dot {
  width: 6px;
  height: 6px;
  background: currentColor;
  border-radius: 50%;
  animation: dot-pulse 1s infinite;
}

.task-btn.blue .indicator-dot { background: #00aaff; }
.task-btn.orange .indicator-dot { background: #ff6b00; }
.task-btn.green .indicator-dot { background: #00ff88; }

@keyframes dot-pulse {
  0%, 100% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.5; transform: scale(0.8); }
}

/* 结果区 */
.result-area {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 8px;
  min-width: 0;
}

.class-result {
  background: rgba(0, 0, 0, 0.3);
  border: 1px solid rgba(0, 255, 255, 0.1);
  border-radius: 6px;
  padding: 8px;
}

.result-header {
  font-size: 0.6rem;
  color: #00ffff;
  margin-bottom: 6px;
  letter-spacing: 1px;
}

.result-bars {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.result-row {
  display: flex;
  align-items: center;
  gap: 6px;
}

.result-label {
  width: 30px;
  font-size: 0.6rem;
  color: #888;
}

.result-track {
  flex: 1;
  height: 10px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 5px;
  overflow: hidden;
}

.result-fill {
  height: 100%;
  border-radius: 5px;
  position: relative;
  transition: width 0.6s ease-out;
}

.fill-glow {
  position: absolute;
  right: 0;
  top: 0;
  bottom: 0;
  width: 20px;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.4));
  animation: glow-move 1s infinite;
}

@keyframes glow-move {
  0%, 100% { opacity: 0; }
  50% { opacity: 1; }
}

.result-value {
  width: 35px;
  font-size: 0.7rem;
  font-weight: bold;
  text-align: right;
}

.education-box {
  display: flex;
  gap: 8px;
  padding: 10px;
  background: rgba(255, 170, 0, 0.08);
  border: 1px solid rgba(255, 170, 0, 0.3);
  border-radius: 6px;
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(-5px); }
  to { opacity: 1; transform: translateY(0); }
}

.edu-icon {
  font-size: 1.2rem;
}

.edu-text {
  flex: 1;
}

.edu-text strong {
  display: block;
  font-size: 0.7rem;
  color: #ffaa00;
  margin-bottom: 4px;
}

.edu-text p {
  margin: 0;
  font-size: 0.6rem;
  color: #aaa;
  line-height: 1.4;
}

/* 状态栏 */
.status-bar {
  display: flex;
  justify-content: space-between;
  padding: 6px 10px;
  background: rgba(0, 0, 0, 0.3);
  border-radius: 6px;
  border-top: 1px solid rgba(0, 255, 255, 0.1);
}

.status-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
}

.s-label {
  font-size: 0.5rem;
  color: #555;
  letter-spacing: 1px;
}

.s-value {
  font-size: 0.65rem;
  color: #00ffff;
  font-weight: bold;
}

.s-value.highlight {
  color: #4ade80;
}
</style>
