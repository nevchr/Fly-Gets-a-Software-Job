interface HeaderProps {
  day: number
  clockMinutes: number
  isDaytime: boolean
  connected: boolean
}

import { formatSimTime } from '../content/clock'

export function Header({ day, clockMinutes, isDaytime, connected }: HeaderProps) {
  return (
    <>
    <div className="broadcastNav" aria-label="Bug cam channel branding">
      <div className="broadcastBrand"><span className="brandIcon" aria-hidden="true">✳</span><strong>BUGCAST</strong><span className="brandDivider" /> <span>THE LIVE BUG CAM</span></div>
      <span className="navTagline">UNSCRIPTED CAREER CHAOS · EST. DAY 001</span>
    </div>
    <header className="siteHeader">
      <div className="brandLockup">
        <div className="flyMark" aria-hidden="true">
          <span className="wing wingLeft" />
          <span className="flyBody" />
          <span className="wing wingRight" />
        </div>
        <div>
          <p className="eyebrow">NOW STREAMING / A LIVE CONNECTOME EXPERIMENT</p>
          <h1>Fly Gets a <span>Software Job</span></h1>
        </div>
      </div>
      <div className="liveGroup" aria-label={connected ? 'Live connection active' : 'Reconnecting'}>
        <span className={`liveDot ${connected ? '' : 'offline'}`} />
        <strong>{connected ? 'LIVE' : 'RECONNECTING'}</strong>
        <span className="dayLabel">DAY {day.toString().padStart(3, '0')}</span>
        <span className="clockLabel">SIM SF · {formatSimTime(clockMinutes)} · {isDaytime ? 'DAY SHIFT' : 'AFTER HOURS'}</span>
      </div>
    </header>
    </>
  )
}
