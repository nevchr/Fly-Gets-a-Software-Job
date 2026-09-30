import random
from dataclasses import dataclass


COMPANIES = [
    "Macrohard",
    "Pear",
    "Rainforest Web Services",
    "FaceNovel",
    "Notflix",
    "LinkedOut",
    "Infinite Systems",
    "NullPointer Labs",
    "Stack Underflow",
    "Junior Senior Technologies",
    "Cloudy With A Chance of SaaS",
    "Agile Waterfall LLC",
    "BugByte Labs",
    "Pixel Orchard",
    "Merge Conflict Media",
    "Infinite Meetings Inc.",
    "Cache Me Outside",
    "Runtime Romance",
    "The Last Sprint",
    "Deploy and Pray",
    "Ctrl Alt Elite",
    "Byte-Sized Ventures",
    "Very Serious Cloud",
    "The Algorithm Department",
    "Circling Back Systems",
    "Ship Happens Studio",
    "Monday Again Software",
    "Mostly Uptime",
    "Tiny Unicorn Labs",
    "Works on My Machine Co.",
]

TITLES = [
    "Junior Backend Engineer",
    "Associate Senior Developer",
    "Full-Stack Generalist III",
    "Python Wrangler",
    "Distributed Systems Intern",
    "Developer Experience Archaeologist",
    "Cloud Reliability Enthusiast",
    "Software Engineer, Growth Synergy",
    "Junior Platform Engineer",
    "Staff Intern, Emerging Technologies",
    "Frontend Experience Specialist",
    "Backend Systems Tinkerer",
    "Senior Junior Full-Stack Developer",
    "API Reliability Associate",
    "Cloud Migration Apprentice",
    "DevOps Vibes Coordinator",
    "Software Generalist, Special Projects",
    "Machine Learning Adjacent Engineer",
    "Build Pipeline Caretaker",
    "Database Performance Explorer",
    "Web Interface Engineer",
    "Product-Minded Bug Fixer",
    "Technical Solutions Human",
    "Platform Engineer, Somehow",
]

STACKS = [
    ["Python", "FastAPI", "PostgreSQL"],
    ["TypeScript", "React", "GraphQL"],
    ["Java", "Spring", "Kafka"],
    ["C", "Linux", "Valgrind"],
    ["Go", "Kubernetes", "Redis"],
    ["COBOL", "Excel", "optimism"],
    ["Rust", "PostgreSQL", "Docker"],
    ["Swift", "SQLite", "CloudKit"],
    ["Kotlin", "Android", "Firebase"],
    ["Node.js", "MongoDB", "queues"],
    ["C#", ".NET", "Azure"],
    ["Ruby", "Rails", "Sidekiq"],
    ["PHP", "Laravel", "MySQL"],
    ["Svelte", "TypeScript", "Vite"],
]

ABSURD_REQUIREMENTS = [
    "8 years of experience with a framework released 3 years ago",
    "Entry-level position requiring 5+ years industry experience",
    "Passion for disrupting spreadsheet workflows",
    "Must thrive in a fast-paced family environment",
    "Must be comfortable wearing many hats; hats not provided",
    "A GitHub contribution graph visible from space",
    "Ability to estimate impossible deadlines with confidence",
    "Prior experience scaling to one billion users preferred",
    "Must communicate asynchronously and attend nine daily meetings",
    "Personal ownership of at least one mechanical keyboard",
    "A minimum of four years using our six-month-old toolchain",
    "Comfortable being the entire team during team-building exercises",
    "Can turn vague stakeholder thoughts into production code by lunch",
    "Must enjoy the phrase 'circle back' in every tense",
    "Experience debugging software nobody remembers writing",
    "Available for occasional meetings that happen daily",
    "Can explain Kubernetes to an executive using only weather metaphors",
    "Portfolio must include a tasteful amount of green squares",
    "Willing to be passionate about internal dashboards",
    "Ability to own a service, its pager, and its emotional baggage",
    "Must work independently while attending all collaborative meetings",
    "Comfortable with a roadmap that changes during the stand-up",
    "Can make an urgent fix without making it look urgent",
    "Experience migrating between two equally mysterious platforms",
    "Must be a self-starter and also wait for approval on everything",
    "Can describe an outage as an opportunity for learning",
    "References from three people who enjoyed your pull requests",
    "Ready to learn five frameworks by next Tuesday",
    "Capable of estimating work before the requirements exist",
    "Can distinguish a feature request from a cry for help",
    "Willing to wear the on-call crown on rotating weekends",
    "Prior experience making the loading spinner feel faster",
    "Must thrive amid ambiguity, urgency, and a very small budget",
    "Can remain calm when the demo account stops working",
    "Ability to write clean code in a room full of opinions",
    "Comfortable being called a rockstar without receiving concert pay",
]


@dataclass(frozen=True)
class GeneratedJob:
    company_name: str
    title: str
    salary: int
    work_mode: str
    required_experience_years: int
    tech_stack: list[str]
    difficulty: int
    application_length: int
    absurd_requirement: str
    qualification_match: float


class JobFactory:
    """Procedural environment generator, separate from brain decisions."""

    def __init__(self, seed: int):
        self.seed = seed

    def generate(self, sequence: int) -> GeneratedJob:
        randomizer = random.Random(self.seed + sequence * 7919)
        difficulty = randomizer.randint(1, 5)
        experience = randomizer.randint(0, 9)
        salary = randomizer.randrange(58_000, 191_000, 2_000)
        match = round(max(0.03, min(0.98, randomizer.gauss(0.53, 0.23))), 2)
        return GeneratedJob(
            company_name=randomizer.choice(COMPANIES),
            title=randomizer.choice(TITLES),
            salary=salary,
            work_mode=randomizer.choice(["remote", "hybrid", "onsite"]),
            required_experience_years=experience,
            tech_stack=list(randomizer.choice(STACKS)),
            difficulty=difficulty,
            application_length=randomizer.randint(4, 38),
            absurd_requirement=randomizer.choice(ABSURD_REQUIREMENTS),
            qualification_match=match,
        )
