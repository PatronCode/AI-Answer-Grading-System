from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import json
import os
from typing import Optional

from app.models.schemas import AnswerSubmission, FeedbackResponse, OCRResponse
from app.services.llm_service import generate_feedback
from app.services.ocr_service import process_image
from fastapi.staticfiles import StaticFiles



app = FastAPI(
    title="Exam Answer Marking API",
    description="API for automated marking of exam answers using LLM",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", include_in_schema=False)
async def serve_frontend():
    return FileResponse("app/static/index.html")

@app.on_event("startup")
async def startup_db_client():
    # Load questions from JSON file
    try:
        # Use the direct path to the questions.json file
        json_path = r"C:\Users\mozzam.suleman\Videos\My_project\questions.json"
        
        print(f"Attempting to load questions from: {json_path}")
        
        if os.path.exists(json_path):
            print(f"File exists at: {json_path}")
            with open(json_path, "r", encoding="utf-8") as file:
                file_content = file.read()
                print(f"File content length: {len(file_content)} characters")
                
                # Parse the JSON content
                app.questions_data = json.loads(file_content)
                
                # Verify the loaded data
                print(f"Loaded data keys: {app.questions_data.keys()}")
                print(f"Number of questions: {len(app.questions_data.get('questions', []))}")
                
                if len(app.questions_data.get('questions', [])) > 0:
                    print(f"First question ID: {app.questions_data['questions'][0].get('question_id', 'N/A')}")
                
                print(f"Successfully loaded questions from {json_path}")
        else:
            print(f"File does not exist at: {json_path}")
            # Fallback to empty structure if file can't be loaded
            app.questions_data = {"subject": "Physics", "questions": []}
    except Exception as e:
        print(f"Error loading questions from file: {e}")
        import traceback
        traceback.print_exc()
        # Fallback to empty structure if file can't be loaded
        app.questions_data = {"subject": "Physics", "questions": []}

@app.get("/questions")
async def get_questions():
    """Return all available questions"""
    return app.questions_data

@app.get("/questions/{question_id}")
async def get_question(question_id: str):
    """Get a specific question by ID"""
    for question in app.questions_data["questions"]:
        if question["question_id"] == question_id:
            # Remove model_answer from the response for students
            question_for_student = {k: v for k, v in question.items() if k != "model_answer"}
            return question_for_student
    
    raise HTTPException(status_code=404, detail=f"Question {question_id} not found")

@app.post("/submit-answer", response_model=FeedbackResponse)
async def submit_answer(submission: AnswerSubmission):
    """
    Submit a student answer for evaluation
    - Finds the question from our database
    - Sends to LLM for evaluation against model answer
    - Returns feedback with marks and explanations
    """
    # Find the question in our database
    question = None
    for q in app.questions_data["questions"]:
        if q["question_id"] == submission.question_id:
            question = q
            break
    
    if not question:
        raise HTTPException(status_code=404, detail=f"Question {submission.question_id} not found")
    
    # Generate feedback using LLM
    feedback = await generate_feedback(
        question_text=question["question"],
        student_answer=submission.answer,
        model_answer=question["model_answer"],
        marking_scheme=question["marking_scheme"],
        max_marks=question["max_marks"],
        topic=question["topic"]
    )
    
    return feedback

@app.post("/submit-image", response_model=OCRResponse)
async def submit_image(
    question_id: str = Form(...),
    image: UploadFile = File(...),
    grade: Optional[bool] = Form(False)
):
    """
    Submit an image of a handwritten answer for OCR processing and optional grading
    - Extracts text from the image using OCR
    - Optionally grades the extracted text using the LLM
    - Returns the extracted text and optional feedback
    """
    # Find the question in our database if grading is requested
    question = None
    if grade:
        for q in app.questions_data["questions"]:
            if q["question_id"] == question_id:
                question = q
                break
        
        if not question:
            raise HTTPException(status_code=404, detail=f"Question {question_id} not found")
    
    # Process the image and get OCR results
    ocr_response = await process_image(
        file=image,
        question_id=question_id,
        question=question,
        grade=grade
    )
    
    return ocr_response
