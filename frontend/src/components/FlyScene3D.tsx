import { useEffect, useRef } from 'react'
import * as THREE from 'three'
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js'
import type { BrainActivity, InterviewStats, Job, Status } from '../types/simulation'
import { flyMotion } from './flyMotion'
import { createBayView } from './bayView'

interface Props { status: Status; activity: BrainActivity; job: Job | null; interviews: InterviewStats; onReady: () => void }
const interviewStages = new Set(['RECRUITER_SCREEN', 'TECHNICAL_INTERVIEW', 'BEHAVIORAL_INTERVIEW'])

function cube(parent: THREE.Object3D, name: string, size: [number, number, number], pos: [number, number, number], mat: THREE.Material) {
  const mesh = new THREE.Mesh(new THREE.BoxGeometry(...size), mat)
  mesh.name = name
  mesh.position.set(...pos)
  parent.add(mesh)
  return mesh
}
function mat(color: number, metalness = 0) { return new THREE.MeshStandardMaterial({ color, metalness, roughness: 0.7 }) }
function screenTexture() {
  const canvas = document.createElement('canvas')
  canvas.width = 1024; canvas.height = 512
  const context = canvas.getContext('2d')!
  const texture = new THREE.CanvasTexture(canvas)
  texture.colorSpace = THREE.SRGBColorSpace
  return { context, texture }
}
function drawScreen(context: CanvasRenderingContext2D, texture: THREE.CanvasTexture, status: Status, job: Job | null, interviews: InterviewStats) {
  const interview = status.is_daytime && interviewStages.has(status.stage)
  const afterHours = !status.is_daytime && (interviewStages.has(status.stage) || status.stage === 'APPLICATION_RESULT' || status.stage === 'FINAL_RESULT')
  context.fillStyle = interview ? '#0a1b29' : '#0d211c'; context.fillRect(0, 0, 1024, 512)
  context.fillStyle = interview ? '#78dceb' : '#c8fa5c'; context.fillRect(0, 0, 1024, 8)
  context.font = 'bold 22px monospace'; context.fillText(interview ? 'LIVE / INTERVIEW ROOM' : afterHours ? 'AFTER HOURS / DESK CAM' : 'OPEN ROLES / JOB BOARD', 54, 58)
  context.fillStyle = '#607e80'; context.fillText(`TICK ${String(status.tick_count).padStart(6, '0')}`, 750, 58)
  context.strokeStyle = '#3f6061'; context.strokeRect(45, 91, 934, 370)
  context.fillStyle = '#eef9e9'; context.font = 'bold 36px monospace'
  context.fillText(interview ? status.stage === 'TECHNICAL_INTERVIEW' ? 'TECHNICAL CHALLENGE' : 'MEET THE TEAM' : afterHours ? 'RESUMES AT 7:00 AM' : status.stage === 'APPLICATION_SENT' ? 'APPLICATION SENT' : 'THE NEXT OPPORTUNITY', 75, 156)
  const value = interview ? interviews.latest_attempt?.question ?? 'Tell us a little about yourself.' : job ? `${job.title} / ${job.company_name}` : 'Scanning for entry-level roles...'
  context.font = '26px monospace'
  const words = value.split(/\s+/); const lines: string[] = []; let line = ''
  for (const word of words) { const next = line ? `${line} ${word}` : word; if (context.measureText(next).width > 820 && line) { lines.push(line); line = word } else line = next }
  if (line) lines.push(line)
  lines.slice(0, 3).forEach((text, index) => context.fillText(text, 78, 228 + index * 40))
  context.fillStyle = interview ? '#4c9baf' : '#789e49'; context.fillRect(78, 382, 830, 1)
  context.fillStyle = '#b8d2c7'; context.font = '22px monospace'; context.fillText(status.stage.replaceAll('_', ' '), 79, 421)
  texture.needsUpdate = true
}

