<template>
  <div class="mi-simulator">
    <div class="simulator-header">
      <span class="sim-title">🎯 运动想象模拟</span>
      <span class="algo-badge">Hopfield网络</span>
    </div>
    
    <div class="mi-buttons">
      <button 
        v-for="task in tasks" 
        :key="task.id"
        class="mi-btn"
        :class="{ active: currentTask === task.id, [task.class]: true }"
        @click="selectTask(task.id)"
      >
        <span class="mi-icon">{{ task.icon }}</span>
        <span class="mi-label">{{ task.label }}</span>
        <span class="mi-region">{{ task.region }}</span>
      </button>
    </div>
    
    <div class="mi-info" v-if="currentTask">
      <div class="info-header">分类结果</div>
      <div class="result-bars">
        <div class="result-bar" v-for="result in classificationResults" :key="result.label">
          <span class="bar-label">{{ result.label }}</span>
          <div class="bar-track">
            <div class="bar-fill" :style="{ width: result.value + '%', background: result.color }"></div>
          </div>
          <span class="bar-value" :style="{ color: result.color }">{{ result.value }}%</span>
        </div>
      </div>
      
      <div class="task-info">
        <div class="info-row">
          <span class="info-label">ERD区域</span>
          <span class="info-value highlight">{{ currentTaskRegion }}</span>
        </div>
        <div class="info-row">
          <span class="info-label">节律</span>
          <span class="info-value">8-30Hz (Mu/Beta)</span>
        </div>
      </div>
    </div>
    
    <!-- 算法信息面板 -->
    <div class="algo-panel">
      <div class="algo-header">Hopfield网络参数</div>
      <div class="algo-grid">
        <div class="algo-item">
          <span class="algo-label">PCA维度</span>
          <span class="algo-value">16</span>
        </div>
        <div class="algo-item">
          <span class="algo-label">被试数</span>
          <span class="algo-value">109</span>
        </div>
        <div class="algo-item">
          <span class="algo-label">采样率</span>
          <span class="algo-value">160Hz</span>
        </div>
        <div class="algo-item">
          <span class="algo-label">通道数</span>
          <span class="algo-value">64</span>
        </div>
      </div>
      <div class="algo-accuracy">
        <span class="acc-label">模型准确率</span>
        <span class="acc-value">85.6%</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'

const emit = defineEmits<{
  taskChange: [task: 'left' | 'right' | 'foot' | null]
}>()

const currentTask = ref<'left' | 'right' | 'foot' | null>(null)

const tasks = [
  { id: 'left', label: '左手', icon: '👈', region: 'C4', class: 'left-hand' },
  { id: 'right', label: '右手', icon: '👉', region: 'C3', class: 'right-hand' },
  { id: 'foot', label: '双脚', icon: '🦶', region: 'Cz', class: 'foot' },
]

const taskInfo: Record<string, {region: string, accuracy: number}> = {
  left: {
    region: '右脑C4区',
    accuracy: 89  // 混淆矩阵中的实际准确率
  },
  right: {
    region: '左脑C3区', 
    accuracy: 85
  },
  foot: {
    region: '中央Cz区',
    accuracy: 85
  }
}

const currentTaskRegion = computed(() => currentTask.value ? taskInfo[currentTask.value].region : '')

// 基于Hopfield网络混淆矩阵的真实分类结果
const classificationResults = ref([
  { label: '左手', value: 10, color: '#00ffff' },
  { label: '右手', value: 8, color: '#ff6b00' },
  { label: '脚', value: 6, color: '#00ff88' }
])

// 基于混淆矩阵的真实预测结果
// 混淆矩阵:
// 真实左手: 左手=89%, 右手=7%, 脚=4%
// 真实右手: 左手=8%, 右手=85%, 脚=7%
// 真实脚:   左手=5%, 右手=10%, 脚=85%

const confusionMatrix = {
  left: [89, 7, 4],    // 真实左手时的分类概率
  right: [8, 85, 7],   // 真实右手时的分类概率
  foot: [5, 10, 85]    // 真实双脚时的分类概率
}

const selectTask = (task: 'left' | 'right' | 'foot') => {
  currentTask.value = currentTask.value === task ? null : task
  emit('taskChange', currentTask.value)
  
  if (currentTask.value) {
    simulateClassification(task)
  }
}

const simulateClassification = (task: 'left' | 'right' | 'foot') => {
  // 使用混淆矩阵数据
  const probs = confusionMatrix[task]
  
  let frame = 0
  const targetValues = [probs[0], probs[1], probs[2]]
  const startValues = [10, 8, 6]
  
  const animateResults = () => {
    frame++
    const progress = Math.min(1, frame / 25)
    const eased = 1 - Math.pow(1 - progress, 3) // easeOutCubic
    
    classificationResults.value.forEach((result, idx) => {
      result.value = Math.round(startValues[idx] + (targetValues[idx] - startValues[idx]) * eased)
    })
    
    if (frame < 25) {
      requestAnimationFrame(animateResults)
    }
  }
  
  // Reset first
  classificationResults.value = [
    { label: '左手', value: 10, color: '#00ffff' },
    { label: '右手', value: 8, color: '#ff6b00' },
    { label: '脚', value: 6, color: '#00ff88' }
  ]
  
  setTimeout(animateResults, 100)
}

