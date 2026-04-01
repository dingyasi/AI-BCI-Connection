<template>
  <div ref="containerRef" class="brain3d-container" @click="handleClick" @dblclick="handleDoubleClick">
    <canvas ref="canvasRef"></canvas>
    
    <!-- Hover tooltip -->
    <div v-if="hoveredNeuron" class="neuron-tooltip" :style="{
      top: (currentEvent?.clientY || 0) + 'px',
      left: (currentEvent?.clientX || 0) + 'px'
    }">
      <div class="tooltip-header">⚡ {{ hoveredNeuron.typeName }}</div>
      <div class="tooltip-row">
        <span class="tooltip-label">区域</span>
        <span class="tooltip-value">{{ hoveredNeuron.region }}</span>
      </div>
      <div class="tooltip-row">
        <span class="tooltip-label">信号</span>
        <span class="tooltip-value highlight">{{ hoveredNeuron.signal }}</span>
      </div>
      <div class="tooltip-row">
        <span class="tooltip-label">频率</span>
        <span class="tooltip-value">{{ hoveredNeuron.freq }}Hz</span>
      </div>
      <div class="tooltip-row">
        <span class="tooltip-label">活动度</span>
        <div class="activity-bar">
          <div class="activity-fill" :style="{width: hoveredNeuron.activity + '%'}"></div>
        </div>
      </div>
    </div>
    
    
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount } from 'vue'
import * as THREE from 'three'
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js'

const containerRef = ref<HTMLDivElement>()
const canvasRef = ref<HTMLCanvasElement>()
const activityFreq = ref('12.4')
const hoveredNeuron = ref<{
  typeName: string, 
  region: string, 
  signal: string, 
  freq: string,
  activity: number
} | null>(null)

let scene: THREE.Scene
let camera: THREE.PerspectiveCamera
let renderer: THREE.WebGLRenderer
let controls: OrbitControls
let brainGroup: THREE.Group
let neurons: THREE.Mesh[] = []
let connections: THREE.Line[] = []
let raycaster: THREE.Raycaster
let mouse: THREE.Vector2
let mouseWorldPos: THREE.Vector3
let animationId: number
let clock: THREE.Clock
const currentEvent = ref<MouseEvent | null>(null)

const emit = defineEmits<{
  brainClick: []
}>()

// Smooth noise function for organic patterns
const smoothNoise = (x: number, y: number, z: number): number => {
  const dot = x * 12.9898 + y * 78.233 + z * 45.164
  const s = Math.sin(dot) * 43758.5453
  return (s - Math.floor(s)) * 2 - 1
}

const smoothedNoise = (x: number, y: number, z: number): number => {
  const ix = Math.floor(x), iy = Math.floor(y), iz = Math.floor(z)
  const fx = x - ix, fy = y - iy, fz = z - iz
  
  const sx = fx * fx * (3 - 2 * fx)
  const sy = fy * fy * (3 - 2 * fy)
  const sz = fz * fz * (3 - 2 * fz)
  
  const n000 = smoothNoise(ix, iy, iz)
  const n100 = smoothNoise(ix + 1, iy, iz)
  const n010 = smoothNoise(ix, iy + 1, iz)
  const n110 = smoothNoise(ix + 1, iy + 1, iz)
  const n001 = smoothNoise(ix, iy, iz + 1)
  const n101 = smoothNoise(ix + 1, iy, iz + 1)
  const n011 = smoothNoise(ix, iy + 1, iz + 1)
  const n111 = smoothNoise(ix + 1, iy + 1, iz + 1)
  
  const nx00 = n000 * (1 - sx) + n100 * sx
  const nx10 = n010 * (1 - sx) + n110 * sx
  const nx01 = n001 * (1 - sx) + n101 * sx
  const nx11 = n011 * (1 - sx) + n111 * sx
  
  const nxy0 = nx00 * (1 - sy) + nx10 * sy
  const nxy1 = nx01 * (1 - sy) + nx11 * sy
  
  return nxy0 * (1 - sz) + nxy1 * sz
}