function buildRoom(scene: THREE.Scene) {
  const wall = mat(0x15212c), floor = mat(0x121c24, 0.2), edge = mat(0x35515b, 0.5)
  const desk = mat(0x37484b, 0.3), dark = mat(0x26323a, 0.5)
  const glow = new THREE.MeshStandardMaterial({ color: 0x84e1e5, emissive: 0x247689, emissiveIntensity: 1.1 })
  const lime = new THREE.MeshStandardMaterial({ color: 0xc8fa5c, emissive: 0x597c22, emissiveIntensity: 0.7 })
  cube(scene, 'floor', [16, 0.13, 12], [0, -0.1, 0], floor)
  cube(scene, 'rear wall above glass', [16, 2.65, 0.15], [0, 6.67, 4.7], wall)
  cube(scene, 'rear wall below glass', [16, 1.4, 0.15], [0, 0.7, 4.7], wall)
  for (const x of [-7.38, 7.38]) cube(scene, 'window surround', [1.24, 4.06, 0.15], [x, 3.4, 4.7], wall)
  cube(scene, 'side wall', [0.15, 8, 12], [-7.9, 4, 0], wall)
  const lines: number[] = []
  for (let x = -8; x <= 8; x += 0.7) lines.push(x, 0.004, -6, x, 0.004, 5)
  for (let z = -6; z <= 5; z += 0.7) lines.push(-8, 0.004, z, 8, 0.004, z)
  scene.add(new THREE.LineSegments(new THREE.BufferGeometry().setAttribute('position', new THREE.Float32BufferAttribute(lines, 3)), new THREE.LineBasicMaterial({ color: 0x3c7479, transparent: true, opacity: 0.22 })))
  const bay = createBayView()
  scene.add(bay.mesh)
  const glass = new THREE.MeshBasicMaterial({ color: 0x9bc4d2, transparent: true, opacity: 0.045, depthWrite: false, side: THREE.DoubleSide })
  for (let index = 0; index < 4; index++) {
    const x = -5.05 + index * 3.37
    cube(scene, 'glass window pane', [3.28, 3.84, 0.012], [x, 3.38, 4.4], glass)
    cube(scene, 'glass reflection', [0.014, 3.56, 0.012], [x + 1.43, 3.38, 4.387], new THREE.MeshBasicMaterial({ color: 0xd2f5ff, transparent: true, opacity: 0.1 }))
  }
  cube(scene, 'window top', [13.5, 0.11, 0.17], [0, 5.35, 4.35], edge)
  cube(scene, 'window sill', [13.5, 0.15, 0.21], [0, 1.4, 4.32], edge)
  for (let x = -6.75; x <= 6.75; x += 3.375) cube(scene, 'window frame', [0.1, 3.9, 0.16], [x, 3.38, 4.34], edge)
  cube(scene, 'window transom', [13.5, 0.045, 0.08], [0, 4.59, 4.32], edge)
  cube(scene, 'ceiling neon', [11, 0.035, 0.06], [0.4, 5.98, 4.58], glow)

  const work = new THREE.Group(), interview = new THREE.Group(); scene.add(work, interview)
  cube(work, 'desk top', [5.6, 0.22, 2.3], [1, 1.04, 0.35], desk)
  cube(work, 'desk front', [5.25, 0.5, 0.1], [1, 0.74, -0.77], dark)
  for (const x of [-1.42, 3.42]) for (const z of [-0.55, 1.25]) cube(work, 'desk leg', [0.16, 1, 0.16], [x, 0.5, z], dark)
  cube(work, 'monitor stand', [0.12, 0.55, 0.12], [1.67, 1.43, 0.9], edge)
  cube(work, 'monitor base', [1.1, 0.05, 0.53], [1.67, 1.18, 0.9], edge)
  cube(work, 'monitor case', [2.85, 1.72, 0.14], [1.67, 2.35, 0.78], dark)
  const workScreen = cube(work, 'job board', [2.65, 1.48, 0.016], [1.67, 2.35, 0.695], new THREE.MeshBasicMaterial({ color: 0xffffff }))
  cube(work, 'screen accent', [2.86, 0.025, 0.025], [1.67, 3.23, 0.68], lime)
  cube(work, 'keyboard', [1.85, 0.09, 0.63], [0.3, 1.2, -0.43], dark)
  for (let row = 0; row < 4; row++) for (let col = 0; col < 11; col++) cube(work, 'key', [0.11, 0.016, 0.08], [-0.48 + col * 0.15, 1.26, -0.66 + row * 0.13], (row + col) % 13 ? edge : lime)
  cube(work, 'coffee', [0.33, 0.4, 0.32], [3.08, 1.35, -0.3], mat(0xf48468))
  cube(work, 'desk lamp stem', [0.05, 1.1, 0.05], [-1.15, 1.64, 1.2], edge)
  cube(work, 'desk lamp', [0.72, 0.13, 0.32], [-0.93, 2.2, 1.09], glow)
  for (let i = 0; i < 3; i++) cube(work, 'resume', [0.64, 0.012, 0.42], [2.7 + i * 0.055, 1.18 + i * 0.014, 1.02], mat(0xb6cbb9))

  cube(interview, 'meeting table', [6.4, 0.19, 2.6], [0.75, 1, 0.15], desk)
  for (const x of [-1.95, 3.45]) cube(interview, 'table leg', [0.19, 1, 0.2], [x, 0.49, 0.8], dark)
  cube(interview, 'wall display frame', [3.2, 1.9, 0.12], [1.25, 3.05, 4.14], edge)
  const interviewScreen = cube(interview, 'question display', [3.02, 1.72, 0.016], [1.25, 3.05, 4.045], new THREE.MeshBasicMaterial({ color: 0xffffff }))
  cube(interview, 'wall display neon', [3.2, 0.03, 0.05], [1.25, 4.02, 4.065], glow)
  cube(interview, 'laptop base', [1.7, 0.09, 0.9], [-0.2, 1.13, -0.44], dark)
  cube(interview, 'laptop lid', [1.7, 1.15, 0.09], [-0.2, 1.75, 0.02], edge)
  cube(interview, 'laptop screen', [1.5, 0.95, 0.014], [-0.2, 1.75, -0.03], glow)
  const person = new THREE.Group(); person.position.set(2.5, 0, 2.45); interview.add(person)
  cube(person, 'chair', [1.06, 1.7, 0.2], [0, 1.47, 0.48], dark)
  const torso = new THREE.Mesh(new THREE.CapsuleGeometry(0.45, 0.55, 5, 10), mat(0x49616d)); torso.position.y = 1.6; person.add(torso)
  const head = new THREE.Mesh(new THREE.SphereGeometry(0.3, 16, 12), mat(0xd5baa2)); head.position.y = 2.4; person.add(head)
  cube(person, 'hair', [0.54, 0.12, 0.53], [0, 2.68, 0], mat(0x24313b))
  for (const x of [-0.54, 0.54]) cube(person, 'arm', [0.18, 0.66, 0.18], [x, 1.58, -0.23], mat(0x49616d))
  return { work, interview, workScreen, interviewScreen, bay }
}

