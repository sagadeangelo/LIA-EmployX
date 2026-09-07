"""Compatibility entry point using the same service as the API."""
from backend.modules.cv.services.cv_analyzer import CVAnalyzer


class SmartCVPipeline:
    def __init__(self):
        self.analyzer = CVAnalyzer()

    def process(self, file_path: str, mode='local'):
        return self.analyzer.analyze(file_path, mode)