// Create realistic brain with anatomically correct folds
// Reference: BrainBrowser style brain surface
const createBrainGeometry = (): THREE.BufferGeometry => {
  const geometry = new THREE.SphereGeometry(1, 180, 128)
  const positions = geometry.attributes.position.array as Float32Array
  
  for (let i = 0; i < positions.length; i += 3) {
    let x = positions[i]
    let y = positions[i + 1]
    let z = positions[i + 2]
    
    // Normalize to get direction
    const len = Math.sqrt(x * x + y * y + z * z)
    const nx = x / len, ny = y / len, nz = z / len
    
    // ===== BRAIN PROPORTIONS (more rounded/full) =====
    x *= 1.55  // width
    y *= 1.15  // height - increased for more fullness
    z *= 1.4   // depth
    
    // ===== BASE SHAPE =====
    
    // Flatten bottom slightly (brain base) - less flat
    if (ny < -0.1) {
      const t = Math.min(1, Math.abs(ny + 0.1) / 0.9)
      y = -0.35 - t * 0.18
    }
    
    // Dome the top - more prominent
    if (ny > 0.3) {
      const t = (ny - 0.3) / 0.7
      y *= 1 + t * 0.22
    }
    
    // Round frontal lobe (front is more bulbous)
    if (nz > 0.4) {
      const t = Math.min(1, (nz - 0.4) / 0.6)
      z += Math.pow(t, 0.7) * 0.12
    }
    
    // Taper occipital lobe (back is more pointed)
    if (nz < -0.4) {
      const t = Math.min(1, Math.abs(nz + 0.4) / 0.6)
      const taper = 1 - Math.pow(t, 1.3) * 0.18
      z *= taper
    }
    
    // ===== TEMPORAL LOBES (bulge on lower sides) =====
    if (y > -0.35 && y < 0.2 && Math.abs(x) > 0.7) {
      const yFactor = 1 - Math.pow((y - (-0.08)) / 0.3, 2)
      const xFactor = Math.min(1, (Math.abs(x) - 0.7) / 0.5)
      const zFactor = Math.exp(-Math.pow(z / 0.8, 2))
      const bulge = Math.max(0, yFactor) * xFactor * zFactor * 0.15
      x += Math.sign(x) * bulge
    }
    
    // ===== LONGITUDINAL FISSURE (deep central groove) =====
    if (y > -0.1 && Math.abs(x) < 0.2) {
      const xFactor = Math.exp(-Math.pow(Math.abs(x) / 0.06, 2))
      const yFactor = Math.pow(Math.max(0, (y + 0.1) / 0.9), 0.6)
      y -= 0.2 * xFactor * yFactor
    }
    
    // ===== ANATOMICAL SULCI (major grooves) =====
    // These follow actual brain anatomy
    
    const theta = Math.atan2(z, x)  // angle around Y axis
    const phi = Math.acos(Math.max(-1, Math.min(1, ny)))  // angle from top
    
    // Central sulcus (separates frontal from parietal) - runs top to side
    const centralSulcus = Math.sin(phi * 2.5 - 0.3) * Math.cos(theta * 0.8)
    const centralDepth = Math.max(0, centralSulcus) * 0.06
    
    // Lateral sulcus (Sylvian fissure) - separates temporal lobe
    const lateralSulcus = Math.sin(phi * 3.5 + 0.8) * Math.cos(theta * 1.2 + 0.5)
    const lateralDepth = Math.max(0, lateralSulcus) * 0.05
    
    // Parieto-occipital sulcus
    const poSulcus = Math.sin(phi * 2 + 1.5) * Math.cos(theta * 1.5 + 1.2)
    const poDepth = Math.max(0, poSulcus) * 0.04
    
    // ===== GYRI PATTERN (the characteristic brain ridges) =====
    // Multiple frequencies for realistic look
    
    // Large folds (major gyri)
    const largeGyri1 = Math.sin(theta * 7 + phi * 5) * 0.035
    const largeGyri2 = Math.sin(theta * 6 - phi * 4 + 1.0) * 0.03
    const largeGyri3 = Math.sin(theta * 5 + phi * 7 + 2.1) * 0.028
    
    // Medium folds
    const medGyri1 = Math.sin(theta * 14 + phi * 10) * 0.018
    const medGyri2 = Math.sin(theta * 12 - phi * 8 + 0.6) * 0.015
    const medGyri3 = Math.sin(phi * 16 + theta * 9 + 1.4) * 0.012
    
    // Fine folds (small gyri)
    const fineGyri1 = Math.sin(theta * 24 + phi * 18) * 0.008
    const fineGyri2 = Math.sin(theta * 20 - phi * 22 + 0.9) * 0.006
    
    // Very fine texture
    const micro1 = Math.sin(theta * 35 + phi * 28) * 0.004
    const micro2 = Math.sin(theta * 30 - phi * 32 + 1.7) * 0.003
    
    // ===== COMBINE ALL DISPLACEMENTS =====
    // Sulci go IN (negative), gyri go OUT (positive)
    
    const sulciDisplacement = -(centralDepth + lateralDepth + poDepth)
    const gyriDisplacement = largeGyri1 + largeGyri2 + largeGyri3
                            + medGyri1 + medGyri2 + medGyri3
                            + fineGyri1 + fineGyri2
                            + micro1 + micro2
    
    const totalDisplacement = sulciDisplacement + gyriDisplacement
    
    // Apply along surface normal
    x += nx * totalDisplacement
    y += ny * totalDisplacement
    z += nz * totalDisplacement
    
    positions[i] = x
    positions[i + 1] = y
    positions[i + 2] = z
  }
  
  geometry.computeVertexNormals()
  return geometry
}

// Create cerebellum - the "little brain" at back-bottom
const createCerebellum = (): THREE.BufferGeometry => {
  const geometry = new THREE.SphereGeometry(0.48, 64, 48)
  const positions = geometry.attributes.position.array as Float32Array
  
  for (let i = 0; i < positions.length; i += 3) {
    let x = positions[i]
    let y = positions[i + 1]
    let z = positions[i + 2]
    
    const len = Math.sqrt(x * x + y * y + z * z)
    const nx = x / len, ny = y / len, nz = z / len
    
    // Cerebellum shape: wide, flat, with two hemispheres
    x *= 1.4   // wide
    y *= 0.45  // very flat
    z *= 1.0   // normal depth
    
    // Flatten bottom
    if (ny < 0) {
      y *= 0.6
    }
    
    // Slight bulge on sides (cerebellar hemispheres)
    const sideBulge = Math.exp(-Math.pow(Math.abs(x) - 0.8, 2) * 5) * 
                     Math.exp(-Math.pow(y, 2) * 3)
    x *= 1 + sideBulge * 0.15
    
    // Prominent parallel grooves (folia)
    const folia1 = Math.sin(y * 45) * 0.02
    const folia2 = Math.sin(z * 30 + y * 20) * 0.012
    
    x += nx * (folia1 + folia2)
    z += nz * folia1
    
    positions[i] = x
    positions[i + 1] = y
    positions[i + 2] = z
  }
  
  geometry.computeVertexNormals()
  geometry.translate(0, -0.65, -1.15)  // Position below and behind brain
  return geometry
}

