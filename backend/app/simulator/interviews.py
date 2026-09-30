from dataclasses import dataclass


@dataclass(frozen=True)
class InterviewQuestion:
    id: str
    category: str
    difficulty: int
    prompt: str
    choices: list[str]
    correct_index: int


def q(id: str, category: str, difficulty: int, prompt: str, choices: list[str], correct: int):
    return InterviewQuestion(id, category, difficulty, prompt, choices, correct)


QUESTION_BANK = [
    q("bigo-1", "Big-O", 1, "What is binary search's worst-case time?", ["O(1)", "O(log n)", "O(n)", "O(n²)"], 1),
    q("bigo-2", "Big-O", 2, "What is hash-table lookup on average?", ["O(1)", "O(log n)", "O(n)", "O(n!)"], 0),
    q("bigo-3", "Big-O", 2, "Two nested n-length loops usually take…", ["O(log n)", "O(n)", "O(n²)", "O(2ⁿ)"], 2),
    q("arr-1", "arrays", 1, "Random access in an array is usually…", ["O(1)", "O(n)", "O(n²)", "impossible"], 0),
    q("arr-2", "arrays", 2, "Appending to a dynamic array is amortized…", ["O(1)", "O(log n)", "O(n)", "O(n²)"], 0),
    q("arr-3", "arrays", 2, "Which technique finds a pair sum in sorted data efficiently?", ["Two pointers", "Bubble sort", "Recursion only", "DNS"], 0),
    q("ll-1", "linked lists", 1, "A singly linked node stores data and…", ["a next pointer", "an index table", "SQL", "a process ID"], 0),
    q("ll-2", "linked lists", 2, "Insert at a known linked-list head is…", ["O(1)", "O(log n)", "O(n)", "O(n²)"], 0),
    q("ll-3", "linked lists", 3, "Floyd's tortoise and hare detects…", ["cycles", "sorting", "deadlocks", "packet loss"], 0),
    q("rec-1", "recursion", 1, "Every terminating recursive function needs…", ["a base case", "a GPU", "two classes", "a socket"], 0),
    q("rec-2", "recursion", 2, "Deep uncontrolled recursion risks…", ["stack overflow", "SQL injection", "packet duplication", "cache warmth"], 0),
    q("rec-3", "recursion", 3, "Tail-call optimization primarily reduces…", ["stack growth", "network hops", "disk writes", "merge conflicts"], 0),
    q("os-1", "operating systems", 1, "Which resource is private to a process?", ["virtual address space", "the whole CPU", "the internet", "wall clock"], 0),
    q("os-2", "operating systems", 2, "A context switch changes…", ["the running execution context", "the source language", "the database schema", "DNS TTL"], 0),
    q("os-3", "operating systems", 3, "Deadlock requires mutual exclusion plus…", ["hold-and-wait, no preemption, circular wait", "HTTP, DNS, TCP", "sorting", "garbage collection"], 0),
    q("net-1", "networking", 1, "HTTP normally runs over…", ["TCP", "HTML", "SQL", "JPEG"], 0),
    q("net-2", "networking", 2, "DNS primarily maps names to…", ["network addresses", "passwords", "source code", "CPU cores"], 0),
    q("net-3", "networking", 2, "A 404 response means…", ["resource not found", "server exploded", "success", "redirect forever"], 0),
    q("db-1", "databases", 1, "A primary key should identify…", ["one row", "one database vendor", "all tables", "a CSS class"], 0),
    q("db-2", "databases", 2, "An index usually trades write cost for…", ["faster reads", "more nulls", "network encryption", "smaller code"], 0),
    q("db-3", "databases", 3, "ACID isolation concerns…", ["concurrent transactions", "UI colors", "DNS", "compiler flags"], 0),
    q("c-1", "C", 1, "Which function releases malloc'd memory?", ["free", "delete", "drop", "collect"], 0),
    q("c-2", "C", 2, "A dangling pointer references…", ["invalidated storage", "a constant", "a socket only", "a macro"], 0),
    q("c-3", "C", 2, "sizeof(char) is defined as…", ["1", "2", "4", "platform uptime"], 0),
    q("py-1", "Python", 1, "Which Python collection is immutable?", ["tuple", "list", "set", "dict"], 0),
    q("py-2", "Python", 2, "A context manager commonly uses…", ["with", "goto", "switch", "defer"], 0),
    q("py-3", "Python", 2, "A generator yields values…", ["lazily", "only at import", "as SQL", "in parallel always"], 0),
    q("java-1", "Java", 1, "Java bytecode commonly runs on the…", ["JVM", "DOM", "BIOS", "CDN"], 0),
    q("java-2", "Java", 2, "Which keyword creates a subclass?", ["extends", "inherits", "using", "derive"], 0),
    q("java-3", "Java", 2, "An interface primarily defines…", ["a contract", "heap size", "a database", "a thread scheduler"], 0),
    q("git-1", "Git", 1, "Which command records staged changes?", ["git commit", "git fetch", "git status", "git blame"], 0),
    q("git-2", "Git", 2, "A branch is best described as…", ["a movable commit reference", "a full server", "an issue", "a password"], 0),
    q("git-3", "Git", 2, "Rebase typically rewrites…", ["commit ancestry", "the operating system", "DNS", "file permissions only"], 0),
    q("bigo-4", "Big-O", 1, "One pass through n items usually takes…", ["O(1)", "O(log n)", "O(n)", "O(n²)"], 2),
    q("bigo-5", "Big-O", 2, "Lookup in a balanced search tree is usually…", ["O(1)", "O(log n)", "O(n²)", "O(n!)"], 1),
    q("arr-4", "arrays", 2, "Inserting at the front of an array usually takes…", ["O(1)", "O(log n)", "O(n)", "O(n²)"], 2),
    q("arr-5", "arrays", 1, "Which structure supports constant-time indexing?", ["array", "singly linked list", "queue only", "binary heap only"], 0),
    q("ll-4", "linked lists", 2, "Finding the kth item in a singly linked list takes…", ["O(1)", "O(log n)", "O(n)", "O(n²)"], 2),
    q("ll-5", "linked lists", 1, "A doubly linked node usually stores…", ["previous and next links", "a SQL query", "a hash function", "two array indexes only"], 0),
    q("rec-4", "recursion", 2, "Memoization helps avoid…", ["repeating the same subproblem", "writing base cases", "function calls entirely", "all memory use"], 0),
    q("rec-5", "recursion", 1, "Active recursive calls are tracked on the…", ["call stack", "network socket", "database index", "GPU shader"], 0),
    q("os-4", "operating systems", 2, "A mutex mainly protects…", ["a shared critical section", "a screen resolution", "a URL", "a file extension"], 0),
    q("os-5", "operating systems", 2, "Virtual memory gives processes…", ["isolated address spaces", "unlimited physical RAM", "faster Wi-Fi", "automatic backups"], 0),
    q("net-4", "networking", 2, "TLS primarily adds…", ["encryption and authentication", "faster CSS", "database indexing", "source control"], 0),
    q("net-5", "networking", 1, "Which HTTP status normally means created?", ["200", "201", "301", "404"], 1),
    q("db-4", "databases", 2, "A JOIN combines table rows using…", ["a related condition", "a CSS selector", "a compiler flag", "a random number"], 0),
    q("db-5", "databases", 1, "Rolling back a transaction…", ["undoes its uncommitted changes", "deletes the database", "sorts the rows", "creates an index"], 0),
    q("c-4", "C", 2, "malloc returns…", ["a pointer to allocated memory", "a Java object", "a file descriptor", "a boolean"], 0),
    q("c-5", "C", 2, "Which operator accesses a struct member through a pointer?", [".", "->", "::", "??"], 1),
    q("py-4", "Python", 1, "enumerate commonly produces…", ["index and value pairs", "only values", "thread IDs", "database rows"], 0),
    q("py-5", "Python", 1, "A list comprehension is used to…", ["build a list concisely", "compile Python into C", "open a socket", "avoid all loops"], 0),
    q("java-4", "Java", 1, "Garbage collection reclaims…", ["unreachable objects", "every local variable", "network packets", "source files"], 0),
    q("java-5", "Java", 1, "Which of these is a Java primitive type?", ["String", "ArrayList", "int", "Object"], 2),
    q("git-4", "Git", 1, "git status summarizes…", ["working tree and staging changes", "CPU usage", "DNS records", "database locks"], 0),
    q("git-5", "Git", 2, "A merge conflict usually means…", ["competing edits need resolution", "the repository is deleted", "the network is offline", "the branch is read-only"], 0),
]


