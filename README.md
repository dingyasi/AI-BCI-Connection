# 🧠 BCI脑机接口 - 基于Hopfield神经网络的运动想象分类系统

> **本科毕业设计项目** - 连接思维，探索未来

![Vue](https://img.shields.io/badge/Vue-3-green)
![TypeScript](https://img.shields.io/badge/TypeScript-5.3-blue)
![Algorithm](https://img.shields.io/badge/Hopfield-85.6%25-orange)
![License](https://img.shields.io/badge/License-MIT-yellow)

---

## 📸 效果展示

### 🏠 首页 - 3D交互大脑

![进入脑机接口的世界](image/进入脑机接口的世界.gif)

*科幻风格的着陆页 - 3D大脑模型与神经元粒子动画*

---

### 📊 主应用界面

![主界面](image/1first.gif)

**功能亮点：**
- 左侧面板：实时EEG波形、地形图、频谱分析、Hopfield分类结果
- 右侧面板：3D交互式大脑模型
- 底部功能按钮：脑科学普、BCI历史、AI助手、脑电游戏

---

### 🎮 脑电小游戏

![脑电小游戏](image/脑电小游戏.gif)

**游戏玩法：**
- 🤛 想象左手 → 飞机上升（右脑C4区ERD）
- 🤚 想象右手 → 飞机下降（左脑C3区ERD）
- 避开障碍物，收集能量球得分

---

### 🧠 脑科学普

![脑科学普](image/脑科学普.gif)

**科普内容：**
- 大脑区域功能介绍（M1、PMC、S1、PFC、枕叶、顶叶）
- BCI基础知识（信号类型、三大范式）
- 未来发展展望（2025-2050）

---

### 📅 BCI发展史

![BCI历史](image/BCI历史.gif)

**时间线亮点：**
- 1924年：Hans Berger发现脑电波
- 2004年：BrainGate首次人体试验
- 2024年：本项目Hopfield网络BCI
- 2030年：双向BCI预计突破

---

### 🤖 AI专家助手

![AI助手](image/AI助手.gif)

**智能问答：**
- Hopfield网络原理详解
- EEG信号处理方法
- 运动想象特征识别
- 支持语音输入

---

## 🔬 技术架构

### 前端技术栈

| 技术 | 版本 | 用途 |
|------|------|------|
| **Vue 3** | 3.4+ | 核心框架 |
| **TypeScript** | 5.3+ | 类型安全 |
| **Vite** | 5.0+ | 构建工具 |
| **Element Plus** | 2.4+ | UI组件 |
| **Three.js** | 0.160+ | 3D渲染 |
| **Vue Router** | 4.x | 路由管理 |
| **Vue I18n** | 9.x | 国际化 |

### 后端技术栈

| 技术 | 用途 |
|------|------|
| **FastAPI** | Web框架 |
| **LangChain** | LLM集成 |
| **OpenAI API** | AI问答 |

### 算法核心

| 技术 | 说明 |
|------|------|
| **Hopfield神经网络** | 联想记忆分类器 |
| **PCA** | 特征降维（16维） |
| **EEG预处理** | 陷波50Hz + 带通8-30Hz |

---

## 📁 项目结构

```
study/
├── frontend/                    # Vue3前端
│   ├── src/
│   │   ├── App.vue             # 根组件
│   │   ├── main.ts             # 入口文件
│   │   ├── views/
│   │   │   ├── Home.vue        # 主页（含3D大脑）
│   │   │   └── BrainGame.vue   # 脑电游戏
│   │   ├── components/
│   │   │   ├── Brain3D.vue              # 3D大脑模型
│   │   │   ├── BCIMotionAnalyzer.vue    # BCI分析面板
│   │   │   ├── BrainRegionExplainer.vue # 脑科学普
│   │   │   └── BCITimeline.vue          # 发展史时间线
│   │   ├── router/index.ts     # 路由配置
│   │   └── i18n/index.ts       # 多语言
│   └── package.json
│
├── backend/                     # FastAPI后端
│   ├── app/
│   │   ├── api/
│   │   │   ├── agent.py        # AI问答接口
│   │   │   └── train.py        # 训练接口
│   │   ├── algorithm/
│   │   │   ├── pca.py          # PCA降维
│   │   │   └── hopfield.py     # Hopfield网络
│   │   └── main.py             # FastAPI入口
│   └── requirements.txt
│
├── matlab/                      # MATLAB算法
│   ├── train_hopfield.m        # Hopfield训练
│   ├── preprocess_eeg.m        # EEG预处理
│   └── processed/              # 预处理数据
│       ├── hopfield_model_all.mat
│       └── S001-S109.mat
│
├── image/                       # 项目截图
│   ├── 1first.gif
│   ├── 进入脑机接口的世界.gif
│   ├── 脑电小游戏.gif
│   ├── 脑科学普.gif
│   ├── BCI历史.gif
│   └── AI助手.gif
│
└── README.md
```

---

## 🚀 快速开始

### 环境要求

- Node.js 18+
- Python 3.10+
- MATLAB R2023a+（可选，用于算法训练）

### 前端启动

```bash
cd frontend
npm install
npm run dev
```

访问 http://localhost:5173

### 后端启动

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

访问 http://localhost:8000/docs 查看API文档

### MATLAB训练（可选）

```bash
cd matlab
matlab -batch "train_hopfield"
```

---

## 📊 模型性能

| 指标 | 数值 |
|------|------|
| 被试数量 | 109 |
| 分类准确率 | **85.6%** |
| PCA维度 | 16 |
| 预处理 | 陷波50Hz + 带通8-30Hz + Z-score |
| 采样率 | 160 Hz |
| 电极数 | 64 |
| 数据集 | BCI Competition IV Dataset 2a |

---

## 🔬 BCI原理简介

### 什么是脑机接口？

脑机接口（Brain-Computer Interface, BCI）是一种在大脑与外部设备之间建立**直接通信通道**的技术，无需依赖肌肉或外周神经。

### 运动想象与ERD

当人想象肢体运动时，大脑感觉运动皮层的 **Mu节律（8-13Hz）** 和 **Beta节律（13-30Hz）** 能量会显著下降：

```
想象左手运动 → 右脑C4区ERD
想象右手运动 → 左脑C3区ERD
想象双脚运动 → 中央Cz区ERD
```

**对侧控制原理**：大脑左半球控制右半身，右半球控制左半身。

### Hopfield神经网络

本项目使用Hopfield联想记忆网络进行分类：
- **输入**：PCA降维后的EEG特征（16维）
- **学习规则**：Hebb学习
- **能量函数**：$E = -\frac{1}{2}\sum_{i \neq j} w_{ij} s_i s_j$
- **准确率**：85.6%（109名被试）

---

## 🔧 API文档

### 训练接口
```bash
POST /api/v1/train/train
{
  "subject_id": "S001",
  "n_components": 16,
  "max_iterations": 1000
}
```

### 问答接口
```bash
POST /api/v1/agent/qa
{
  "question": "什么是Hopfield神经网络?"
}
```

---

## 📖 核心概念速查

| 概念 | 说明 |
|------|------|
| **EEG** | 脑电图 - 通过头皮电极记录的大脑电活动 |
| **BCI** | 脑机接口 - 大脑与计算机的直接通信 |
| **PCA** | 主成分分析 - 降维方法 |
| **ERD** | 事件相关去同步 - 运动想象时的能量下降 |
| **ERS** | 事件相关同步 - 运动后能量上升 |
| **Hebb规则** | "一起激活的神经元连接加强" |
| **能量函数** | Hopfield网络的稳定性指标 |

---

## 🙏 致谢

- **BCI Competition IV** - 提供标准数据集
- **Vue.js团队** - 优秀的前端框架
- **Three.js社区** - 强大的3D渲染库

---

## 📄 License

MIT License

---

<div align="center">

**🧠 连接思维，探索未来 🧠**

Made with ❤️ for BCI Research

</div>
