<template>
  <div class="region-explainer">
    <div class="explainer-header">
      <span class="explainer-title">🧠 脑科学与脑机接口</span>
    </div>
    
    <!-- 标签切换 -->
    <div class="tab-bar">
      <button 
        v-for="tab in tabs" 
        :key="tab.id"
        class="tab-btn"
        :class="{ active: activeTab === tab.id }"
        @click="activeTab = tab.id"
      >
        {{ tab.icon }} {{ tab.name }}
      </button>
    </div>
    
    <!-- 大脑区域科普 -->
    <div v-show="activeTab === 'brain'" class="tab-content brain-tab">
    
    <div class="brain-diagram">
      <canvas ref="diagramCanvas" class="diagram-canvas" @click="handleClick"></canvas>
      
      <!-- 可点击区域覆盖 -->
      <div 
        v-for="region in brainRegions" 
        :key="region.id"
        class="region-hitbox"
        :class="{ active: selectedRegion?.id === region.id, [region.id]: true }"
        :style="{ 
          left: region.hitbox.x + '%', 
          top: region.hitbox.y + '%',
          width: region.hitbox.width + '%',
          height: region.hitbox.height + '%'
        }"
        @click="selectRegion(region)"
        @mouseenter="hoverRegion = region"
        @mouseleave="hoverRegion = null"
      >
        <span class="region-name">{{ region.shortName }}</span>
      </div>
      
      <!-- 悬停提示 -->
      <div v-if="hoverRegion && !selectedRegion" class="hover-tooltip">
        {{ hoverRegion.name }}
      </div>
    </div>
    
    <!-- 区域详情面板 -->
    <div v-if="selectedRegion" class="region-detail">
      <div class="detail-header">
        <span class="detail-icon" :style="{ color: selectedRegion.color }">{{ selectedRegion.icon }}</span>
        <span class="detail-title">{{ selectedRegion.name }}</span>
        <button class="close-btn" @click="selectedRegion = null">✕</button>
      </div>
      
      <div class="detail-content">
        <p class="detail-desc">{{ selectedRegion.description }}</p>
        
        <div class="detail-section">
          <div class="section-title">🔬 功能</div>
          <ul class="feature-list">
            <li v-for="func in selectedRegion.functions" :key="func">{{ func }}</li>
          </ul>
        </div>
        
        <div class="detail-section bci-section">
          <div class="section-title">🧠 BCI应用</div>
          <p class="bci-text">{{ selectedRegion.bciRole }}</p>
        </div>
        
        <div class="detail-section" v-if="selectedRegion.frequency">
          <div class="section-title">📊 相关节律</div>
          <div class="freq-badge">
            <span class="freq-name">{{ selectedRegion.frequency.name }}</span>
            <span class="freq-range">{{ selectedRegion.frequency.range }}</span>
          </div>
          <p class="freq-desc">{{ selectedRegion.frequency.description }}</p>
        </div>
      </div>
    </div>
    
    <div v-else class="default-tip">
        <div class="tip-icon">👆</div>
        <p>点击上方大脑区域</p>
        <p class="tip-sub">了解各区域在脑机接口中的作用</p>
      </div>
    </div>
    
    <!-- BCI基础知识 -->
    <div v-show="activeTab === 'bci'" class="tab-content bci-tab">
      <div class="bci-section">
        <div class="bci-title">什么是脑机接口？</div>
        <p class="bci-desc">脑机接口(Brain-Computer Interface, BCI)是一种在大脑与外部设备之间建立直接通信通道的技术，无需依赖肌肉或外周神经。</p>
        
        <div class="bci-types">
          <div class="type-card">
            <div class="type-icon">📥</div>
            <div class="type-name">输入型BCI</div>
            <div class="type-desc">读取大脑信号，如本项目使用的EEG脑电图</div>
          </div>
          <div class="type-card">
            <div class="type-icon">📤</div>
            <div class="type-name">输出型BCI</div>
            <div class="type-desc">向大脑输入信息，如人工耳蜗、视觉假体</div>
          </div>
          <div class="type-card">
            <div class="type-icon">🔄</div>
            <div class="type-name">双向BCI</div>
            <div class="type-desc">同时读取和写入，实现闭环控制</div>
          </div>
        </div>
      </div>
      
      <div class="bci-section">
        <div class="bci-title">BCI信号类型</div>
        <div class="signal-list">
          <div class="signal-item">
            <span class="signal-badge eeg">EEG</span>
            <span class="signal-name">脑电图</span>
            <span class="signal-desc">非侵入式，本项目使用</span>
          </div>
          <div class="signal-item">
            <span class="signal-badge ecog">ECoG</span>
            <span class="signal-name">皮层电图</span>
            <span class="signal-desc">半侵入式，高空间分辨率</span>
          </div>
          <div class="signal-item">
            <span class="signal-badge implanted">Utah Array</span>
            <span class="signal-name">植入电极</span>
            <span class="signal-desc">侵入式，最高信号质量</span>
          </div>
        </div>
      </div>
      
      <div class="bci-section">
        <div class="bci-title">三大BCI范式</div>
        <div class="paradigm-list">
          <div class="paradigm-item">
            <div class="para-name">🧠 运动想象 (MI)</div>
            <div class="para-desc">想象肢体运动产生ERD/ERS，如本项目实现</div>
            <div class="para-acc">准确率: 70-90%</div>
          </div>
          <div class="paradigm-item">
            <div class="para-name">🎯 P300拼写器</div>
            <div class="para-desc">注视目标时产生P300事件相关电位</div>
            <div class="para-acc">准确率: 80-95%</div>
          </div>
          <div class="paradigm-item">
            <div class="para-name">👁️ SSVEP</div>
            <div class="para-desc">注视闪烁光源产生稳态视觉诱发电位</div>
            <div class="para-acc">准确率: 90-99%</div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 未来展望 -->
    <div v-show="activeTab === 'future'" class="tab-content future-tab">
      <div class="future-section">
        <div class="future-title">🔮 BCI未来发展预测</div>
        
        <div class="timeline-future">
          <div class="future-item">
            <div class="future-year">2025-2028</div>
            <div class="future-content">
              <div class="future-head">近期发展</div>
              <ul>
                <li>非侵入式BCI准确率突破90%</li>
                <li>便携式干电极EEG设备普及</li>
                <li>AI辅助信号解码大幅进步</li>
                <li>BCI在康复医疗广泛应用</li>
              </ul>
            </div>
          </div>
          
          <div class="future-item">
            <div class="future-year">2028-2035</div>
            <div class="future-content">
              <div class="future-head">中期突破</div>
              <ul>
                <li>双向BCI实现触觉反馈</li>
                <li>植入式电极安全性大幅提升</li>
                <li>脑控假肢实现精细操作</li>
                <li>意念打字速度接近正常打字</li>
              </ul>
            </div>
          </div>
          
          <div class="future-item">
            <div class="future-year">2035-2050</div>
            <div class="future-content">
              <div class="future-head">远期愿景</div>
              <ul>
                <li>脑脑通信 (Brain-to-Brain)</li>
                <li>记忆增强与知识下载</li>
                <li>意识上传探索</li>
                <li>人机融合新时代</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
      
      <div class="future-section">
        <div class="future-title">🏥 医疗应用前景</div>
        <div class="medical-grid">
          <div class="medical-card">
            <div class="med-icon">🦽</div>
            <div class="med-name">瘫痪康复</div>
            <div class="med-desc">帮助脊髓损伤患者恢复运动控制</div>
          </div>
          <div class="medical-card">
            <div class="med-icon">🗣️</div>
            <div class="med-name">语言恢复</div>
            <div class="med-desc">为失语症患者提供沟通能力</div>
          </div>
          <div class="medical-card">
            <div class="med-icon">🧠</div>
            <div class="med-name">神经疾病</div>
            <div class="med-desc">治疗帕金森、癫痫等神经系统疾病</div>
          </div>
          <div class="medical-card">
            <div class="med-icon">👁️</div>
            <div class="med-name">视觉恢复</div>
            <div class="med-desc">为盲人提供人工视觉感知</div>
          </div>
        </div>
      </div>
      
      <div class="future-section ethics">
        <div class="future-title">⚖️ 伦理思考</div>
        <div class="ethics-content">
          <p>随着BCI技术发展，我们需要思考：</p>
          <ul>
            <li><strong>隐私保护</strong>：如何保护个人思维数据？</li>
            <li><strong>公平获取</strong>：技术是否会加剧社会不平等？</li>
            <li><strong>自主权</strong>：脑增强是否会改变人的本质？</li>
            <li><strong>安全风险</strong>：如何防止"黑客入侵"大脑？</li>
          </ul>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'

