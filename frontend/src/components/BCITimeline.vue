<template>
  <div class="timeline-container">
    <div class="timeline-header">
      <span class="timeline-title">📅 BCI发展史</span>
      <div class="era-tabs">
        <button 
          v-for="era in eras" 
          :key="era.id"
          class="era-btn"
          :class="{ active: currentEra === era.id }"
          @click="currentEra = era.id"
        >
          {{ era.label }}
        </button>
      </div>
    </div>
    
    <div class="timeline-content" ref="timelineRef">
      <div class="timeline-line"></div>
      
      <div 
        v-for="(event, idx) in filteredEvents" 
        :key="event.year"
        class="timeline-item"
        :class="{ active: selectedEvent?.year === event.year }"
        :style="{ animationDelay: idx * 0.1 + 's' }"
        @click="selectEvent(event)"
      >
        <div class="timeline-dot" :style="{ background: event.color }">
          <span class="dot-icon">{{ event.icon }}</span>
        </div>
        
        <div class="timeline-card">
          <div class="card-year" :style="{ color: event.color }">{{ event.year }}</div>
          <div class="card-title">{{ event.title }}</div>
          <div class="card-desc">{{ event.description }}</div>
          
          <div v-if="selectedEvent?.year === event.year" class="card-detail">
            <div class="detail-section" v-if="event.scientist">
              <span class="detail-label">科学家</span>
              <span class="detail-value">{{ event.scientist }}</span>
            </div>
            <div class="detail-section" v-if="event.significance">
              <span class="detail-label">意义</span>
              <span class="detail-value">{{ event.significance }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <div class="timeline-footer">
      <span class="footer-text">脑机接口发展至今已有100年历史</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'

const currentEra = ref('all')
const selectedEvent = ref<BCIEvent | null>(null)
const timelineRef = ref<HTMLElement>()

interface BCIEvent {
  year: number
  title: string
  description: string
  icon: string
  color: string
  scientist?: string
  significance?: string
  era: string
}

const eras = [
  { id: 'all', label: '全部' },
  { id: 'early', label: '早期探索' },
  { id: 'development', label: '发展期' },
  { id: 'modern', label: '现代' },
  { id: 'future', label: '未来' }
]

const events: BCIEvent[] = [
  {
    year: 1924,
    title: '发现脑电波',
    description: 'Hans Berger首次记录到人类脑电波，开创了脑电图(EEG)技术',
    icon: '⚡',
    color: '#ffaa00',
    scientist: 'Hans Berger',
    significance: '奠定了所有BCI技术的基础',
    era: 'early'
  },
  {
    year: 1969,
    title: '神经元 operant conditioning',
    description: 'Monkey通过调节单个神经元的活动来控制光标',
    icon: '🐒',
    color: '#ff6b00',
    scientist: 'Eberhard Fetz',
    significance: '首次证明大脑可以学习控制外部设备',
    era: 'early'
  },
  {
    year: 1978,
    title: '视觉皮层植入物',
    description: '首次在人类视觉皮层植入电极阵列',
    icon: '👁️',
    color: '#00aaff',
    scientist: 'William Dobelle',
    significance: '开创了侵入式BCI的先河',
    era: 'development'
  },
  {
    year: 1998,
    title: 'BrainGate概念',
    description: 'Philip Kennedy植入首个神经信号接口',
    icon: '🎯',
    color: '#00ff88',
    scientist: 'Philip Kennedy',
    significance: '为现代运动皮层BCI奠定基础',
    era: 'development'
  },
  {
    year: 2004,
    title: 'BrainGate首次人体试验',
    description: '瘫痪患者首次通过BCI控制机械臂',
    icon: '🦾',
    color: '#ff00ff',
    scientist: 'John Donoghue团队',
    significance: 'BCI首次在实际瘫痪患者中验证',
    era: 'development'
  },
  {
    year: 2006,
    title: 'BCI Competition IV',
    description: '发布标准BCI竞赛数据集，推动算法发展',
    icon: '📊',
    color: '#00ffff',
    significance: '你的研究使用的就是这个数据集！',
    era: 'development'
  },
  {
    year: 2012,
    title: '高精度机械臂控制',
    description: '瘫痪患者通过BCI控制机械臂完成复杂任务',
    icon: '🤖',
    color: '#ff6b00',
    significance: '展示了BCI在日常生活中的应用潜力',
    era: 'modern'
  },
  {
    year: 2016,
    title: '双向BCI系统',
    description: '结合运动控制和感觉反馈的闭环BCI系统',
    icon: '🔄',
    color: '#aa00ff',
    significance: '实现了更自然的假肢控制体验',
    era: 'modern'
  },
  {
    year: 2019,
    title: '脑波打字速度突破',
    description: '瘫痪患者通过BCI实现每分钟90字符的打字速度',
    icon: '⌨️',
    color: '#00ff88',
    significance: '接近正常人打字速度的1/3',
    era: 'modern'
  },
  {
    year: 2020,
    title: 'Neuralink发布',
    description: 'Elon Musk展示高带宽脑机接口芯片',
    icon: '💉',
    color: '#00aaff',
    scientist: 'Neuralink',
    significance: '将BCI推向公众视野和商业化',
    era: 'modern'
  },
  {
    year: 2023,
    title: 'AI增强BCI',
    description: '深度学习与BCI结合，准确率大幅提升',
    icon: '🤖',
    color: '#ff6b00',
    significance: 'AI+BCI开启新纪元',
    era: 'modern'
  },
  {
    year: 2024,
    title: 'Hopfield网络BCI',
    description: '基于Hopfield联想记忆的运动想象分类系统（你的研究！）',
    icon: '🧠',
    color: '#ffaa00',
    significance: '你的本科毕设在这里！',
    era: 'future'
  },
  {
    year: 2025,
    title: 'AI辅助EEG解码',
    description: 'Transformer和大语言模型应用于脑电信号解码，准确率突破95%',
    icon: '🤖',
    color: '#00ff88',
    significance: 'AI+BCI融合加速',
    era: 'future'
  },
  {
    year: 2028,
    title: '便携式消费级BCI',
    description: '干电极头戴设备进入消费市场，支持游戏和冥想',
    icon: '🎧',
    color: '#aa00ff',
    significance: 'BCI从实验室走向大众',
    era: 'future'
  },
  {
    year: 2030,
    title: '高精度双向BCI',
    description: '预计实现高精度、低延迟的双向脑机通信',
    icon: '🌐',
    color: '#00ffff',
    significance: 'BCI的下一个重大突破',
    era: 'future'
  },
  {
    year: 2035,
    title: '脑控假肢商用',
    description: '带触觉反馈的智能假肢获FDA批准上市',
    icon: '🦾',
    color: '#ff6b00',
    significance: '瘫痪患者获得新生活',
    era: 'future'
  },
  {
    year: 2040,
    title: '记忆增强研究',
    description: '海马体BCI实现记忆编码和检索增强',
    icon: '💾',
    color: '#ff00ff',
    significance: '人类认知能力边界被拓展',
    era: 'future'
  }
]

const filteredEvents = computed(() => {
  if (currentEra.value === 'all') return events
  return events.filter(e => e.era === currentEra.value)
})

const selectEvent = (event: BCIEvent) => {
  selectedEvent.value = selectedEvent.value?.year === event.year ? null : event
}
</script>

<style scoped>
.timeline-container {
  background: linear-gradient(135deg, rgba(0, 20, 40, 0.95), rgba(0, 10, 30, 0.98));
  border: 1px solid rgba(255, 170, 0, 0.3);
  border-radius: 12px;
  padding: 12px;
  display: flex;
  flex-direction: column;
  gap: 10px;
  height: 100%;
}

.timeline-header {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding-bottom: 8px;
  border-bottom: 1px solid rgba(255, 170, 0, 0.2);
}

.timeline-title {
  color: #ffaa00;
  font-size: 0.85rem;
  font-weight: bold;
  letter-spacing: 1px;
}

.era-tabs {
  display: flex;
  gap: 4px;
  flex-wrap: wrap;
}

.era-btn {
  padding: 4px 10px;
  font-size: 0.6rem;
  background: rgba(0, 0, 0, 0.3);
  border: 1px solid rgba(255, 170, 0, 0.2);
  border-radius: 12px;
  color: #888;
  cursor: pointer;
  transition: all 0.2s;
}

.era-btn:hover {
  border-color: rgba(255, 170, 0, 0.5);
  color: #ffaa00;
}

.era-btn.active {
  background: rgba(255, 170, 0, 0.2);
  border-color: #ffaa00;
  color: #ffaa00;
}

.timeline-content {
  flex: 1;
  overflow-y: auto;
  position: relative;
  padding-left: 20px;
}

.timeline-line {
  position: absolute;
  left: 8px;
  top: 0;
  bottom: 0;
  width: 2px;
  background: linear-gradient(180deg, #ffaa00, #ff6b00, #00ffff);
  border-radius: 1px;
}

.timeline-item {
  position: relative;
  padding: 8px 0 8px 25px;
  cursor: pointer;
  animation: fadeInLeft 0.4s ease forwards;
  opacity: 0;
}

@keyframes fadeInLeft {
  from {
    opacity: 0;
    transform: translateX(-10px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

.timeline-dot {
  position: absolute;
  left: -12px;
  top: 12px;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 2px solid rgba(255, 255, 255, 0.3);
  box-shadow: 0 0 10px currentColor;
  transition: all 0.3s;
}

.timeline-item:hover .timeline-dot,
.timeline-item.active .timeline-dot {
  transform: scale(1.2);
  box-shadow: 0 0 20px currentColor;
}

.dot-icon {
  font-size: 0.8rem;
}

.timeline-card {
  background: rgba(0, 0, 0, 0.3);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  padding: 10px;
  transition: all 0.3s;
}

.timeline-item:hover .timeline-card,
.timeline-item.active .timeline-card {
  border-color: rgba(255, 170, 0, 0.4);
  background: rgba(255, 170, 0, 0.05);
}

.card-year {
  font-size: 0.9rem;
  font-weight: bold;
  margin-bottom: 4px;
}

.card-title {
  color: #fff;
  font-size: 0.75rem;
  font-weight: bold;
  margin-bottom: 4px;
}

.card-desc {
  color: #999;
  font-size: 0.65rem;
  line-height: 1.4;
}

.card-detail {
  margin-top: 10px;
  padding-top: 10px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  display: flex;
  flex-direction: column;
  gap: 6px;
  animation: slideDown 0.3s ease;
}

@keyframes slideDown {
  from {
    opacity: 0;
    max-height: 0;
  }
  to {
    opacity: 1;
    max-height: 100px;
  }
}

.detail-section {
  display: flex;
  gap: 8px;
  font-size: 0.65rem;
}

.detail-label {
  color: #888;
  min-width: 40px;
}

.detail-value {
  color: #ccc;
}

.timeline-footer {
  padding-top: 8px;
  border-top: 1px solid rgba(255, 170, 0, 0.2);
  text-align: center;
}

.footer-text {
  font-size: 0.6rem;
  color: #666;
}

/* 滚动条美化 */
.timeline-content::-webkit-scrollbar {
  width: 4px;
}

.timeline-content::-webkit-scrollbar-track {
  background: rgba(0, 0, 0, 0.2);
}

.timeline-content::-webkit-scrollbar-thumb {
  background: rgba(255, 170, 0, 0.4);
  border-radius: 2px;
}
</style>
