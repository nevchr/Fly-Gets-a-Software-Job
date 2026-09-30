import { CurrentSituation } from './components/CurrentSituation'
import { EventFeed } from './components/EventFeed'
import { FlyStage } from './components/FlyStage'
import { Header } from './components/Header'
import { InterviewAccuracy } from './components/InterviewAccuracy'
import { NeuralActivity } from './components/NeuralActivity'
import { StatsGrid } from './components/StatsGrid'
import { useSimulation } from './hooks/useSimulation'
import './styles/app.css'

export default function App() {
  const { status, stats, job, events, interviews, connected, error } = useSimulation()
  if (!status || !stats || !interviews) {
    return <main className="loadingScreen"><div className="loadingFly">FLY</div><h1>Establishing neural link…</h1><p>{error ?? 'Contacting the shared career timeline.'}</p></main>
  }
  return (
    <main className="appShell">
      <Header day={status.simulated_day} clockMinutes={status.clock_minutes} isDaytime={status.is_daytime} connected={connected} />
      {error && <div className="connectionWarning">{error}</div>}
      <div className="broadcastGrid">
        <div className="broadcastMain">
          <FlyStage status={status} job={job} activity={status.brain_activity} interviews={interviews} />
          <div className="streamDetails">
            <div className="channelAvatar" aria-hidden="true">F</div>
            <div className="channelCopy">
              <p className="channelName">fly.exe <span>· the world’s smallest job seeker</span></p>
              <h2>Trying to get a software job with one borrowed connectome</h2>
              <div className="streamTags"><span>LIVE BUG CAM</span><span>CAREER SIM</span><span>NO REFERRALS</span></div>
            </div>
            <div className="channelStatus"><span className="liveDot" />{connected ? 'ON AIR' : 'RECONNECTING'}</div>
          </div>
        </div>
        <EventFeed events={events} />
      </div>
      <div className="cockpitGrid">
        <div className="leftColumn">
          <CurrentSituation status={status} job={job} interviews={interviews} />
          <StatsGrid stats={stats} />
        </div>
        <NeuralActivity activity={status.brain_activity} />
      </div>
      <div className="lowerGrid">
        <InterviewAccuracy stats={interviews} />
        <div className="afterHoursCard">
          <span>ABOUT THE STREAM</span>
          <h2>One fly. An entire hiring pipeline. Absolutely no networking skills.</h2>
          <p>The career decisions come from the running neural simulation. The fly cam and connectome view visualize those signals; they are not a recording of a real fly at work.</p>
        </div>
      </div>
      <footer><span>SIMULATION TICK {status.tick_count.toString().padStart(6, '0')}</span><p>One fly. One timeline. No referrals.</p><span>MALECNS // LIVE EXPERIMENT</span></footer>
    </main>
  )
}
