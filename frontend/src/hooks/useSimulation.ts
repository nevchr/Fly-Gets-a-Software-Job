import { useCallback, useEffect, useRef, useState } from 'react'
import type { CareerStats, InterviewStats, Job, LiveUpdate, SimulationEvent, Status } from '../types/simulation'

const API_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:8000'
const WS_URL = import.meta.env.VITE_WS_URL ?? 'ws://localhost:8000/ws/live'

async function getJson<T>(path: string): Promise<T> {
  const response = await fetch(`${API_URL}${path}`)
  if (!response.ok) throw new Error(`Request failed: ${response.status}`)
  return response.json() as Promise<T>
}

export function useSimulation() {
  const [status, setStatus] = useState<Status | null>(null)
  const [stats, setStats] = useState<CareerStats | null>(null)
  const [job, setJob] = useState<Job | null>(null)
  const [events, setEvents] = useState<SimulationEvent[]>([])
  const [interviews, setInterviews] = useState<InterviewStats | null>(null)
  const [connected, setConnected] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const retryRef = useRef<number | null>(null)

  const refreshInterviews = useCallback(() => {
    getJson<InterviewStats>('/api/interview-stats').then(setInterviews).catch(() => undefined)
  }, [])

  useEffect(() => {
    let disposed = false
    let socket: WebSocket | null = null

    Promise.all([
      getJson<Status>('/api/status'),
      getJson<CareerStats>('/api/stats'),
      getJson<Job | null>('/api/current-job'),
      getJson<SimulationEvent[]>('/api/events?limit=120'),
      getJson<InterviewStats>('/api/interview-stats'),
    ])
      .then(([nextStatus, nextStats, nextJob, nextEvents, nextInterviews]) => {
        if (disposed) return
        setStatus(nextStatus)
        setStats(nextStats)
        setJob(nextJob)
        setEvents(nextEvents)
        setInterviews(nextInterviews)
        setError(null)
      })
      .catch(() => !disposed && setError('Backend signal unavailable. Is the simulator running?'))

    const connect = () => {
      if (disposed) return
      socket = new WebSocket(WS_URL)
      socket.onopen = () => {
        setConnected(true)
        setError(null)
      }
      socket.onmessage = (message) => {
        const update = JSON.parse(message.data) as LiveUpdate
        setStatus(update.status)
        setStats(update.stats)
        setJob(update.current_job)
        if (update.events.length) {
          setEvents((current) => {
            const existing = new Set(current.map((event) => event.id))
            const incoming = update.events.filter((event) => !existing.has(event.id)).reverse()
            return [...incoming, ...current].slice(0, 180)
          })
          if (update.events.some((event) => event.type === 'TECHNICAL_ANSWERED')) refreshInterviews()
        }
      }
      socket.onclose = () => {
        setConnected(false)
        if (!disposed) retryRef.current = window.setTimeout(connect, 1800)
      }
      socket.onerror = () => socket?.close()
    }
    connect()

    return () => {
      disposed = true
      if (retryRef.current) window.clearTimeout(retryRef.current)
      socket?.close()
    }
  }, [refreshInterviews])

  return { status, stats, job, events, interviews, connected, error }
}