const diagramCanvas = ref<HTMLCanvasElement>()
const selectedRegion = ref<BrainRegion | null>(null)
const hoverRegion = ref<BrainRegion | null>(null)
const activeTab = ref('brain')

const tabs = [
  { id: 'brain', name: '大脑区域', icon: '🧠' },
  { id: 'bci', name: 'BCI基础', icon: '📚' },
  { id: 'future', name: '未来展望', icon: '🔮' }
]

interface BrainRegion {
  id: string
  name: string
  shortName: string
  icon: string
  color: string
  description: string
  functions: string[]
  bciRole: string
  frequency?: { name: string; range: string; description: string }
  hitbox: { x: number; y: number; width: number; height: number }
}

const brainRegions: BrainRegion[] = [
  {
    id: 'motor',
    name: '初级运动皮层 (M1)',
    shortName: 'M1',
    icon: '🎯',
    color: '#ff6b00',
    description: '位于中央前回，是控制随意运动的最高级中枢。每个身体部位在此都有对应的代表区（运动小人）。',
    functions: [
      '控制对侧肢体的随意运动',
      '调节肌肉张力和运动精度',
      '规划和执行精细动作'
    ],
    bciRole: '运动想象(MI)的主要目标区域。想象左手/右手/脚运动时，对侧M1区域会产生ERD（事件相关去同步），这是BCI识别运动意图的关键信号。',
    frequency: {
      name: 'Mu节律',
      range: '8-13 Hz',
      description: '静息时M1区域的特征节律，运动想象时会抑制（ERD）'
    },
    hitbox: { x: 25, y: 40, width: 50, height: 15 }
  },
  {
    id: 'premotor',
    name: '前运动皮层 (PMC)',
    shortName: 'PMC',
    icon: '🔗',
    color: '#ff9500',
    description: '位于运动皮层前方，参与运动的准备、规划和学习，是运动执行的重要前级区域。',
    functions: [
      '运动计划和准备',
      '学习新的运动序列',
      '基于外部线索的运动规划'
    ],
    bciRole: '在运动想象的早期阶段活跃，参与运动意图的形成。高阶BCI系统可以结合PMC活动来预测用户的运动准备状态。',
    frequency: {
      name: 'Beta节律',
      range: '13-30 Hz',
      description: '与运动准备和维持有关，运动执行前会先出现Beta ERD'
    },
    hitbox: { x: 25, y: 25, width: 50, height: 15 }
  },
  {
    id: 'sensory',
    name: '初级感觉皮层 (S1)',
    shortName: 'S1',
    icon: '✋',
    color: '#00aaff',
    description: '位于中央后回，接收来自全身的躯体感觉信息（触觉、痛觉、温度觉等）。',
    functions: [
      '接收对侧身体的感觉输入',
      '处理触觉和本体感觉',
      '感觉信息的初步整合'
    ],
    bciRole: '感觉反馈BCI的重要区域。当BCI系统提供触觉或电刺激反馈时，S1会产生活动，可用于闭环BCI系统。',
    frequency: {
      name: 'Alpha/Beta节律',
      range: '8-30 Hz',
      description: '感觉刺激时会产生事件相关电位(ERP)'
    },
    hitbox: { x: 25, y: 55, width: 50, height: 15 }
  },
  {
    id: 'prefrontal',
    name: '前额叶皮层 (PFC)',
    shortName: 'PFC',
    icon: '💡',
    color: '#aa00ff',
    description: '位于大脑最前端，是高级认知功能的核心区域，包括决策、注意力和工作记忆。',
    functions: [
      '注意力调控和执行控制',
      '决策和计划',
      '情绪调节',
      '工作记忆'
    ],
    bciRole: '基于P300的BCI（如P300拼写器）利用前额叶的P300电位。注意力BCI也依赖PFC的注意力调控功能。',
    frequency: {
      name: 'Theta节律',
      range: '4-8 Hz',
      description: '与注意力、记忆编码和认知负荷有关'
    },
    hitbox: { x: 30, y: 10, width: 40, height: 15 }
  },
  {
    id: 'parietal',
    name: '顶叶皮层',
    shortName: '顶叶',
    icon: '🗺️',
    color: '#00ff88',
    description: '位于大脑后上部，整合感觉信息，形成空间感知和身体意识。',
    functions: [
      '空间感知和定向',
      '感觉信息整合',
      '注意空间定位',
      '数学和逻辑处理'
    ],
    bciRole: 'SSVEP（稳态视觉诱发电位）BCI中，顶叶区域会产生视觉相关的脑电信号。空间注意力BCI也依赖顶叶功能。',
    frequency: {
      name: 'Alpha节律',
      range: '8-13 Hz',
      description: '顶枕区最明显的节律，闭眼时增强'
    },
    hitbox: { x: 30, y: 70, width: 40, height: 15 }
  },
  {
    id: 'occipital',
    name: '枕叶视觉皮层',
    shortName: '枕叶',
    icon: '👁️',
    color: '#ff00ff',
    description: '位于大脑最后部，是视觉信息处理的核心区域，接收并处理来自眼睛的视觉输入。',
    functions: [
      '视觉信息初级处理',
      '颜色、形状、运动检测',
      '视觉特征提取'
    ],
    bciRole: 'SSVEP BCI的核心区域。当用户注视特定频率的闪烁光源时，枕叶视觉皮层会产生同频率的脑电响应，是SSVEP-BCI的信号来源。',
    frequency: {
      name: 'SSVEP响应',
      range: '取决于刺激频率',
      description: '注视闪烁光时，枕叶会产生与刺激频率相同的脑电响应'
    },
    hitbox: { x: 35, y: 82, width: 30, height: 12 }
  }
]

