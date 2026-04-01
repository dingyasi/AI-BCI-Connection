<template>
  <div class="app-container" @click="handlePageClick" @keydown="handleKeydown" tabindex="0">
    <canvas ref="neuralCanvas" class="neural-canvas"></canvas>
    
    <!-- 着陆页 -->
    <div class="landing-page" :class="{ 'transitioning': showMainApp }">
      <!-- 3D Brain -->
      <div class="landing-center">
        <Brain3D class="brain-3d-component" @brain-click="handleBrainClick" />
      </div>
      
      <!-- 着陆页覆盖层 -->
      <div class="landing-overlay" :class="{ 'fade-out': showMainApp }">
        <p class="landing-desc">连接思维，探索未来</p>
        
        <button class="enter-btn" @click="enterMainApp">
          <span class="btn-text">进入脑机接口的世界</span>
        </button>
      </div>
    </div>

    <!-- 主应用 -->
    <div class="main-app" :class="{ 'active': showMainApp }">
      <!-- 背景 -->
      <div class="main-app-bg">
        <div class="brain-waves"></div>
        <div class="grid-overlay"></div>
      </div>
      
      <!-- 头部导航 -->
      <header class="header">
        <div class="logo">
          <span class="logo-icon">⚡</span>
          <span class="logo-text">脑电<span class="highlight">神经</span>接口</span>
        </div>
        <div class="status-indicator">
          <span class="pulse"></span>
          <span>系统在线</span>
        </div>
      </header>

      <!-- 主内容区域 -->
      <main class="main-content">
        <!-- 左侧脑活动面板 -->
        <div class="eeg-panel">
          <h2 class="panel-title">
            <span class="icon">◈</span>
            脑活动分析
          </h2>
          
          <div class="eeg-content">
            <BCIMotionAnalyzer 
              :motor-imagery="currentMotorImagery"
              @brain-pulse="handleBrainPulse"
            />
          </div>
        </div>

        <!-- 右侧3D大脑模型 -->
        <div class="brain-panel" ref="brainPanelRef">
          <div class="brain-pulse-effect" :class="[pulseRegion, { active: showPulse }]"></div>
          <Brain3D class="brain-3d" @brain-click="handleBrainClick" />
        </div>
      </main>

      <!-- 功能按钮组 -->
      <div class="fab-group">
        <!-- 脑电小游戏 -->
        <router-link to="/brain-game" class="fab-btn game-fab">
          <div class="fab-icon">🎮</div>
          <span class="fab-label">脑电游戏</span>
        </router-link>
        
        <!-- BCI发展史按钮 -->
        <div class="fab-btn timeline-fab" @click="toggleTimelinePanel" :class="{ active: showTimelinePanel }">
          <div class="fab-icon">📅</div>
          <span class="fab-label">BCI历史</span>
        </div>
        
        <!-- 脑科学普按钮 -->
        <div class="fab-btn region-fab" @click="toggleRegionPanel" :class="{ active: showRegionPanel }">
          <div class="fab-icon">🧠</div>
          <span class="fab-label">脑科学普</span>
        </div>
        
        <!-- AI专家助手按钮 -->
        <div class="fab-btn ai-fab" @click="toggleAIPanel" :class="{ active: showAIPanel }">
          <div class="fab-icon">🤖</div>
          <span class="fab-label">AI助手</span>
        </div>
      </div>
      
      <!-- 脑区域科普面板 -->
      <div v-if="showRegionPanel" class="region-panel-popup">
        <BrainRegionExplainer />
      </div>
      
      <!-- BCI发展史时间线面板 -->
      <div v-if="showTimelinePanel" class="timeline-panel-popup">
        <BCITimeline />
      </div>

      <!-- AI专家面板 - 弹出式 -->
      <div v-if="showAIPanel" class="ai-panel-popup">
        <div class="ai-panel-header">
          <span>◈ AI专家助手</span>
          <button class="close-btn" @click="showAIPanel = false">✕</button>
        </div>
        
        <div class="chat-container" ref="chatContainer">
          <div v-for="(msg, idx) in messages" :key="idx" 
               :class="['message', msg.role]">
            <div class="message-role">{{ msg.role === 'user' ? '◉ 用户' : '◈ AI专家' }}</div>
            <div class="message-content" v-html="formatMarkdown(msg.content)"></div>
          </div>
          <div v-if="loading" class="message assistant">
            <div class="message-role">◈ AI专家</div>
            <div class="message-content loading">
              <span class="dot"></span>
              <span class="dot"></span>
              <span class="dot"></span>
            </div>
          </div>
        </div>

        <div class="input-area">
          <el-input
            v-model="question"
            type="textarea"
            :rows="2"
            placeholder="询问关于Hopfield网络、PCA降维、脑电预处理等问题..."
            @keyup.enter.ctrl="sendQuestion"
            :disabled="loading"
          />
          <el-button 
            type="primary" 
            :loading="loading" 
            @click="sendQuestion" 
            class="send-btn"
            title="发送 (Ctrl+Enter)"
          >
            发送
          </el-button>
        </div>
      </div>

      <footer class="footer">
        <span>BCI脑机接口系统 v1.0 | 神经接口已激活</span>
      </footer>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, nextTick, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import axios from 'axios'