// Create brain stem - curved tube connecting to spinal cord
const createBrainstem = (): THREE.BufferGeometry => {
  const geometry = new THREE.CylinderGeometry(0.1, 0.08, 0.55, 16)
  const positions = geometry.attributes.position.array as Float32Array
  
  for (let i = 0; i < positions.length; i += 3) {
    let x = positions[i]
    let y = positions[i + 1]
    let z = positions[i + 2]
    
    // Curve forward as it goes down (anatomically correct)
    const t = (y + 0.275) / 0.55  // 0 to 1 from top to bottom
    z += t * 0.15  // forward curve
    
    // Slight widening at top (medulla)
    const widen = 1 + (1 - t) * 0.15
    x *= widen
    
    positions[i] = x
    positions[i + 1] = y
    positions[i + 2] = z
  }
  
  geometry.computeVertexNormals()
  geometry.translate(0, -1.05, -0.9)  // Position below cerebellum
  geometry.rotateX(0.15)  // Slight forward tilt
  return geometry
}

const createBrain = () => {
  // Main brain hemispheres - sci-fi style
  const brainGeometry = createBrainGeometry()
  
  // Layer 1: Inner glow core
  const innerMat = new THREE.MeshBasicMaterial({
    color: 0x00ffff,
    transparent: true,
    opacity: 0.3
  })
  const innerMesh = new THREE.Mesh(brainGeometry.clone(), innerMat)
  innerMesh.scale.setScalar(0.92)
  brainGroup.add(innerMesh)
  
  // Layer 2: Main brain surface - holographic style
  const brainMaterial = new THREE.MeshPhongMaterial({
    color: 0x0a2a4a,  // Deep blue
    emissive: 0x001a33,  // Cyan glow
    specular: 0x00ffff,
    shininess: 40,
    transparent: true,
    opacity: 0.7
  })
  const brainMesh = new THREE.Mesh(brainGeometry, brainMaterial)
  brainGroup.add(brainMesh)
  
  // Layer 3: Wireframe overlay - bright cyan
  const wireMaterial = new THREE.MeshBasicMaterial({
    color: 0x00ffff,
    wireframe: true,
    transparent: true,
    opacity: 0.15
  })
  const wireMesh = new THREE.Mesh(brainGeometry.clone(), wireMaterial)
  brainGroup.add(wireMesh)
  
  // Layer 4: Outer edge glow
  const glowMaterial = new THREE.MeshBasicMaterial({
    color: 0x00ffff,
    transparent: true,
    opacity: 0.1,
    side: THREE.BackSide
  })
  const glowMesh = new THREE.Mesh(brainGeometry.clone(), glowMaterial)
  glowMesh.scale.setScalar(1.03)
  brainGroup.add(glowMesh)
  
  // Cerebellum - sci-fi style
  const cerebellumGeometry = createCerebellum()
  const cerebellumMat = new THREE.MeshPhongMaterial({
    color: 0x0a2a4a,
    emissive: 0x001a33,
    specular: 0xff6b00,
    shininess: 30,
    transparent: true,
    opacity: 0.6
  })
  const cerebellum = new THREE.Mesh(cerebellumGeometry, cerebellumMat)
  brainGroup.add(cerebellum)
  
  // Cerebellum wireframe
  const cerebellumWire = new THREE.Mesh(cerebellumGeometry.clone(), wireMaterial.clone())
  brainGroup.add(cerebellumWire)
  
  // Brain stem - with orange accent
  const brainstemGeometry = createBrainstem()
  const brainstemMat = new THREE.MeshPhongMaterial({
    color: 0x1a1a3a,
    emissive: 0x331100,
    specular: 0xff6b00,
    shininess: 20,
    transparent: true,
    opacity: 0.7
  })
  const brainstem = new THREE.Mesh(brainstemGeometry, brainstemMat)
  brainGroup.add(brainstem)
  
  // Central energy core
  const coreGeo = new THREE.IcosahedronGeometry(0.3, 2)
  const coreMat = new THREE.MeshBasicMaterial({
    color: 0x00ffff,
    transparent: true,
    opacity: 0.5,
    wireframe: true
  })
  const core = new THREE.Mesh(coreGeo, coreMat)
  core.name = 'brainCore'
  brainGroup.add(core)
}

const createNeurons = () => {
  const neuronCount = 400  // Increased from 200
  const neuronGeo = new THREE.SphereGeometry(0.015, 8, 8)
  
  for (let i = 0; i < neuronCount; i++) {
    const theta = Math.random() * Math.PI * 2
    const phi = Math.acos(2 * Math.random() - 1)
    const r = 0.88 + Math.random() * 0.3
    
    let x = r * Math.sin(phi) * Math.cos(theta) * 1.5
    let y = r * Math.cos(phi) * 1.1
    let z = r * Math.sin(phi) * Math.sin(theta) * 1.35
    
    // Variety of neuron types with different colors
    const typeRand = Math.random()
    const color = new THREE.Color()
    let neuronType = 'normal'
    
    if (typeRand > 0.85) {
      color.setHex(0xffffff)  // White - interneurons
      neuronType = 'inter'
    } else if (typeRand > 0.65) {
      color.setHex(0xff6b00)  // Orange - excitatory
      neuronType = 'excite'
    } else if (typeRand > 0.45) {
      color.setHex(0x00ff88)  // Green - inhibitory
      neuronType = 'inhibit'
    } else if (typeRand > 0.25) {
      color.setHex(0xff00ff)  // Magenta - motor neurons
      neuronType = 'motor'
    } else {
      color.setHex(0x00ffff)  // Cyan - default
      neuronType = 'normal'
    }
    
    const mat = new THREE.MeshBasicMaterial({
      color: color,
      transparent: true,
      opacity: 0.9
    })
    
    const neuron = new THREE.Mesh(neuronGeo, mat)
    neuron.position.set(x, y, z)
    neuron.userData = {
      baseColor: color.getHex(),
      pulseOffset: Math.random() * Math.PI * 2,
      pulseSpeed: 1 + Math.random() * 3,
      excited: false,
      excitedTime: 0,
      index: i,
      type: neuronType,
      activity: Math.random()  // Random activity level
    }
    
    neurons.push(neuron)
    brainGroup.add(neuron)
  }
}

