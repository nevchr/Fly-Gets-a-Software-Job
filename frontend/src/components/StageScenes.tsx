import type { InterviewStats } from '../types/simulation'

function FallbackFly() {
  return (
    <g className="heroFly">
      <ellipse className="flyShadow" cx="394" cy="411" rx="126" ry="18" />
      <g className="flyBodyGroup">
        <ellipse className="heroWing heroWing--left" cx="351" cy="228" rx="92" ry="44" transform="rotate(-31 351 228)" />
        <ellipse className="heroWing heroWing--right" cx="460" cy="216" rx="92" ry="44" transform="rotate(25 460 216)" />
        <ellipse className="heroThorax" cx="407" cy="287" rx="68" ry="83" />
        <path className="heroAbdomen" d="M370 326c-6 67 11 94 45 94s54-30 43-94Z" />
        <path className="abdomenStripe" d="M374 348h79M376 371h72M386 394h50" />
        <circle className="heroHead" cx="409" cy="187" r="72" />
        <ellipse className="heroEye" cx="374" cy="182" rx="31" ry="39" />
        <ellipse className="heroEye" cx="444" cy="182" rx="31" ry="39" />
        <circle className="eyeGlint" cx="365" cy="170" r="7" /><circle className="eyeGlint" cx="435" cy="170" r="7" />
        <path className="flySmile" d="M394 215q15 13 30 0" />
        <path className="antenna antenna--left" d="M388 124c-8-28-27-37-44-45" /><circle className="antennaTip" cx="342" cy="78" r="6" />
        <path className="antenna antenna--right" d="M430 123c8-28 27-37 44-45" /><circle className="antennaTip" cx="476" cy="78" r="6" />
      </g>
      <path className="flyArm flyArm--left" d="M360 277c-55 21-64 70-16 105l75 21" />
      <path className="flyArm flyArm--right" d="M452 279c52 21 55 66 7 101l-44 23" />
      <circle className="flyHand flyHand--left" cx="419" cy="402" r="8" /><circle className="flyHand flyHand--right" cx="414" cy="402" r="8" />
      <path className="flyLeg" d="M382 407c-20 31-45 37-70 30M435 408c16 31 38 38 63 31" />
    </g>
  )
}

function SharedSceneArt() {
  return (
    <>
      <path className="roomGrid" d="M0 430H1100M68 0V430M168 0V430M268 0V430M368 0V430M468 0V430M568 0V430M668 0V430M768 0V430M868 0V430M968 0V430" />
      <g className="signalOrbit">
        <ellipse cx="505" cy="245" rx="184" ry="146" />
        <circle cx="341" cy="180" r="5" /><circle cx="651" cy="311" r="4" /><circle cx="590" cy="105" r="3" />
      </g>
      <path className="chair" d="M262 287h101c25 0 42 20 42 45v82H277l-15-127Z" />
      <path className="chairLeg" d="M342 412v54m-43 31 43-31 48 31m-48-31-2 44" />
      <g className="deskScene">
        <path className="deskTop" d="M80 404h940l34 26H45Z" />
        <path className="deskFront" d="M64 430h974v29H64Z" />
        <path className="deskLeg" d="M110 459h35l-17 81H93ZM952 459h35l17 81h-35Z" />
      </g>
    </>
  )
}