// 绘制简化的大脑图
const drawBrainDiagram = () => {
  const canvas = diagramCanvas.value
  if (!canvas) return
  
  const ctx = canvas.getContext('2d')
  if (!ctx) return
  
  const w = canvas.width
  const h = canvas.height
  const cx = w / 2
  const cy = h / 2
  
  ctx.clearRect(0, 0, w, h)
  
  // 绘制头部轮廓
  ctx.beginPath()
  ctx.ellipse(cx, cy - 10, w * 0.42, h * 0.45, 0, 0, Math.PI * 2)
  ctx.strokeStyle = 'rgba(0, 255, 255, 0.4)'
  ctx.lineWidth = 2
  ctx.stroke()
  ctx.fillStyle = 'rgba(0, 40, 60, 0.3)'
  ctx.fill()
  
  // 绘制脑沟
  ctx.strokeStyle = 'rgba(0, 255, 255, 0.2)'
  ctx.lineWidth = 1
  
  // 中央沟
  ctx.beginPath()
  ctx.moveTo(cx, cy - h * 0.35)
  ctx.quadraticCurveTo(cx + 20, cy, cx - 10, cy + h * 0.3)
  ctx.stroke()
  
  // 外侧裂
  ctx.beginPath()
  ctx.moveTo(cx - w * 0.2, cy - h * 0.1)
  ctx.quadraticCurveTo(cx, cy + h * 0.1, cx + w * 0.35, cy + h * 0.15)
  ctx.stroke()
  
  // 顶部纵裂
  ctx.beginPath()
  ctx.moveTo(cx, cy - h * 0.42)
  ctx.lineTo(cx, cy - h * 0.2)
  ctx.stroke()
  
  // 绘制区域
  brainRegions.forEach(region => {
    drawRegion(ctx, region, w, h)
  })
  
  // 绘制鼻子和耳朵
  ctx.beginPath()
  ctx.moveTo(cx - 10, cy - h * 0.45)
  ctx.lineTo(cx, cy - h * 0.52)
  ctx.lineTo(cx + 10, cy - h * 0.45)
  ctx.strokeStyle = 'rgba(0, 255, 255, 0.5)'
  ctx.lineWidth = 2
  ctx.stroke()
}

