import type { InterviewStats } from '../types/simulation'

export function InterviewAccuracy({ stats }: { stats: InterviewStats }) {
  return (
    <section className="panel accuracyPanel">
      <div className="miniHeading"><span>04</span><h2>TECHNICAL ACCURACY</h2><strong>{Math.round(stats.accuracy * 100)}%</strong></div>
      {stats.categories.length ? <div className="accuracyRows">
        {stats.categories.map((row) => <div className="accuracyRow" key={row.category}>
          <span>{row.category}</span><div><i style={{ width: `${row.accuracy * 100}%` }} /></div><b>{row.correct}/{row.attempts}</b>
        </div>)}
      </div> : <p className="emptyCopy">Awaiting the first whiteboard-related incident.</p>}
    </section>
  )
}

