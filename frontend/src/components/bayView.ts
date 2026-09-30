import * as THREE from 'three'

type Palette = { hour: number; top: string; horizon: string; water: string; hill: string; city: string }

const palettes: Palette[] = [
  { hour: 0, top: '#071326', horizon: '#233352', water: '#0b2740', hill: '#101f33', city: '#15243a' },
  { hour: 5, top: '#13223d', horizon: '#9b637b', water: '#3b5271', hill: '#353a5c', city: '#2b354b' },
  { hour: 7, top: '#536b9e', horizon: '#ffc18b', water: '#88a9b7', hill: '#667585', city: '#5c667b' },
  { hour: 11, top: '#397fc0', horizon: '#c4e8e8', water: '#448db1', hill: '#839c9e', city: '#566e84' },
  { hour: 16, top: '#5c9fca', horizon: '#f6d6b3', water: '#5796aa', hill: '#8e9692', city: '#697882' },
  { hour: 19, top: '#51487c', horizon: '#f4a77d', water: '#53607c', hill: '#6d566e', city: '#47465d' },
  { hour: 21, top: '#101a3b', horizon: '#485078', water: '#193854', hill: '#24304c', city: '#1d2b46' },
  { hour: 24, top: '#071326', horizon: '#233352', water: '#0b2740', hill: '#101f33', city: '#15243a' },
]

const clamp = (value: number) => Math.min(1, Math.max(0, value))
function mixColor(a: string, b: string, t: number): string {
  const first = new THREE.Color(a), second = new THREE.Color(b)
  first.lerp(second, t)
  return `#${first.getHexString()}`
}

function colorsAt(hour: number) {
  const end = palettes.findIndex(point => point.hour >= hour)
  const right = palettes[Math.max(1, end)]
  const left = palettes[Math.max(0, end - 1)]
  const t = clamp((hour - left.hour) / (right.hour - left.hour))
  return {
    top: mixColor(left.top, right.top, t),
    horizon: mixColor(left.horizon, right.horizon, t),
    water: mixColor(left.water, right.water, t),
    hill: mixColor(left.hill, right.hill, t),
    city: mixColor(left.city, right.city, t),
  }
}

function hill(context: CanvasRenderingContext2D, color: string, points: number[], baseline: number) {
  context.fillStyle = color
  context.beginPath()
  context.moveTo(0, baseline)
  context.lineTo(0, points[0])
  for (let index = 1; index < points.length; index++) {
    context.lineTo(index * 128, points[index])
  }
  context.lineTo(1536, baseline)
  context.closePath()
  context.fill()
}

function skyline(context: CanvasRenderingContext2D, color: string, hour: number) {
  const nighttime = clamp((7 - hour) / 2) + clamp((hour - 19) / 2)
  context.fillStyle = color
  for (let index = 0; index < 47; index++) {
    const x = 30 + index * 33
    const height = 38 + ((index * 41 + index * index * 11) % 100)
    const width = 20 + (index % 4) * 5
    context.fillRect(x, 347 - height, width, height)
    if (nighttime > 0.05) {
      context.fillStyle = `rgba(255,206,129,${nighttime * 0.48})`
      for (let row = 0; row < Math.floor(height / 13); row++) {
        for (let col = 0; col < Math.floor(width / 8); col++) {
          if ((index * 7 + row * 3 + col * 5) % 4 === 0) context.fillRect(x + 5 + col * 8, 347 - height + 7 + row * 13, 2, 3)
        }
      }
      context.fillStyle = color
    }
  }
  // Two recognizable but stylized SF towers: a tapering pyramid and a rounded spire.
  context.beginPath()
  context.moveTo(895, 347); context.lineTo(920, 196); context.lineTo(945, 347); context.closePath(); context.fill()
  context.fillRect(1115, 165, 30, 182)
  context.beginPath(); context.ellipse(1130, 165, 15, 10, 0, Math.PI, 0); context.fill()
  context.fillRect(1128, 147, 4, 20)
}

