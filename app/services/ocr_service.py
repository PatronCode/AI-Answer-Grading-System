import os
import cv2
import numpy as np
import re
import pytesseract
from PIL import Image
from io import BytesIO
from spellchecker import SpellChecker
from fastapi import UploadFile
from app.models.schemas import OCRResponse, FeedbackResponse
from app.services.llm_service import generate_feedback

# Set the path to the Tesseract executable
pytesseract.pytesseract.tesseract_cmd = r"C:\Users\mozzam.suleman\AppData\Local\Programs\Tesseract-OCR\tesseract.exe"

async def process_image(file: UploadFile, question_id: str, question=None, grade=False) -> OCRResponse:
    """
    Process an uploaded image using OCR to extract text.
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
        
        # Convert to OpenCV format
        nparr = np.frombuffer(contents, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        # Step 1: Preprocessing
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Enhance contrast
        gray = cv2.convertScaleAbs(gray, alpha=1.5, beta=0)
        
        # Apply adaptive thresholding
        thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C,
                                      cv2.THRESH_BINARY_INV, 15, 10)
        
        # Dilate to connect text components
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2,2))
        dilate = cv2.dilate(thresh, kernel, iterations=1)
        
        # Step 2: OCR
        custom_config = r'--oem 1 --psm 6'
        raw_text = pytesseract.image_to_string(dilate, config=custom_config)
        
        # Step 3: Cleaning
        # Remove duplicate lines
        lines = raw_text.split('\n')
        unique_lines = []
        for line in lines:
            clean_line = line.strip()
            if clean_line and clean_line not in unique_lines:
                unique_lines.append(clean_line)
        
        # Step 4: Spell correction
        spell = SpellChecker()
        final_lines = []
        for line in unique_lines:
            corrected_words = []
            for word in re.findall(r'\b\w+\b', line):
                if len(word) > 2:  # Only correct words longer than 2 characters
                    corrected_word = spell.correction(word)
                    if corrected_word:
                        corrected_words.append(corrected_word)
                    else:
                        corrected_words.append(word)
                else:
                    corrected_words.append(word)
            corrected_line = ' '.join(corrected_words)
            final_lines.append(corrected_line)
        
        # Step 5: Final cleaned text
        extracted_text = '\n'.join(final_lines)
        
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
