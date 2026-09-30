import { useEffect, useRef, useState } from 'react'
import * as THREE from 'three'
import { OrbitControls } from 'three/addons/controls/OrbitControls.js'
import type { BrainActivity } from '../types/simulation'

interface SkeletonEntry {
  body_id: number
  label: string
  color: string
  soma: [number, number, number]
  file: string
  distance_file: string
  segment_count: number
  surge_path_file: string
  surge_path_point_count: number
}

interface PopulationEntry {
  name: string
  color: string
  point_count: number
  file: string
}

interface Manifest {
  overview: { file: string; point_count: number }
  population_groups: PopulationEntry[]
  skeletons: SkeletonEntry[]
}

interface TracedNeuron {
  bodyId: number
  line: THREE.LineSegments
  lineMaterial: THREE.LineBasicMaterial
  surgeLine: THREE.LineSegments
  surgeLineMaterial: THREE.ShaderMaterial
  surgePoints: THREE.Points
  surgePointMaterial: THREE.ShaderMaterial
  surgeSpark: THREE.Sprite
  surgeSparkMaterial: THREE.SpriteMaterial
  surgePath: Float32Array
  soma: THREE.Mesh
  somaMaterial: THREE.MeshBasicMaterial
  halo: THREE.Sprite
  haloMaterial: THREE.SpriteMaterial
  pulseStartedAt: number
}

interface ActivePopulation {
  name: string
  points: THREE.Points
  material: THREE.PointsMaterial
  pulseStartedAt: number
}

const DATA_ROOT = '/data/malecns/'
const PULSE_DURATION_MS = 1700
const SURGE_VERTEX = `
  attribute float aPath;
  varying float vPath;
  void main() {
    vPath = aPath;
    gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
  }
`
const SURGE_LINE_FRAGMENT = `
  uniform vec3 uColor;
  uniform float uProgress;
  uniform float uStrength;
  varying float vPath;
  void main() {
    float delta = vPath - uProgress;
    float core = exp(-900.0 * delta * delta);
    float aura = exp(-75.0 * delta * delta);
    gl_FragColor = vec4(uColor * 1.7, (core + 0.38 * aura) * uStrength);
  }
`
const SURGE_POINT_VERTEX = `
  attribute float aPath;
  varying float vPath;
  void main() {
    vPath = aPath;
    gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
    gl_PointSize = 5.5;
  }
`
const SURGE_POINT_FRAGMENT = `
  uniform vec3 uColor;
  uniform float uProgress;
  uniform float uStrength;
  varying float vPath;
  void main() {
    float delta = vPath - uProgress;
    float front = exp(-650.0 * delta * delta);
    float disc = 1.0 - smoothstep(0.12, 0.5, length(gl_PointCoord - vec2(0.5)));
    gl_FragColor = vec4(uColor * 2.1, front * disc * uStrength);
  }
`

async function getBinary(file: string, signal: AbortSignal) {
  const response = await fetch(`${DATA_ROOT}${file}`, { signal })
  if (!response.ok) throw new Error(`Could not load ${file}`)
  return new Float32Array(await response.arrayBuffer())
}