const createNeuralConnections = () => {
  // Connect nearby neurons
  for (let i = 0; i < neurons.length; i++) {
    for (let j = i + 1; j < neurons.length; j++) {
      const dist = neurons[i].position.distanceTo(neurons[j].position)
      if (dist < 0.25 && Math.random() > 0.5) {
        const mat = new THREE.LineBasicMaterial({
          color: 0x00ffff,
          transparent: true,
          opacity: 0.05
        })
        const points = [neurons[i].position.clone(), neurons[j].position.clone()]
        const geo = new THREE.BufferGeometry().setFromPoints(points)
        const line = new THREE.Line(geo, mat)
        line.userData = { from: i, to: j, baseOpacity: 0.05 }
        connections.push(line)
        brainGroup.add(line)
      }
    }
  }
}

const createEnergyRings = () => {
  for (let i = 0; i < 3; i++) {
    const radius = 1.8 + i * 0.3
    const geo = new THREE.TorusGeometry(radius, 0.004, 8, 100)
    const mat = new THREE.MeshBasicMaterial({
      color: i % 2 === 0 ? 0x00ffff : 0xff6b00,
      transparent: true,
      opacity: 0.35
    })
    const ring = new THREE.Mesh(geo, mat)
    ring.rotation.x = Math.PI / 2 + i * 0.25
    ring.rotation.y = i * 0.4
    ring.userData = { speed: 0.2 + i * 0.1 }
    ring.name = `energyRing${i}`
    brainGroup.add(ring)
  }
}

const createHolographicShell = () => {
  const shellGeo = new THREE.SphereGeometry(2.1, 64, 48)
  const shellMat = new THREE.ShaderMaterial({
    uniforms: {
      time: { value: 0 }
    },
    vertexShader: `
      varying vec3 vNormal;
      varying vec3 vPosition;
      uniform float time;
      
      void main() {
        vNormal = normalize(normalMatrix * normal);
        vPosition = position;
        
        vec3 pos = position;
        float wave = sin(time * 2.0 + position.y * 4.0) * 0.02;
        pos += normal * wave;
        
        gl_Position = projectionMatrix * modelViewMatrix * vec4(pos, 1.0);
      }
    `,
    fragmentShader: `
      uniform float time;
      varying vec3 vNormal;
      varying vec3 vPosition;
      
      void main() {
        float fresnel = pow(1.0 - abs(dot(vNormal, vec3(0.0, 0.0, 1.0))), 2.0);
        
        // Horizontal scan lines
        float scan = smoothstep(0.97, 1.0, sin(vPosition.y * 50.0 + time * 6.0));
        
        // Color gradient
        float gradient = sin(time + vPosition.y * 3.0) * 0.5 + 0.5;
        vec3 cyan = vec3(0.0, 1.0, 1.0);
        vec3 orange = vec3(1.0, 0.4, 0.0);
        vec3 color = mix(cyan, orange, gradient);
        
        float alpha = fresnel * 0.15 + scan * 0.2;
        
        gl_FragColor = vec4(color, alpha);
      }
    `,
    transparent: true,
    side: THREE.BackSide,
    blending: THREE.AdditiveBlending,
    depthWrite: false
  })
  
  const shell = new THREE.Mesh(shellGeo, shellMat)
  shell.name = 'hologramShell'
  brainGroup.add(shell)
}

const createParticles = () => {
  const count = 800
  const geo = new THREE.BufferGeometry()
  const positions = new Float32Array(count * 3)
  const colors = new Float32Array(count * 3)
  
  for (let i = 0; i < count; i++) {
    const theta = Math.random() * Math.PI * 2
    const phi = Math.acos(2 * Math.random() - 1)
    const r = 2.5 + Math.random() * 2
    
    positions[i * 3] = r * Math.sin(phi) * Math.cos(theta)
    positions[i * 3 + 1] = r * Math.sin(phi) * Math.sin(theta)
    positions[i * 3 + 2] = r * Math.cos(phi)
    
    const isCyan = Math.random() > 0.3
    colors[i * 3] = isCyan ? 0 : 1
    colors[i * 3 + 1] = isCyan ? 1 : 0.5
    colors[i * 3 + 2] = isCyan ? 1 : 0
  }
  
  geo.setAttribute('position', new THREE.BufferAttribute(positions, 3))
  geo.setAttribute('color', new THREE.BufferAttribute(colors, 3))
  
  const mat = new THREE.PointsMaterial({
    size: 0.03,
    vertexColors: true,
    transparent: true,
    opacity: 0.5,
    blending: THREE.AdditiveBlending,
    depthWrite: false
  })
  
  const particles = new THREE.Points(geo, mat)
  particles.name = 'particles'
  brainGroup.add(particles)
}