BEHAVIORAL_PROMPTS = [
    "Tell me about a time you demonstrated leadership.",
    "Why do you want to work here?",
    "Where do you see yourself in five years?",
    "Tell me about a conflict with a teammate.",
    "Why should we hire you?",
    "Tell me about a time you adapted to a change.",
    "How do you handle feedback?",
    "Describe a project you are proud of.",
    "What motivates you at work?",
    "How do you prioritize competing deadlines?",
    "Tell me about a mistake you learned from.",
    "How do you work with a difficult stakeholder?",
    "Describe a time you solved an unfamiliar problem.",
    "What does good collaboration look like to you?",
    "How do you respond when a project changes direction?",
    "Tell me about a time you helped a teammate.",
    "How do you stay organized under pressure?",
    "What would your previous manager say about you?",
    "Describe a time you had to ask for help.",
    "How do you know when a task is finished?",
    "What is one skill you are trying to improve?",
    "Tell me about a time you disagreed respectfully.",
    "How do you keep learning outside work?",
    "Why are you leaving your current role?",
    "What would you do in your first month here?",
]

RESPONSE_STYLES = [
    "confident",
    "confused",
    "silent",
    "overly honest",
    "irrelevant",
    "surprisingly competent",
]

BEHAVIORAL_SCORES = {
    "confident": 0.78,
    "confused": 0.28,
    "silent": 0.08,
    "overly honest": 0.47,
    "irrelevant": 0.18,
    "surprisingly competent": 0.9,
}
