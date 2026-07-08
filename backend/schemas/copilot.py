from pydantic import BaseModel
from typing import Optional

class ConversationContext(BaseModel):
    response_mode: str = "text"
    language: str = "English"
    user_message: str
    current_page: str = "Dashboard"
    selected_state: str
    selected_district: str
    user_profile: Optional[dict] = None
