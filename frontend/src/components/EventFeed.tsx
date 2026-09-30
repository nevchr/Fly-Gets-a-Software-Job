import type { SimulationEvent } from '../types/simulation'

function time(timestamp: string) {
  return new Date(timestamp).toLocaleTimeString([], { hour12: false })
}

export function EventFeed({ events }: { events: SimulationEvent[] }) {
  return (
    <section className="panel feedPanel chatPanel" aria-labelledby="chat-title">
      <div className="chatHeading"><div><span className="chatLiveDot" /><h2 id="chat-title">BUG CHAT</h2></div><span>LIVE LOG</span></div>
      <div className="chatNotice"><b>careerbot</b> Welcome to the bug cam. These are automated simulation updates, not messages from viewers.</div>
      <div className="eventList" aria-live="polite">
        {events.length ? events.map((event, index) => (
          <article className={index === 0 ? 'newEvent' : ''} key={event.id}>
            <time>{time(event.timestamp)}</time>
            <div><strong><span className={`eventGlyph type-${event.type}`} />careerbot <em>{event.type.replaceAll('_', ' ')}</em></strong><p>{event.message}</p></div>
          </article>
        )) : <p className="emptyCopy">The feed is quiet. The fly is probably networking.</p>}
      </div>
      <div className="chatFooter"><span>🔒</span> READ-ONLY / THE ALGORITHM IS TYPING</div>
    </section>
  )
}