export function ApplicationScene({ screen }: { screen: string }) {
  return (
    <svg className="officeScene applicationScene" viewBox="0 0 1100 540" role="img" aria-label="The fly applying for jobs at a computer">
      <defs>
        <linearGradient id="applicationWindowGlow" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0" stopColor="#d7ff68" stopOpacity=".22" />
          <stop offset="1" stopColor="#6ed4ff" stopOpacity=".03" />
        </linearGradient>
        <linearGradient id="applicationScreenGlow" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0" stopColor="#eaffaa" />
          <stop offset="1" stopColor="#a9e744" />
        </linearGradient>
        <filter id="applicationSoftGlow"><feGaussianBlur stdDeviation="9" /></filter>
      </defs>
      <SharedSceneArt />
      <rect className="officeWindow" x="720" y="52" width="300" height="206" rx="8" />
      <rect className="officeWindowGlow" x="720" y="52" width="300" height="206" rx="8" fill="url(#applicationWindowGlow)" />
      <path className="windowLines" d="M870 52v206M720 155h300" />
      <circle className="windowSun" cx="948" cy="103" r="25" />
      <path className="skyline" d="M721 223h40v-40h25v40h34v-72h39v72h42v-32h29v32h52v-58h38v93H721Z" />

      <g className="plant">
        <path d="M914 402c-2-48 12-77 31-104M929 402c2-44-5-80-19-112M926 359c21-12 35-27 43-46M919 338c-21-12-32-29-36-48" />
        <ellipse cx="947" cy="302" rx="23" ry="10" transform="rotate(-40 947 302)" />
        <ellipse cx="893" cy="283" rx="23" ry="10" transform="rotate(48 893 283)" />
        <ellipse cx="906" cy="326" rx="21" ry="9" transform="rotate(25 906 326)" />
        <path className="plantPot" d="M890 381h74l-10 36h-54Z" />
      </g>
      <g className="monitor">
        <rect className="monitorGlow" x="601" y="175" width="252" height="164" rx="10" filter="url(#applicationSoftGlow)" />
        <rect className="monitorFrame" x="592" y="164" width="270" height="174" rx="11" />
        <rect className="monitorScreen" x="607" y="180" width="240" height="142" rx="3" fill="url(#applicationScreenGlow)" />
        <circle className="screenDot screenDot--one" cx="623" cy="194" r="3" />
        <circle className="screenDot screenDot--two" cx="635" cy="194" r="3" />
        <circle className="screenDot screenDot--three" cx="647" cy="194" r="3" />
        <text className="screenLabel" x="727" y="229" textAnchor="middle">{screen}</text>
        <rect className="screenLine screenLine--one" x="643" y="247" width="167" height="8" rx="4" />
        <rect className="screenLine screenLine--two" x="657" y="265" width="138" height="7" rx="4" />
        <rect className="screenButton" x="687" y="287" width="80" height="17" rx="8" />
        <path className="monitorStand" d="M705 338h43v38h-66 109-65v-38" />
      </g>
      <g className="keyboard">
        <path d="M558 385h260l34 28H531Z" />
        {Array.from({ length: 10 }, (_, index) => <path key={index} d={`M${566 + index * 24} 395h16`} />)}
      </g>
      <g className="coffee">
        <path d="M841 360h50v47h-50Z" /><path d="M891 370c28-2 29 27 1 27" />
        <path className="steam steam--one" d="M853 350c-10-12 10-17 0-29" /><path className="steam steam--two" d="M873 350c-10-12 10-17 0-29" />
      </g>
      <FallbackFly />
      <g className="thoughtBubble">
        <circle cx="518" cy="117" r="9" /><circle cx="545" cy="91" r="14" />
        <path d="M563 25h211q18 0 18 18v36q0 18-18 18H563q-18 0-18-18V43q0-18 18-18Z" />
        <text x="668" y="68" textAnchor="middle">IS THIS O(n²)?</text>
      </g>
    </svg>
  )
}

function promptForStage(stage: string, interviews: InterviewStats) {
  if (stage === 'TECHNICAL_INTERVIEW') {
    return {
      label: interviews.latest_attempt ? 'RECENT QUESTION' : 'TECHNICAL QUESTION',
      text: interviews.latest_attempt?.question ?? 'Find the bug before the timer runs out.',
    }
  }
  if (stage === 'BEHAVIORAL_INTERVIEW') return { label: 'BEHAVIORAL QUESTION', text: 'Tell us about a time you led a team.' }
  if (stage === 'FINAL_RESULT') return { label: 'FINAL ROUND', text: 'One last question: did the fly get the job?' }
  return { label: 'RECRUITER QUESTION', text: 'Tell us a little about yourself.' }
}

