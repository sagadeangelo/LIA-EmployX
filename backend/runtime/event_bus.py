"""
LIA EmployX — Mission Runtime
Layer 3: RuntimeEventBus (Typed Internal Event Bus)

Reemplaza completamente el print() y el EventBus primitivo del orchestrator.

Características:
  - Suscriptores tipados por clase de evento
  - Async-friendly (los handlers pueden ser coroutines)
  - Logging estructurado en lugar de print()
  - Desacoplado de Flutter/SSE — solo emite, no conoce el destino

El camino futuro:
    Runtime → EventBus → SSEHandler → Flutter
    Runtime → EventBus → CeleryPublisher → Worker
"""
from __future__ import annotations

import asyncio
import logging
from collections import defaultdict
from typing import Any, Callable, Dict, List, Type, TypeVar, Awaitable, Union

from backend.runtime.runtime_events import RuntimeEvent

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=RuntimeEvent)
Handler = Union[Callable[[T], None], Callable[[T], Awaitable[None]]]


class RuntimeEventBus:
    """
    Bus de eventos tipado para el Mission Runtime.

    Uso:
        bus = RuntimeEventBus()

        @bus.on(MissionStarted)
        async def handle_start(event: MissionStarted):
            ...

        await bus.publish(MissionStarted(mission_id="abc"))
    """

    def __init__(self) -> None:
        self._handlers: Dict[str, List[Handler]] = defaultdict(list)

    # ─────────────────────────────────────────────
    # Registro de handlers
    # ─────────────────────────────────────────────

    def on(self, event_class: Type[T]) -> Callable[[Handler], Handler]:
        """Decorador para registrar un handler para un tipo de evento."""
        def decorator(func: Handler) -> Handler:
            self._handlers[event_class.__name__].append(func)
            return func
        return decorator

    def subscribe(self, event_class: Type[T], handler: Handler) -> None:
        """Registra un handler de forma programática."""
        self._handlers[event_class.__name__].append(handler)

    # ─────────────────────────────────────────────
    # Publicación de eventos
    # ─────────────────────────────────────────────

    async def publish(self, event: RuntimeEvent) -> None:
        """
        Publica un evento. Invoca todos los handlers registrados para su tipo.
        Si el handler es una coroutine, la awaita. Si es síncrono, lo llama directamente.
        """
        event_name = event.__class__.__name__
        logger.info(
            "[EventBus] %s | mission=%s | ts=%s",
            event_name,
            event.mission_id,
            event.timestamp.isoformat(),
        )

        for handler in self._handlers.get(event_name, []):
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(event)
                else:
                    handler(event)
            except Exception as exc:
                logger.exception(
                    "[EventBus] Error en handler de %s: %s", event_name, exc
                )

    # ─────────────────────────────────────────────
    # Introspección (para el Runtime Inspector)
    # ─────────────────────────────────────────────

    def registered_event_types(self) -> List[str]:
        return list(self._handlers.keys())


# ─────────────────────────────────────────────
# Instancia global — singleton del proceso
# ─────────────────────────────────────────────
# Se importa así en cualquier módulo:
#   from backend.runtime.event_bus import runtime_bus

runtime_bus = RuntimeEventBus()