const drawRegion = (ctx: CanvasRenderingContext2D, region: BrainRegion, w: number, h: number) => {
  const x = (region.hitbox.x / 100) * w
  const y = (region.hitbox.y / 100) * h
  const width = (region.hitbox.width / 100) * w
  const height = (region.hitbox.height / 100) * h
  
  const isSelected = selectedRegion.value?.id === region.id
  const isHovered = hoverRegion.value?.id === region.id
  
  ctx.beginPath()
  ctx.ellipse(x + width / 2, y + height / 2, width / 2, height / 2, 0, 0, Math.PI * 2)
  
  if (isSelected) {
    ctx.fillStyle = region.color + '60'
    ctx.strokeStyle = region.color
    ctx.lineWidth = 3
  } else if (isHovered) {
    ctx.fillStyle = region.color + '40'
    ctx.strokeStyle = region.color + 'aa'
    ctx.lineWidth = 2
  } else {
    ctx.fillStyle = region.color + '20'
    ctx.strokeStyle = region.color + '50'
    ctx.lineWidth = 1
  }
  
  ctx.fill()
  ctx.stroke()
  
  // 绘制标签
  ctx.font = isSelected || isHovered ? 'bold 12px sans-serif' : '10px sans-serif'
  ctx.fillStyle = isSelected || isHovered ? region.color : 'rgba(255, 255, 255, 0.7)'
  ctx.textAlign = 'center'
  ctx.textBaseline = 'middle'
  ctx.fillText(region.shortName, x + width / 2, y + height / 2)
}

