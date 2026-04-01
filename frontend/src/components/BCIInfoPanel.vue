<template>
  <div class="bci-info-panel">
    <div class="info-tabs">
      <button 
        v-for="tab in tabs" 
        :key="tab.id"
        class="tab-btn"
        :class="{ active: activeTab === tab.id }"
        @click="activeTab = tab.id"
      >
        {{ tab.icon }} {{ tab.label }}
      </button>
    </div>
    
    <div class="tab-content">
      <!-- Algorithm Flow -->
      <div v-if="activeTab === 'flow'" class="flow-content">
        <div class="flow-title">算法处理流程</div>
        <div class="flow-chart">
          <div class="flow-step">
            <div class="step-box input">📥 原始EEG</div>
            <div class="flow-arrow">→</div>
          </div>
          <div class="flow-step">
            <div class="step-box process">🔧 预处理</div>
            <div class="step-detail">陷波50Hz + 带通8-30Hz</div>
            <div class="flow-arrow">→</div>
          </div>
          <div class="flow-step">
            <div class="step-box process">📊 PCA降维</div>
            <div class="step-detail">64维 → 16维</div>
            <div class="flow-arrow">→</div>
          </div>
          <div class="flow-step">
            <div class="step-box model">🧠 Hopfield网络</div>
            <div class="step-detail">联想记忆分类</div>
            <div class="flow-arrow">→</div>
          </div>
          <div class="flow-step">
            <div class="step-box output">🎯 分类结果</div>
            <div class="step-detail">左手/右手/脚</div>
          </div>
        </div>
      </div>
      
      <!-- Math Formulas -->
      <div v-if="activeTab === 'math'" class="math-content">
        <div class="formula-card">
          <div class="formula-title">Hopfield能量函数</div>
          <div class="formula">
            <span class="f-math">E = -½ ΣΣ w<sub>ij</sub> x<sub>i</sub> x<sub>j</sub></span>
          </div>
          <div class="formula-desc">能量随迭代单调递减，网络收敛到稳定状态</div>
        </div>
        
        <div class="formula-card">
          <div class="formula-title">权重矩阵</div>
          <div class="formula">
            <span class="f-math">W = Σ (x<sup>p</sup>)(x<sup>p</sup>)<sup>T</sup> - nI</span>
          </div>
          <div class="formula-desc">Hebb学习规则，n为模式数量</div>
        </div>
        
        <div class="formula-card">
          <div class="formula-title">PCA协方差</div>
          <div class="formula">
            <span class="f-math">C = (1/n) X<sup>T</sup>X</span>
          </div>
          <div class="formula-desc">主成分分析降维核心公式</div>
        </div>
        
        <div class="formula-card">
          <div class="formula-title">更新规则</div>
          <div class="formula">
            <span class="f-math">x<sub>i</sub>(t+1) = sign(Σ w<sub>ij</sub> x<sub>j</sub>(t))</span>
          </div>
          <div class="formula-desc">异步更新直到收敛</div>
        </div>
      </div>
      
      <!-- Parameters -->
      <div v-if="activeTab === 'params'" class="params-content">
        <div class="param-section">
          <div class="section-title">采集参数</div>
          <div class="param-row">
            <span class="param-label">采样率</span>
            <span class="param-value">250 Hz</span>
          </div>
          <div class="param-row">
            <span class="param-label">通道数</span>
            <span class="param-value">64通道 (10-20系统)</span>
          </div>
          <div class="param-row">
            <span class="param-label">分辨率</span>
            <span class="param-value">24位</span>
          </div>
        </div>
        
        <div class="param-section">
          <div class="section-title">预处理参数</div>
          <div class="param-row">
            <span class="param-label">陷波频率</span>
            <span class="param-value">50Hz (工频干扰)</span>
          </div>
          <div class="param-row">
            <span class="param-label">带通范围</span>
            <span class="param-value">8-30Hz</span>
          </div>
          <div class="param-row">
            <span class="param-label">时间窗</span>
            <span class="param-value">250-750ms</span>
          </div>
        </div>
        
        <div class="param-section">
          <div class="section-title">模型参数</div>
          <div class="param-row">
            <span class="param-label">PCA维度</span>
            <span class="param-value">16</span>
          </div>
          <div class="param-row">
            <span class="param-label">被试数量</span>
            <span class="param-value">109 (BCI Competition IV)</span>
          </div>
          <div class="param-row">
            <span class="param-label">平均准确率</span>
            <span class="param-value highlight">85.6%</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const activeTab = ref('flow')