const createMouseLightning = () => {
  const geo = new THREE.BufferGeometry()
  const positions = new Float32Array(60 * 3)
  geo.setAttribute('position', new THREE.BufferAttribute(positions, 3))
  geo.setDrawRange(0, 0)
  
  const mat = new THREE.LineBasicMaterial({
    color: 0x00ffff,
    transparent: true,
    opacity: 0
  })
  
  const lightning = new THREE.Line(geo, mat)
  lightning.name = 'mouseLightning'
  brainGroup.add(lightning)
}

// Create expanding pulse wave rings
const createPulseWaves = () => {
  for (let i = 0; i < 5; i++) {
    const geo = new THREE.RingGeometry(0.1, 0.15, 64)
    const mat = new THREE.MeshBasicMaterial({
      color: 0x00ffff,
      transparent: true,
      opacity: 0,
      side: THREE.DoubleSide
    })
    const ring = new THREE.Mesh(geo, mat)
    ring.name = `pulseWave${i}`
    ring.userData = { active: false, startTime: 0, scale: 0.1 }
    brainGroup.add(ring)
  }
}

// Trigger pulse wave from a point
let pulseWaveIndex = 0
const triggerPulseWave = (position: THREE.Vector3) => {
  const ring = brainGroup.getObjectByName(`pulseWave${pulseWaveIndex}`) as THREE.Mesh
  if (!ring) return
  
  ring.position.copy(position)
  ring.lookAt(camera.position)
  ring.scale.setScalar(0.1)
  ring.material.opacity = 0.8
  ring.userData.active = true
  ring.userData.startTime = clock.getElapsedTime()
  
  pulseWaveIndex = (pulseWaveIndex + 1) % 5
}

// Scan line that sweeps across brain
const createScanLine = () => {
  const geo = new THREE.PlaneGeometry(4, 0.02)
  const mat = new THREE.MeshBasicMaterial({
    color: 0x00ffff,
    transparent: true,
    opacity: 0.6,
    side: THREE.DoubleSide
  })
  const scanLine = new THREE.Mesh(geo, mat)
  scanLine.name = 'scanLine'
  brainGroup.add(scanLine)
}

// Data streams - lines of data flowing along brain surface
const createDataStreams = () => {
  const streamCount = 8
  for (let i = 0; i < streamCount; i++) {
    const points: THREE.Vector3[] = []
    const startTheta = (i / streamCount) * Math.PI * 2
    
    for (let j = 0; j < 20; j++) {
      const t = j / 20
      const theta = startTheta + t * 2
      const r = 1.4 + Math.sin(t * 4) * 0.1
      const y = (t - 0.5) * 2
      
      points.push(new THREE.Vector3(
        Math.cos(theta) * r,
        y,
        Math.sin(theta) * r
      ))
    }
    
    const curve = new THREE.CatmullRomCurve3(points)
    const geo = new THREE.TubeGeometry(curve, 40, 0.008, 4, false)
    const mat = new THREE.MeshBasicMaterial({
      color: i % 2 === 0 ? 0x00ffff : 0xff6b00,
      transparent: true,
      opacity: 0.4
    })
    const stream = new THREE.Mesh(geo, mat)
    stream.name = `dataStream${i}`
    stream.userData = { offset: Math.random() * Math.PI * 2 }
    brainGroup.add(stream)
  }
}

const init = () => {
  if (!containerRef.value || !canvasRef.value) return
  
  const container = containerRef.value
  const canvas = canvasRef.value
  
  scene = new THREE.Scene()
  scene.background = new THREE.Color(0x000510)
  scene.fog = new THREE.FogExp2(0x000510, 0.06)
  
  camera = new THREE.PerspectiveCamera(45, container.clientWidth / container.clientHeight, 0.1, 100)
  camera.position.set(0, 0.5, 4.5)
  
  renderer = new THREE.WebGLRenderer({ canvas, antialias: true })
  renderer.setSize(container.clientWidth, container.clientHeight)
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2))
  renderer.toneMapping = THREE.ACESFilmicToneMapping
  renderer.toneMappingExposure = 1.2
  
  controls = new OrbitControls(camera, canvas)
  controls.enableDamping = true
  controls.dampingFactor = 0.05
  controls.enableZoom = true
  controls.minDistance = 2.5
  controls.maxDistance = 7
  controls.autoRotate = true
  controls.autoRotateSpeed = 0.5
  controls.enablePan = false
  
  raycaster = new THREE.Raycaster()
  mouse = new THREE.Vector2(-999, -999)
  mouseWorldPos = new THREE.Vector3()
  
  clock = new THREE.Clock()
  
  brainGroup = new THREE.Group()
  scene.add(brainGroup)
  
  // Create all elements
  createBrain()
  createNeurons()
  createNeuralConnections()
  createEnergyRings()
  createHolographicShell()
  createParticles()
  createMouseLightning()
  createPulseWaves()
  createScanLine()
  createDataStreams()
  
  // Lighting
  scene.add(new THREE.AmbientLight(0x404060, 0.5))
  
  const mainLight = new THREE.DirectionalLight(0xffffff, 0.7)
  mainLight.position.set(3, 4, 5)
  scene.add(mainLight)
  
  const cyanLight = new THREE.PointLight(0x00ffff, 1.5, 10)
  cyanLight.position.set(2, 1, 2)
  scene.add(cyanLight)
  
  const orangeLight = new THREE.PointLight(0xff6b00, 1, 10)
  orangeLight.position.set(-2, -1, 3)
  scene.add(orangeLight)
  
  const backLight = new THREE.PointLight(0x4466ff, 0.8, 10)
  backLight.position.set(0, 2, -3)
  scene.add(backLight)
  
  animate()
}