const selectRegion = (region: BrainRegion) => {
  selectedRegion.value = selectedRegion.value?.id === region.id ? null : region
  drawBrainDiagram()
}

const handleClick = (e: MouseEvent) => {
  // 如果点击在空白处，取消选择
  if (selectedRegion.value) {
    selectedRegion.value = null
    drawBrainDiagram()
  }
}

watch(selectedRegion, () => {
  drawBrainDiagram()
})

onMounted(() => {
  if (diagramCanvas.value) {
    diagramCanvas.value.width = 280
    diagramCanvas.value.height = 280
    drawBrainDiagram()
  }
})
</script>

<style scoped>
.region-explainer {
  background: linear-gradient(135deg, rgba(0, 20, 40, 0.95), rgba(0, 10, 30, 0.98));
  border: 1px solid rgba(0, 255, 255, 0.3);
  border-radius: 12px;
  padding: 12px;
  display: flex;
  flex-direction: column;
  gap: 10px;
  height: 100%;
  overflow: hidden;
}

.explainer-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-bottom: 8px;
  border-bottom: 1px solid rgba(0, 255, 255, 0.2);
}

.explainer-title {
  color: #00ffff;
  font-size: 0.9rem;
  font-weight: bold;
  letter-spacing: 1px;
}

/* 标签栏 */
.tab-bar {
  display: flex;
  gap: 6px;
  padding: 6px 0;
  border-bottom: 1px solid rgba(0, 255, 255, 0.1);
}

.tab-btn {
  flex: 1;
  padding: 8px 6px;
  background: rgba(0, 50, 80, 0.3);
  border: 1px solid rgba(0, 255, 255, 0.2);
  border-radius: 6px;
  color: #888;
  font-size: 0.7rem;
  cursor: pointer;
  transition: all 0.2s;
}

.tab-btn:hover {
  background: rgba(0, 100, 150, 0.3);
  color: #aaa;
}

.tab-btn.active {
  background: rgba(0, 255, 255, 0.15);
  border-color: #00ffff;
  color: #00ffff;
}

.tab-content {
  flex: 1;
  overflow-y: auto;
  padding-right: 5px;
}