import Brain3D from '../components/Brain3D.vue'
import BCIMotionAnalyzer from '../components/BCIMotionAnalyzer.vue'
import BrainRegionExplainer from '../components/BrainRegionExplainer.vue'
import BCITimeline from '../components/BCITimeline.vue'

const fileInput = ref<HTMLInputElement>()
const chatContainer = ref<HTMLElement>()
const bciChatContainer = ref<HTMLElement>()
const neuralCanvas = ref<HTMLCanvasElement>()

interface NeuralNode {
  x: number
  y: number
  vx: number
  vy: number
  life: number
  maxLife: number
  connections: number[]
}

interface NeuralLink {
  x1: number
  y1: number
  x2: number
  y2: number
  life: number
}

const neuralNodes = ref<NeuralNode[]>([])
const neuralLinks = ref<NeuralLink[]>([])
const clickEffects = ref<Array<{x: number, y: number, time: number}>>([])
const showMainApp = ref(false)
const showAIPanel = ref(false)
const showRegionPanel = ref(false)
const showTimelinePanel = ref(false)
const showPulse = ref(false)
const pulseRegion = ref('')
const currentMotorImagery = ref<'left' | 'right' | 'foot' | null>(null)

const preprocessEnabled = ref(true)
const pcaDimensions = ref(16)
const maxIterations = ref(1000)
const selectedSubject = ref<string>('S001')
const training = ref(false)
const trainingResult = ref<{accuracy: number, iterations: number, energy: number} | null>(null)

const question = ref('')
const loading = ref(false)
const listening = ref(false)
const isSpeaking = ref(false)
const voiceOutputEnabled = ref(false)
let recognition: any = null
let synthesis: any = null

const messages = ref<Array<{role: string, content: string}>>([
  { role: 'assistant', content: '神经接口已在线。\n\n我是**脑电信号处理专家**，基于Hopfield神经网络的BCI模式识别系统。\n\n📊 **模型概况**：\n• 被试数：**109** (BCI Competition IV Dataset 2a)\n• 分类准确率：**85.6%**\n• PCA降维：**16维**\n• 预处理：陷波50Hz + 带通8-30Hz + Z-score\n\n可以为您解答：\n• *Hopfield网络*Hebb学习规则\n• *PCA主成分分析*降维方法\n• *ERD/ERS*运动想象特征\n• *混淆矩阵*结果分析\n\n有什么可以帮您的？' }
])

onMounted(() => {
  console.log('脑电神经接口已加载')
  initNeuralCanvas()
  
  if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
    const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition
    recognition = new SpeechRecognition()
    recognition.continuous = false
    recognition.interimResults = true
    recognition.lang = 'zh-CN'
    
    recognition.onresult = (event: any) => {
      const transcript = Array.from(event.results)
        .map((r: any) => r[0].transcript)
        .join('')
      question.value = transcript
      if (event.results[0].isFinal) {
        sendQuestion()
      }
    }
    
    recognition.onerror = () => {
      listening.value = false
    }
    
    recognition.onend = () => {
      listening.value = false
    }
  }
  
  if ('speechSynthesis' in window) {
    synthesis = window.speechSynthesis
  }
})

const toggleVoice = () => {
  if (!recognition) {
    ElMessage.warning('您的浏览器不支持语音识别')
    return
  }
  
  if (listening.value) {
    recognition.stop()
    listening.value = false
  } else {
    question.value = ''
    recognition.start()
    listening.value = true
  }
}

const speak = (text: string) => {
  if (!synthesis || !voiceOutputEnabled.value) return
  
  synthesis.cancel()
  const utterance = new SpeechSynthesisUtterance(text)
  utterance.lang = 'zh-CN'
  utterance.rate = 1.0
  utterance.pitch = 1.0
  
  utterance.onstart = () => { isSpeaking.value = true }
  utterance.onend = () => { isSpeaking.value = false }
  utterance.onerror = () => { isSpeaking.value = false }
  
  synthesis.speak(utterance)
}

const toggleVoiceOutput = () => {
  voiceOutputEnabled.value = !voiceOutputEnabled.value
  if (voiceOutputEnabled.value) {
    ElMessage.success('语音播报已开启')
  } else {
    synthesis?.cancel()
    ElMessage.info('语音播报已关闭')
  }
}

