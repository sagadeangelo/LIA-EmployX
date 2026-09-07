"""CV agent shares the application's analysis service."""
from backend.agents.base.base_agent import BaseAgent, AgentStatus
from backend.modules.cv.services.cv_analyzer import CVAnalyzer


class CVAgent(BaseAgent):
    def __init__(self):
        super().__init__('CV Specialist', 'Extrae un perfil para revisión del usuario.')
        self.analyzer = CVAnalyzer()

    def run(self, file_path: str, mode='local'):
        self.status = AgentStatus.RUNNING
        try:
            result = self.analyzer.analyze_document(file_path, mode)
            if self.context is not None:
                self.context.set('professional_profile', result.profile)
                self.context.set('cv_analysis', result.to_dict())
                self.context.add_event('CV extraído; pendiente de revisión.')
            self.emit_event('CV_ANALYZED')
            self.status = AgentStatus.STOPPED
            return result.profile
        except Exception:
            self.status = AgentStatus.ERROR
            raise
