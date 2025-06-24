from pydantic import BaseModel
from typing import Dict

class JDInput(BaseModel):
    job_title: str
    job_description: str
    skills: Dict[str, int]  # key = skill name, value = weight