const initNeuralCanvas = () => {
  const canvas = neuralCanvas.value
  if (!canvas) return
  
  const ctx = canvas.getContext('2d')
  if (!ctx) return
  
  const resize = () => {
    canvas.width = window.innerWidth
    canvas.height = window.innerHeight
  }
  resize()
  window.addEventListener('resize', resize)
  
  for (let i = 0; i < 50; i++) {
    neuralNodes.value.push({
      x: Math.random() * canvas.width,
      y: Math.random() * canvas.height,
      vx: (Math.random() - 0.5) * 0.5,
      vy: (Math.random() - 0.5) * 0.5,
      life: Math.random() * 200 + 100,
      maxLife: 300,
      connections: []
    })
  }
  
  const animate = () => {
    if (!ctx || !canvas) return
    
    ctx.clearRect(0, 0, canvas.width, canvas.height)
    
    neuralNodes.value.forEach((node, i) => {
      node.x += node.vx
      node.y += node.vy
      node.life--
      
      if (node.x < 0 || node.x > canvas.width) node.vx *= -1
      if (node.y < 0 || node.y > canvas.height) node.vy *= -1
      if (node.life <= 0) {
        node.x = Math.random() * canvas.width
        node.y = Math.random() * canvas.height
        node.life = node.maxLife
      }
      
      const alpha = Math.min(1, node.life / 100)
      ctx.beginPath()
      ctx.arc(node.x, node.y, 3, 0, Math.PI * 2)
      ctx.fillStyle = `rgba(255, 107, 0, ${alpha})`
      ctx.fill()
      
      neuralNodes.value.forEach((other, j) => {
        if (i >= j) return
        const dx = node.x - other.x
        const dy = node.y - other.y
        const dist = Math.sqrt(dx * dx + dy * dy)
        if (dist < 150) {
          const linkAlpha = (1 - dist / 150) * 0.3 * Math.min(alpha, Math.min(1, other.life / 100))
          ctx.beginPath()
          ctx.moveTo(node.x, node.y)
          ctx.lineTo(other.x, other.y)
          ctx.strokeStyle = `rgba(255, 107, 0, ${linkAlpha})`
          ctx.lineWidth = 1
          ctx.stroke()
        }
      })
    })
    
    clickEffects.value = clickEffects.value.filter(effect => {
      const age = Date.now() - effect.time
      if (age > 2000) return false
      
      const progress = age / 2000
      const radius = progress * 200
      const alpha = 1 - progress
      
      ctx.beginPath()
      ctx.arc(effect.x, effect.y, radius, 0, Math.PI * 2)
      ctx.strokeStyle = `rgba(255, 107, 0, ${alpha})`
      ctx.lineWidth = 2 - progress * 2
      ctx.stroke()
      
      for (let i = 0; i < 8; i++) {
        const angle = (i / 8) * Math.PI * 2 + progress * Math.PI
        const particleX = effect.x + Math.cos(angle) * radius
        const particleY = effect.y + Math.sin(angle) * radius
        
        ctx.beginPath()
        ctx.arc(particleX, particleY, 3 - progress * 3, 0, Math.PI * 2)
        ctx.fillStyle = `rgba(255, 200, 0, ${alpha})`
        ctx.fill()
      }
      
      return true
    })
    
    requestAnimationFrame(animate)
  }
  animate()
}

const handlePageClick = (e: MouseEvent) => {
  if (!showMainApp.value) return
  
  clickEffects.value.push({
    x: e.clientX,
    y: e.clientY,
    time: Date.now()
  })
  
  const canvas = neuralCanvas.value
  if (!canvas) return
  
  for (let i = 0; i < 10; i++) {
    const angle = Math.random() * Math.PI * 2
    const speed = Math.random() * 3 + 2
    neuralNodes.value.push({
      x: e.clientX,
      y: e.clientY,
      vx: Math.cos(angle) * speed,
      vy: Math.sin(angle) * speed,
      life: 100 + Math.random() * 50,
      maxLife: 150,
      connections: []
    })
  }
  
  if (neuralNodes.value.length > 100) {
    neuralNodes.value = neuralNodes.value.slice(-100)
  }
}

const enterMainApp = () => {
  showMainApp.value = true
  nextTick(() => {
    window.scrollTo({ top: 0, behavior: 'smooth' })
  })
}

const toggleAIPanel = () => {
  showAIPanel.value = !showAIPanel.value
  showRegionPanel.value = false
}

const toggleRegionPanel = () => {
  showRegionPanel.value = !showRegionPanel.value
  showAIPanel.value = false
  showTimelinePanel.value = false
}

const toggleTimelinePanel = () => {
  showTimelinePanel.value = !showTimelinePanel.value
  showAIPanel.value = false
  showRegionPanel.value = false
}

const handleBrainClick = () => {
  ElMessage.info('神经元已激活')
}

const handleTaskChange = (task: 'left' | 'right' | 'foot' | null) => {
  currentMotorImagery.value = task
  if (task) {
    const taskNames = { left: '左手', right: '右手', foot: '双脚' }
    ElMessage.info(`运动想象: ${taskNames[task]}`)
  }
}

// 处理脑活动地形图发送的脉冲 - CSS视觉效果
const handleBrainPulse = (region: 'left' | 'center' | 'right', intensity: number) => {
  // 设置脉冲区域和显示
  pulseRegion.value = region
  showPulse.value = true
  
  // 触发动画
  setTimeout(() => {
    showPulse.value = false
  }, 800)
}

const handleKeydown = (e: KeyboardEvent) => {
  // Global keyboard shortcuts
  switch (e.key) {
    case ' ':
      e.preventDefault()
      break
    case 'h':
    case 'H':
      // Toggle help
      break
  }
}

const triggerUpload = () => {
  fileInput.value?.click()
}

const handleFileSelect = (e: Event) => {
  const target = e.target as HTMLInputElement
  if (target.files?.length) {
    ElMessage.success(`已选择: ${target.files[0].name}`)
  }
}

const handleDrop = (e: DragEvent) => {
  if (e.dataTransfer?.files.length) {
    ElMessage.success(`已拖入: ${e.dataTransfer.files[0].name}`)
  }
}

