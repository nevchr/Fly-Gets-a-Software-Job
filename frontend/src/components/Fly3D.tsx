import { useEffect, useRef } from 'react'
import * as THREE from 'three'
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js'
import type { BrainActivity } from '../types/simulation'

interface Props {
  stage: string
  activity: BrainActivity
  onReady: () => void
}

function clipForStage(stage: string) {
  if (stage === 'SEARCHING_FOR_JOB') return 'Walk'
  if (stage === 'APPLICATION_SENT' || stage === 'TECHNICAL_INTERVIEW') return 'Type'
  if (stage === 'FINAL_RESULT') return 'Startle'
  return 'Idle'
}

export function Fly3D({ stage, activity, onReady }: Props) {
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const stateRef = useRef({ stage, activity })

  useEffect(() => {
    stateRef.current = { stage, activity }
  }, [stage, activity])

  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return

    let renderer: THREE.WebGLRenderer
    try {
      renderer = new THREE.WebGLRenderer({ canvas, alpha: true, antialias: true, powerPreference: 'low-power' })
    } catch {
      return // The illustrated fly remains visible on devices without WebGL.
    }

    renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2))
    renderer.outputColorSpace = THREE.SRGBColorSpace
    renderer.toneMapping = THREE.ACESFilmicToneMapping
    renderer.toneMappingExposure = 1.08

    const scene = new THREE.Scene()
    scene.add(new THREE.AmbientLight(0xe8f5df, 1.25))
    const key = new THREE.DirectionalLight(0xf5ffd9, 1.6)
    key.position.set(3, 7, -5)
    scene.add(key)
    const rim = new THREE.DirectionalLight(0x8ac9d8, 0.85)
    rim.position.set(-5, 3, 5)
    scene.add(rim)

    const camera = new THREE.OrthographicCamera(-4, 4, 3.5, -3.5, 0.1, 100)
    camera.position.set(8, 4.3, -8.5)
    camera.lookAt(0, 0, 0)

    const resize = () => {
      const width = Math.max(canvas.clientWidth, 1)
      const height = Math.max(canvas.clientHeight, 1)
      const halfHeight = 3.55
      const halfWidth = halfHeight * width / height
      camera.left = -halfWidth
      camera.right = halfWidth
      camera.top = halfHeight
      camera.bottom = -halfHeight
      camera.updateProjectionMatrix()
      renderer.setSize(width, height, false)
    }
    const resizeObserver = new ResizeObserver(resize)
    resizeObserver.observe(canvas)
    resize()

    let disposed = false
    let frameId = 0
    let mixer: THREE.AnimationMixer | null = null
    let currentAction: THREE.AnimationAction | null = null
    let currentClip = ''
    let wingAction: THREE.AnimationAction | null = null
    const clips = new Map<string, THREE.AnimationClip>()
    const eyeMaterials: THREE.MeshStandardMaterial[] = []
    let lastFrame = window.performance.now()
    const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)')

    new GLTFLoader().load('/models/fly-v1.glb', gltf => {
      if (disposed) return
      const fly = gltf.scene
      const bounds = new THREE.Box3().setFromObject(fly)
      const center = bounds.getCenter(new THREE.Vector3())
      fly.position.sub(center)
      fly.traverse(object => {
        if (object instanceof THREE.Mesh && object.name.startsWith('Fly_Eye.')) {
          const material = object.material
          if (material instanceof THREE.MeshStandardMaterial) {
            material.emissive.setHex(0x8b2110)
            eyeMaterials.push(material)
          }
        }
      })
      scene.add(fly)

      mixer = new THREE.AnimationMixer(fly)
      for (const clip of gltf.animations) clips.set(clip.name, clip)
      const wingClip = clips.get('WingFlap')
      if (wingClip) {
        const additiveWings = THREE.AnimationUtils.makeClipAdditive(wingClip.clone())
        wingAction = mixer.clipAction(additiveWings, undefined, THREE.AdditiveAnimationBlendMode)
        wingAction.play()
      }
      onReady()
    }, undefined, () => {
      // Keep the existing SVG illustration if the asset cannot load.
    })

    const animate = () => {
      frameId = window.requestAnimationFrame(animate)
      const { stage: liveStage, activity: liveActivity } = stateRef.current
      const neuralDrive = THREE.MathUtils.clamp(liveActivity.activation || 0, 0, 1)
      const desiredClip = clipForStage(liveStage)
      if (mixer && desiredClip !== currentClip) {
        const nextClip = clips.get(desiredClip) ?? clips.get('Idle')
        if (nextClip) {
          const nextAction = mixer.clipAction(nextClip)
          nextAction.reset()
          nextAction.setLoop(desiredClip === 'Startle' ? THREE.LoopOnce : THREE.LoopRepeat, Infinity)
          nextAction.clampWhenFinished = desiredClip === 'Startle'
          nextAction.play()
          if (currentAction) nextAction.crossFadeFrom(currentAction, 0.25, true)
          currentAction = nextAction
          currentClip = desiredClip
        }
      }
      if (currentAction) currentAction.timeScale = 0.65 + neuralDrive * 1.5
      if (wingAction) {
        wingAction.setEffectiveWeight(0.08 + neuralDrive * 0.4)
        wingAction.timeScale = 0.7 + neuralDrive * 2.8
      }
      for (const material of eyeMaterials) material.emissiveIntensity = 0.12 + neuralDrive * 0.8
      key.intensity = 1.45 + neuralDrive * 0.65
      const now = window.performance.now()
      const delta = Math.min((now - lastFrame) / 1000, 0.05)
      lastFrame = now
      if (!reducedMotion.matches) mixer?.update(delta)
      renderer.render(scene, camera)
    }
    animate()

    return () => {
      disposed = true
      window.cancelAnimationFrame(frameId)
      resizeObserver.disconnect()
      mixer?.stopAllAction()
      scene.traverse(object => {
        if (object instanceof THREE.Mesh) object.geometry.dispose()
      })
      renderer.dispose()
    }
  }, [onReady])

  return <canvas ref={canvasRef} className="flyViewport" aria-hidden="true" />
}
