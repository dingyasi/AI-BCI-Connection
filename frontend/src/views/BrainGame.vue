<template>
  <div class="game-page">
    <header class="game-header">
      <div class="header-left">
        <router-link to="/" class="back-btn">← 返回</router-link>
        <div class="header-divider"></div>
        <h1 class="page-title">🎮 意念控制飞机</h1>
      </div>
      <div class="header-right">
        <span class="score-info">得分: <strong>{{ score }}</strong></span>
        <span class="score-info">最高: <strong>{{ highScore }}</strong></span>
      </div>
    </header>

    <main class="game-main">
      <!-- 游戏说明 -->
      <div class="game-intro">
        <h2>🧠 体验脑机接口：用"意念"控制飞机</h2>
        <p>想象你有一台BCI设备，通过<strong>运动想象</strong>产生脑电信号，控制屏幕上的飞机。左手想象让飞机<strong>上升</strong>，右手想象让飞机<strong>下降</strong>，避开障碍物，收集能量球！</p>
      </div>

      <!-- 游戏区域 -->
      <div class="game-area">
        <div class="canvas-wrapper">
          <canvas ref="canvas" width="800" height="400"></canvas>
          
          <div v-if="state === 'idle'" class="overlay">
            <div class="overlay-box">
              <div class="overlay-icon">✈️</div>
              <h2>意念控制飞机</h2>
              <p>用"想象"控制飞机上下飞行<br>体验脑机接口如何控制外部设备</p>
              <button class="start-btn" @click="startGame">开始游戏</button>
            </div>
          </div>
          
          <div v-if="state === 'over'" class="overlay">
            <div class="overlay-box">
              <div class="overlay-icon">💥</div>
              <h2>游戏结束</h2>
              <p>得分: <span class="final-score">{{ score }}</span></p>
              <button class="start-btn" @click="startGame">再来一局</button>
            </div>
          </div>
        </div>

        <!-- 控制按钮 -->
        <div class="controls">
          <button 
            class="ctrl-btn up-btn"
            :class="{ active: holding === 'up' }"
            @mousedown="startHold('up')"
            @mouseup="stopHold"
            @mouseleave="stopHold"
            @touchstart.prevent="startHold('up')"
            @touchend.prevent="stopHold"
          >
            <span class="ctrl-icon">🤛</span>
            <span class="ctrl-text">想象左手</span>
            <span class="ctrl-arrow">↑ 上升</span>
          </button>
          
          <button 
            class="ctrl-btn down-btn"
            :class="{ active: holding === 'down' }"
            @mousedown="startHold('down')"
            @mouseup="stopHold"
            @mouseleave="stopHold"
            @touchstart.prevent="startHold('down')"
            @touchend.prevent="stopHold"
          >
            <span class="ctrl-icon">🤚</span>
            <span class="ctrl-text">想象右手</span>
            <span class="ctrl-arrow">↓ 下降</span>
          </button>
          
          <div class="signal-box">
            <div class="signal-label">脑电信号强度</div>
            <div class="signal-bar">
              <div class="signal-fill" :style="{ width: signalStr + '%' }"></div>
            </div>
            <div class="signal-percent">{{ signalStr }}%</div>
          </div>
        </div>
      </div>

      <!-- 侧边信息 -->
      <div class="side-info">
        <div class="info-card">
          <h4>📊 EEG信号</h4>
          <canvas ref="eegCanvas" class="eeg-canvas" width="280" height="100"></canvas>
          <div class="eeg-legend">
            <span class="ch3">C3(左脑)</span>
            <span class="ch4">C4(右脑)</span>
          </div>
        </div>
        
        <div class="info-card">
          <h4>🎯 Hopfield分类</h4>
          <div class="class-row">
            <span>左手上升</span>
            <div class="class-bar"><div class="class-fill-up" :style="{ width: classUp + '%' }"></div></div>
            <span>{{ classUp }}%</span>
          </div>
          <div class="class-row">
            <span>右手下降</span>
            <div class="class-bar"><div class="class-fill-down" :style="{ width: classDown + '%' }"></div></div>
            <span>{{ classDown }}%</span>
          </div>
        </div>

        <div class="info-card tip">
          <h4>💡 BCI原理</h4>
          <p>想象左手运动时，<strong>右脑C4区</strong>的Mu节律能量下降（ERD）；想象右手时，<strong>左脑C3区</strong>出现ERD。BCI系统通过检测ERD来识别你的运动意图。</p>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount } from 'vue'