const startTraining = async () => {
  training.value = true
  ElMessage.info('正在初始化Hopfield网络训练...')
  
  try {
    const res = await axios.post('/api/v1/train/train', {
      subject_id: selectedSubject.value || 'S001',
      n_components: pcaDimensions.value,
      max_iterations: maxIterations.value
    })
    
    trainingResult.value = {
      accuracy: res.data.accuracy,
      iterations: res.data.iterations,
      energy: res.data.energy
    }
    ElMessage.success(`训练完成！准确率: ${res.data.accuracy}%`)
  } catch (err: any) {
    ElMessage.error('训练失败: ' + (err.message || '未知错误'))
  } finally {
    training.value = false
  }
}

const sendQuestion = async () => {
  if (!question.value.trim() || loading.value) return
  
  const q = question.value.trim()
  messages.value.push({ role: 'user', content: q })
  
  messages.value.push({ role: 'assistant', content: '正在思考...' })
  const msgIndex = messages.value.length - 1
  
  question.value = ''
  loading.value = true
  
  await nextTick()
  scrollToBottom()
  
  try {
    const response = await fetch('/api/v1/agent/qa', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        question: q,
        context: trainingResult.value ? JSON.stringify(trainingResult.value) : null
      })
    })
    
    if (!response.ok) {
      messages.value[msgIndex].content = '请求失败: ' + response.status
      return
    }
    
    const reader = response.body?.getReader()
    if (!reader) {
      messages.value[msgIndex].content = '无法读取响应'
      return
    }
    
    const decoder = new TextDecoder()
    let buffer = ''
    
    while (true) {
      const { done, value } = await reader.read()
      if (done) break
      
      buffer += decoder.decode(value, { stream: true })
      
      const lines = buffer.split('\n')
      buffer = lines.pop() || ''
      
      for (const line of lines) {
        if (line.startsWith('data: ')) {
          const dataStr = line.slice(6).trim()
          if (dataStr === '[DONE]' || !dataStr) continue
          
            try {
            const data = JSON.parse(dataStr)
            const content = data?.choices?.[0]?.delta?.content
            if (content) {
              messages.value[msgIndex].content += content
              await nextTick()
              scrollToBottom()
              await new Promise(r => setTimeout(r, 10))
            }
          } catch {
            messages.value[msgIndex].content += dataStr
            await nextTick()
            scrollToBottom()
            await new Promise(r => setTimeout(r, 10))
          }
        }
      }
    }
  } catch (err: any) {
    console.error('错误:', err)
    messages.value[msgIndex].content = '错误: ' + err.message
  } finally {
    loading.value = false
    await nextTick()
    scrollToBottom()
  }
}

const scrollToBottom = async () => {
  await nextTick()
  if (chatContainer.value) {
    chatContainer.value.scrollTop = chatContainer.value.scrollHeight
  }
}

