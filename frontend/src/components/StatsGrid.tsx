import type { CareerStats } from '../types/simulation'

const fmt = new Intl.NumberFormat('en-CA')
const moods = [
  'HOPEFUL AGAINST EVIDENCE', 'OPTIMISM BUFFERING', 'BUZZING THROUGH IT',
  'ONE TAB FROM BREAKTHROUGH', 'STILL SOMEHOW MOTIVATED', 'CAUTIOUSLY EMPLOYABLE',
  'REJECTION RESILIENT', 'ASK AGAIN AFTER THE NEXT EMAIL', 'ABSOLUTELY COOKED',
  'PRACTICING POSITIVE SPIN', 'MILDLY OVERQUALIFIED FOR FLIGHT', 'READY TO CIRCLE BACK',
]

export function StatsGrid({ stats }: { stats: CareerStats }) {
  const rejected = stats.immediate_rejections + stats.ghosted
    + (stats.recruiter_screens - stats.technical_interviews)
    + (stats.technical_interviews - stats.behavioral_interviews)
    + (stats.behavioral_interviews - stats.final_rounds)
    + (stats.final_rounds - stats.offers)
  const core = [
    ['APPLICATIONS', stats.applications_sent], ['REJECTIONS', rejected],
    ['INTERVIEWS', stats.technical_interviews], ['OFFERS', stats.offers],
  ] as const
  const mood = stats.offers > 0 && stats.current_rejection_streak === 0
    ? 'ONE SMALL VICTORY'
    : moods[stats.jobs_viewed % moods.length]
  return (
    <section className="panel statsPanel">
      <div className="miniHeading"><span>02</span><h2>CAREER STATS</h2></div>
      <div className="bigStats">
        {core.map(([label, value], index) => <div key={label}><i>0{index + 1}</i><strong>{fmt.format(value)}</strong><span>{label}</span></div>)}
      </div>
      <dl className="detailStats">
        <div><dt>Current rejection streak</dt><dd>{stats.current_rejection_streak}</dd></div>
        <div><dt>Longest application streak</dt><dd>{stats.longest_application_streak}</dd></div>
        <div><dt>Highest salary attempted</dt><dd>${fmt.format(stats.highest_salary_applied_to)}</dd></div>
        <div><dt>Lowest qualification match</dt><dd>{stats.lowest_qualification_match === null ? '—' : `${Math.round(stats.lowest_qualification_match * 100)}%`}</dd></div>
      </dl>
      <p className="emotionalState"><span>UNSCIENTIFIC VIBE CHECK</span><b>{mood}</b></p>
    </section>
  )
}
