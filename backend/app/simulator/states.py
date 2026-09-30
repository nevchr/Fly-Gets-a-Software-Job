from enum import StrEnum


class SimulationStage(StrEnum):
    SEARCHING_FOR_JOB = "SEARCHING_FOR_JOB"
    VIEWING_JOB = "VIEWING_JOB"
    DECIDING_TO_APPLY = "DECIDING_TO_APPLY"
    APPLICATION_SENT = "APPLICATION_SENT"
    APPLICATION_RESULT = "APPLICATION_RESULT"
    RECRUITER_SCREEN = "RECRUITER_SCREEN"
    TECHNICAL_INTERVIEW = "TECHNICAL_INTERVIEW"
    BEHAVIORAL_INTERVIEW = "BEHAVIORAL_INTERVIEW"
    FINAL_RESULT = "FINAL_RESULT"


STAGE_LABELS = {
    SimulationStage.SEARCHING_FOR_JOB: "Refreshing the job board",
    SimulationStage.VIEWING_JOB: "Reading a suspiciously enthusiastic posting",
    SimulationStage.DECIDING_TO_APPLY: "Consulting the connectome",
    SimulationStage.APPLICATION_SENT: "Application launched into the void",
    SimulationStage.APPLICATION_RESULT: "Awaiting the automated judgment",
    SimulationStage.RECRUITER_SCREEN: "Attempting professional small talk",
    SimulationStage.TECHNICAL_INTERVIEW: "Selecting an algorithm under pressure",
    SimulationStage.BEHAVIORAL_INTERVIEW: "Demonstrating culture-adjacent behavior",
    SimulationStage.FINAL_RESULT: "The committee is typing…",
}
