"""Offline integration checks. No real CVs, model downloads or external requests."""
from dataclasses import asdict
import pytest
import fitz
from fastapi.testclient import TestClient
from backend.main import create_app
from backend.agents.cv_agent.agent import CVAgent
from backend.agents.base.base_agent import AgentStatus
from backend.modules.cv.engine.pipeline import SmartCVPipeline
from backend.modules.cv.services.cv_analyzer import CVAnalyzer

TEXT = 'Nombre: Persona de Prueba\nCorreo: demo@example.com\nTeléfono: 5551234567\n'


@pytest.fixture
def client(tmp_path):
    return TestClient(create_app(tmp_path / 'profiles.sqlite'))


def upload(client, data=TEXT.encode(), filename='cv.txt', mode='local'):
    return client.post('/api/cvs/analyze', params={'mode': mode},
                       files={'file': (filename, data)})


def test_review_save_restart_reopen_update(tmp_path):
    path = tmp_path / 'profiles.sqlite'
    with TestClient(create_app(path)) as client:
        draft = upload(client).json()
        assert draft['profile']['personal_info']['email'] == 'demo@example.com'
        assert draft['profile']['experience'] == []
        assert draft['extraction_method'] == 'local'
        assert draft['warnings']
        assert client.get('/api/cvs').json() == []  # Analyze never implicitly saves.
        draft['profile']['personal_info']['full_name'] = 'Nombre corregido'
        draft['profile']['experience'] = [{'company': 'Empresa de prueba', 'position': 'Ventas',
                                          'achievements': ['Dato revisado'], 'current': True}]
        draft['profile']['education'] = [{'institution': 'Escuela de prueba'}]
        draft['profile']['skills'] = [{'name': 'Python'}]
        draft['profile']['languages'] = [{'name': 'Español'}]
        draft['profile']['certifications'] = [{'name': 'Curso de prueba'}]
        draft['profile']['projects'] = [{'name': 'Proyecto de prueba', 'technologies': ['Python']}]
        response = client.post('/api/cvs', json=draft)
        assert response.status_code == 201
        saved = response.json()
    with TestClient(create_app(path)) as restarted:
        recovered = restarted.get('/api/cvs/' + saved['id']).json()
        assert recovered == saved
        assert recovered['source_text'] == TEXT
        assert recovered['profile']['skills'][0]['years'] is None
        assert restarted.get('/api/cvs').json()[0]['full_name'] == 'Nombre corregido'
        draft['title'] = 'CV corregido'
        updated = restarted.put('/api/cvs/' + saved['id'], json=draft)
        assert updated.status_code == 200
        assert updated.json()['created_at'] == saved['created_at']
        assert len(restarted.get('/api/cvs').json()) == 1
        assert restarted.get('/api/cvs/' + saved['id']).json()['title'] == 'CV corregido'


def test_real_pdf_text_extraction(client):
    with fitz.open() as document:
        document.new_page().insert_text((72, 72), TEXT)
        pdf = document.tobytes()
    result = upload(client, pdf, 'cv.pdf')
    assert result.status_code == 200
    assert result.json()['profile']['personal_info']['email'] == 'demo@example.com'


@pytest.mark.parametrize('data,name,status', [
    (b'', 'cv.txt', 422), (b'  \n', 'cv.txt', 422), (b'fake', 'cv.docx', 415),
    (b'\x00binary', 'cv.txt', 422), (b'fake', 'cv.jpg', 415), (b'not a pdf', 'cv.pdf', 422),
    (b'a' * (10 * 1024 * 1024 + 1), 'cv.txt', 413),
    (b'a' * 60001, 'cv.txt', 422),
])
def test_invalid_uploads(client, data, name, status):
    result = upload(client, data, name)
    assert result.status_code == status
    assert isinstance(result.json()['detail'], str)
    assert client.get('/api/cvs').json() == []


def test_image_only_pdf(client):
    with fitz.open() as document:
        document.new_page()
        result = upload(client, document.tobytes(), 'scan.pdf')
    assert result.status_code == 422
    assert 'OCR' in result.json()['detail']


def test_agent_and_pipeline_share_analysis(tmp_path):
    path = tmp_path / 'cv.txt'
    path.write_text(TEXT)
    expected = asdict(CVAnalyzer().analyze(path))
    assert asdict(SmartCVPipeline().process(str(path))) == expected
    agent = CVAgent()
    assert asdict(agent.run(str(path))) == expected
    with pytest.raises(ValueError):
        agent.run(str(tmp_path / 'missing.txt'))
    assert agent.status == AgentStatus.ERROR


def test_absent_information_not_invented(client):
    draft = upload(client, b'Some unlabelled text').json()
    assert draft['profile']['personal_info']['full_name'] == ''
    assert draft['profile']['personal_info']['phone'] == ''
    assert draft['profile']['experience'] == []
    assert draft['profile']['preferences']['desired_salary'] is None
    assert draft['source_text'] == 'Some unlabelled text'


def test_missing_and_invalid_profiles(client):
    assert client.get('/api/cvs/missing').status_code == 404
    draft = upload(client).json()
    assert client.put('/api/cvs/missing', json=draft).status_code == 404
    draft['profile']['experience'] = 'bad type'
    assert client.post('/api/cvs', json=draft).status_code == 422


def test_lmstudio_offline_is_explicit(tmp_path):
    class OfflineParser:
        def is_ready(self): return False
    client = TestClient(create_app(tmp_path / 'db.sqlite', CVAnalyzer(OfflineParser)))
    response = upload(client, mode='lmstudio')
    assert response.status_code == 503
    assert 'LM Studio' in response.json()['detail']
    assert client.get('/api/cvs').json() == []


def test_lmstudio_contract_with_mocked_provider(tmp_path, monkeypatch):
    # Real prompt/parser/validator/mapper; only the provider transport is mocked.
    from backend.ai.llm_manager import LLMManager
    monkeypatch.setattr(LLMManager, '__init__', lambda self: None)
    monkeypatch.setattr(LLMManager, 'is_online', lambda self: True)
    monkeypatch.setattr(LLMManager, 'ask', lambda *a, **kw: {
        'answer': '{"personal_info":{"email":"demo@example.com"},"education":[]}'})
    client = TestClient(create_app(tmp_path / 'db.sqlite'))
    result = upload(client, mode='lmstudio')
    assert result.status_code == 200
    assert result.json()['extraction_method'] == 'lmstudio'
    assert result.json()['profile']['personal_info']['email'] == 'demo@example.com'


def test_lmstudio_invalid_result_is_not_success(tmp_path, monkeypatch):
    from backend.ai.llm_manager import LLMManager
    monkeypatch.setattr(LLMManager, '__init__', lambda self: None)
    monkeypatch.setattr(LLMManager, 'is_online', lambda self: True)
    monkeypatch.setattr(LLMManager, 'ask', lambda *a, **kw: {'answer': 'invalid json'})
    client = TestClient(create_app(tmp_path / 'db.sqlite'))
    assert upload(client, mode='lmstudio').status_code == 503


def test_loopback_web_cors(client):
    allowed = client.options('/api/cvs', headers={
        'Origin': 'http://localhost:5173', 'Access-Control-Request-Method': 'POST'})
    assert allowed.headers['access-control-allow-origin'] == 'http://localhost:5173'
    denied = client.options('/api/cvs', headers={
        'Origin': 'https://unrelated.example', 'Access-Control-Request-Method': 'POST'})
    assert 'access-control-allow-origin' not in denied.headers
