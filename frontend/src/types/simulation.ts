export interface BrainActivity {
  activation: number
  firing_rate: number
  dominant_region: string
  spikes: number[]
  decision_count: number
  backend: 'connectome' | 'mock' | string
  dataset: string | null
  neuron_count: number
  connection_count: number
  device: string
  mean_activity: number
  active_neurons: number
  spike_rate: number
  input_activity: Array<{
    name: string
    population: string
    side: string
    magnitude: number
    neurons: number
    spikes: number
    spike_rate: number
  }>
  output_activity: Array<{
    name: string
    spike_rate: number
    spikes: number
    neurons: number
    selected: boolean
  }>
  sampled_neurons: number[]
  visual_neurons: Array<{
    body_id: number
    spike_count: number
    spike_rate: number
  }>
  decision_latency_ms: number
}

export interface Status {
  stage: string
  stage_label: string
  tick_count: number
  simulated_day: number
  clock_minutes: number
  day_phase: number
  is_daytime: boolean
  tick_seconds: number
  current_status: string
  current_company: string | null
  current_job_title: string | null
  brain_activity: BrainActivity
}

export interface CareerStats {
  simulation_start_time: string
  simulated_days_unemployed: number
  jobs_viewed: number
  jobs_skipped: number
  applications_sent: number
  immediate_rejections: number
  ghosted: number
  recruiter_screens: number
  technical_interviews: number
  behavioral_interviews: number
  final_rounds: number
  offers: number
  accepted_offers: number
  rejected_offers: number
  total_interview_questions: number
  correct_interview_answers: number
  current_rejection_streak: number
  longest_rejection_streak: number
  highest_salary_applied_to: number
  lowest_qualification_match: number | null
  fastest_rejection_seconds: number | null
  longest_application_streak: number
  current_status: string
  current_company: string | null
  current_job_title: string | null
}

export interface Job {
  id: number
  company_name: string
  title: string
  salary: number
  work_mode: string
  required_experience_years: number
  tech_stack: string[]
  difficulty: number
  application_length: number
  absurd_requirement: string
  qualification_match: number
  status: string
  created_at: string
}

export interface SimulationEvent {
  id: number
  timestamp: string
  type: string
  message: string
  metadata: Record<string, unknown>
}

export interface CategoryAccuracy {
  category: string
  attempts: number
  correct: number
  accuracy: number
}

export interface InterviewStats {
  total: number
  correct: number
  accuracy: number
  categories: CategoryAccuracy[]
  latest_attempt: {
    question: string
    choices: string[]
    selected_index: number
    correct_index: number
    is_correct: boolean
    category: string
    difficulty: number
  } | null
}

export interface LiveUpdate {
  kind: 'simulation_update'
  events: SimulationEvent[]
  status: Status
  stats: CareerStats
  current_job: Job | null
}
