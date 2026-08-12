"""
LIA EmployX — Agent Bootstrap

Punto de entrada para configurar el AgentRegistry con todos los agentes del sistema.
Este archivo es el UNICO lugar donde se instancian y registran los agentes.

Para agregar un nuevo agente desde Agent Hub:
  1. Implementar BaseAgent en backend/agents/<nombre>/agent.py
  2. Importarlo aqui y llamar registry.register()
  
El MissionController y el resto del sistema no necesitan ser modificados.
"""
from backend.agents.base.agent_registry import AgentRegistry
from backend.agents.llm.llm_provider import MockLLMProvider

from backend.agents.career_agent.agent import CareerAgent
from backend.agents.cv_expert.agent import CVExpert
from backend.agents.ats_agent.agent import ATSAnalyzer
from backend.agents.search_agent.agent import JobHunter
from backend.agents.networking_agent.agent import LinkedInOptimizer
from backend.agents.cover_letter_agent.agent import CoverLetterGenerator
from backend.agents.interview_agent.agent import InterviewCoach
from backend.agents.negotiation_agent.agent import NegotiationCoach


def build_registry(llm_provider=None) -> AgentRegistry:
    """
    Construye y devuelve un AgentRegistry con todos los agentes registrados.
    
    Args:
        llm_provider: Proveedor de IA. Por defecto usa MockLLMProvider.
                      En produccion pasar OpenAIProvider, GeminiProvider, etc.
    
    Returns:
        AgentRegistry listo para usar con el MissionController.
    """
    llm = llm_provider or MockLLMProvider()
    registry = AgentRegistry()

    # Orden de registro (el priority en metadata define el orden de ejecucion)
    from backend.agents.cv_agent.agent import CVParserAgent
    registry.register(CVParserAgent())         # priority=10
    registry.register(CareerAgent(llm))        # priority=15 (assuming it gets executed after parsing)
    registry.register(CVExpert(llm))           # priority=20
    registry.register(ATSAnalyzer(llm))        # priority=30
    registry.register(JobHunter(llm))          # priority=40
    registry.register(LinkedInOptimizer(llm))  # priority=50
    registry.register(CoverLetterGenerator(llm)) # priority=60
    registry.register(InterviewCoach(llm))     # priority=70
    registry.register(NegotiationCoach(llm))   # priority=80

    print(f"[Bootstrap] AgentRegistry inicializado con {len(registry)} agentes.")
    print(f"[Bootstrap] Capacidades disponibles: {registry.get_capabilities()}")
    
    return registry