// Keyboard shortcuts
const handleKeydown = (e: KeyboardEvent) => {
  switch (e.key) {
    case '1':
      selectTask('left')
      break
    case '2':
      selectTask('right')
      break
    case '3':
      selectTask('foot')
      break
    case 'Escape':
      currentTask.value = null
      emit('taskChange', null)
      break
  }
}

// Register keyboard shortcuts
if (typeof window !== 'undefined') {
  window.addEventListener('keydown', handleKeydown)
}
</script>

<style scoped>
.mi-simulator {
  background: rgba(0, 10, 20, 0.8);
  border: 1px solid rgba(255, 107, 0, 0.3);
  border-radius: 12px;
  padding: 12px;
  backdrop-filter: blur(10px);
}

.simulator-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  padding-bottom: 8px;
  border-bottom: 1px solid rgba(255, 107, 0, 0.2);
}

.sim-title {
  color: #ff6b00;
  font-size: 0.8rem;
  font-weight: bold;
  letter-spacing: 1px;
}

.algo-badge {
  font-size: 0.55rem;
  color: #00ffff;
  background: rgba(0, 255, 255, 0.1);
  padding: 2px 6px;
  border-radius: 4px;
  border: 1px solid rgba(0, 255, 255, 0.3);
}

.mi-buttons {
  display: flex;
  gap: 8px;
  margin-bottom: 12px;
}

.mi-btn {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 10px 6px;
  background: rgba(0, 20, 30, 0.6);
  border: 2px solid rgba(0, 255, 255, 0.2);
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s;
}

.mi-btn:hover {
  border-color: rgba(0, 255, 255, 0.5);
  background: rgba(0, 30, 40, 0.8);
  transform: translateY(-2px);
}

.mi-btn.active {
  border-color: #00ffff;
  background: rgba(0, 255, 255, 0.15);
  box-shadow: 0 0 15px rgba(0, 255, 255, 0.3);
}

.mi-btn.left-hand.active {
  border-color: #00ffff;
  box-shadow: 0 0 15px rgba(0, 255, 255, 0.4);
}

.mi-btn.right-hand.active {
  border-color: #ff6b00;
  box-shadow: 0 0 15px rgba(255, 107, 0, 0.4);
}

.mi-btn.foot.active {
  border-color: #00ff88;
  box-shadow: 0 0 15px rgba(0, 255, 136, 0.4);
}

.mi-icon {
  font-size: 1.2rem;
  margin-bottom: 2px;
}

.mi-label {
  color: #fff;
  font-size: 0.75rem;
  font-weight: bold;
}

.mi-region {
  color: #888;
  font-size: 0.55rem;
  margin-top: 2px;
}

.mi-info {
  background: rgba(0, 0, 0, 0.3);
  border-radius: 8px;
  padding: 10px;
  margin-bottom: 10px;
}

.info-header {
  color: #00ffff;
  font-size: 0.7rem;
  margin-bottom: 8px;
  letter-spacing: 1px;
}

.task-info {
  margin-top: 8px;
  padding-top: 8px;
  border-top: 1px solid rgba(0, 255, 255, 0.15);
}

.info-row {
  display: flex;
  justify-content: space-between;
  margin: 4px 0;
}

.info-label {
  color: #888;
  font-size: 0.6rem;
}

.info-value {
  color: #ccc;
  font-size: 0.6rem;
}

.info-value.highlight {
  color: #ff6b00;
}

.result-bars {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.result-bar {
  display: flex;
  align-items: center;
  gap: 8px;
}

.bar-label {
  width: 35px;
  font-size: 0.6rem;
  color: #aaa;
}

.bar-track {
  flex: 1;
  height: 10px;
  background: rgba(0, 0, 0, 0.3);
  border-radius: 5px;
  overflow: hidden;
}

.bar-fill {
  height: 100%;
  border-radius: 5px;
  transition: width 0.4s ease-out;
  box-shadow: 0 0 8px currentColor;
}

.bar-value {
  width: 40px;
  font-size: 0.65rem;
  font-weight: bold;
  text-align: right;
}

/* 算法信息面板 */
.algo-panel {
  background: rgba(0, 20, 30, 0.6);
  border: 1px solid rgba(0, 255, 255, 0.2);
  border-radius: 8px;
  padding: 10px;
}

.algo-header {
  color: #00ffff;
  font-size: 0.65rem;
  margin-bottom: 8px;
  letter-spacing: 1px;
}

.algo-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 6px;
  margin-bottom: 8px;
}

.algo-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 4px 6px;
  background: rgba(0, 0, 0, 0.2);
  border-radius: 4px;
}

.algo-label {
  color: #888;
  font-size: 0.55rem;
}

.algo-value {
  color: #00ffff;
  font-size: 0.65rem;
  font-weight: bold;
}

.algo-accuracy {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 6px 10px;
  background: rgba(255, 107, 0, 0.1);
  border: 1px solid rgba(255, 107, 0, 0.3);
  border-radius: 6px;
}

.acc-label {
  color: #ff6b00;
  font-size: 0.6rem;
}

.acc-value {
  color: #4ade80;
  font-size: 0.9rem;
  font-weight: bold;
  text-shadow: 0 0 10px rgba(74, 222, 128, 0.5);
}
</style>