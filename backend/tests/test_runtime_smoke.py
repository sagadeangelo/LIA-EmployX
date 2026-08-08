import unittest

from backend.main import app
from backend.runtime.mission_state import (
    MissionStatus,
    MissionStage,
    can_transition_status,
)


class RuntimeSmokeTest(unittest.TestCase):
    def test_app_imports(self) -> None:
        self.assertEqual(app.title, "LIA EmployX — Career Operating System")

    def test_official_fsm_transitions(self) -> None:
        self.assertTrue(
            can_transition_status(MissionStatus.QUEUED, MissionStatus.PROCESSING)
        )
        self.assertTrue(
            can_transition_status(MissionStatus.PROCESSING, MissionStatus.WAITING_AGENT)
        )
        self.assertTrue(
            can_transition_status(MissionStatus.PROCESSING, MissionStatus.COMPLETED)
        )
        self.assertTrue(
            can_transition_status(MissionStatus.PAUSED, MissionStatus.PROCESSING)
        )
        self.assertFalse(
            can_transition_status(MissionStatus.COMPLETED, MissionStatus.PROCESSING)
        )
        self.assertEqual(MissionStage.RECEIVE_FILE.value, "RECEIVE_FILE")


if __name__ == "__main__":
    unittest.main()
