import { createI18n } from 'vue-i18n'

const messages = {
  zh: {
    nav: {
      back: '返回首页',
      erdDemo: 'ERD/ERS动画演示',
      brainGame: '脑电小游戏',
      home: '首页'
    },
    erd: {
      title: 'ERD/ERS 动画演示',
      subtitle: '事件相关去同步/同步 - 运动想象的核心机制',
      whatIsERD: '什么是ERD？',
      erdDesc: '事件相关去同步 (Event-Related Desynchronization) 是指在运动想象或运动执行时，大脑感觉运动皮层的Mu (8-13Hz) 和 Beta (13-30Hz) 频段能量显著下降的现象。',
      whatIsERS: '什么是ERS？',
      ersDesc: '事件相关同步 (Event-Related Synchronization) 是指运动结束后，相关频段能量短暂上升超过基线水平的现象，反映皮层抑制状态。',
      selectTask: '选择运动想象任务',
      leftHand: '🤚 左手运动想象',
      rightHand: '🤛 右手运动想象',
      feet: '🦶 双脚运动想象',
      rest: '😌 静息状态',
      activation: '激活区域',
      leftBrain: '左脑 (C3)',
      rightBrain: '右脑 (C4)',
      center: '中央 (Cz)',
      erdEffect: 'ERD效应',
      ersEffect: 'ERS效应',
      contralateral: '对侧控制原理',
      contralateralDesc: '大脑左半球控制右半身，右半球控制左半身。因此想象左手运动时，右脑C4区出现ERD；想象右手运动时，左脑C3区出现ERD。',
      muRhythm: 'Mu节律 (8-13Hz)',
      betaRhythm: 'Beta节律 (13-30Hz)',
      power: '能量',
      baseline: '基线',
      time: '时间',
      frequency: '频率',
      powerChange: '能量变化',
      erdExplanation: 'ERD原理',
      erdExplanationText: '当你想象运动时，大脑皮层中负责该运动的区域会"激活"，神经元同步放电，导致该频段的脑电能量下降。这就是ERD现象。BCI系统正是通过检测ERD来识别用户的运动意图。',
      ersExplanation: 'ERS原理',
      ersExplanationText: '运动结束后，皮层进入抑制状态，脑电能量短暂上升超过基线水平，形成ERS。ERS反映了皮层的"休息"状态。',
      interactive: '交互演示',
      interactiveDesc: '点击下方按钮，观察不同运动想象任务下大脑各区域的活动变化。注意ERD区域（能量下降）和ERS区域（能量上升）的位置变化。',
      watchDemo: '观看演示',
      startDemo: '开始演示',
      stopDemo: '停止演示'
    },
    game: {
      title: '脑电小游戏',
      subtitle: '通过运动想象控制小球移动',
      instruction: '点击按钮模拟运动想象信号，控制小球避开障碍物',
      startGame: '开始游戏',
      pauseGame: '暂停',
      resumeGame: '继续',
      gameOver: '游戏结束',
      score: '得分',
      highScore: '最高分',
      leftImagery: '左手想象',
      rightImagery: '右手想象',
      footImagery: '双脚想象',
      moveLeft: '向左移动',
      moveRight: '向右移动',
      jump: '跳跃',
      signalStrength: '信号强度',
      eegSignal: 'EEG信号',
      classification: '分类结果',
      playAgain: '再来一局',
      howToPlay: '如何游戏',
      howToPlayText: '使用运动想象控制小球：左手想象→左移，右手想象→右移，双脚想象→跳跃。避开红色障碍物，收集绿色能量球获得分数。',
      difficulty: '难度',
      easy: '简单',
      normal: '普通',
      hard: '困难',
      level: '关卡'
    },
    common: {
      theme: {
        dark: '深色模式',
        light: '浅色模式',
        toggle: '切换主题'
      },
      language: {
        zh: '中文',
        en: 'English',
        switch: '切换语言'
      }
    }
  },
  en: {
    nav: {
      back: 'Back to Home',
      erdDemo: 'ERD/ERS Animation',
      brainGame: 'Brain Game',
      home: 'Home'
    },
    erd: {
      title: 'ERD/ERS Animation Demo',
      subtitle: 'Event-Related Desynchronization/Synchronization - Core Mechanism of Motor Imagery',
      whatIsERD: 'What is ERD?',
      erdDesc: 'Event-Related Desynchronization (ERD) refers to the significant decrease in Mu (8-13Hz) and Beta (13-30Hz) band energy in the sensorimotor cortex during motor imagery or execution.',
      whatIsERS: 'What is ERS?',
      ersDesc: 'Event-Related Synchronization (ERS) is the phenomenon where band energy briefly rises above baseline after movement ends, reflecting cortical inhibition.',
      selectTask: 'Select Motor Imagery Task',
      leftHand: '🤚 Left Hand Imagery',
      rightHand: '🤛 Right Hand Imagery',
      feet: '🦶 Feet Imagery',
      rest: '😌 Rest State',
      activation: 'Activation Area',
      leftBrain: 'Left Brain (C3)',
      rightBrain: 'Right Brain (C4)',
      center: 'Center (Cz)',
      erdEffect: 'ERD Effect',
      ersEffect: 'ERS Effect',
      contralateral: 'Contralateral Control',
      contralateralDesc: 'The left hemisphere controls the right body side and vice versa. Thus, left hand imagery causes ERD in right brain C4; right hand imagery causes ERD in left brain C3.',
      muRhythm: 'Mu Rhythm (8-13Hz)',
      betaRhythm: 'Beta Rhythm (13-30Hz)',
      power: 'Power',
      baseline: 'Baseline',
      time: 'Time',
      frequency: 'Frequency',
      powerChange: 'Power Change',
      erdExplanation: 'ERD Principle',
      erdExplanationText: 'When you imagine movement, the cortical area responsible for that movement "activates," neurons fire synchronously, causing a decrease in EEG power at that frequency band. This is the ERD phenomenon. BCI systems detect ERD to identify user intentions.',
      ersExplanation: 'ERS Principle',
      ersExplanationText: 'After movement ends, the cortex enters an inhibitory state, with EEG power briefly rising above baseline, forming ERS. ERS reflects the cortical "rest" state.',
      interactive: 'Interactive Demo',
      interactiveDesc: 'Click the buttons below to observe activity changes in different brain regions during various motor imagery tasks. Watch the ERD (power decrease) and ERS (power increase) regions.',
      watchDemo: 'Watch Demo',
      startDemo: 'Start Demo',
      stopDemo: 'Stop Demo'
    },
    game: {
      title: 'Brain-EEG Game',
      subtitle: 'Control the ball with motor imagery',
      instruction: 'Click buttons to simulate motor imagery signals, control the ball to avoid obstacles',
      startGame: 'Start Game',
      pauseGame: 'Pause',
      resumeGame: 'Resume',
      gameOver: 'Game Over',
      score: 'Score',
      highScore: 'High Score',
      leftImagery: 'Left Hand Imagery',
      rightImagery: 'Right Hand Imagery',
      footImagery: 'Feet Imagery',
      moveLeft: 'Move Left',
      moveRight: 'Move Right',
      jump: 'Jump',
      signalStrength: 'Signal Strength',
      eegSignal: 'EEG Signal',
      classification: 'Classification',
      playAgain: 'Play Again',
      howToPlay: 'How to Play',
      howToPlayText: 'Use motor imagery to control the ball: Left Hand → Move Left, Right Hand → Move Right, Feet → Jump. Avoid red obstacles and collect green energy orbs for points.',
      difficulty: 'Difficulty',
      easy: 'Easy',
      normal: 'Normal',
      hard: 'Hard',
      level: 'Level'
    },
    common: {
      theme: {
        dark: 'Dark Mode',
        light: 'Light Mode',
        toggle: 'Toggle Theme'
      },
      language: {
        zh: '中文',
        en: 'English',
        switch: 'Switch Language'
      }
    }
  }
}

const i18n = createI18n({
  legacy: false,
  locale: 'zh',
  fallbackLocale: 'zh',
  messages
})

export default i18n
