import os
import io
from google.cloud import vision
from fastapi import UploadFile
from app.models.schemas import OCRResponse, FeedbackResponse
from app.services.llm_service import generate_feedback

# Set Google Cloud credentials
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = r"C:\Users\mozzam.suleman\Videos\My_project\handwritingocrproject-458118-3c328f893a41.json"

async def process_image(file: UploadFile, question_id: str, question=None, grade=False) -> OCRResponse:
    """
    Process an uploaded image using Google Vision API to extract text.
    Optionally grade the extracted text if requested.
    
    Args:
        file: The uploaded image file
        question_id: ID of the question being answered
        question: The question object from the database (required if grade=True)
        grade: Whether to grade the extracted text
        
    Returns:
        OCRResponse object with extracted text and optional feedback
    """
    try:
        # Read the image file
        contents = await file.read()
        
        # Initialize Google Vision client
        client = vision.ImageAnnotatorClient()
        image = vision.Image(content=contents)
        
        # Perform document text detection (optimized for handwriting)
        response = client.document_text_detection(image=image)
        
        # Extract the full text
        if response.error.message:
            raise Exception(f'Google Vision API error: {response.error.message}')
            
        extracted_text = response.full_text_annotation.text
        
        # Create response object
        response = OCRResponse(
            question_id=question_id,
            extracted_text=extracted_text,
            feedback=None
        )
        
        # Grade the extracted text if requested
        if grade and question:
            feedback = await generate_feedback(
                question_text=question["question"],
                student_answer=extracted_text,
                model_answer=question["model_answer"],
                marking_scheme=question["marking_scheme"],
                max_marks=question["max_marks"],
                topic=question["topic"]
            )
            response.feedback = feedback
        
        return response
    
    except Exception as e:
        print(f"Error processing image: {e}")
        # Return a response with the error
        return OCRResponse(
            question_id=question_id,
            extracted_text=f"Error extracting text: {str(e)}",
            feedback=None
        )
