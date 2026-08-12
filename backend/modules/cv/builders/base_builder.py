from typing import Generic, TypeVar, List
from pydantic import BaseModel, Field
from abc import ABC, abstractmethod

T = TypeVar('T')

class BuildResult(BaseModel, Generic[T]):
    """
    Standard response format for all Builders.
    """
    data: T
    confidence: float = Field(default=100.0, description="Confidence score from 0.0 to 100.0")
    warnings: List[str] = Field(default_factory=list, description="List of extraction warnings")

class BaseBuilder(ABC, Generic[T]):
    """
    Common interface for all section builders.
    Enables replacing a deterministic implementation with an LLM implementation seamlessly.
    """
    
    @abstractmethod
    def build(self, text: str) -> BuildResult[T]:
        """
        Builds the domain model from a specific section's text.
        
        Args:
            text: The raw text of the section.
            
        Returns:
            A BuildResult containing the structured data, confidence score, and warnings.
        """
        pass