.brain-diagram {
  position: relative;
  width: 100%;
  aspect-ratio: 1;
  flex-shrink: 0;
}

.diagram-canvas {
  width: 100%;
  height: 100%;
  display: block;
}

.region-hitbox {
  position: absolute;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  transition: all 0.2s;
}

.region-hitbox:hover {
  background: rgba(255, 255, 255, 0.1);
}

.region-hitbox.active {
  background: rgba(255, 255, 255, 0.15);
  transform: scale(1.05);
}

.region-name {
  font-size: 0;
  opacity: 0;
  transition: all 0.2s;
}

.region-hitbox:hover .region-name,
.region-hitbox.active .region-name {
  font-size: 0.6rem;
  opacity: 1;
  color: #fff;
  text-shadow: 0 0 5px rgba(0, 0, 0, 0.8);
}

.hover-tooltip {
  position: absolute;
  bottom: 10px;
  left: 50%;
  transform: translateX(-50%);
  background: rgba(0, 0, 0, 0.8);
  color: #00ffff;
  padding: 4px 10px;
  border-radius: 4px;
  font-size: 0.7rem;
  white-space: nowrap;
  pointer-events: none;
}

.region-detail {
  flex: 1;
  background: rgba(0, 0, 0, 0.3);
  border-radius: 8px;
  padding: 10px;
  overflow-y: auto;
}

.detail-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 10px;
  padding-bottom: 8px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.detail-icon {
  font-size: 1.5rem;
}

.detail-title {
  flex: 1;
  color: #fff;
  font-size: 0.85rem;
  font-weight: bold;
}

.close-btn {
  background: none;
  border: none;
  color: #666;
  cursor: pointer;
  font-size: 1rem;
  padding: 2px 6px;
}

.close-btn:hover {
  color: #fff;
}

.detail-content {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.detail-desc {
  color: #ccc;
  font-size: 0.75rem;
  line-height: 1.5;
}

.detail-section {
  padding: 8px;
  background: rgba(0, 255, 255, 0.05);
  border-radius: 6px;
  border-left: 3px solid rgba(0, 255, 255, 0.5);
}

.detail-section.bci-section {
  border-left-color: #ff6b00;
}

.section-title {
  color: #00ffff;
  font-size: 0.7rem;
  margin-bottom: 6px;
  font-weight: bold;
}

.bci-section .section-title {
  color: #ff6b00;
}

.feature-list {
  margin: 0;
  padding-left: 15px;
  color: #aaa;
  font-size: 0.7rem;
  line-height: 1.6;
}

.feature-list li {
  margin: 2px 0;
}

.bci-text {
  color: #ccc;
  font-size: 0.7rem;
  line-height: 1.5;
  margin: 0;
}

.freq-badge {
  display: inline-flex;
  gap: 8px;
  align-items: center;
  margin-bottom: 6px;
}

.freq-name {
  background: rgba(255, 107, 0, 0.2);
  color: #ff6b00;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 0.7rem;
  font-weight: bold;
}

.freq-range {
  color: #ff9500;
  font-size: 0.7rem;
}

.freq-desc {
  color: #888;
  font-size: 0.65rem;
  margin: 0;
}

.default-tip {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 5px;
  color: #666;
}

.tip-icon {
  font-size: 1.5rem;
  animation: bounce 2s infinite;
}

@keyframes bounce {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-5px); }
}

.default-tip p {
  margin: 0;
  font-size: 0.75rem;
}

.tip-sub {
  font-size: 0.65rem !important;
  color: #555;
}

/* BCI基础标签页 */
.bci-section {
  background: rgba(0, 30, 50, 0.4);
  border-radius: 8px;
  padding: 12px;
  margin-bottom: 10px;
}

.bci-title {
  color: #ff6b00;
  font-size: 0.85rem;
  font-weight: bold;
  margin-bottom: 10px;
  padding-bottom: 6px;
  border-bottom: 1px solid rgba(255, 107, 0, 0.3);
}

.bci-desc {
  color: #ccc;
  font-size: 0.75rem;
  line-height: 1.6;
  margin-bottom: 12px;
}

