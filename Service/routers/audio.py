import logging
from fastapi import APIRouter, WebSocket
from Service.common.handle_disconnection import *
from Service.common.http.context_request import ContextRequest
from Service.common.audio_transcription_processor import *
from Service.config import *
from Service.common.http.context_response import ContextResponse
from Service.services.audio_service import create_context_logic, transcription_logic

router = APIRouter(prefix="/audio", tags=["Audio"])

@router.websocket("/transcribe")
async def websocket_endpoint(websocket: WebSocket):
    await transcription_logic(websocket)


@router.post("/create-context")
async def create_context(request: ContextRequest):
    if request.command:
        message,subject_conversation =  await create_context_logic()
        logging.info("Offline Context creation Completed")
    return ContextResponse(Summarized_message= message, response_text = subject_conversation)
