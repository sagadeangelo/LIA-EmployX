"""
EmployX Orchestrator
"""

from backend.orchestrator.context import EmployXContext
from backend.orchestrator.registry import AgentRegistry
from backend.orchestrator.event_bus import EventBus


class EmployXOrchestrator:

    def __init__(self):

        self.context = EmployXContext()

        self.registry = AgentRegistry()

        self.bus = EventBus()

    # --------------------------------------------------------

    def register(self, agent):

        agent.initialize(self.context)

        self.registry.register(agent)

    # --------------------------------------------------------

    def start(self):

        print()

        print("=" * 70)

        print("          LIA EmployX Orchestrator")

        print("=" * 70)

        print()

        print("Especialistas registrados:\n")

        for agent in self.registry.all():

            print(f"✔ {agent.name}")

        print()

        print("Sistema listo.\n")