export function FlyScene3D({ status, activity, job, interviews, onReady }: Props) {
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const live = useRef({ status, activity, job, interviews })
  useEffect(() => { live.current = { status, activity, job, interviews } }, [status, activity, job, interviews])
  useEffect(() => {
    const canvas = canvasRef.current; if (!canvas) return
    let renderer: THREE.WebGLRenderer
    try { renderer = new THREE.WebGLRenderer({ canvas, antialias: true, powerPreference: 'high-performance' }) } catch { return }
    renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 1.75))
    renderer.outputColorSpace = THREE.SRGBColorSpace; renderer.toneMapping = THREE.ACESFilmicToneMapping; renderer.toneMappingExposure = 1.15
    const scene = new THREE.Scene(); scene.background = new THREE.Color(0x0b121b); scene.fog = new THREE.FogExp2(0x0b121b, 0.035)
    const ambient = new THREE.AmbientLight(0xa4c7d2, 0.9); scene.add(ambient)
    const key = new THREE.SpotLight(0xd9ffb8, 65, 22, Math.PI / 4, 0.55); key.position.set(-3, 7, -4); key.target.position.set(0, 1, 0); scene.add(key, key.target)
    const blue = new THREE.PointLight(0x60d8f2, 28, 11); blue.position.set(3, 3, 2); scene.add(blue)
    const room = buildRoom(scene)
    const { context, texture } = screenTexture()
    for (const screen of [room.workScreen, room.interviewScreen]) { const meshMat = screen.material as THREE.MeshBasicMaterial; meshMat.map = texture; meshMat.needsUpdate = true }
    const camera = new THREE.PerspectiveCamera(42, 1, 0.1, 100)
    const target = new THREE.Vector3(0.3, 1.65, 0.4)
    let orbit = 0.28, dragging = false, dragX = 0
    const placeCamera = () => { camera.position.set(target.x + Math.sin(orbit) * 10.1, target.y + 2.4, target.z - Math.cos(orbit) * 9.75); camera.lookAt(target) }
    const resize = () => { camera.aspect = Math.max(canvas.clientWidth, 1) / Math.max(canvas.clientHeight, 1); camera.fov = camera.aspect < 1 ? 49 : 42; camera.updateProjectionMatrix(); renderer.setSize(Math.max(canvas.clientWidth, 1), Math.max(canvas.clientHeight, 1), false); placeCamera() }
    const observer = new ResizeObserver(resize); observer.observe(canvas); resize()
    const down = (event: PointerEvent) => { dragging = true; dragX = event.clientX; canvas.setPointerCapture(event.pointerId) }
    const move = (event: PointerEvent) => { if (!dragging) return; orbit = THREE.MathUtils.clamp(orbit - (event.clientX - dragX) * 0.004, -0.9, 0.9); dragX = event.clientX; placeCamera() }
    const up = () => { dragging = false }
    canvas.addEventListener('pointerdown', down); canvas.addEventListener('pointermove', move); canvas.addEventListener('pointerup', up); canvas.addEventListener('pointercancel', up)
    const flyRoot = new THREE.Group(); scene.add(flyRoot)
    let disposed = false, mixer: THREE.AnimationMixer | null = null, currentAction: THREE.AnimationAction | null = null, currentClip = '', wingAction: THREE.AnimationAction | null = null
    const clips = new Map<string, THREE.AnimationClip>(), eyes: THREE.MeshStandardMaterial[] = [], antennae: THREE.Object3D[] = []
    new GLTFLoader().load('/models/fly-v1.glb', gltf => {
      if (disposed) return
      const fly = gltf.scene, bounds = new THREE.Box3().setFromObject(fly), size = bounds.getSize(new THREE.Vector3()), center = bounds.getCenter(new THREE.Vector3())
      const scale = 1.35 / Math.max(size.y, 0.01)
      fly.scale.setScalar(scale)
      fly.position.set(-center.x * scale, -bounds.min.y * scale, -center.z * scale)
      fly.traverse(object => {
        if (object.name.startsWith('Antenna.') && object.children.length) antennae.push(object)
        if (object instanceof THREE.Mesh && object.name.startsWith('Fly_Eye.') && object.material instanceof THREE.MeshStandardMaterial) {
          const eye = object.material.clone(); eye.emissive.setHex(0x963719); object.material = eye; eyes.push(eye)
        }
      })
      flyRoot.add(fly); mixer = new THREE.AnimationMixer(fly)
      for (const clip of gltf.animations) clips.set(clip.name, clip)
      const wing = clips.get('WingFlap')
      if (wing) { wingAction = mixer.clipAction(THREE.AnimationUtils.makeClipAdditive(wing.clone()), undefined, THREE.AdditiveAnimationBlendMode); wingAction.play() }
      onReady()
    }, undefined, () => undefined)
    let frame = 0, lastFrame = performance.now(), lastTick = -1, lastStage = '', lastDecision = -1, decisionAge = 0, impulse = 0, gait = 0, turn = 0, threat = 0, tickReceivedAt = performance.now()
    const reduced = window.matchMedia('(prefers-reduced-motion: reduce)')
    const animate = () => {
      frame = requestAnimationFrame(animate)
      const now = performance.now(), dt = Math.min((now - lastFrame) / 1000, 0.05); lastFrame = now
      const { status: current, activity: brain, job: currentJob, interviews: currentInterviews } = live.current
      const motor = flyMotion(brain), interview = current.is_daytime && interviewStages.has(current.stage)
      room.work.visible = !interview; room.interview.visible = interview
      if (lastTick !== current.tick_count || lastStage !== current.stage) { lastTick = current.tick_count; lastStage = current.stage; tickReceivedAt = now; drawScreen(context, texture, current, currentJob, currentInterviews) }
      const clockMinutes = Number.isFinite(current.clock_minutes) ? current.clock_minutes : 8 * 60
      const tickSeconds = Number.isFinite(current.tick_seconds) ? Math.max(current.tick_seconds, 0.02) : 4.5
      const clockHour = (clockMinutes / 60 + Math.min((now - tickReceivedAt) / (tickSeconds * 1000), 1) * 0.25) % 24
      room.bay.update(clockHour)
      const sun = Math.max(0, Math.sin((clockHour - 6) / 14 * Math.PI))
      ambient.intensity = 0.36 + sun * 0.6
      key.intensity = 13 + sun * 52
      key.color.setHex(clockHour >= 17 && clockHour < 20 ? 0xffcaa1 : 0xd9ffdf)
      if (lastDecision !== brain.decision_count) { lastDecision = brain.decision_count; decisionAge = 0; impulse = 0.3 + motor.drive * 0.6 }
      decisionAge += dt
      const fresh = Math.max(0, 1 - decisionAge / 5)
      const typing = current.stage === 'APPLICATION_SENT' || (current.is_daytime && current.stage === 'TECHNICAL_INTERVIEW')
      const searching = current.stage === 'SEARCHING_FOR_JOB' || current.stage === 'VIEWING_JOB'
      const desired = current.stage === 'FINAL_RESULT' || motor.escape * fresh > 0.52 || motor.threat * fresh > 0.75 ? 'Startle' : typing ? 'Type' : searching && fresh > 0.3 && motor.approach > motor.avoidance ? 'Walk' : 'Idle'
      if (mixer && desired !== currentClip) {
        const clip = clips.get(desired) ?? clips.get('Idle')
        if (clip) { const action = mixer.clipAction(clip); action.reset().setLoop(desired === 'Startle' ? THREE.LoopOnce : THREE.LoopRepeat, Infinity).play(); action.clampWhenFinished = desired === 'Startle'; if (currentAction) action.crossFadeFrom(currentAction, 0.38, true); currentAction = action; currentClip = desired }
      }
      if (currentAction) currentAction.timeScale = 0.24 + motor.drive * fresh * 0.9 + (typing ? motor.approach * fresh * 0.3 : 0)
      if (wingAction) { wingAction.setEffectiveWeight(reduced.matches ? 0 : 0.04 + motor.threat * fresh * 0.46 + impulse * 0.24); wingAction.timeScale = 0.55 + motor.threat * fresh * 2.4 + motor.drive * fresh * 0.8 }
      if (!reduced.matches) mixer?.update(dt)
      turn = THREE.MathUtils.damp(turn, motor.turn * fresh, 4.2, dt); threat = THREE.MathUtils.damp(threat, motor.threat * fresh, 3.4, dt)
      impulse = Math.max(0, impulse - dt * 0.27); gait += dt * (1.4 + motor.drive * fresh * 2.8 + (typing ? 0.6 : 0))
      flyRoot.position.x = THREE.MathUtils.damp(flyRoot.position.x, -1.0 + (motor.approach - motor.avoidance + motor.forward - motor.escape) * fresh * 0.25, 2, dt)
      flyRoot.position.y = 1.15 + (reduced.matches ? 0 : Math.sin(gait) * (0.018 + motor.drive * fresh * 0.045) + impulse * 0.09)
      flyRoot.position.z = THREE.MathUtils.damp(flyRoot.position.z, (interview ? -1.05 : -0.35) + (-motor.escape * 0.18 + motor.forward * 0.12) * fresh, 2, dt)
      flyRoot.rotation.y = THREE.MathUtils.damp(flyRoot.rotation.y, -0.7 + turn * 0.44 + (interview ? 0.22 : 0), 2, dt)
      flyRoot.rotation.z = reduced.matches ? 0 : turn * 0.11 + Math.sin(gait * 0.5) * (current.stage === 'DECIDING_TO_APPLY' ? motor.uncertainty * 0.075 : 0.015)
      flyRoot.rotation.x = reduced.matches ? 0 : -threat * 0.07
      antennae.forEach((antenna, index) => { antenna.rotation.z = (index ? -1 : 1) * motor.uncertainty * fresh * (reduced.matches ? 0.04 : 0.06 + Math.sin(gait * 1.6 + index) * 0.04) })
      eyes.forEach(eye => { eye.emissiveIntensity = 0.14 + motor.drive * fresh * 0.75 + impulse * 0.45 })
      blue.intensity = 16 + motor.threat * fresh * 20 + (1 - sun) * 10
      renderer.render(scene, camera)
    }
    animate()
    return () => { disposed = true; cancelAnimationFrame(frame); observer.disconnect(); canvas.removeEventListener('pointerdown', down); canvas.removeEventListener('pointermove', move); canvas.removeEventListener('pointerup', up); canvas.removeEventListener('pointercancel', up); mixer?.stopAllAction(); scene.traverse(object => { if (object instanceof THREE.Mesh) { object.geometry.dispose(); (Array.isArray(object.material) ? object.material : [object.material]).forEach(m => m.dispose()) } }); room.bay.dispose(); texture.dispose(); renderer.dispose() }
  }, [onReady])
  return <canvas ref={canvasRef} className="flyViewport" aria-label="Interactive 3D fly scene. Drag to rotate the camera." />
}