const updateMouseLightning = () => {
  const lightning = brainGroup.getObjectByName('mouseLightning') as THREE.Line
  if (!lightning) return
  
  raycaster.setFromCamera(mouse, camera)
  const intersects = raycaster.intersectObjects(neurons)
  
  if (intersects.length > 0) {
    const nearestNeuron = intersects[0].object as THREE.Mesh
    const pos = nearestNeuron.position
    
    // Find nearby neurons
    const nearby: THREE.Vector3[] = []
    neurons.forEach((n) => {
      if (n !== nearestNeuron && n.position.distanceTo(pos) < 0.4 && nearby.length < 3) {
        nearby.push(n.position)
      }
    })
    
    const positions = lightning.geometry.attributes.position.array as Float32Array
    let idx = 0
    
    // Draw lightning to nearby neurons
    nearby.forEach(targetPos => {
      const steps = 8
      for (let i = 0; i <= steps; i++) {
        const t = i / steps
        const jitter = 0.02
        positions[idx * 3] = pos.x + (targetPos.x - pos.x) * t + (Math.random() - 0.5) * jitter
        positions[idx * 3 + 1] = pos.y + (targetPos.y - pos.y) * t + (Math.random() - 0.5) * jitter
        positions[idx * 3 + 2] = pos.z + (targetPos.z - pos.z) * t + (Math.random() - 0.5) * jitter
        idx++
      }
    })
    
    lightning.geometry.attributes.position.needsUpdate = true
    lightning.geometry.setDrawRange(0, Math.min(idx, 60))
    lightning.material.opacity = 0.7
  } else {
    (lightning.material as THREE.LineBasicMaterial).opacity *= 0.9
  }
}

const animate = () => {
  animationId = requestAnimationFrame(animate)
  
  const time = clock.getElapsedTime()
  
  controls.update()
  
  // Update activity display
  activityFreq.value = (12 + Math.sin(time * 2) * 3).toFixed(1)
  
  // Animate neurons
  neurons.forEach((neuron, i) => {
    const data = neuron.userData
    const mat = neuron.material as THREE.MeshBasicMaterial
    
    if (data.excited) {
      const elapsed = time - data.excitedTime
      if (elapsed < 0.4) {
        mat.color.setHex(0xffffff)
        mat.opacity = 1 - elapsed * 2
        neuron.scale.setScalar(1.5 - elapsed * 2)
      } else {
        data.excited = false
        mat.color.setHex(data.baseColor)
        mat.opacity = 0.8
        neuron.scale.setScalar(1)
      }
    } else {
      const pulse = Math.sin(time * data.pulseSpeed + data.pulseOffset) * 0.5 + 0.5
      mat.opacity = 0.4 + pulse * 0.5
      neuron.scale.setScalar(0.8 + pulse * 0.3)
    }
  })
  
  // Animate connections near mouse
  connections.forEach(conn => {
    const mat = conn.material as THREE.LineBasicMaterial
    const fromPos = neurons[conn.userData.from]?.position
    const toPos = neurons[conn.userData.to]?.position
    
    if (fromPos && toPos) {
      const mid = new THREE.Vector3().addVectors(fromPos, toPos).multiplyScalar(0.5)
      const dist = mid.distanceTo(mouseWorldPos)
      
      if (dist < 0.6) {
        const intensity = 1 - dist / 0.6
        mat.opacity = conn.userData.baseOpacity + intensity * 0.35
        mat.color.setHSL(0.52, 1, 0.5 + intensity * 0.3)
      } else {
        mat.opacity = conn.userData.baseOpacity
        mat.color.setHex(0x00ffff)
      }
    }
  })
  
  // Animate energy rings
  for (let i = 0; i < 3; i++) {
    const ring = brainGroup.getObjectByName(`energyRing${i}`) as THREE.Mesh
    if (ring) {
      ring.rotation.z += ring.userData.speed * 0.008
      const mat = ring.material as THREE.MeshBasicMaterial
      mat.opacity = 0.25 + Math.sin(time * 2 + i) * 0.1
    }
  }
  
  // Holographic shell
  const shell = brainGroup.getObjectByName('hologramShell') as THREE.Mesh
  if (shell?.material) {
    (shell.material as THREE.ShaderMaterial).uniforms.time.value = time
  }
  
  // Brain core pulse
  const core = brainGroup.getObjectByName('brainCore') as THREE.Mesh
  if (core) {
    const pulse = Math.sin(time * 1.5) * 0.5 + 0.5
    const mat = core.material as THREE.MeshBasicMaterial
    mat.opacity = 0.08 + pulse * 0.12
    core.scale.setScalar(0.9 + pulse * 0.3)
  }
  
  // Particles
  const particles = brainGroup.getObjectByName('particles') as THREE.Points
  if (particles) {
    particles.rotation.y = time * 0.02
  }
  
  // Mouse lightning
  updateMouseLightning()
  
  // Animate pulse waves
  for (let i = 0; i < 5; i++) {
    const ring = brainGroup.getObjectByName(`pulseWave${i}`) as THREE.Mesh
    if (ring && ring.userData.active) {
      const elapsed = time - ring.userData.startTime
      if (elapsed < 2) {
        const progress = elapsed / 2
        ring.scale.setScalar(0.1 + progress * 3)
        ring.material.opacity = 0.8 * (1 - progress)
        ring.lookAt(camera.position)
      } else {
        ring.userData.active = false
        ring.material.opacity = 0
      }
    }
  }
  
  // Animate scan line
  const scanLine = brainGroup.getObjectByName('scanLine') as THREE.Mesh
  if (scanLine) {
    const scanY = Math.sin(time * 0.8) * 1.5
    scanLine.position.y = scanY
    scanLine.rotation.x = Math.PI / 2
    const scanMat = scanLine.material as THREE.MeshBasicMaterial
    scanMat.opacity = 0.3 + Math.sin(time * 3) * 0.2
  }
  
  // Animate data streams (pulsing opacity)
  for (let i = 0; i < 8; i++) {
    const stream = brainGroup.getObjectByName(`dataStream${i}`) as THREE.Mesh
    if (stream) {
      const mat = stream.material as THREE.MeshBasicMaterial
      mat.opacity = 0.2 + Math.sin(time * 2 + stream.userData.offset) * 0.2
    }
  }
  
  // Brain breathing
  brainGroup.scale.setScalar(1 + Math.sin(time * 0.5) * 0.008)
  
  // Raycasting for hover effect
  raycaster.setFromCamera(mouse, camera)
  const intersects = raycaster.intersectObjects(neurons)
  
  // Reset neurons (except excited ones)
  neurons.forEach(n => {
    if (!n.userData.excited) {
      const mat = n.material as THREE.MeshBasicMaterial
      mat.color.setHex(n.userData.baseColor)
      mat.opacity = 0.4 + n.userData.activity * 0.5
      n.scale.setScalar(0.7 + n.userData.activity * 0.5)
    }
  })
  
  if (intersects.length > 0) {
    document.body.style.cursor = 'pointer'
    const hovered = intersects[0].object as THREE.Mesh
    const mat = hovered.material as THREE.MeshBasicMaterial
    mat.color.setHex(0xffffff)
    mat.opacity = 1
    hovered.scale.setScalar(1.8)
    
    const neuronData = hovered.userData
    const regions = ['运动皮层', '感觉皮层', '前额叶', '顶叶', '颞叶', '枕叶', '小脑']
    const signals = ['α波(8-13Hz)', 'β波(13-30Hz)', 'μ节律', 'γ振荡(30-100Hz)', 'θ波(4-8Hz)']
    const typeNames: Record<string, string> = {
      'normal': '🧠 普通神经元',
      'inter': '⭐ 中间神经元',
      'excite': '🔥 兴奋性神经元',
      'inhibit': '❄️ 抑制性神经元',
      'motor': '💪 运动神经元'
    }
    
    hoveredNeuron.value = {
      typeName: typeNames[neuronData.type] || '神经元',
      region: regions[neuronData.index % regions.length],
      signal: signals[neuronData.index % signals.length],
      freq: (8 + neuronData.activity * 25).toFixed(1),
      activity: Math.round(neuronData.activity * 100)
    }
  } else {
    document.body.style.cursor = 'default'
    hoveredNeuron.value = null
  }
  
  renderer.render(scene, camera)
}

