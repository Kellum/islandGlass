"""
Job Comment Models
Pydantic models for job comments API
"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class JobCommentBase(BaseModel):
    """Base job comment model with common fields"""
    job_id: int
    comment_text: str
    comment_type: str = "Note"  # 'Note', 'Update', 'Issue', 'Resolution', 'Question', 'Answer'
    parent_comment_id: Optional[int] = None


class JobCommentCreate(JobCommentBase):
    """Model for creating a new job comment"""
    pass


class JobCommentUpdate(BaseModel):
    """Model for updating a job comment - only comment_text can be edited"""
    comment_text: str
    edited: bool = True


class JobCommentResponse(JobCommentBase):
    """Model for job comment responses"""
    comment_id: int
    user_id: str
    user_name: Optional[str] = None
    edited: bool = False
    edited_at: Optional[datetime] = None
    company_id: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True
