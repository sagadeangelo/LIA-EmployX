"""Local development API for the first end-to-end CV flow."""
import os
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Literal
from fastapi import FastAPI, File, HTTPException, Query, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from starlette.concurrency import run_in_threadpool
from backend.database.db import ProfileRepository
from backend.modules.cv.api_models import ProfileDraft
from backend.modules.cv.services.cv_analyzer import AIUnavailableError, CVAnalyzer, MAX_FILE_BYTES


def create_app(db_path=None, analyzer=None):
    app = FastAPI(title='LIA EmployX — CV', version='0.1.0')
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[v.strip() for v in os.getenv(
            'EMPLOYX_CORS_ORIGINS', 'http://localhost:5173,http://127.0.0.1:5173').split(',') if v.strip()],
        allow_methods=['GET', 'POST', 'PUT'], allow_headers=['Content-Type'],
    )
    service = analyzer or CVAnalyzer()
    repository = None

    def repo():
        nonlocal repository
        if repository is None:
            repository = ProfileRepository(db_path)
        return repository

    @app.get('/health')
    def health():
        repo().list()
        return {'status': 'ok', 'formats': ['pdf', 'txt']}

    @app.post('/api/cvs/analyze')
    async def analyze(file: UploadFile = File(...), mode: Literal['local', 'lmstudio'] = Query('local')):
        suffix = Path(file.filename or '').suffix.lower()
        try:
            if suffix not in {'.pdf', '.txt'}:
                raise HTTPException(415, 'Formato no admitido. Selecciona PDF con texto o TXT.')
            with TemporaryDirectory(prefix='employx-cv-') as folder:
                path = Path(folder) / ('cv' + suffix)
                size = 0
                with path.open('wb') as output:
                    while chunk := await file.read(65536):
                        size += len(chunk)
                        if size > MAX_FILE_BYTES:
                            raise HTTPException(413, 'El archivo supera el límite de 10 MB.')
                        output.write(chunk)
                if size == 0:
                    raise HTTPException(422, 'El archivo está vacío.')
                try:
                    result = await run_in_threadpool(service.analyze_document, path, mode)
                except AIUnavailableError as error:
                    raise HTTPException(503, str(error)) from error
                except ValueError as error:
                    raise HTTPException(422, str(error)) from error
            return {'title': Path(file.filename or 'CV').stem[:160] or 'CV', **result.to_dict()}
        finally:
            await file.close()

    @app.get('/api/cvs')
    def list_profiles():
        return [{'id': item['id'], 'title': item['title'], 'updated_at': item['updated_at'],
                 'full_name': item['profile']['personal_info']['full_name']} for item in repo().list()]

    @app.get('/api/cvs/{profile_id}')
    def get_profile(profile_id: str):
        result = repo().get(profile_id)
        if result is None:
            raise HTTPException(404, 'No se encontró este perfil.')
        return result

    @app.post('/api/cvs', status_code=201)
    def create_profile(draft: ProfileDraft):
        return repo().save(draft.model_dump(mode='json'))

    @app.put('/api/cvs/{profile_id}')
    def update_profile(profile_id: str, draft: ProfileDraft):
        try:
            return repo().save(draft.model_dump(mode='json'), profile_id)
        except KeyError as error:
            raise HTTPException(404, 'No se encontró este perfil.') from error

    return app


app = create_app()
