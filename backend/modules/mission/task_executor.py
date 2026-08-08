import asyncio
from typing import Callable, Any, Coroutine

class TaskExecutor:
    """
    Abstracción para ejecutar tareas en segundo plano.
    Actualmente usa asyncio, pero puede ser migrado a Celery/RQ sin cambiar 
    el código del MissionController.
    """
    
    @classmethod
    def execute(cls, func: Callable[..., Coroutine[Any, Any, Any]], *args, **kwargs):
        """
        Ejecuta una función asíncrona en segundo plano.
        """
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # Programa la tarea en el loop actual de eventos
            asyncio.create_task(func(*args, **kwargs))
        else:
            # Si no hay un loop corriendo, se ejecuta con run (útil para pruebas)
            asyncio.run(func(*args, **kwargs))
