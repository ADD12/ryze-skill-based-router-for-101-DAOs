import json
from typing import List
from openai import OpenAI
from .models import JobError
from .config import settings

class AITriage:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or settings.openai_api_key
        self.client = OpenAI(api_key=self.api_key) if self.api_key else None
        
    def analyze_error(self, error: JobError) -> List[str]:
        """
        Parses the error to understand context and extract required skills.
        Returns a list of required skills (e.g., ['python', 'cuda']).
        """
        if not self.client:
            return self._mock_analyze_error(error)

        try:
            prompt = f"""
Analyze the following error report from a {error.system} system.
Error Message: {error.error_message}
Stack Trace: {error.stack_trace or "None"}

Identify the key technical skills required to fix this error. 
Return ONLY a valid JSON array of strings representing the skills in lowercase (e.g., ["python", "cuda", "database-admin"]).
Do not include any other text or markdown formatting.
            """
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert technical triage assistant. You extract skills needed to solve bugs."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.0,
            )
            
            content = response.choices[0].message.content.strip()
            
            # Clean up potential markdown formatting
            if content.startswith("```json"):
                content = content[7:]
            if content.endswith("```"):
                content = content[:-3]
                
            skills = json.loads(content.strip())
            if isinstance(skills, list):
                return [str(s).lower() for s in skills]
            
        except Exception as e:
            print(f"OpenAI Triage failed: {e}. Falling back to mock triage.")
            
        return self._mock_analyze_error(error)

    def _mock_analyze_error(self, error: JobError) -> List[str]:
        skills = []
        error_text = (error.error_message + " " + (error.stack_trace or "")).lower()
        
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