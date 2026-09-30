import { lazy, Suspense, useCallback, useEffect, useRef, useState } from 'react'
import type { BrainActivity, InterviewStats, Job, Status } from '../types/simulation'
import { ApplicationScene, InterviewScene } from './StageScenes'
import { sceneCopyFor } from '../content/stageCopy'

const FlyScene3D = lazy(() => import('./FlyScene3D').then(module => ({ default: module.FlyScene3D })))

interface Props {
  status: Status
  job: Job | null
  activity: BrainActivity
  interviews: InterviewStats
}

const interviewStages = new Set(['RECRUITER_SCREEN', 'TECHNICAL_INTERVIEW', 'BEHAVIORAL_INTERVIEW'])
const sceneFor = (stage: string, daytime: boolean) => daytime && interviewStages.has(stage) ? 'interview' : 'application'

type SceneSwitch = { from: string; to: string; title: string; detail: string }

export function FlyStage({ status, job, activity, interviews }: Props) {
  const [modelReady, setModelReady] = useState(false)
  const [visibleStage, setVisibleStage] = useState(status.stage)
  const [visibleDaytime, setVisibleDaytime] = useState(status.is_daytime)
  const [sceneSwitch, setSceneSwitch] = useState<SceneSwitch | null>(null)
  const visibleStageRef = useRef(status.stage)
  const visibleDaytimeRef = useRef(status.is_daytime)
  const switchTimers = useRef<ReturnType<typeof setTimeout>[]>([])
  const handleModelReady = useCallback(() => setModelReady(true), [])
  useEffect(() => {
    const nextStage = status.stage
    const from = sceneFor(visibleStageRef.current, visibleDaytimeRef.current)
    const to = sceneFor(nextStage, status.is_daytime)
    switchTimers.current.forEach(clearTimeout)
    switchTimers.current = []
    if (from === to) {
      visibleStageRef.current = nextStage
      visibleDaytimeRef.current = status.is_daytime
      setVisibleStage(nextStage)
      setVisibleDaytime(status.is_daytime)
      setSceneSwitch(null)
      return
    }
    setSceneSwitch(to === 'interview'
      ? { from, to, title: 'INTERVIEW CALL INCOMING', detail: 'Office hours are open · joining the interview room' }
      : !status.is_daytime
        ? { from, to, title: 'AFTER HOURS', detail: 'Interview paused · applications and job searching only until 7:00 AM' }
        : { from, to, title: 'BACK TO THE JOB HUNT', detail: 'Interview ended · returning to the application desk' })
    switchTimers.current = [
      setTimeout(() => { visibleStageRef.current = nextStage; visibleDaytimeRef.current = status.is_daytime; setVisibleStage(nextStage); setVisibleDaytime(status.is_daytime) }, 900),
      setTimeout(() => setSceneSwitch(null), 1850),
    ]
  }, [status.stage, status.is_daytime])
  useEffect(() => () => switchTimers.current.forEach(clearTimeout), [])

  const scene = sceneCopyFor(visibleStage, status.tick_count, job?.id)
  const sceneKind = sceneFor(visibleStage, visibleDaytime)
  const visibleStatus = visibleStage === status.stage && visibleDaytime === status.is_daytime ? status : { ...status, stage: visibleStage, is_daytime: visibleDaytime }
  const waitingForMorning = !visibleDaytime && (interviewStages.has(visibleStage) || visibleStage === 'APPLICATION_RESULT' || visibleStage === 'FINAL_RESULT')
  const signal = Math.round(activity.activation * 100)
  const selectedMotor = activity.output_activity.find(output => output.selected)

  return (
    <section
      className={`flyStage flyStage--${sceneKind} flyStage--${scene.mode}${modelReady ? ' flyStage--modelReady' : ''}`}
      data-scene={sceneKind}
      aria-labelledby="fly-stage-title"
    >
      <div className="stageChrome">
        <div><span className="recordDot" />FLY CAM / LIVE</div>
        <span>{sceneKind === 'interview' ? 'INTERVIEW ROOM' : visibleDaytime ? 'APPLICATION DESK' : 'APPLICATION DESK · AFTER HOURS'}</span>
        <span>NEURAL SIGNAL {signal}%</span>
      </div>

      <div className="stageCopy">
        <p>{waitingForMorning ? 'AFTER HOURS' : scene.kicker} // {visibleStage.replaceAll('_', ' ')}</p>
        <h2 id="fly-stage-title">{waitingForMorning ? interviewStages.has(visibleStage) ? 'Interview resumes at 7:00 AM' : 'Hiring replies wait until morning' : scene.title}</h2>
        <span>{job ? `${job.company_name} · ${job.title}` : 'Scanning the internet for “entry level”'}</span>
      </div>

      {!modelReady && (sceneKind === 'interview'
        ? <InterviewScene stage={visibleStage} screen={scene.screen} interviews={interviews} />
        : <ApplicationScene screen={scene.screen} />)}

      <Suspense fallback={null}>
        <FlyScene3D status={visibleStatus} activity={activity} job={job} interviews={interviews} onReady={handleModelReady} />
      </Suspense>

      {sceneSwitch && <div className="sceneSwitch" key={`${sceneSwitch.from}-${sceneSwitch.to}-${status.tick_count}`} role="status" aria-live="polite">
        <div className="sceneSwitchScan" aria-hidden="true" />
        <div className="sceneSwitchCard"><span className="sceneSwitchLabel"><i /> LIVE CAMERA SWITCH</span><strong>{sceneSwitch.title}</strong><p>{sceneSwitch.detail}</p><div className="sceneSwitchRoute"><span>{sceneSwitch.from === 'interview' ? 'INTERVIEW ROOM' : 'APPLICATION DESK'}</span><b>→</b><span>{sceneSwitch.to === 'interview' ? 'INTERVIEW ROOM' : 'APPLICATION DESK'}</span></div></div>
      </div>}

      <div className="stageNeural" aria-live="polite">
        <span>LATEST MOTOR READOUT / {activity.backend === 'connectome' ? 'MALECNS' : 'SIMULATED'}</span>
        <strong>{selectedMotor?.name ?? 'AWAITING SIGNAL'}</strong>
        <small>Latest decision spikes → fly rig <i>·</i> drag to orbit</small>
      </div>

      <div className="stageStatus">
        <span>NOW</span>
        <p>{visibleStage === status.stage ? status.current_status : 'Switching to the next camera'}</p>
        <i aria-hidden="true" />
      </div>
    </section>
  )
}
