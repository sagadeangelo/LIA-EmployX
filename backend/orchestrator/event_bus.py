"""
Bus de eventos simple.
"""


class EventBus:

    def __init__(self):

        self.listeners = {}

    # --------------------------------------------------------

    def subscribe(self, event, callback):

        self.listeners.setdefault(event, []).append(callback)

    # --------------------------------------------------------

    def publish(self, event):

        print(f"\nEVENTO -> {event}")

        for callback in self.listeners.get(event, []):

            callback(event)