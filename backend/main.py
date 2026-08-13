from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.upload import router as upload_router
from backend.api.routes.missions import router as missions_router
from backend.api.routes.command_center import router as command_center_router
from backend.api.routes.runtime import router as runtime_router
from backend.api.routes.health import router as health_router
from backend.modules.cv.controllers.cv_controller import router as cv_controller_router
from backend.modules.profile.controllers.profile_controller import router as profile_router
from backend.modules.location.controllers.location_controller import router as location_router
from backend.api.routes.jobs_proxy import router as jobs_proxy_router

from backend.storage.json_provider import JsonStorageProvider
from backend.modules.mission.repositories import MissionRepository, MissionEventRepository
from backend.runtime.runtime_registry import init_runtime_registry
from backend.runtime.recovery_engine import RecoveryEngine

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Startup: inicializa el RuntimeRegistry y el RecoveryEngine.
    Shutdown: limpieza de recursos.
    """
    logger.info("=" * 60)
    logger.info("  LIA EmployX — Career Operating System")
    logger.info("=" * 60)

    import os
    pid = os.getpid()
    logger.info(f"[Startup] Inicializando servidor en PID: {pid}")
    # Nota: Uvicorn no expone host/port directamente al lifespan, 
    # pero típicamente LIA corre en 127.0.0.1:8000
    logger.info("[Startup] Host: 127.0.0.1 | Puerto: 8000")

    # Inicializar Storage y Repositorios
    storage = JsonStorageProvider()
    mission_repo = MissionRepository(storage)
    event_repo = MissionEventRepository(storage)

    # Inicializar RuntimeRegistry (singleton global)
    registry = init_runtime_registry(mission_repo, event_repo)
    logger.info("[Startup] RuntimeRegistry inicializado.")

    # Recovery Engine — restaurar misiones interrumpidas
    recovery = RecoveryEngine(mission_repo, event_repo, registry)
    report = await recovery.get_recovery_report()
    recovered_ids = await recovery.recover_all()

    logger.info("[Startup] Estado del sistema:")
    logger.info("  Total misiones: %d", report["total_missions"])
    for state, count in report["by_state"].items():
        logger.info("  %s: %d", state, count)

    if recovered_ids:
        logger.info("[Startup] Misiones recuperadas: %s", recovered_ids)
    else:
        logger.info("[Startup] No hay misiones para recuperar.")

    logger.info("[Startup] Career OS listo.\n")

    yield  # ← aquí corre la aplicación

    # Shutdown
    logger.info("[Shutdown] LIA EmployX cerrando...")


app = FastAPI(
    title="LIA EmployX — Career Operating System",
    version="1.0.0",
    description="The kernel of the Career OS — Mission Runtime, Agent Orchestration, Recovery Engine.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"^https?://(localhost|127\.0\.0\.1)(:\d+)?$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload_router)
app.include_router(missions_router)
app.include_router(command_center_router)
app.include_router(cv_controller_router)
app.include_router(profile_router)
app.include_router(runtime_router)
app.include_router(health_router)
app.include_router(location_router)
app.include_router(jobs_proxy_router)


@app.get("/")
def root():
    return {
        "app": "LIA EmployX",
        "tagline": "Career Operating System",
        "status": "running",
        "runtime": "active",
    }


@app.get("/api/v1/ping")
def ping():
    return {"ok": True}