const canvas = ref<HTMLCanvasElement>()
const eegCanvas = ref<HTMLCanvasElement>()

type State = 'idle' | 'playing' | 'over'
const state = ref<State>('idle')
const score = ref(0)
const highScore = ref(0)
const holding = ref<'up' | 'down' | null>(null)
const signalStr = ref(0)
const classUp = ref(10)
const classDown = ref(10)

let animId: number | null = null
let frame = 0
let planeY = 200
let planeVy = 0
let pipes: { x: number; gapY: number; gapH: number; passed: boolean }[] = []
let orbs: { x: number; y: number; r: number }[] = []
let particles: { x: number; y: number; vx: number; vy: number; life: number; color: string }[] = []

const W = 800, H = 400

const startGame = () => {
  state.value = 'playing'
  score.value = 0
  planeY = H / 2
  planeVy = 0
  pipes = []
  orbs = []
  particles = []
  frame = 0
  loop()
}

const startHold = (dir: 'up' | 'down') => {
  holding.value = dir
  signalStr.value = Math.min(100, 70 + Math.random() * 30)
  classUp.value = dir === 'up' ? 88 : 8
  classDown.value = dir === 'down' ? 88 : 8
}

const stopHold = () => {
  holding.value = null
  signalStr.value = Math.max(0, signalStr.value - 30)
  classUp.value = 10
  classDown.value = 10
}

const loop = () => {
  if (state.value !== 'playing') return
  frame++

  // 飞机物理 - 更温和
  if (holding.value === 'up') planeVy -= 0.5
  else if (holding.value === 'down') planeVy += 0.5
  planeVy += 0.3 // 更轻的重力
  planeVy = Math.max(-6, Math.min(6, planeVy))
  planeY += planeVy
  planeY = Math.max(20, Math.min(H - 20, planeY))

  // 生成管道 - 更慢更宽
  if (frame % 150 === 0) {
    const gapH = 180
    const gapY = 40 + Math.random() * (H - 80 - gapH)
    pipes.push({ x: W + 40, gapY, gapH, passed: false })
  }

  // 生成能量球 - 更频繁
  if (frame % 100 === 0) {
    orbs.push({ x: W + 20, y: 50 + Math.random() * (H - 100), r: 14 })
  }

  // 更新管道 - 更慢的速度
  pipes = pipes.filter(p => {
    p.x -= 2
    // 碰撞
    if (Math.abs(p.x - 120) < 25) {
      if (planeY < p.gapY || planeY > p.gapY + p.gapH) {
        state.value = 'over'
        if (score.value > highScore.value) highScore.value = score.value
        addParticles(120, planeY, '#ff4444', 15)
        draw()
        return false
      }
    }
    // 计分
    if (!p.passed && p.x < 100) {
      p.passed = true
      score.value += 10
      addParticles(120, planeY, '#00ff88', 8)
    }
    return p.x > -50
  })

  // 更新能量球 - 更慢
  orbs = orbs.filter(o => {
    o.x -= 2
    const dx = o.x - 120, dy = o.y - planeY
    if (dx * dx + dy * dy < (o.r + 15) * (o.r + 15)) {
      score.value += 20
      addParticles(o.x, o.y, '#ffaa00', 10)
      return false
    }
    return o.x > -30
  })

  // 更新粒子
  particles = particles.filter(p => {
    p.x += p.vx; p.y += p.vy; p.life--
    return p.life > 0
  })

  // 信号衰减
  if (!holding.value) signalStr.value = Math.max(0, signalStr.value - 2)

  draw()
  drawEEG()
  animId = requestAnimationFrame(loop)
}

