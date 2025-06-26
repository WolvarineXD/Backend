from pydantic import BaseModel
from typing import Dict, Optional

class JDInput(BaseModel):
    job_title: str
    job_description: str
    skills: Dict[str, int]
    is_draft: Optional[bool] = False  # 👈 Add this
