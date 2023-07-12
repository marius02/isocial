from fastapi import HTTPException
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from db.base import get_db
from api.openai.models import CommentsRequest, SummaryResponse

from api.openai.services import OpenAIService
from dotenv import load_dotenv
import os

load_dotenv()


router = APIRouter(prefix="/openai", tags=["OpenAI API"])


ACCESS_TOKEN = os.getenv("OPENAI_TOKEN")


@router.post("/{platform}/summarize-comments")
def summarize_comments(platform: str, request: CommentsRequest):
    comments = request.comments

    # Create an instance of the OpenAIService
    summarization_service = OpenAIService()

    # Perform summarization
    summary = summarization_service.summarize_comments(platform, comments)

    # Create and return the response
    return SummaryResponse(summary=summary)
