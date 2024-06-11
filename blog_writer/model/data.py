


from typing import Dict, List

from pydantic import BaseModel


class EmbedData:
    id: str 
    content: str
    metadata: Dict[str, str]
    

class StepTracker(BaseModel):
    current_step: int = -1
    
    
class OutlineModel(BaseModel):
    outline: List[Dict[str, str]] = []
    title: str = ""
    description: str = ""