const addParticles = (x: number, y: number, color: string, count: number) => {
  for (let i = 0; i < count; i++) {
    particles.push({
      x, y,
      vx: (Math.random() - 0.5) * 6,
      vy: (Math.random() - 0.5) * 6,
      life: 20 + Math.random() * 10,
      color
    })
  }
}

const draw = () => {
  const ctx = canvas.value?.getContext('2d')
  if (!ctx) return

  // 背景
  ctx.fillStyle = '#0a1628'
  ctx.fillRect(0, 0, W, H)

  // 星星
  ctx.fillStyle = 'rgba(255,255,255,0.3)'
  for (let i = 0; i < 50; i++) {
    ctx.fillRect((i * 137 + frame) % W, (i * 89) % H, 1, 1)
  }

  // 地面
  ctx.fillStyle = '#1a2a3a'
  ctx.fillRect(0, H - 5, W, 5)

  // 管道
  pipes.forEach(p => {
    const grad = ctx.createLinearGradient(p.x - 15, 0, p.x + 15, 0)
    grad.addColorStop(0, '#cc3333')
    grad.addColorStop(0.5, '#ff5555')
    grad.addColorStop(1, '#cc3333')
    ctx.fillStyle = grad
    ctx.fillRect(p.x - 15, 0, 30, p.gapY)
    ctx.fillRect(p.x - 15, p.gapY + p.gapH, 30, H - p.gapY - p.gapH)
    // 门边缘
    ctx.strokeStyle = '#00ff88'
    ctx.lineWidth = 2
    ctx.beginPath()
    ctx.moveTo(p.x - 15, p.gapY); ctx.lineTo(p.x + 15, p.gapY); ctx.stroke()
    ctx.beginPath()
    ctx.moveTo(p.x - 15, p.gapY + p.gapH); ctx.lineTo(p.x + 15, p.gapY + p.gapH); ctx.stroke()
  })

  // 能量球
  orbs.forEach(o => {
    ctx.beginPath()
    ctx.arc(o.x, o.y, o.r + 4, 0, Math.PI * 2)
    ctx.fillStyle = 'rgba(255,170,0,0.2)'
    ctx.fill()
    ctx.beginPath()
    ctx.arc(o.x, o.y, o.r, 0, Math.PI * 2)
    ctx.fillStyle = '#ffaa00'
    ctx.shadowColor = '#ffaa00'
    ctx.shadowBlur = 10
    ctx.fill()
    ctx.shadowBlur = 0
    ctx.fillStyle = '#fff'
    ctx.font = 'bold 10px sans-serif'
    ctx.textAlign = 'center'
    ctx.fillText('+', o.x, o.y + 4)
  })

  // 粒子
  particles.forEach(p => {
    ctx.beginPath()
    ctx.arc(p.x, p.y, 2, 0, Math.PI * 2)
    ctx.globalAlpha = p.life / 30
    ctx.fillStyle = p.color
    ctx.fill()
    ctx.globalAlpha = 1
  })

  // 飞机
  const px = 120, py = planeY
  ctx.save()
  ctx.translate(px, py)
  const angle = Math.atan2(planeVy, 8)
  ctx.rotate(angle)
  // 尾焰
  ctx.beginPath()
  ctx.moveTo(-20, 0)
  ctx.lineTo(-30, -4)
  ctx.lineTo(-30, 4)
  ctx.closePath()
  ctx.fillStyle = holding.value ? '#00ffff' : '#ff6b00'
  ctx.fill()
  // 机身
  ctx.beginPath()
  ctx.moveTo(15, 0)
  ctx.lineTo(-10, -8)
  ctx.lineTo(-10, 8)
  ctx.closePath()
  const bodyGrad = ctx.createLinearGradient(-10, 0, 15, 0)
  bodyGrad.addColorStop(0, '#00aaff')
  bodyGrad.addColorStop(1, '#88ffff')
  ctx.fillStyle = bodyGrad
  ctx.shadowColor = '#00ffff'
  ctx.shadowBlur = 12
  ctx.fill()
  ctx.shadowBlur = 0
  // 翅膀
  ctx.fillStyle = '#0066aa'
  ctx.fillRect(-5, -12, 10, 4)
  ctx.fillRect(-5, 8, 10, 4)
  ctx.restore()

  // 分数
  ctx.fillStyle = '#00ffff'
  ctx.font = 'bold 18px sans-serif'
  ctx.textAlign = 'left'
  ctx.fillText(`得分: ${score.value}`, 15, 30)
}

