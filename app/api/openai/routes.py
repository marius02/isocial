from fastapi import APIRouter
from api.openai.models import CommentsRequest

from api.openai.services import OpenAIService
from dotenv import load_dotenv
import os

load_dotenv()


router = APIRouter(prefix="/openai", tags=["OpenAI API"])


ACCESS_TOKEN = os.getenv("OPENAI_TOKEN")


@router.post("/prompt-processing")
def openai_processing_data(prompt: str, comments: CommentsRequest):
    openai_service = OpenAIService()
    processing_result = openai_service.get_completion(comments.comments, prompt)
    
    return processing_result