const triggerElectricPulse = (startIdx: number) => {
  const source = neurons[startIdx]
  if (!source) return
  
  source.userData.excited = true
  source.userData.excitedTime = clock.getElapsedTime()
  
  // Trigger visual pulse wave from click point
  triggerPulseWave(source.position.clone())
  
  // Propagate to nearby neurons
  const propagate = (idx: number, depth: number) => {
    if (depth >= 4) return
    
    setTimeout(() => {
      const sourcePos = neurons[idx]?.position
      if (!sourcePos) return
      
      neurons.forEach((n, i) => {
        if (i !== idx && n.position.distanceTo(sourcePos) < 0.4 && Math.random() > 0.35) {
          n.userData.excited = true
          n.userData.excitedTime = clock.getElapsedTime()
          propagate(i, depth + 1)
        }
      })
    }, 60 + depth * 40)
  }
  
  propagate(startIdx, 0)
}

const handleClick = (event: MouseEvent) => {
  const rect = containerRef.value!.getBoundingClientRect()
  mouse.x = ((event.clientX - rect.left) / rect.width) * 2 - 1
  mouse.y = -((event.clientY - rect.top) / rect.height) * 2 + 1
  
  raycaster.setFromCamera(mouse, camera)
  const intersects = raycaster.intersectObjects(neurons)
  
  if (intersects.length > 0) {
    const idx = neurons.indexOf(intersects[0].object as THREE.Mesh)
    if (idx >= 0) {
      triggerElectricPulse(idx)
    }
    emit('brainClick')
  }
}

// Double-click triggers full brain wave
const handleDoubleClick = (event: MouseEvent) => {
  const rect = containerRef.value!.getBoundingClientRect()
  mouse.x = ((event.clientX - rect.left) / rect.width) * 2 - 1
  mouse.y = -((event.clientY - rect.top) / rect.height) * 2 + 1
  
  // Trigger wave from center outward
  const centerPos = new THREE.Vector3(0, 0, 0)
  
  // Activate all neurons in waves based on distance from click point
  raycaster.setFromCamera(mouse, camera)
  const plane = new THREE.Plane(new THREE.Vector3(0, 0, 1), 0)
  const clickPos = new THREE.Vector3()
  raycaster.ray.intersectPlane(plane, clickPos)
  
  // Sort neurons by distance and activate in waves
  const neuronsWithDist = neurons.map((n, i) => ({
    idx: i,
    dist: n.position.distanceTo(clickPos || centerPos)
  }))
  neuronsWithDist.sort((a, b) => a.dist - b.dist)
  
  // Activate in waves
  neuronsWithDist.forEach((item, waveIndex) => {
    setTimeout(() => {
      neurons[item.idx].userData.excited = true
      neurons[item.idx].userData.excitedTime = clock.getElapsedTime()
    }, waveIndex * 3) // 3ms delay between each
  })
  
  // Trigger multiple pulse waves
  for (let i = 0; i < 3; i++) {
    setTimeout(() => {
      triggerPulseWave(clickPos || centerPos)
    }, i * 200)
  }
}

