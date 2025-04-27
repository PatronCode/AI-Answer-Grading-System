from pydantic import BaseModel, Field
from typing import Dict, List, Optional

class AnswerSubmission(BaseModel):
    """Model for student answer submission"""
    question_id: str = Field(description="ID of the question being answered")
    answer: str = Field(description="Student's answer text")

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

class OCRRequest(BaseModel):
    """Model for OCR request"""
    question_id: str = Field(description="ID of the question being answered")
    # Note: The actual image file will be handled separately as a form upload

class OCRResponse(BaseModel):
    """Model for OCR response"""
    question_id: str = Field(description="ID of the question")
    extracted_text: str = Field(description="Text extracted from the image")
    feedback: Optional[FeedbackResponse] = Field(None, description="Feedback on the extracted answer if grading was requested")
