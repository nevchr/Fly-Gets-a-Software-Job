import { lazy, Suspense } from 'react'
import type { BrainActivity } from '../types/simulation'

const Connectome3D = lazy(() => import('./Connectome3D').then(module => ({ default: module.Connectome3D })))

const visualCatalog = [
  { bodyId: 10573, label: 'LC10a_L', color: '#66d6db' },
  { bodyId: 21065, label: 'LC10a_R', color: '#8fb8ee' },
  { bodyId: 16128, label: 'LC4_R', color: '#e9a078' },
  { bodyId: 14465, label: 'LPLC2_R', color: '#c8aaec' },
  { bodyId: 12052, label: 'LPLC1_L', color: '#e5cf7e' },
  { bodyId: 523769, label: 'DNa02_L', color: '#cbf570' },
  { bodyId: 10360, label: 'DNa02_R', color: '#ed8068' },
]

export function NeuralActivity({ activity }: { activity: BrainActivity }) {
  const isConnectome = activity.backend === 'connectome'
  const hasTracedActivity = visualCatalog.every(neuron =>
    activity.visual_neurons?.some(sample => sample.body_id === neuron.bodyId),
  )
  const peakOutput = Math.max(1, ...activity.output_activity.map((output) => output.spike_rate))
  const nodes = Array.from({ length: 54 }, (_, index) => ({
    x: 52 + (index * 79) % 456,
    y: 50 + (index * 47 + (index % 4) * 23) % 205,
    signal: activity.spikes.length ? activity.spikes[index % activity.spikes.length] : 0,
  }))
  return (
    <section className="panel neuralPanel">
      <div className="miniHeading"><span>03</span><h2>BRAIN VISUAL / REAL DATA</h2><i>{isConnectome ? 'LIVE CONNECTOME' : 'MOCK BRAIN'}</i></div>
      {isConnectome && (
        <>
          <div className="connectomeIdentity">
            <strong>MALECNS v1.0</strong>
            <span>{activity.neuron_count.toLocaleString()} NEURONS</span>
            <span>{activity.connection_count.toLocaleString()} MODEL EDGES</span>
          </div>
          <p className="connectomeSource">
            REAL ANATOMY: MALECNS v1.0 ·{' '}
            <a
              href="https://male-cns.janelia.org/download/"
              target="_blank"
              rel="noreferrer"
            >
              HHMI JANELIA DATA ↗
            </a>
          </p>
        </>
      )}
      <div className={`brainViz${isConnectome ? ' brainViz--3d' : ''}`} aria-label={`Normalized mean neural firing rate ${Math.round(activity.activation * 100)} percent`}>
        {isConnectome ? (
          <Suspense fallback={<p className="connectomeLoad">Loading real MaleCNS anatomy…</p>}>
            <Connectome3D activity={activity} />
          </Suspense>
        ) : (
          <svg viewBox="0 0 560 300" role="img" aria-hidden="true">
            <path className="brainOutline" d="M84 168C32 72 143 18 224 70c45-69 162-59 183 17 97-20 140 99 69 153-59 44-142 12-189 18-79 41-170 2-203-90Z" />
            {nodes.slice(1).map((node, index) => <line className="synapse" key={`line-${index}`} x1={nodes[index].x} y1={nodes[index].y} x2={node.x} y2={node.y} />)}
            {nodes.map((node, index) => <circle key={index} cx={node.x} cy={node.y} r={node.signal > 0.52 ? 5 : 2.4} className={node.signal > 0.52 ? 'neuron active' : 'neuron'} />)}
            <text className="brainWatermark" x="280" y="284" textAnchor="middle">MOCK ACTIVITY</text>
          </svg>
        )}
        {!isConnectome && <div className="scanLine" />}
        <div className="activityBadge"><b>{Math.round(activity.activation * 100)}%</b><span>NORM. RATE</span></div>
      </div>
      {isConnectome && (
        <div className="connectomeLegend">
          <p>REAL ANATOMY <span>125,020 POSITION POINTS · 7 TRACED CELLS</span></p>
          <div>
            {visualCatalog.map(neuron => {
              const sampled = activity.visual_neurons?.find(item => item.body_id === neuron.bodyId)
              return <span key={`${neuron.bodyId}-${activity.decision_count}`} className={sampled?.spike_count ? 'isFiring' : undefined}><i style={{ background: neuron.color, boxShadow: sampled?.spike_count ? `0 0 10px 2px ${neuron.color}` : 'none' }} /><b>{neuron.label}</b><em>{sampled ? `${sampled.spike_rate.toFixed(1)} Hz` : '—'}</em></span>
            })}
          </div>
          <small>{hasTracedActivity
            ? 'MaleCNS v1.0 · CC BY 4.0. A glowing surge follows the real branches, with a spark on one continuous branch. Travel direction and speed are illustrative, not measured.'
            : 'Anatomy is loaded; live rates for traced cells need the updated backend. Restart the backend to enable them.'}</small>
        </div>
      )}
      <div className="waveform">{activity.spikes.map((spike, index) => <i key={index} style={{ height: `${8 + spike * 38}px` }} />)}</div>
      {isConnectome && activity.input_activity.length > 0 && (
        <div className="inputReadout">
          <p>SENSORY POPULATIONS · SIMULATED FIRING</p>
          <div>{activity.input_activity.map((input) => <span key={`${input.name}-${activity.decision_count}`}><b>{input.population}_{input.side}</b>{input.spike_rate?.toFixed(1) ?? '—'} Hz</span>)}</div>
        </div>
      )}
      {isConnectome && activity.output_activity.length > 0 && (
        <div className="outputReadout">
          <p>DESCENDING OUTPUTS</p>
          {activity.output_activity.map((output) => (
            <div className={output.selected ? 'selectedOutput' : ''} key={output.name}>
              <span>{output.name}</span>
              <i><b style={{ width: `${(output.spike_rate / peakOutput) * 100}%` }} /></i>
              <em>{output.spike_rate.toFixed(1)} Hz</em>
            </div>
          ))}
        </div>
      )}
      <div className="brainReadout">
        <span><b>{activity.spike_rate.toFixed(1)}</b> MEAN HZ</span>
        <span>ACTIVE: <b>{activity.active_neurons.toLocaleString()}</b></span>
        <span>LATENCY: <b>{activity.decision_latency_ms.toFixed(0)} MS</b></span>
        <span>DECISIONS: <b>{activity.decision_count}</b></span>
      </div>
    </section>
  )
}
