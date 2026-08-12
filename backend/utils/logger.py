import logging
import time

class AppLogger:
    @staticmethod
    def _format_msg(component: str, msg: str, mission_id: str = None, duration_ms: int = None) -> str:
        mission_prefix = f"[Mission: {mission_id}] " if mission_id else ""
        duration_suffix = f" - {duration_ms}ms" if duration_ms is not None else ""
        return f"{mission_prefix}[{component}] {msg}{duration_suffix}"

    @staticmethod
    def info(component: str, msg: str, mission_id: str = None, duration_ms: int = None):
        logging.getLogger(component).info(AppLogger._format_msg(component, msg, mission_id, duration_ms))

    @staticmethod
    def debug(component: str, msg: str, mission_id: str = None, duration_ms: int = None):
        logging.getLogger(component).debug(AppLogger._format_msg(component, msg, mission_id, duration_ms))

    @staticmethod
    def warning(component: str, msg: str, mission_id: str = None, duration_ms: int = None):
        logging.getLogger(component).warning(AppLogger._format_msg(component, msg, mission_id, duration_ms))

    @staticmethod
    def error(component: str, msg: str, mission_id: str = None, duration_ms: int = None, exc_info=False):
        logging.getLogger(component).error(AppLogger._format_msg(component, msg, mission_id, duration_ms), exc_info=exc_info)

    @staticmethod
    def get_time_ms():
        return int(time.time() * 1000)
