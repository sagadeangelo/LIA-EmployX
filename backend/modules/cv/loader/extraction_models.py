"""Typed contracts for document extraction diagnostics."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class ExtractionStatus(str, Enum):
    SUCCESS = "success"
    EMPTY = "empty"
    IMAGE_ONLY = "image_only"
    UNSUPPORTED = "unsupported"
    FAILED = "failed"


@dataclass(frozen=True)
class ExtractionChunk:
    """A source-attributed fragment produced by one extraction strategy."""

    text: str
    source: str
    part_name: str
    ordinal: int
    identity: str


@dataclass(frozen=True)
class StrategyExecution:
    strategy: str
    chunk_count: int
    character_count: int
    error: str | None = None


@dataclass
class ExtractionReport:
    """Explains how a document was handled, including non-success outcomes."""

    status: ExtractionStatus
    file_path: str
    strategies: list[StrategyExecution] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    text_node_count: int = 0
    image_count: int = 0
    signals: list[str] = field(default_factory=list)

    @property
    def is_success(self) -> bool:
        return self.status is ExtractionStatus.SUCCESS

    def summary(self) -> str:
        return (
            f"status={self.status.value}, text_nodes={self.text_node_count}, "
            f"images={self.image_count}, strategies={len(self.strategies)}"
        )


@dataclass(frozen=True)
class ExtractionResult:
    raw_text: str
    report: ExtractionReport
    chunks: tuple[ExtractionChunk, ...] = ()


class DocumentExtractionError(RuntimeError):
    """Raised by the legacy text-only API when an extraction is not successful."""

    def __init__(self, report: ExtractionReport) -> None:
        self.report = report
        message = report.errors[0] if report.errors else report.summary()
        super().__init__(f"Document extraction failed: {message}")