function wrapPrompt(value: string, maxChars = 23, maxLines = 4) {
  const words = value.split(/\s+/)
  const lines: string[] = []
  let line = ''
  for (const word of words) {
    if (line && `${line} ${word}`.length > maxChars) {
      lines.push(line)
      line = word
    } else {
      line = line ? `${line} ${word}` : word
    }
  }
  if (line) lines.push(line)
  if (lines.length > maxLines) {
    lines.length = maxLines
    lines[maxLines - 1] = `${lines[maxLines - 1].replace(/[.!?]$/, '').slice(0, maxChars - 1)}…`
  }
  return lines
}

export function InterviewScene({ stage, screen, interviews }: { stage: string; screen: string; interviews: InterviewStats }) {
  const prompt = promptForStage(stage, interviews)
  const promptLines = wrapPrompt(prompt.text)
  return (
    <svg className="officeScene interviewScene" viewBox="0 0 1100 540" role="img" aria-label="The fly facing an interviewer and solving a problem">
      <defs>
        <linearGradient id="interviewScreenGlow" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0" stopColor="#1d323a" />
          <stop offset="1" stopColor="#101b20" />
        </linearGradient>
        <linearGradient id="interviewVideoGlow" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0" stopColor="#3c6272" />
          <stop offset="1" stopColor="#14232d" />
        </linearGradient>
      </defs>
      <SharedSceneArt />
      <g className="interviewWall">
        <rect x="608" y="77" width="410" height="293" rx="15" />
        <path d="M608 119h410M792 119v251" />
        <circle cx="634" cy="98" r="5" /><circle cx="651" cy="98" r="5" /><circle cx="668" cy="98" r="5" />
        <text x="691" y="102">{screen} / LIVE</text>
        <circle className="interviewLiveDot" cx="974" cy="99" r="5" />
      </g>
      <g className="interviewerPortrait">
        <rect x="626" y="138" width="148" height="181" rx="8" fill="url(#interviewVideoGlow)" />
        <path d="M626 268h148M647 252c0-30 24-47 53-47s53 17 53 47v16H647Z" />
        <circle cx="700" cy="188" r="35" />
        <path d="M672 182c4-25 45-37 60-7M684 198q16 7 31 0" />
        <rect x="637" y="284" width="126" height="22" rx="3" />
        <text x="700" y="299" textAnchor="middle">HIRING MANAGER</text>
      </g>
      <g className="interviewProblem">
        <rect x="804" y="138" width="198" height="181" rx="7" fill="url(#interviewScreenGlow)" />
        <text className="problemLabel" x="819" y="163">{prompt.label}</text>
        <text className="problemText" x="819" y="190">
          {promptLines.map((line, index) => <tspan key={`${line}-${index}`} x="819" dy={index === 0 ? 0 : 24}>{line}</tspan>)}
        </text>
        <path className="codeRule" d="M819 283h168" />
        <rect className="codeLine" x="819" y="295" width="95" height="5" rx="2" />
        <rect className="codeLine codeLine--short" x="923" y="295" width="47" height="5" rx="2" />
      </g>
      <g className="interviewControls">
        <circle cx="709" cy="344" r="12" /><path d="M705 339v8m8-8v8" />
        <circle cx="747" cy="344" r="12" /><path d="m743 341 8 6m0-6-8 6" />
        <rect x="867" y="332" width="119" height="24" rx="12" />
        <text x="927" y="349" textAnchor="middle">{stage === 'TECHNICAL_INTERVIEW' ? 'NEURAL SOLVER' : 'ON THE CALL'}</text>
      </g>
      <g className="interviewDeskObjects">
        <path d="M575 383h229l32 27H544Z" />
        <path d="M592 392h23m9 0h23m9 0h23m9 0h23m9 0h23m9 0h23" />
        <path d="M866 377h85l-11 31h-60Z" />
        <path d="M880 379v-27h57v27" />
        <text x="908" y="369" textAnchor="middle">NOTES</text>
      </g>
      <FallbackFly />
      <g className="speechBubble">
        <path d="M505 35h218q17 0 17 17v42q0 17-17 17H599l-25 22 3-22h-72q-17 0-17-17V52q0-17 17-17Z" />
        <text x="614" y="68" textAnchor="middle">MY GREATEST WEAKNESS?</text>
        <text x="614" y="89" textAnchor="middle">COMPOUND EYES.</text>
      </g>
    </svg>
  )
}