const tabs = [
  { id: 'flow', label: '流程', icon: '📊' },
  { id: 'math', label: '公式', icon: '📐' },
  { id: 'params', label: '参数', icon: '⚙️' }
]
</script>

<style scoped>
.bci-info-panel {
  background: rgba(0, 10, 20, 0.8);
  border: 1px solid rgba(0, 255, 255, 0.3);
  border-radius: 12px;
  padding: 12px;
  backdrop-filter: blur(10px);
}

.info-tabs {
  display: flex;
  gap: 6px;
  margin-bottom: 12px;
}

.tab-btn {
  flex: 1;
  padding: 8px;
  background: rgba(0, 20, 30, 0.6);
  border: 1px solid rgba(0, 255, 255, 0.2);
  border-radius: 6px;
  color: #888;
  font-size: 0.7rem;
  cursor: pointer;
  transition: all 0.2s;
}

.tab-btn:hover {
  border-color: rgba(0, 255, 255, 0.5);
  color: #ccc;
}

.tab-btn.active {
  background: rgba(0, 255, 255, 0.15);
  border-color: #00ffff;
  color: #00ffff;
}

.tab-content {
  min-height: 200px;
}

/* Flow Chart */
.flow-title {
  color: #00ffff;
  font-size: 0.75rem;
  margin-bottom: 12px;
  text-align: center;
}

.flow-chart {
  display: flex;
  flex-direction: column;
  gap: 4px;
  align-items: center;
}

.flow-step {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
}

.step-box {
  padding: 8px 20px;
  border-radius: 6px;
  font-size: 0.75rem;
  font-weight: bold;
  text-align: center;
  min-width: 140px;
}

.step-box.input {
  background: rgba(0, 255, 255, 0.15);
  border: 1px solid rgba(0, 255, 255, 0.4);
  color: #00ffff;
}

.step-box.process {
  background: rgba(255, 107, 0, 0.15);
  border: 1px solid rgba(255, 107, 0, 0.4);
  color: #ff6b00;
}

.step-box.model {
  background: rgba(0, 255, 136, 0.15);
  border: 1px solid rgba(0, 255, 136, 0.4);
  color: #00ff88;
}

.step-box.output {
  background: rgba(255, 170, 0, 0.15);
  border: 1px solid rgba(255, 170, 0, 0.4);
  color: #ffaa00;
}

.step-detail {
  font-size: 0.6rem;
  color: #888;
}

.flow-arrow {
  color: #00ffff;
  font-size: 1rem;
  animation: arrow-pulse 1s infinite;
}

@keyframes arrow-pulse {
  0%, 100% { opacity: 0.5; }
  50% { opacity: 1; }
}

/* Math Formulas */
.formula-card {
  background: rgba(0, 20, 30, 0.6);
  border: 1px solid rgba(0, 255, 255, 0.2);
  border-radius: 8px;
  padding: 10px;
  margin-bottom: 8px;
}

.formula-title {
  color: #ff6b00;
  font-size: 0.7rem;
  margin-bottom: 6px;
}

.formula {
  background: rgba(0, 0, 0, 0.3);
  padding: 8px;
  border-radius: 4px;
  text-align: center;
  margin-bottom: 6px;
}

.f-math {
  color: #00ffff;
  font-family: 'Courier New', monospace;
  font-size: 0.85rem;
  letter-spacing: 1px;
}

.formula-desc {
  font-size: 0.6rem;
  color: #888;
}

/* Parameters */
.param-section {
  margin-bottom: 12px;
}

.section-title {
  color: #00ffff;
  font-size: 0.7rem;
  margin-bottom: 8px;
  padding-bottom: 4px;
  border-bottom: 1px solid rgba(0, 255, 255, 0.2);
}

.param-row {
  display: flex;
  justify-content: space-between;
  padding: 4px 0;
}

.param-label {
  color: #888;
  font-size: 0.65rem;
}

.param-value {
  color: #ccc;
  font-size: 0.65rem;
}

.param-value.highlight {
  color: #00ff88;
  font-weight: bold;
}
</style>