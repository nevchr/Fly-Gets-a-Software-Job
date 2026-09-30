import type { BrainActivity } from '../types/simulation'

const clamp = (n: number) => Math.max(0, Math.min(1, Number.isFinite(n) ? n : 0))

// An authored rig-control mapping, not a claim that MaleCNS encodes job tasks.
export function flyMotion(activity: BrainActivity) {
  const input = (name: string) => activity.input_activity.find(group => group.name === name)?.spike_rate ?? 0
  const output = activity.output_activity
  const left = output.filter(group => /steer left|approach/i.test(group.name)).reduce((n, group) => n + group.spike_rate, 0)
  const right = output.filter(group => /steer right|avoid/i.test(group.name)).reduce((n, group) => n + group.spike_rate, 0)
  return {
    approach: clamp(input('approach') / 32),
    avoidance: clamp(input('avoidance') / 32),
    threat: clamp(Math.max(input('threat'), input('looming_work')) / 40),
    uncertainty: clamp(input('choice_uncertainty') / 30),
    turn: (left - right) / Math.max(left + right, 3.85),
    drive: clamp((activity.spike_rate - 1) / 13),
    selected: output.find(group => group.selected)?.name ?? 'no decision yet',
    escape: clamp(output.filter(group => /escape|backward/i.test(group.name)).reduce((n, group) => n + group.spike_rate, 0) / 20 + (/escape|backward/i.test(output.find(group => group.selected)?.name ?? '') ? 0.3 : 0)),
    forward: clamp(output.filter(group => /forward|approach/i.test(group.name)).reduce((n, group) => n + group.spike_rate, 0) / 20),
  }
}
