from typing import List
from .models import JobError

class AITriage:
    def __init__(self, api_key: str = None):
        self.api_key = api_key
        # In the future, initialize OpenAI or local LLM client here
        
    def analyze_error(self, error: JobError) -> List[str]:
        """
        Parses the error to understand context and extract required skills.
        Returns a list of required skills (e.g., ['Python', 'CUDA']).
        """
        # TODO: Implement actual LLM parsing logic
        skills = []
        error_text = (error.error_message + " " + (error.stack_trace or "")).lower()
        
        # Mock logic based on keywords
        if "python" in error_text or "traceback" in error_text:
            skills.append("python")
        if "cuda" in error_text or "gpu" in error_text:
            skills.append("cuda")
        if "cesium" in error_text:
            skills.append("cesiumjs")
        if "sql" in error_text or "database" in error_text:
            skills.append("database-admin")
            
        if not skills:
            skills.append("general-debugging")
            
        return list(set(skills))