function bridge(context: CanvasRenderingContext2D, hour: number) {
  const warm = hour >= 7 && hour < 19
  context.strokeStyle = warm ? '#c96c59' : '#a85357'
  context.lineWidth = 8
  context.beginPath(); context.moveTo(0, 370); context.lineTo(735, 370); context.stroke()
  context.lineWidth = 11
  for (const x of [160, 555]) {
    context.beginPath(); context.moveTo(x, 370); context.lineTo(x, 221); context.stroke()
    context.beginPath(); context.moveTo(x - 14, 236); context.lineTo(x + 14, 236); context.stroke()
  }
  context.lineWidth = 4
  context.beginPath()
  context.moveTo(-40, 278)
  context.bezierCurveTo(45, 310, 90, 315, 160, 234)
  context.bezierCurveTo(258, 349, 448, 349, 555, 234)
  context.bezierCurveTo(620, 308, 670, 310, 765, 280)
  context.stroke()
  context.lineWidth = 1.5
  for (let x = 0; x < 735; x += 24) {
    const sag = x < 160 ? 234 + (160 - x) * 0.3 : x < 555 ? 234 + 114 * Math.sin((x - 160) / 395 * Math.PI) : 234 + (x - 555) * 0.3
    context.beginPath(); context.moveTo(x, sag); context.lineTo(x, 369); context.stroke()
  }
}

export function createBayView() {
  const canvas = document.createElement('canvas')
  canvas.width = 1536
  canvas.height = 512
  const context = canvas.getContext('2d')!
  const texture = new THREE.CanvasTexture(canvas)
  texture.colorSpace = THREE.SRGBColorSpace
  const material = new THREE.MeshBasicMaterial({ map: texture, depthWrite: false, side: THREE.DoubleSide })
  const mesh = new THREE.Mesh(new THREE.PlaneGeometry(13.42, 3.9), material)
  mesh.name = 'San Francisco-inspired bay panorama'
  mesh.position.set(0, 3.37, 4.52)

  let lastHour = -1
  function update(hour: number) {
    if (!Number.isFinite(hour)) return
    if (Math.abs(hour - lastHour) < 0.015) return
    lastHour = hour
    const palette = colorsAt(hour)
    const sky = context.createLinearGradient(0, 0, 0, 355)
    sky.addColorStop(0, palette.top)
    sky.addColorStop(1, palette.horizon)
    context.fillStyle = sky
    context.fillRect(0, 0, 1536, 512)

    const daylight = clamp((hour - 6) / 2) * clamp((20 - hour) / 2)
    const sunX = 90 + ((hour - 6) / 14) * 1350
    const sunY = 245 - Math.sin(clamp((hour - 6) / 14) * Math.PI) * 195
    if (daylight > 0) {
      const glow = context.createRadialGradient(sunX, sunY, 1, sunX, sunY, 118)
      glow.addColorStop(0, `rgba(255,228,165,${daylight * 0.56})`)
      glow.addColorStop(1, 'rgba(255,228,165,0)')
      context.fillStyle = glow; context.fillRect(sunX - 118, sunY - 118, 236, 236)
      context.fillStyle = `rgba(255,245,207,${daylight * 0.9})`
      context.beginPath(); context.arc(sunX, sunY, 17, 0, Math.PI * 2); context.fill()
    } else {
      context.fillStyle = '#d5dded'
      context.beginPath(); context.arc(1160, 84, 12, 0, Math.PI * 2); context.fill()
    }

    const stars = clamp((7 - hour) / 2) + clamp((hour - 19) / 2)
    if (stars > 0) {
      context.fillStyle = `rgba(233,244,255,${Math.min(stars, 1) * 0.65})`
      for (let index = 0; index < 80; index++) {
        const x = (index * 227 + index * index * 17) % 1536
        const y = 12 + (index * 89 + index * index * 7) % 250
        context.fillRect(x, y, index % 7 === 0 ? 2 : 1, index % 7 === 0 ? 2 : 1)
      }
    }

    hill(context, palette.hill, [320, 314, 326, 299, 308, 323, 302, 310, 291, 302, 322, 314, 301], 390)
    context.fillStyle = palette.water; context.fillRect(0, 347, 1536, 165)
    context.fillStyle = `rgba(241,220,176,${0.06 + daylight * 0.12})`
    for (let index = 0; index < 110; index++) {
      const x = (index * 211 + index * index * 23) % 1536
      const y = 360 + (index * 61) % 135
      context.fillRect(x, y, 7 + index % 18, 1)
    }
    skyline(context, palette.city, hour)
    bridge(context, hour)
    texture.needsUpdate = true
  }

  update(8)
  return { mesh, update, dispose: () => texture.dispose() }
}
