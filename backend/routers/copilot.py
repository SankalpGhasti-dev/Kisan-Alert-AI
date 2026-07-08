from fastapi import APIRouter
from backend.schemas.copilot import ConversationContext
from backend.services.copilot.copilot import handle_copilot_interaction

router = APIRouter()

@router.post("/chat")
async def process_chat(req: ConversationContext):
    """
    Process a text-based chat request.
    """
    if not req.user_message or not req.user_message.strip():
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail="Empty message")
        
    response = await handle_copilot_interaction(req)
    return response
