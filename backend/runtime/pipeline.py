from typing import List
from backend.runtime.mission_state import MissionStage

class MissionPipeline:
    """
    Defines the sequential stages of a Mission in the Career Operating System.
    The Pipeline allows automatic calculation of progress and determination of the next stage.
    """
    
    # The official order of execution for a Mission
    STEPS: List[MissionStage] = [
        MissionStage.RECEIVE_FILE,
        MissionStage.STORE_FILE,
        MissionStage.DETECT_FORMAT,
        MissionStage.READ_DOCUMENT,
        MissionStage.EXTRACT_TEXT,
        MissionStage.NORMALIZE_TEXT,
        MissionStage.BUILD_PROFILE,
        MissionStage.SAVE_PROFILE,
        MissionStage.UPDATE_RUNTIME,
        MissionStage.COMPLETE
    ]
    
    @classmethod
    def get_progress(cls, current_step: MissionStage) -> int:
        """
        Calculates the progress automatically based on the current step in the pipeline.
        Returns a percentage (0-100).
        """
        if current_step not in cls.STEPS:
            return 0
        
        index = cls.STEPS.index(current_step)
        total = len(cls.STEPS) - 1 # -1 because index starts at 0, and FINISHED should be 100%
        
        if total <= 0:
            return 100
            
        progress = int((index / total) * 100)
        return min(progress, 100)
        
    @classmethod
    def get_next_step(cls, current_step: MissionStage) -> MissionStage:
        """
        Returns the next step in the pipeline, or COMPLETE if it's the last step.
        """
        if current_step not in cls.STEPS:
            return MissionStage.COMPLETE
            
        index = cls.STEPS.index(current_step)
        if index + 1 < len(cls.STEPS):
            return cls.STEPS[index + 1]
            
        return MissionStage.COMPLETE