const formatMarkdown = (text: string) => {
  if (!text) return ''
  
  // Escape HTML to prevent XSS
  let html = text
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
  
  // Remove markdown headers (# symbols) - convert to styled text
  html = html.replace(/^#{1,6}\s+(.+)$/gm, '<div style="color:#00ffff;font-weight:bold;font-size:1.1em;margin:12px 0 6px 0;">$1</div>')
  
  // Convert LaTeX formulas to styled text
  // Inline math: \( ... \) or $...$
  html = html.replace(/\\\((.*?)\\\)/g, '<span style="color:#00ffff;font-family:monospace;background:rgba(0,255,255,0.1);padding:2px 4px;border-radius:3px;">$1</span>')
  html = html.replace(/\$([^$]+)\$/g, '<span style="color:#00ffff;font-family:monospace;background:rgba(0,255,255,0.1);padding:2px 4px;border-radius:3px;">$1</span>')
  
  // Block math: $$...$$
  html = html.replace(/\$\$([\s\S]*?)\$\$/g, '<div style="color:#00ffff;font-family:monospace;margin:8px 0;padding:10px;background:rgba(0,255,255,0.1);border-radius:4px;border-left:3px solid #00ffff;">$1</div>')
  
  // Convert markdown bold: **text**
  html = html.replace(/\*\*(.*?)\*\*/g, '<strong style="color:#ff6b00;font-weight:600;">$1</strong>')
  
  // Convert markdown italic: *text*
  html = html.replace(/(?<!\*)\*([^*]+)\*(?!\*)/g, '<em>$1</em>')
  
  // Convert code blocks
  html = html.replace(/```(\w+)?\n([\s\S]*?)```/g, '<pre style="background:rgba(0,0,0,0.3);padding:10px;border-radius:4px;overflow-x:auto;margin:8px 0;"><code>$2</code></pre>')
  html = html.replace(/`([^`]+)`/g, '<code style="background:rgba(255,107,0,0.2);padding:2px 6px;border-radius:3px;font-family:monospace;font-size:0.9em;">$1</code>')
  
  // Process line by line for better formatting
  const lines = html.split('\n')
  let result = '<div style="padding:4px 0;line-height:1.8;font-size:0.8em;">'
  
  for (let i = 0; i < lines.length; i++) {
    let line = lines[i].trim()
    
    // Skip empty lines but add spacing
    if (!line) {
      result += '<div style="height:8px;"></div>'
      continue
    }
    
    // Already processed headers (now contain div tags)
    if (line.includes('<div style="color:#00ffff;font-weight:bold')) {
      result += line
      continue
    }
    
    // Numbered list
    if (line.match(/^\d+[\.\、]\s/) || line.match(/^[一二三四五六七八九十]+[\.\、]\s/)) {
      result += `<div style="margin:6px 0;padding-left:12px;border-left:2px solid #00ffff;background:rgba(0,255,255,0.05);padding:6px 12px;border-radius:0 4px 4px 0;"><span style="color:#00ffff;font-weight:600;">${line}</span></div>`
    } else if (line.match(/^[-•●]\s/)) {
      // Bullet point
      const content = line.replace(/^[-•●]\s/, '')
      result += `<div style="margin:4px 0;padding-left:16px;"><span style="color:#00ffff;margin-right:6px;">●</span><span style="color:#ddd;">${content}</span></div>`
    } else if (line.match(/^[a-zA-Z]\)\s/) || line.match(/^[①-⑩]\s/)) {
      // Lettered list
      result += `<div style="margin:4px 0;padding-left:16px;"><span style="color:#ffaa00;">${line.substring(0, 2)}</span><span style="color:#ddd;margin-left:4px;">${line.substring(2)}</span></div>`
    } else if (line.length > 50) {
      // Long paragraph
      result += `<div style="margin:6px 0;color:#ddd;line-height:1.6;">${line}</div>`
    } else {
      // Short text / title
      result += `<div style="margin:4px 0;color:#eee;">${line}</div>`
    }
  }
  
  result += '</div>'
  return result
}
</script>

<style>
:root {
  --primary: #ff6b00;
  --primary-dark: #cc5500;
  --primary-glow: rgba(255, 107, 0, 0.4);
  --bg-dark: #0a0a0f;
  --bg-panel: rgba(15, 15, 25, 0.9);
  --border-color: rgba(255, 107, 0, 0.3);
  --text-primary: #e0e0e0;
  --text-secondary: #888;
}

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html, body {
  width: 100%;
  min-height: 100%;
  overflow-x: hidden;
}

body {
  font-family: 'Microsoft YaHei', 'PingFang SC', 'Segoe UI', sans-serif;
  background: var(--bg-dark);
  color: var(--text-primary);
}

.app-container {
  width: 100%;
  min-height: 100vh;
  position: relative;
  overflow-x: hidden;
  cursor: crosshair;
}

.neural-canvas {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 2;
}

/* 主应用 */
.main-app {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 5;
  opacity: 0;
  visibility: hidden;
  pointer-events: none;
  transition: opacity 1s ease 0.5s, visibility 1s ease 0.5s, z-index 0s 1.5s;
}

.main-app.active {
  z-index: 15;
  opacity: 1;
  visibility: visible;
  pointer-events: auto;
  transition: opacity 1s ease 0.5s, visibility 1s ease 0.5s, z-index 0s 0s;
}

/* 主应用背景 */
.main-app-bg {
  position: absolute;
  inset: 0;
  background: var(--bg-dark);
  z-index: 0;
}

/* 头部导航 */
.header {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 20px;
  background: linear-gradient(180deg, rgba(15, 15, 25, 0.98) 0%, rgba(15, 15, 25, 0.92) 100%);
  border-bottom: 1px solid var(--border-color);
  z-index: 100;
  backdrop-filter: blur(15px);
  box-shadow: 0 2px 20px rgba(0, 0, 0, 0.3);
}

.header::after {
  content: '';
  position: absolute;
  bottom: -1px;
  left: 0;
  right: 0;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(0, 255, 255, 0.5), rgba(255, 107, 0, 0.5), transparent);
  animation: header-glow 3s ease-in-out infinite;
}

@keyframes header-glow {
  0%, 100% { opacity: 0.5; }
  50% { opacity: 1; }
}

/* 主内容 */
.main-content {
  position: absolute;
  top: 60px;
  left: 0;
  right: 0;
  bottom: 40px;
  display: flex;
  gap: 20px;
  padding: 20px;
}

/* 左侧脑电面板 */
.eeg-panel {
  width: 380px;
  flex-shrink: 0;
  background: linear-gradient(180deg, rgba(15, 15, 25, 0.95) 0%, rgba(10, 10, 18, 0.98) 100%);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 15px;
  display: flex;
  flex-direction: column;
  backdrop-filter: blur(10px);
  animation: slideInLeft 0.8s ease 1s both;
  box-shadow: 0 4px 30px rgba(0, 0, 0, 0.3), inset 0 1px 0 rgba(255, 255, 255, 0.05);
  position: relative;
  overflow: hidden;
}

.eeg-panel::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 2px;
  background: linear-gradient(90deg, transparent, #00ffff, transparent);
  opacity: 0.5;
}

@keyframes slideInLeft {
  from {
    opacity: 0;
    transform: translateX(-50px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

.eeg-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 15px;
  overflow-y: auto;
  overflow-x: hidden;
  padding-right: 5px;
}

/* 右侧3D大脑面板 */
.brain-panel {
  flex: 1;
  background: linear-gradient(180deg, rgba(15, 15, 25, 0.95) 0%, rgba(10, 10, 18, 0.98) 100%);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  overflow: hidden;
  animation: fadeIn 0.8s ease 1.2s both;
  position: relative;
  box-shadow: 0 4px 30px rgba(0, 0, 0, 0.3), inset 0 1px 0 rgba(255, 255, 255, 0.05);
}

.brain-panel::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 2px;
  background: linear-gradient(90deg, transparent, #ff6b00, transparent);
  opacity: 0.5;
  z-index: 1;
}

/* 脉冲效果覆盖层 */
.brain-pulse-effect {
  position: absolute;
  inset: 0;
  pointer-events: none;
  z-index: 10;
  border-radius: 12px;
  opacity: 0;
  transition: opacity 0.1s;
}

.brain-pulse-effect.active {
  opacity: 1;
  animation: pulse-flash 0.8s ease-out;
}

.brain-pulse-effect.left.active {
  box-shadow: inset 0 0 80px 40px rgba(0, 170, 255, 0.7),
              inset 0 0 120px 60px rgba(0, 170, 255, 0.4),
              0 0 40px rgba(0, 170, 255, 0.5);
  border: 2px solid rgba(0, 170, 255, 0.8);
}

.brain-pulse-effect.right.active {
  box-shadow: inset 0 0 80px 40px rgba(255, 107, 0, 0.7),
              inset 0 0 120px 60px rgba(255, 107, 0, 0.4),
              0 0 40px rgba(255, 107, 0, 0.5);
  border: 2px solid rgba(255, 107, 0, 0.8);
}

.brain-pulse-effect.center.active {
  box-shadow: inset 0 0 80px 40px rgba(0, 255, 136, 0.7),
              inset 0 0 120px 60px rgba(0, 255, 136, 0.4),
              0 0 40px rgba(0, 255, 136, 0.5);
  border: 2px solid rgba(0, 255, 136, 0.8);
}

@keyframes pulse-flash {
  0% {
    opacity: 1;
    transform: scale(1);
  }
  50% {
    opacity: 0.8;
  }
  100% {
    opacity: 0;
    transform: scale(1.02);
  }
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

/* 着陆页 - 原始样式 */
.landing-page {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 10;
  display: flex;
  overflow: hidden;
  background: 
    repeating-linear-gradient(
      0deg,
      transparent,
      transparent 2px,
      rgba(0, 255, 255, 0.03) 2px,
      rgba(0, 255, 255, 0.03) 4px
    ),
    radial-gradient(ellipse at 50% 30%, rgba(0, 255, 255, 0.1) 0%, transparent 50%),
    radial-gradient(ellipse at 20% 80%, rgba(255, 107, 0, 0.15) 0%, transparent 50%),
    radial-gradient(ellipse at 80% 80%, rgba(255, 107, 0, 0.1) 0%, transparent 50%);
  transition: opacity 1s ease, transform 1s ease, pointer-events 0s 1s;
}

.landing-page::after {
  content: '';
  position: absolute;
  inset: 0;
  background: 
    radial-gradient(circle at 30% 40%, rgba(0, 255, 255, 0.05) 0%, transparent 50%),
    radial-gradient(circle at 70% 60%, rgba(255, 107, 0, 0.05) 0%, transparent 50%);
  animation: float-glow 10s ease-in-out infinite;
  pointer-events: none;
}

@keyframes float-glow {
  0%, 100% { transform: translate(0, 0) scale(1); }
  33% { transform: translate(20px, -20px) scale(1.05); }
  66% { transform: translate(-20px, 20px) scale(0.95); }
}

.landing-page.transitioning {
  opacity: 0;
  transform: scale(1.1);
  pointer-events: none;
}

.landing-page::before {
  content: '';
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(
    180deg,
    transparent 0%,
    rgba(0, 255, 255, 0.02) 50%,
    transparent 100%
  );
  animation: scan-line 8s linear infinite;
  pointer-events: none;
  z-index: 1;
}

@keyframes scan-line {
  from { transform: translateY(-100%); }
  to { transform: translateY(100%); }
}

/* 着陆页中心 */
.landing-center {
  flex: 1;
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
}

.brain-3d-component {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 2;
}

/* 着陆页覆盖层 */
.landing-overlay {
  position: absolute;
  bottom: 80px;
  left: 50%;
  transform: translateX(-50%);
  text-align: center;
  z-index: 20;
  transition: opacity 0.6s ease;
  pointer-events: auto;
}

.landing-overlay.fade-out {
  opacity: 0;
  pointer-events: none;
}

.landing-desc {
  font-size: 1.1rem;
  color: rgba(0, 255, 255, 0.9);
  margin-bottom: 25px;
  letter-spacing: 4px;
  font-family: 'Microsoft YaHei', sans-serif;
  text-shadow: 0 0 20px rgba(0, 255, 255, 0.5);
}





.landing-desc {
  font-size: 1.2rem;
  color: rgba(0, 255, 255, 0.9);
  margin-bottom: 30px;
  letter-spacing: 4px;
  font-family: 'Microsoft YaHei', sans-serif;
  text-shadow: 0 0 20px rgba(0, 255, 255, 0.5);
}

.enter-btn {
  position: relative;
  padding: 14px 40px;
  font-size: 1rem;
  font-weight: 600;
  color: #fff;
  background: linear-gradient(135deg, rgba(0, 80, 100, 0.8), rgba(0, 150, 180, 0.9));
  border: 1px solid rgba(0, 255, 255, 0.6);
  border-radius: 30px;
  cursor: pointer;
  overflow: hidden;
  transition: all 0.3s ease;
  letter-spacing: 2px;
  font-family: 'Microsoft YaHei', sans-serif;
  box-shadow: 
    0 0 15px rgba(0, 255, 255, 0.3),
    inset 0 0 15px rgba(0, 255, 255, 0.1);
  backdrop-filter: blur(5px);
}

.enter-btn:hover {
  transform: scale(1.05);
  box-shadow: 
    0 0 25px rgba(0, 255, 255, 0.5),
    0 0 50px rgba(0, 255, 255, 0.2),
    inset 0 0 20px rgba(0, 255, 255, 0.2);
  background: linear-gradient(135deg, rgba(0, 100, 120, 0.9), rgba(0, 180, 210, 1));
  border-color: rgba(0, 255, 255, 0.9);
}

.enter-btn::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
  transition: left 0.5s;
}

.enter-btn:hover::before {
  left: 100%;
}

.enter-btn .btn-text {
  position: relative;
  z-index: 1;
}

/* 背景动画 */
.brain-waves {
  position: absolute;
  inset: 0;
  background: 
    repeating-linear-gradient(
      0deg,
      transparent,
      transparent 2px,
      rgba(255, 107, 0, 0.03) 2px,
      rgba(255, 107, 0, 0.03) 4px
    );
  animation: scan 8s linear infinite;
}

@keyframes scan {
  from { transform: translateY(0); }
  to { transform: translateY(100px); }
}

.grid-overlay {
  position: absolute;
  inset: 0;
  background-image: 
    linear-gradient(rgba(255, 107, 0, 0.05) 1px, transparent 1px),
    linear-gradient(90deg, rgba(255, 107, 0, 0.05) 1px, transparent 1px);
  background-size: 50px 50px;
}

.logo {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 1.2rem;
  font-weight: 700;
}

.logo-icon {
  color: var(--primary);
  font-size: 1.5rem;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

.logo-text {
  letter-spacing: 2px;
}

.highlight {
  color: var(--primary);
}

.status-indicator {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.85rem;
  color: #4ade80;
}

.status-indicator .pulse {
  width: 8px;
  height: 8px;
  background: #4ade80;
  border-radius: 50%;
  animation: blink 1.5s infinite;
}

@keyframes blink {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.3; }
}

/* FAB按钮组 */
.fab-group {
  position: fixed;
  bottom: 30px;
  right: 30px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  z-index: 1000;
}

.fab-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 16px;
  border-radius: 30px;
  cursor: pointer;
  transition: all 0.3s;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
}

.timeline-fab {
  background: linear-gradient(135deg, #aa6600, #ffaa00);
  border: 1px solid rgba(255, 170, 0, 0.5);
}

.timeline-fab:hover, .timeline-fab.active {
  transform: scale(1.05);
  box-shadow: 0 6px 25px rgba(255, 170, 0, 0.5);
}

.region-fab {
  background: linear-gradient(135deg, #0066ff, #00aaff);
  border: 1px solid rgba(0, 255, 255, 0.5);
}

.region-fab:hover, .region-fab.active {
  transform: scale(1.05);
  box-shadow: 0 6px 25px rgba(0, 170, 255, 0.5);
}

.ai-fab {
  background: linear-gradient(135deg, #ff6b00, #ff8c00);
  border: 1px solid rgba(255, 140, 0, 0.5);
}

.ai-fab:hover, .ai-fab.active {
  transform: scale(1.05);
  box-shadow: 0 6px 25px rgba(255, 107, 0, 0.5);
}

.erd-fab {
  background: linear-gradient(135deg, #00aa66, #00ff88);
  border: 1px solid rgba(0, 255, 136, 0.5);
  text-decoration: none;
}

.erd-fab:hover {
  transform: scale(1.05);
  box-shadow: 0 6px 25px rgba(0, 255, 136, 0.5);
}

.game-fab {
  background: linear-gradient(135deg, #aa00ff, #ff00ff);
  border: 1px solid rgba(255, 0, 255, 0.5);
  text-decoration: none;
}

.game-fab:hover {
  transform: scale(1.05);
  box-shadow: 0 6px 25px rgba(255, 0, 255, 0.5);
}

.fab-icon {
  font-size: 1.3rem;
}

.fab-label {
  color: #fff;
  font-size: 0.75rem;
  font-weight: bold;
  white-space: nowrap;
}

/* 脑区域科普弹出面板 */
.region-panel-popup {
  position: fixed;
  bottom: 30px;
  right: 250px;
  width: 450px;
  height: 650px;
  background: var(--bg-panel);
  border: 1px solid rgba(0, 170, 255, 0.4);
  border-radius: 12px;
  z-index: 999;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.5);
  animation: slideIn 0.3s ease;
}

/* BCI发展史时间线面板 */
.timeline-panel-popup {
  position: fixed;
  bottom: 30px;
  right: 330px;
  width: 450px;
  height: 650px;
  background: var(--bg-panel);
  border: 1px solid rgba(255, 170, 0, 0.4);
  border-radius: 12px;
  z-index: 999;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.5);
  animation: slideInLeft 0.3s ease;
}

@keyframes slideInLeft {
  from {
    opacity: 0;
    transform: translateX(-20px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateX(20px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

/* AI专家弹出面板 */
.ai-panel-popup {
  position: fixed;
  bottom: 30px;
  right: 340px;
  width: 500px;
  height: 650px;
  background: var(--bg-panel);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  display: flex;
  flex-direction: column;
  backdrop-filter: blur(10px);
  z-index: 999;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.5);
  animation: slideInLeft 0.3s ease;
}

.ai-panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 15px;
  border-bottom: 1px solid var(--border-color);
  color: var(--primary);
  font-weight: 600;
}

.close-btn {
  background: none;
  border: none;
  color: var(--text-secondary);
  cursor: pointer;
  font-size: 1.2rem;
  padding: 5px;
  transition: color 0.2s;
}

.close-btn:hover {
  color: var(--primary);
}

.panel {
  background: var(--bg-panel);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 15px;
  display: flex;
  flex-direction: column;
  backdrop-filter: blur(10px);
  overflow: visible;
}

.panel-title {
  font-size: 1rem;
  color: var(--primary);
  margin-bottom: 15px;
  display: flex;
  align-items: center;
  gap: 8px;
  letter-spacing: 1px;
  border-bottom: 1px solid var(--border-color);
  padding-bottom: 10px;
  flex-shrink: 0;
}

.panel-title .icon {
  font-size: 1.2rem;
}





.chat-container {
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;
  padding: 10px;
  background: rgba(0, 0, 0, 0.3);
  margin: 10px;
  border-radius: 8px;
  scrollbar-width: thin;
  scrollbar-color: #ff6b00 #1a1a2e;
}

.message {
  margin-bottom: 12px;
  padding: 10px;
  border-radius: 8px;
}

.message.user {
  background: rgba(255, 107, 0, 0.15);
  margin-left: 15%;
}

.message.assistant {
  background: rgba(255, 107, 0, 0.08);
  margin-right: 15%;
  border: 1px solid var(--border-color);
}

.message-role {
  font-size: 0.6rem;
  color: var(--primary);
  margin-bottom: 4px;
  letter-spacing: 1px;
}

.message-content {
  line-height: 1.4;
  font-size: 0.75rem;
  color: #ddd;
  word-wrap: break-word;
  overflow-wrap: break-word;
  white-space: pre-wrap;
}

.message-content p {
  margin: 5px 0;
  padding: 0;
  display: inline;
}

.message-content code {
  background: rgba(255, 107, 0, 0.15);
  padding: 2px 6px;
  border-radius: 4px;
  font-family: 'Consolas', 'Monaco', monospace;
  font-size: 0.85em;
}

.message-content.loading {
  display: flex;
  gap: 5px;
}

.message-content.loading .dot {
  width: 7px;
  height: 7px;
  background: var(--primary);
  border-radius: 50%;
  animation: bounce 1.4s infinite ease-in-out;
}

.message-content.loading .dot:nth-child(1) { animation-delay: 0s; }
.message-content.loading .dot:nth-child(2) { animation-delay: 0.2s; }
.message-content.loading .dot:nth-child(3) { animation-delay: 0.4s; }

@keyframes bounce {
  0%, 80%, 100% { transform: scale(0.6); opacity: 0.5; }
  40% { transform: scale(1); opacity: 1; }
}

.input-area {
  display: flex;
  gap: 10px;
  flex-shrink: 0;
  padding: 10px;
  border-top: 1px solid var(--border-color);
}

.input-area .el-textarea {
  flex: 1;
}

.input-area :deep(.el-textarea__inner) {
  background: rgba(0, 0, 0, 0.5);
  border: 1px solid var(--border-color);
  color: var(--text-primary);
  border-radius: 6px;
}

.input-area :deep(.el-textarea__inner:focus) {
  border-color: var(--primary);
  box-shadow: 0 0 10px var(--primary-glow);
}

.send-btn {
  background: var(--primary);
  border: none;
  border-radius: 6px;
  font-weight: 700;
  letter-spacing: 1px;
  padding: 0 20px;
}

.send-btn:hover {
  background: var(--primary-dark);
  box-shadow: 0 0 15px var(--primary-glow);
}

.footer {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  text-align: center;
  padding: 10px;
  font-size: 0.75rem;
  color: var(--text-secondary);
  letter-spacing: 1px;
  background: var(--bg-panel);
  border-top: 1px solid var(--border-color);
  z-index: 100;
}

/* 滚动条美化 */
html {
  scrollbar-width: thin;
  scrollbar-color: #ff6b00 #1a1a2e;
}

::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

::-webkit-scrollbar-track {
  background: rgba(0, 0, 0, 0.2);
  border-radius: 3px;
}

::-webkit-scrollbar-thumb {
  background: var(--primary);
  border-radius: 3px;
}

::-webkit-scrollbar-thumb:hover {
  background: var(--primary-dark);
}

</style>
