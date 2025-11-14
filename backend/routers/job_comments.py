"""
Job Comments Router
FastAPI endpoints for job comments
"""
from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional
from models.job_comment import JobCommentCreate, JobCommentUpdate, JobCommentResponse
from models.user import TokenData
from middleware.auth import get_current_user
from database import Database

router = APIRouter(tags=["job-comments"])


@router.get("/", response_model=List[JobCommentResponse])
async def list_job_comments(
    job_id: int = Query(..., description="Filter by job ID (required)"),
    comment_type: Optional[str] = Query(None, description="Filter by comment type"),
    current_user: TokenData = Depends(get_current_user)
):
    """Get all comments for a job with optional filters"""
    db = Database()

    try:
        # Get comments for specific job
        comments = db.get_job_comments(job_id)

        # Apply comment_type filter if provided
        if comment_type:
            comments = [c for c in comments if c.get('comment_type') == comment_type]

        return comments
    except Exception as e:
        print(f"Error fetching job comments: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch job comments")


@router.get("/{comment_id}", response_model=JobCommentResponse)
async def get_job_comment(
    comment_id: int,
    current_user: TokenData = Depends(get_current_user)
):
    """Get a specific job comment by ID"""
    db = Database()

    comment = db.get_job_comment_by_id(comment_id)
    if not comment:
        raise HTTPException(status_code=404, detail="Job comment not found")

    return comment


@router.post("/", response_model=JobCommentResponse, status_code=201)
async def create_job_comment(
    comment_data: JobCommentCreate,
    current_user: TokenData = Depends(get_current_user)
):
    """Create a new job comment"""
    db = Database()

    # Convert to dict
    comment_dict = comment_data.model_dump()

    # Get user's email from token as user_name
    # In a real scenario, you might want to fetch this from a user profile
    user_name = current_user.email if hasattr(current_user, 'email') else current_user.user_id

    # Insert the comment
    created_comment = db.insert_job_comment(comment_dict, current_user.user_id, user_name)

    if not created_comment:
        raise HTTPException(status_code=400, detail="Failed to create job comment")

    return created_comment


@router.put("/{comment_id}", response_model=JobCommentResponse)
async def update_job_comment(
    comment_id: int,
    comment_data: JobCommentUpdate,
    current_user: TokenData = Depends(get_current_user)
):
    """Update a job comment (edit the text)"""
    db = Database()

    # Check if comment exists
    existing_comment = db.get_job_comment_by_id(comment_id)
    if not existing_comment:
        raise HTTPException(status_code=404, detail="Job comment not found")

    # Check if user is the author of the comment
    if existing_comment.get('user_id') != current_user.user_id:
        raise HTTPException(status_code=403, detail="You can only edit your own comments")

    # Convert to dict
    updates = comment_data.model_dump()

    # Update the comment
    updated_comment = db.update_job_comment(comment_id, updates)

    if not updated_comment:
        raise HTTPException(status_code=400, detail="Failed to update job comment")

    return updated_comment


@router.delete("/{comment_id}", status_code=204)
async def delete_job_comment(
    comment_id: int,
    current_user: TokenData = Depends(get_current_user)
):
    """Delete a job comment"""
    db = Database()

    # Check if comment exists
    existing_comment = db.get_job_comment_by_id(comment_id)
    if not existing_comment:
        raise HTTPException(status_code=404, detail="Job comment not found")

    # Check if user is the author of the comment
    if existing_comment.get('user_id') != current_user.user_id:
        raise HTTPException(status_code=403, detail="You can only delete your own comments")

    # Delete the comment
    success = db.delete_job_comment(comment_id)

    if not success:
        raise HTTPException(status_code=400, detail="Failed to delete job comment")

    return None
