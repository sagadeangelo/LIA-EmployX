"""
LIA EmployX — Mission Runtime
Layer 1: MissionState (Formal Finite State Machine)

Todos los estados posibles de una Misión en el Career Operating System.
Ningún código escribe strings de estado a mano — todo usa este Enum.
"""

from enum import Enum


class MissionStatus(str, Enum):
    """
    Estado general de la misión.
    """

    CREATED = "CREATED"
    UPLOADING = "UPLOADING"
    STORED = "STORED"
    QUEUED = "QUEUED"
    PROCESSING = "PROCESSING"
    WAITING_AGENT = "WAITING_AGENT"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"
    RECOVERED = "RECOVERED"
    PAUSED = "PAUSED"  # Retained for paused scenarios


class MissionStage(str, Enum):
    """
    Etapa oficial del pipeline. Representa el StageTracker.
    """

    RECEIVE_FILE = "RECEIVE_FILE"
    STORE_FILE = "STORE_FILE"
    DETECT_FORMAT = "DETECT_FORMAT"
    READ_DOCUMENT = "READ_DOCUMENT"
    EXTRACT_TEXT = "EXTRACT_TEXT"
    NORMALIZE_TEXT = "NORMALIZE_TEXT"
    BUILD_PROFILE = "BUILD_PROFILE"
    SAVE_PROFILE = "SAVE_PROFILE"
    UPDATE_RUNTIME = "UPDATE_RUNTIME"
    COMPLETE = "COMPLETE"


# Mapa de transiciones válidas para el Status
VALID_STATUS_TRANSITIONS: dict[MissionStatus, set[MissionStatus]] = {
    MissionStatus.CREATED: {MissionStatus.UPLOADING, MissionStatus.CANCELLED},
    MissionStatus.UPLOADING: {
        MissionStatus.STORED,
        MissionStatus.FAILED,
        MissionStatus.CANCELLED,
    },
    MissionStatus.STORED: {
        MissionStatus.QUEUED,
        MissionStatus.PROCESSING,
        MissionStatus.FAILED,
        MissionStatus.CANCELLED,
    },
    MissionStatus.QUEUED: {MissionStatus.PROCESSING, MissionStatus.CANCELLED},
    MissionStatus.PROCESSING: {
        MissionStatus.WAITING_AGENT,
        MissionStatus.COMPLETED,
        MissionStatus.FAILED,
        MissionStatus.PAUSED,
        MissionStatus.CANCELLED,
    },
    MissionStatus.WAITING_AGENT: {
        MissionStatus.PROCESSING,
        MissionStatus.FAILED,
        MissionStatus.CANCELLED,
    },
    MissionStatus.PAUSED: {
        MissionStatus.PROCESSING,
        MissionStatus.QUEUED,
        MissionStatus.CANCELLED,
    },
    MissionStatus.COMPLETED: set(),  # terminal
    MissionStatus.FAILED: {
        MissionStatus.UPLOADING,
        MissionStatus.STORED,
        MissionStatus.QUEUED,
        MissionStatus.PROCESSING,
        MissionStatus.CANCELLED,
    },  # retry
    MissionStatus.CANCELLED: set(),  # terminal
    MissionStatus.RECOVERED: {
        MissionStatus.QUEUED,
        MissionStatus.PROCESSING,
        MissionStatus.FAILED,
        MissionStatus.CANCELLED,
    },
}

TERMINAL_STATUSES: set[MissionStatus] = {
    MissionStatus.COMPLETED,
    MissionStatus.CANCELLED,
}
ACTIVE_STATUSES: set[MissionStatus] = {
    MissionStatus.STORED,
    MissionStatus.QUEUED,
    MissionStatus.PROCESSING,
    MissionStatus.WAITING_AGENT,
    MissionStatus.PAUSED,
}
RECOVERABLE_STATUSES: set[MissionStatus] = {
    MissionStatus.STORED,
    MissionStatus.QUEUED,
    MissionStatus.PROCESSING,
    MissionStatus.WAITING_AGENT,
    MissionStatus.PAUSED,
}


def can_transition_status(from_status: MissionStatus, to_status: MissionStatus) -> bool:
    """Valida si una transición de Status es legal."""
    return to_status in VALID_STATUS_TRANSITIONS.get(from_status, set())
