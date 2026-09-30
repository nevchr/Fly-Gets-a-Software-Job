import type { InterviewStats, Job, Status } from '../types/simulation'

interface Props {
  status: Status
  job: Job | null
  interviews: InterviewStats | null
}

const stageNumbers: Record<string, string> = {
  SEARCHING_FOR_JOB: '00', VIEWING_JOB: '01', DECIDING_TO_APPLY: '02',
  APPLICATION_SENT: '03', APPLICATION_RESULT: '04', RECRUITER_SCREEN: '05',
  TECHNICAL_INTERVIEW: '06', BEHAVIORAL_INTERVIEW: '07', FINAL_RESULT: '08',
}

const stages = Object.keys(stageNumbers)

function InterviewCard({ interviews }: { interviews: InterviewStats }) {
  const latest = interviews.latest_attempt
  if (!latest) return <p className="emptyCopy">No technical evidence yet. Confidence remains statistically unburdened.</p>
  return (
    <div className="questionCard">
      <div className="questionMeta"><span>{latest.category}</span><span>DIFFICULTY {latest.difficulty}/3</span></div>
      <h3>{latest.question}</h3>
      <div className="answerList">
        {latest.choices.map((choice, index) => (
          <div className={`answer ${index === latest.selected_index ? 'selected' : ''} ${index === latest.correct_index ? 'correct' : ''}`} key={choice}>
            <span>{String.fromCharCode(65 + index)}</span>{choice}
          </div>
        ))}
      </div>
    </div>
  )
}

export function CurrentSituation({ status, job, interviews }: Props) {
  const activeIndex = stages.indexOf(status.stage)
  return (
    <section className="panel stepPanel">
      <div className="miniHeading">
        <span>01</span><h2>CURRENT STEP</h2><i>STAGE_{stageNumbers[status.stage] ?? '??'}</i>
      </div>
      <div className="stepBody">
        <div className="stageProgress" aria-label={`Hiring pipeline: ${status.stage_label}`}>
          {stages.map((stage, index) => <span className={index === activeIndex ? 'active' : index < activeIndex ? 'passed' : ''} key={stage} />)}
        </div>
        <p className="stepEyebrow">{status.stage_label}</p>
        <h3>{status.current_status}</h3>
        {job ? <div className="activeJob">
          <div><strong>{job.company_name}</strong><span>{job.title}</span></div>
          <b>{Math.round(job.qualification_match * 100)}% MATCH</b>
          <dl>
            <div><dt>Salary</dt><dd>${job.salary.toLocaleString()}</dd></div>
            <div><dt>Mode</dt><dd>{job.work_mode}</dd></div>
            <div><dt>Experience</dt><dd>{job.required_experience_years}+ years</dd></div>
          </dl>
          <blockquote>“{job.absurd_requirement}”</blockquote>
        </div> : <p className="stepEmpty">Scanning for a role that requires fewer years of experience than the fly has minutes to live.</p>}
        {status.stage === 'TECHNICAL_INTERVIEW' && interviews && <InterviewCard interviews={interviews} />}
      </div>
    </section>
  )
}