const onMouseMove = (event: MouseEvent) => {
  if (!containerRef.value) return
  currentEvent.value = event
  const rect = containerRef.value.getBoundingClientRect()
  mouse.x = ((event.clientX - rect.left) / rect.width) * 2 - 1
  mouse.y = -((event.clientY - rect.top) / rect.height) * 2 + 1
  
  raycaster.setFromCamera(mouse, camera)
  const plane = new THREE.Plane(new THREE.Vector3(0, 0, 1), 0)
  raycaster.ray.intersectPlane(plane, mouseWorldPos)
}

const onMouseLeave = () => {
  mouse.set(-999, -999)
}

const onResize = () => {
  if (!containerRef.value || !camera || !renderer) return
  const w = containerRef.value.clientWidth
  const h = containerRef.value.clientHeight
  camera.aspect = w / h
  camera.updateProjectionMatrix()
  renderer.setSize(w, h)
}

// 处理来自脑活动地形图的脉冲
const handleBrainPulse = (e: CustomEvent) => {
  const { region, intensity } = e.detail
  
  console.log('收到脑脉冲:', region, intensity)
  
  // 改变大脑整体颜色作为反馈
  if (brainGroup) {
    const shell = brainGroup.getObjectByName('hologramShell')
    if (shell && (shell as THREE.Mesh).material) {
      const mat = (shell as THREE.Mesh).material as THREE.ShaderMaterial
      if (mat.uniforms && mat.uniforms.time) {
        // 临时改变颜色
        const originalColor = new THREE.Color(0, 1, 1)
        const pulseColor = region === 'left' ? new THREE.Color(0, 0.67, 1) :
                          region === 'right' ? new THREE.Color(1, 0.42, 0) :
                          new THREE.Color(0, 1, 0.53)
        
        // 简单的闪烁效果
        let flash = 0
        const flashInterval = setInterval(() => {
          flash++
          if (mat.uniforms) {
            mat.uniforms.time.value = flash * 0.1
          }
          if (flash > 10) {
            clearInterval(flashInterval)
          }
        }, 50)
      }
    }
  }
  
  // 高亮部分神经元
  let count = 0
  neurons.forEach((neuron) => {
    const pos = neuron.position
    let isInRegion = false
    
    switch (region) {
      case 'left':
        isInRegion = pos.x < -0.5
        break
      case 'right':
        isInRegion = pos.x > 0.5
        break
      case 'center':
        isInRegion = Math.abs(pos.x) < 0.3 && pos.y > 0.3
        break
    }
    
    if (isInRegion && count < 30) {
      count++
      const material = neuron.material as THREE.MeshBasicMaterial
      
      const color = region === 'center' ? new THREE.Color(0, 1, 0.53) : 
                    region === 'left' ? new THREE.Color(0, 0.67, 1) :
                    new THREE.Color(1, 0.42, 0)
      material.color.copy(color)
      material.opacity = 1
      
      // 500ms后恢复
      setTimeout(() => {
        material.color.setHex(0x00ffff)
        material.opacity = 0.6
      }, 500)
    }
  })
}

onMounted(() => {
  init()
  window.addEventListener('resize', onResize)
  window.addEventListener('brain-pulse', handleBrainPulse as EventListener)
  containerRef.value?.addEventListener('mousemove', onMouseMove)
  containerRef.value?.addEventListener('mouseleave', onMouseLeave)
})

onBeforeUnmount(() => {
  cancelAnimationFrame(animationId)
  window.removeEventListener('resize', onResize)
  window.removeEventListener('brain-pulse', handleBrainPulse as EventListener)
  containerRef.value?.removeEventListener('mousemove', onMouseMove)
  containerRef.value?.removeEventListener('mouseleave', onMouseLeave)
  renderer?.dispose()
})
</script>

<style scoped>
.brain3d-container {
  width: 100%;
  height: 100%;
  position: relative;
  cursor: grab;
}

.brain3d-container:active {
  cursor: grabbing;
}

canvas {
  width: 100% !important;
  height: 100% !important;
  display: block;
}

.neuron-tooltip {
  position: fixed;
  background: rgba(0, 10, 20, 0.9);
  border: 1px solid rgba(0, 255, 255, 0.5);
  border-radius: 10px;
  padding: 12px 16px;
  min-width: 180px;
  pointer-events: none;
  backdrop-filter: blur(10px);
  animation: tooltipFade 0.15s ease-out;
  z-index: 1000;
  transform: translate(15px, 15px);
}

@keyframes tooltipFade {
  from { opacity: 0; transform: translate(15px, 15px) scale(0.95); }
  to { opacity: 1; transform: translate(15px, 15px) scale(1); }
}

.tooltip-header {
  color: #ff6b00;
  font-size: 0.8rem;
  font-weight: bold;
  margin-bottom: 10px;
  padding-bottom: 8px;
  border-bottom: 1px solid rgba(0, 255, 255, 0.2);
  letter-spacing: 1px;
}

.tooltip-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin: 5px 0;
}

.tooltip-label {
  color: #888;
  font-size: 0.7rem;
}

.tooltip-value {
  color: #00ffff;
  font-size: 0.75rem;
  font-weight: bold;
}

.tooltip-value.highlight {
  color: #ff6b00;
  animation: pulse 1s infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.6; }
}

.activity-bar {
  width: 60px;
  height: 6px;
  background: rgba(0, 255, 255, 0.2);
  border-radius: 3px;
  overflow: hidden;
}

.activity-fill {
  height: 100%;
  background: linear-gradient(90deg, #00ffff, #ff6b00);
  border-radius: 3px;
  transition: width 0.3s;
}

</style>