const drawEEG = () => {
  const ctx = eegCanvas.value?.getContext('2d')
  if (!ctx) return
  const w = 280, h = 100

  ctx.clearRect(0, 0, w, h)
  ctx.fillStyle = '#0a1628'
  ctx.fillRect(0, 0, w, h)

  const channels = ['C3', 'C4']
  const colors = ['#00aaff', '#ff6b00']

  channels.forEach((_, ch) => {
    const baseY = (ch + 0.5) * h / 2
    const isERD = holding.value && (
      (holding.value === 'up' && ch === 1) ||  // 上升→C4 ERD
      (holding.value === 'down' && ch === 0)    // 下降→C3 ERD
    )

    ctx.beginPath()
    ctx.strokeStyle = isERD ? '#ffffff' : colors[ch]
    ctx.lineWidth = isERD ? 2 : 1.2

    for (let x = 0; x < w; x += 2) {
      const t = x / w * Math.PI * 8
      const amp = isERD ? 6 : 12 // ERD时振幅下降
      let y = Math.sin(t * 2 + ch + frame * 0.1) * amp
      y += Math.sin(t * 4 + ch) * amp * 0.3
      y += (Math.random() - 0.5) * 2
      if (x === 0) ctx.moveTo(x, baseY + y)
      else ctx.lineTo(x, baseY + y)
    }
    ctx.stroke()

    if (isERD) {
      ctx.fillStyle = '#ff6b00'
      ctx.font = 'bold 9px sans-serif'
      ctx.textAlign = 'right'
      ctx.fillText('ERD↓', w - 5, baseY - 8)
    }
  })
}

onMounted(() => {
  window.addEventListener('keydown', (e) => {
    if (state.value !== 'playing') return
    if (e.key === 'ArrowUp' || e.key === 'w') startHold('up')
    if (e.key === 'ArrowDown' || e.key === 's') startHold('down')
  })
  window.addEventListener('keyup', (e) => {
    if (['ArrowUp', 'ArrowDown', 'w', 's'].includes(e.key)) stopHold()
  })
})

onBeforeUnmount(() => {
  if (animId) cancelAnimationFrame(animId)
})
</script>

<style scoped>
.game-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #0a0a0f, #0d1117);
  color: #e0e0e0;
  font-family: 'Microsoft YaHei', sans-serif;
}

.game-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 24px;
  background: rgba(15, 15, 25, 0.95);
  border-bottom: 1px solid rgba(0, 255, 255, 0.2);
}

