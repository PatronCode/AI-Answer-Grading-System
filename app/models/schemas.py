from pydantic import BaseModel, Field, EmailStr
from typing import Dict, List, Optional
from datetime import datetime

# Authentication and User Models
class UserBase(BaseModel):
    """Base model for user data"""
    email: EmailStr = Field(description="User's email address")
    student_name: str = Field(description="Student's full name")

class UserCreate(UserBase):
    """Model for user registration"""
    password: str = Field(description="User's password")

class UserLogin(BaseModel):
    """Model for user login"""
    email: EmailStr = Field(description="User's email address")
    password: str = Field(description="User's password")

class UserInDB(UserBase):
    """Model for user in database"""
    id: str = Field(description="User's unique ID")
    hashed_password: str = Field(description="Hashed password")
    created_at: datetime = Field(description="Account creation timestamp")
    
class User(UserBase):
    """Model for user response"""
    id: str = Field(description="User's unique ID")

class Token(BaseModel):
    """Model for JWT token"""
    access_token: str = Field(description="JWT access token")
    token_type: str = Field(description="Token type")

class TokenData(BaseModel):
    """Model for token payload"""
    email: Optional[str] = None

# Existing Models
class AnswerSubmission(BaseModel):
    """Model for student answer submission"""
    question_id: str = Field(description="ID of the question being answered")
    answer: str = Field(description="Student's answer text")
    user_id: Optional[str] = Field(None, description="ID of the user submitting the answer")

class MarkingPoint(BaseModel):
    """Individual marking point with feedback"""
    criterion: str = Field(description="The marking criterion")
    max_mark: int = Field(description="Maximum available marks for this criterion")
    awarded_mark: int = Field(description="Marks awarded for this criterion")
    feedback: str = Field(description="Feedback on this specific criterion")
    explanation: str = Field(description="Explanation of why marks were deducted, if any")

class FeedbackResponse(BaseModel):
    """Model for the feedback response"""
    question_id: str = Field(description="ID of the question")
    total_marks_available: int = Field(description="Maximum available marks")
    total_marks_awarded: int = Field(description="Total marks awarded")
    overall_feedback: str = Field(description="Overall feedback on the answer")
    detailed_marking: List[MarkingPoint] = Field(description="Detailed breakdown of marking")
    user_id: Optional[str] = Field(None, description="ID of the user who submitted the answer")
    created_at: Optional[datetime] = Field(None, description="Timestamp of when the feedback was generated")

class OCRRequest(BaseModel):
    """Model for OCR request"""
    question_id: str = Field(description="ID of the question being answered")
    # Note: The actual image file will be handled separately as a form upload

class OCRResponse(BaseModel):
    """Model for OCR response"""
    question_id: str = Field(description="ID of the question")
    extracted_text: str = Field(description="Text extracted from the image")
    feedback: Optional[FeedbackResponse] = Field(None, description="Feedback on the extracted answer if grading was requested")

class UserFeedbackHistory(BaseModel):
    """Model for user feedback history"""
    user_id: str = Field(description="ID of the user")
    feedback_list: List[FeedbackResponse] = Field(description="List of feedback responses for the user")