.bci-types {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 8px;
}

.type-card {
  background: rgba(0, 0, 0, 0.3);
  border: 1px solid rgba(0, 255, 255, 0.2);
  border-radius: 6px;
  padding: 10px 8px;
  text-align: center;
}

.type-icon {
  font-size: 1.3rem;
  margin-bottom: 6px;
}

.type-name {
  color: #00ffff;
  font-size: 0.7rem;
  font-weight: bold;
  margin-bottom: 4px;
}

.type-desc {
  color: #888;
  font-size: 0.6rem;
  line-height: 1.3;
}

.signal-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.signal-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px;
  background: rgba(0, 0, 0, 0.3);
  border-radius: 6px;
}

.signal-badge {
  padding: 3px 8px;
  border-radius: 4px;
  font-size: 0.6rem;
  font-weight: bold;
}

.signal-badge.eeg { background: rgba(0, 255, 136, 0.2); color: #00ff88; }
.signal-badge.ecog { background: rgba(255, 170, 0, 0.2); color: #ffaa00; }
.signal-badge.implanted { background: rgba(255, 0, 100, 0.2); color: #ff0064; }

.signal-name {
  color: #fff;
  font-size: 0.75rem;
  font-weight: bold;
}

.signal-desc {
  color: #888;
  font-size: 0.65rem;
}

.paradigm-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.paradigm-item {
  background: rgba(0, 0, 0, 0.3);
  border-radius: 6px;
  padding: 10px;
  border-left: 3px solid #00ffff;
}

.para-name {
  color: #00ffff;
  font-size: 0.8rem;
  font-weight: bold;
  margin-bottom: 4px;
}

.para-desc {
  color: #aaa;
  font-size: 0.65rem;
  margin-bottom: 4px;
}

.para-acc {
  color: #00ff88;
  font-size: 0.6rem;
  font-weight: bold;
}

/* 未来展望标签页 */
.future-section {
  background: rgba(0, 30, 50, 0.4);
  border-radius: 8px;
  padding: 12px;
  margin-bottom: 10px;
}

.future-section.ethics {
  background: rgba(80, 40, 0, 0.3);
  border: 1px solid rgba(255, 170, 0, 0.3);
}

.future-title {
  color: #00ffff;
  font-size: 0.85rem;
  font-weight: bold;
  margin-bottom: 12px;
  padding-bottom: 6px;
  border-bottom: 1px solid rgba(0, 255, 255, 0.2);
}

.timeline-future {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.future-item {
  display: flex;
  gap: 12px;
}

.future-year {
  background: linear-gradient(135deg, #ff6b00, #ff9500);
  color: #fff;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 0.65rem;
  font-weight: bold;
  white-space: nowrap;
  height: fit-content;
}

.future-content {
  flex: 1;
}

.future-head {
  color: #00ffff;
  font-size: 0.75rem;
  font-weight: bold;
  margin-bottom: 6px;
}

.future-content ul {
  margin: 0;
  padding-left: 16px;
  color: #aaa;
  font-size: 0.65rem;
  line-height: 1.6;
}

.future-content li {
  margin: 3px 0;
}

.medical-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 8px;
}

.medical-card {
  background: rgba(0, 255, 136, 0.08);
  border: 1px solid rgba(0, 255, 136, 0.2);
  border-radius: 8px;
  padding: 10px;
  text-align: center;
}

.med-icon {
  font-size: 1.3rem;
  margin-bottom: 6px;
}

.med-name {
  color: #00ff88;
  font-size: 0.7rem;
  font-weight: bold;
  margin-bottom: 4px;
}

.med-desc {
  color: #888;
  font-size: 0.6rem;
  line-height: 1.3;
}

.ethics-content {
  color: #ccc;
  font-size: 0.7rem;
  line-height: 1.6;
}

.ethics-content ul {
  margin: 8px 0 0 0;
  padding-left: 16px;
}

.ethics-content li {
  margin: 6px 0;
}

.ethics-content strong {
  color: #ffaa00;
}
</style>
