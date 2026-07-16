"""
Contexto compartido entre todos los especialistas.
"""


class EmployXContext:

    def __init__(self):

        self.user = None

        self.profile = None

        self.jobs = []

        self.applications = []

        self.interviews = []

        self.certifications = []

        self.books = []

        self.languages = []

        self.skills = []

        self.timeline = []

        self.memory = {}

    # --------------------------------------------------------

    def add_event(self, message):

        self.timeline.append(message)

        print(f"[TIMELINE] {message}")

    # --------------------------------------------------------

    def set(self, key, value):

        self.memory[key] = value

    # --------------------------------------------------------

    def get(self, key, default=None):

        return self.memory.get(key, default)