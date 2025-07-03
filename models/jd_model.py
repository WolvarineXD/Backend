from pydantic import BaseModel
from typing import Dict, Optional

class JDInput(BaseModel):
    job_title: str
    job_description: str
    skills: Dict[str, int]
    resume_drive_link: Optional[str] = None  