export function Connectome3D({ activity }: { activity: BrainActivity }) {
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const activityRef = useRef(activity)
  const [state, setState] = useState<'loading' | 'ready' | 'error'>('loading')

  useEffect(() => { activityRef.current = activity }, [activity])

  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return

    let renderer: THREE.WebGLRenderer
    try {
      renderer = new THREE.WebGLRenderer({ canvas, alpha: true, antialias: true, powerPreference: 'low-power' })
    } catch {
      queueMicrotask(() => setState('error'))
      return
    }
    renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 1.5))
    renderer.outputColorSpace = THREE.SRGBColorSpace

    const scene = new THREE.Scene()
    const camera = new THREE.PerspectiveCamera(43, 1, 0.1, 100)
    camera.position.set(0, 0, 6.8)
    const controls = new OrbitControls(camera, canvas)
    controls.enableDamping = true
    controls.enablePan = false
    controls.minDistance = 5
    controls.maxDistance = 17
    const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches
    controls.autoRotate = !reducedMotion
    controls.autoRotateSpeed = 0.32

    const controller = new AbortController()
    const neurons: TracedNeuron[] = []
    const populations: ActivePopulation[] = []
    let overview: THREE.Points | null = null
    let somaGeometry: THREE.SphereGeometry | null = null
    let frameId = 0
    let visible = true
    let disposed = false
    let userInteracted = false
    let lastDecisionCount = -1
    controls.addEventListener('start', () => { userInteracted = true })

    const haloCanvas = document.createElement('canvas')
    haloCanvas.width = haloCanvas.height = 64
    const context = haloCanvas.getContext('2d')
    if (context) {
      const gradient = context.createRadialGradient(32, 32, 2, 32, 32, 32)
      gradient.addColorStop(0, 'rgba(255,255,255,0.8)')
      gradient.addColorStop(0.3, 'rgba(255,255,255,0.35)')
      gradient.addColorStop(1, 'rgba(255,255,255,0)')
      context.fillStyle = gradient
      context.fillRect(0, 0, 64, 64)
    }
    const haloTexture = new THREE.CanvasTexture(haloCanvas)

    const resize = () => {
      const width = Math.max(canvas.clientWidth, 1)
      const height = Math.max(canvas.clientHeight, 1)
      camera.aspect = width / height
      camera.updateProjectionMatrix()
      if (!userInteracted) camera.position.setLength(Math.max(6.8, 11.3 / camera.aspect))
      renderer.setSize(width, height, false)
    }
    const resizeObserver = new ResizeObserver(resize)
    resizeObserver.observe(canvas)
    resize()

    const visibilityObserver = new IntersectionObserver(entries => {
      visible = entries[0]?.isIntersecting ?? true
    })
    visibilityObserver.observe(canvas)

    const loadScene = async () => {
      const response = await fetch(`${DATA_ROOT}manifest.json`, { signal: controller.signal })
      if (!response.ok) throw new Error('Could not load MaleCNS manifest')
      const manifest = await response.json() as Manifest
      const [positions, traces, pathDistances, surgePaths, populationPositions] = await Promise.all([
        getBinary(manifest.overview.file, controller.signal),
        Promise.all(manifest.skeletons.map(entry => getBinary(entry.file, controller.signal))),
        Promise.all(manifest.skeletons.map(entry => getBinary(entry.distance_file, controller.signal))),
        Promise.all(manifest.skeletons.map(entry => getBinary(entry.surge_path_file, controller.signal))),
        Promise.all(manifest.population_groups.map(entry => getBinary(entry.file, controller.signal))),
      ])
      if (disposed) return
      if (positions.length !== manifest.overview.point_count * 3) {
        throw new Error('MaleCNS position count does not match the manifest')
      }

      const overviewGeometry = new THREE.BufferGeometry()
      overviewGeometry.setAttribute('position', new THREE.BufferAttribute(positions, 3))
      overview = new THREE.Points(overviewGeometry, new THREE.PointsMaterial({
        color: 0x7c9d96, size: 0.019, transparent: true, opacity: 0.32,
        depthWrite: false, blending: THREE.AdditiveBlending,
      }))
      scene.add(overview)

      manifest.population_groups.forEach((entry, index) => {
        const positionData = populationPositions[index]
        if (positionData.length !== entry.point_count * 3) {
          throw new Error(`MaleCNS population count mismatch: ${entry.name}`)
        }
        const geometry = new THREE.BufferGeometry()
        geometry.setAttribute('position', new THREE.BufferAttribute(positionData, 3))
        const material = new THREE.PointsMaterial({
          map: haloTexture, color: new THREE.Color(entry.color), size: 0.18,
          transparent: true, opacity: 0, depthWrite: false,
          blending: THREE.AdditiveBlending,
        })
        const points = new THREE.Points(geometry, material)
        scene.add(points)
        populations.push({ name: entry.name, points, material, pulseStartedAt: -Infinity })
      })

      somaGeometry = new THREE.SphereGeometry(0.055, 12, 8)
      manifest.skeletons.forEach((entry, index) => {
        if (pathDistances[index].length !== entry.segment_count * 2) {
          throw new Error(`MaleCNS branch distance mismatch: ${entry.body_id}`)
        }
        if (surgePaths[index].length !== entry.surge_path_point_count * 4 || entry.surge_path_point_count < 2) {
          throw new Error(`MaleCNS surge path mismatch: ${entry.body_id}`)
        }
        const geometry = new THREE.BufferGeometry()
        geometry.setAttribute('position', new THREE.BufferAttribute(traces[index], 3))
        geometry.setAttribute('aPath', new THREE.BufferAttribute(pathDistances[index], 1))
        const color = new THREE.Color(entry.color)
        const lineMaterial = new THREE.LineBasicMaterial({
          color, transparent: true, opacity: 0.48,
          depthWrite: false, blending: THREE.AdditiveBlending,
        })
        const line = new THREE.LineSegments(geometry, lineMaterial)
        const surgeUniforms = () => ({
          uColor: { value: color }, uProgress: { value: 0 }, uStrength: { value: 0 },
        })
        const surgeLineMaterial = new THREE.ShaderMaterial({
          uniforms: surgeUniforms(), vertexShader: SURGE_VERTEX,
          fragmentShader: SURGE_LINE_FRAGMENT, transparent: true,
          depthTest: false, depthWrite: false, blending: THREE.AdditiveBlending,
        })
        const surgeLine = new THREE.LineSegments(geometry, surgeLineMaterial)
        const surgePointMaterial = new THREE.ShaderMaterial({
          uniforms: surgeUniforms(), vertexShader: SURGE_POINT_VERTEX,
          fragmentShader: SURGE_POINT_FRAGMENT, transparent: true,
          depthTest: false, depthWrite: false, blending: THREE.AdditiveBlending,
        })
        const surgePoints = new THREE.Points(geometry, surgePointMaterial)
        const surgeSparkMaterial = new THREE.SpriteMaterial({
          map: haloTexture, color, transparent: true, opacity: 0,
          depthTest: false, depthWrite: false, blending: THREE.AdditiveBlending,
        })
        const surgeSpark = new THREE.Sprite(surgeSparkMaterial)
        surgeSpark.position.set(surgePaths[index][0], surgePaths[index][1], surgePaths[index][2])
        surgeSpark.scale.setScalar(0.45)
        const somaMaterial = new THREE.MeshBasicMaterial({ color, transparent: true })
        const soma = new THREE.Mesh(somaGeometry!, somaMaterial)
        soma.position.set(...entry.soma)
        const haloMaterial = new THREE.SpriteMaterial({
          map: haloTexture, color, transparent: true, opacity: 0,
          depthWrite: false, blending: THREE.AdditiveBlending,
        })
        const halo = new THREE.Sprite(haloMaterial)
        halo.position.set(...entry.soma)
        scene.add(line, surgeLine, surgePoints, surgeSpark, halo, soma)
        neurons.push({
          bodyId: entry.body_id, line, lineMaterial, surgeLine,
          surgeLineMaterial, surgePoints, surgePointMaterial,
          surgeSpark, surgeSparkMaterial, surgePath: surgePaths[index],
          soma, somaMaterial, halo, haloMaterial,
          pulseStartedAt: -Infinity,
        })
      })
      lastDecisionCount = -1
      setState('ready')
    }

    loadScene().catch(() => { if (!disposed) setState('error') })

    const animate = () => {
      frameId = window.requestAnimationFrame(animate)
      if (!visible) return
      const live = activityRef.current
      const byId = new Map((live.visual_neurons ?? []).map(neuron => [neuron.body_id, neuron]))
      const now = performance.now()
      if (live.decision_count !== lastDecisionCount) {
        lastDecisionCount = live.decision_count
        for (const population of populations) {
          if ((live.input_activity.find(input => input.name === population.name)?.spike_rate ?? 0) > 0) {
            population.pulseStartedAt = now
          }
        }
        for (const neuron of neurons) {
          if ((byId.get(neuron.bodyId)?.spike_count ?? 0) > 0) neuron.pulseStartedAt = now
        }
      }
      for (const population of populations) {
        const rate = live.input_activity.find(input => input.name === population.name)?.spike_rate ?? 0
        const strength = Math.min(rate / 15, 1)
        const progress = (now - population.pulseStartedAt) / PULSE_DURATION_MS
        const pulse = reducedMotion || progress < 0 || progress > 1
          ? 0
          : Math.sin(Math.PI * progress) * strength
        population.material.opacity = reducedMotion ? strength * 0.35 : pulse * 0.9
        population.material.size = 0.18 + pulse * 0.08
      }
      for (const neuron of neurons) {
        const spikes = byId.get(neuron.bodyId)?.spike_count ?? 0
        const strength = Math.min(spikes / 3, 1)
        const progress = (now - neuron.pulseStartedAt) / PULSE_DURATION_MS
        const pulseProgress = Math.max(0, Math.min(progress, 1))
        const pulse = reducedMotion || progress < 0 || progress > 1
          ? 0
          : Math.sin(Math.PI * pulseProgress) * strength
        neuron.lineMaterial.opacity = 0.32 + strength * 0.28
        neuron.surgeLineMaterial.uniforms.uProgress.value = pulseProgress
        neuron.surgeLineMaterial.uniforms.uStrength.value = pulse
        neuron.surgePointMaterial.uniforms.uProgress.value = pulseProgress
        neuron.surgePointMaterial.uniforms.uStrength.value = pulse
        neuron.surgeSparkMaterial.opacity = pulse * 0.95
        neuron.surgeSpark.scale.setScalar(0.45 + pulse * 0.25)
        if (pulse > 0) {
          const path = neuron.surgePath
          let low = 0
          let high = path.length / 4 - 1
          while (low + 1 < high) {
            const middle = (low + high) >> 1
            if (path[middle * 4 + 3] < pulseProgress) low = middle
            else high = middle
          }
          const start = low * 4
          const end = high * 4
          const span = path[end + 3] - path[start + 3]
          const fraction = span > 0 ? Math.max(0, Math.min((pulseProgress - path[start + 3]) / span, 1)) : 0
          neuron.surgeSpark.position.set(
            THREE.MathUtils.lerp(path[start], path[end], fraction),
            THREE.MathUtils.lerp(path[start + 1], path[end + 1], fraction),
            THREE.MathUtils.lerp(path[start + 2], path[end + 2], fraction),
          )
        }
        neuron.soma.scale.setScalar(1 + strength * 0.35 + pulse * 1.7)
        neuron.somaMaterial.opacity = 0.65 + strength * 0.3
        neuron.halo.scale.setScalar(0.45 + pulseProgress * 0.85)
        neuron.haloMaterial.opacity = pulse * 0.78
      }
      if (overview?.material instanceof THREE.PointsMaterial) {
        overview.material.opacity = 0.055 + Math.min(live.activation, 1) * 0.1
      }
      controls.update()
      renderer.render(scene, camera)
    }
    animate()

    return () => {
      disposed = true
      controller.abort()
      window.cancelAnimationFrame(frameId)
      resizeObserver.disconnect()
      visibilityObserver.disconnect()
      controls.dispose()
      overview?.geometry.dispose()
      if (overview?.material instanceof THREE.Material) overview.material.dispose()
      for (const population of populations) {
        population.points.geometry.dispose()
        population.material.dispose()
      }
      for (const neuron of neurons) {
        neuron.line.geometry.dispose()
        neuron.lineMaterial.dispose()
        neuron.surgeLineMaterial.dispose()
        neuron.surgePointMaterial.dispose()
        neuron.surgeSparkMaterial.dispose()
        neuron.somaMaterial.dispose()
        neuron.haloMaterial.dispose()
      }
      somaGeometry?.dispose()
      haloTexture.dispose()
      renderer.dispose()
    }
  }, [])

  return (
    <>
      <canvas ref={canvasRef} className="connectomeCanvas" aria-hidden="true" />
      {state !== 'ready' && <p className="connectomeLoad">{state === 'error' ? '3D anatomy unavailable on this device.' : 'Loading real MaleCNS anatomy…'}</p>}
      <span className="connectomeHint">DRAG TO ROTATE · SCROLL TO ZOOM</span>
    </>
  )
}
