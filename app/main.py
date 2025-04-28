from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Depends, Security, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import json
import os
from typing import Optional, List
from datetime import datetime, timedelta

from app.models.schemas import (
    AnswerSubmission, FeedbackResponse, OCRResponse, 
    UserCreate, UserLogin, User, Token, UserFeedbackHistory
)
from app.services.llm_service import generate_feedback
from app.services.ocr_service import process_image
from app.services.db_service import db
from app.services.auth_service import authenticate_user, create_access_token, get_current_user, register_user
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

# OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")

# Static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Dependency to get current user
async def get_current_active_user(token: str = Security(oauth2_scheme)) -> User:
    user = await get_current_user(token)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user

@app.get("/", include_in_schema=False)
async def serve_frontend():
    return FileResponse("app/static/index.html")

@app.get("/login", include_in_schema=False)
async def serve_login():
    return FileResponse("app/static/login.html")

@app.get("/register", include_in_schema=False)
async def serve_register():
    return FileResponse("app/static/register.html")

@app.get("/dashboard", include_in_schema=False)
async def serve_dashboard():
    return FileResponse("app/static/dashboard.html")

@app.on_event("startup")
async def startup_db_client():
    # Connect to MongoDB
    await db.connect_to_mongodb()
    
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

@app.on_event("shutdown")
async def shutdown_db_client():
    # Close MongoDB connection
    await db.close_mongodb_connection()

# Authentication routes
@app.post("/api/auth/register", response_model=User, tags=["Authentication"])
async def register(user_data: UserCreate):
    """Register a new user"""
    user = await register_user(user_data.email, user_data.password, user_data.student_name)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    return user

@app.post("/api/auth/login", response_model=Token, tags=["Authentication"])
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """Login and get access token"""
    user = await authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=60)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/api/auth/me", response_model=User, tags=["Authentication"])
async def get_user_profile(current_user: User = Depends(get_current_active_user)):
    """Get current user profile"""
    return current_user

# Feedback history route
@app.get("/api/feedback/history", response_model=UserFeedbackHistory, tags=["Feedback"])
async def get_feedback_history(current_user: User = Depends(get_current_active_user)):
    """Get feedback history for the current user"""
    feedback_list = await db.get_user_feedback_history(current_user.id)
    return UserFeedbackHistory(user_id=current_user.id, feedback_list=feedback_list)

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
async def submit_answer(
    submission: AnswerSubmission,
    current_user: User = Depends(get_current_active_user)
):
    """
    Submit a student answer for evaluation
    - Finds the question from our database
    - Sends to LLM for evaluation against model answer
    - Returns feedback with marks and explanations
    - Saves feedback to database for the authenticated user
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
    
    # Add user ID to feedback
    feedback.user_id = current_user.id
    feedback.created_at = datetime.utcnow()
    
    # Save feedback to database
    await db.save_feedback(feedback)
    
    return feedback

@app.post("/submit-image", response_model=OCRResponse)
async def submit_image(
    question_id: str = Form(...),
    image: UploadFile = File(...),
    grade: Optional[bool] = Form(False),
    current_user: User = Depends(get_current_active_user)
):
    """
    Submit an image of a handwritten answer for OCR processing and optional grading
    - Extracts text from the image using OCR
    - Optionally grades the extracted text using the LLM
    - Returns the extracted text and optional feedback
    - Saves feedback to database for the authenticated user if grading is requested
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
    
    # If grading was requested and feedback is available, save it to the database
    if grade and ocr_response.feedback:
        # Add user ID to feedback
        ocr_response.feedback.user_id = current_user.id
        ocr_response.feedback.created_at = datetime.utcnow()
        
        # Save feedback to database
        await db.save_feedback(ocr_response.feedback)
    
    return ocr_response