.header-left, .header-right { display: flex; align-items: center; gap: 16px; }
.back-btn { color: #00ffff; text-decoration: none; font-size: 0.85rem; padding: 6px 12px; border: 1px solid rgba(0, 255, 255, 0.3); border-radius: 6px; }
.back-btn:hover { background: rgba(0, 255, 255, 0.1); }
.header-divider { width: 1px; height: 24px; background: rgba(0, 255, 255, 0.2); }
.page-title { font-size: 1.1rem; color: #00ffff; }
.score-info { font-size: 0.85rem; color: #888; }
.score-info strong { color: #00ff88; font-size: 1rem; }

.game-main { max-width: 1100px; margin: 0 auto; padding: 16px; }

.game-intro { padding: 12px 16px; background: rgba(0, 20, 40, 0.6); border: 1px solid rgba(0, 255, 255, 0.15); border-radius: 10px; margin-bottom: 16px; }
.game-intro h2 { color: #00ffff; font-size: 0.95rem; margin-bottom: 6px; }
.game-intro p { color: #aaa; font-size: 0.8rem; line-height: 1.5; }
.game-intro strong { color: #ff6b00; }

.game-area { display: flex; gap: 16px; margin-bottom: 16px; }
.canvas-wrapper { flex: 1; position: relative; border: 2px solid rgba(0, 255, 255, 0.2); border-radius: 12px; overflow: hidden; }
canvas { display: block; width: 100%; }

.overlay { position: absolute; inset: 0; background: rgba(0, 0, 0, 0.85); display: flex; align-items: center; justify-content: center; }
.overlay-box { text-align: center; padding: 30px; }
.overlay-icon { font-size: 3rem; }
.overlay-box h2 { color: #00ffff; margin: 10px 0; }
.overlay-box p { color: #aaa; font-size: 0.9rem; margin-bottom: 15px; }
.final-score { color: #00ff88; font-size: 1.5rem; font-weight: bold; }
.start-btn { padding: 12px 30px; background: linear-gradient(135deg, #00aaff, #00ffff); border: none; border-radius: 8px; color: #000; font-size: 1rem; font-weight: bold; cursor: pointer; }
.start-btn:hover { transform: scale(1.05); box-shadow: 0 0 20px rgba(0, 255, 255, 0.5); }

.controls { display: flex; flex-direction: column; gap: 10px; width: 160px; }
.ctrl-btn { display: flex; flex-direction: column; align-items: center; gap: 4px; padding: 14px 10px; background: rgba(0, 30, 50, 0.5); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 10px; cursor: pointer; transition: all 0.2s; user-select: none; }
.ctrl-btn:hover { border-color: rgba(255, 255, 255, 0.3); }
.ctrl-icon { font-size: 1.8rem; }
.ctrl-text { font-size: 0.75rem; color: #ccc; font-weight: bold; }
.ctrl-arrow { font-size: 0.7rem; color: #888; }
.up-btn.active { background: rgba(0, 170, 255, 0.2); border-color: #00aaff; box-shadow: 0 0 20px rgba(0, 170, 255, 0.4); }
.down-btn.active { background: rgba(255, 107, 0, 0.2); border-color: #ff6b00; box-shadow: 0 0 20px rgba(255, 107, 0, 0.4); }

.signal-box { padding: 10px; background: rgba(0, 20, 40, 0.6); border: 1px solid rgba(0, 255, 255, 0.15); border-radius: 8px; text-align: center; }
.signal-label { font-size: 0.65rem; color: #888; margin-bottom: 6px; }
.signal-bar { height: 12px; background: rgba(255, 255, 255, 0.05); border-radius: 6px; overflow: hidden; margin-bottom: 4px; }
.signal-fill { height: 100%; background: linear-gradient(90deg, #00aaff, #00ff88); border-radius: 6px; transition: width 0.3s; }
.signal-percent { font-size: 0.7rem; color: #00ffff; font-weight: bold; }

.side-info { display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; }
.info-card { background: rgba(0, 20, 40, 0.6); border: 1px solid rgba(0, 255, 255, 0.15); border-radius: 10px; padding: 12px; }
.info-card h4 { color: #00ffff; font-size: 0.75rem; margin-bottom: 8px; }
.info-card.tip { border-color: rgba(255, 170, 0, 0.3); }
.info-card.tip p { font-size: 0.7rem; color: #aaa; line-height: 1.5; }
.info-card.tip strong { color: #ff6b00; }

.eeg-canvas { width: 100%; border-radius: 6px; display: block; }
.eeg-legend { display: flex; justify-content: space-around; margin-top: 4px; font-size: 0.6rem; }
.ch3 { color: #00aaff; }
.ch4 { color: #ff6b00; }

.class-row { display: flex; align-items: center; gap: 6px; margin-bottom: 6px; font-size: 0.65rem; color: #888; }
.class-bar { flex: 1; height: 8px; background: rgba(255, 255, 255, 0.05); border-radius: 4px; overflow: hidden; }
.class-fill-up { height: 100%; background: #00aaff; border-radius: 4px; transition: width 0.3s; }
.class-fill-down { height: 100%; background: #ff6b00; border-radius: 4px; transition: width 0.3s; }

@media (max-width: 900px) {
  .game-area { flex-direction: column; }
  .controls { flex-direction: row; width: 100%; }
  .side-info { grid-template-columns: 1fr; }
}
</style>
