import json
import os
from openai import AsyncOpenAI
from dotenv import load_dotenv
from typing import List, Dict, Any
import uuid
from datetime import datetime
from fastapi import HTTPException

from app.models.schemas import SyllabusQuestion

# Load environment variables from .env file
load_dotenv()

# Initialize OpenAI async client
client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

async def generate_syllabus_questions(
    subject: str,
    syllabus_text: str,
    question_count: int
) -> List[SyllabusQuestion]:
    """Generate questions from a syllabus using OpenAI."""
    
    try:
        # Ensure we have valid input
        if not syllabus_text or len(syllabus_text.strip()) < 50:
            raise ValueError("Syllabus text is too short. Please provide more detailed content.")
        
        if question_count < 1 or question_count > 20:
            question_count = min(max(question_count, 1), 20)  # Clamp between 1 and 20
        # Call OpenAI API with JSON mode
        response = await client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are an expert educator and question creator. Always provide responses in valid JSON format."},
                {"role": "user", "content": f"""You are an expert educator for {subject}.

SYLLABUS CONTENT:
{syllabus_text}

Your task is to create {question_count} high-quality exam questions based on this syllabus.
For each question:
1. Identify an important topic from the syllabus
2. Create a challenging but fair question
3. Provide a comprehensive model answer of the question
4. Create a detailed marking scheme with specific criteria
5. Assign appropriate maximum marks (between 3-5)

Respond with a JSON object containing an array of questions with this structure:
{{
  "questions": [
    {{
      "question_id": "<unique_id>",
      "topic": "<topic_name>",
      "question": "<question_text>",
      "max_marks": <int: maximum marks>,
      "marking_scheme": {{
        "<criterion1>": <int: marks>,
        "<criterion2>": <int: marks>,
        ...
      }},
      "model_answer": "<comprehensive_answer of question>"
    }},
    ...
  ]
}}

Make sure:
- Each question has a unique ID (format: "SQ1", "SQ2", etc. where SQ stands for Syllabus Question)
- The marking scheme criteria are specific and clear
- All values in the marking scheme MUST be integers (whole numbers only, no decimals or fractions)
- The total marks in the marking scheme add up to the max_marks value
- The model answer is comprehensive and would score full marks
- Questions cover different topics from the syllabus
"""}
            ],
            temperature=0.7,
            max_tokens=8000,
            response_format={"type": "json_object"}  # Enable JSON mode
        )
        
        # Get the raw response content
        raw_content = response.choices[0].message.content
        print(f"Raw LLM response: {raw_content}")
        
        # Parse the JSON response
        result_json = json.loads(raw_content)
        
        # Print the parsed JSON for debugging
        print(f"Parsed JSON type: {type(result_json)}")
        print(f"Parsed JSON keys: {result_json.keys() if isinstance(result_json, dict) else 'Not a dict'}")
        
        # Check if the result is a list or has a 'questions' key or is a single question
        if isinstance(result_json, list):
            print("Result is a list")
            result_list = result_json
        elif isinstance(result_json, dict) and 'questions' in result_json:
            print("Result is a dict with 'questions' key")
            result_list = result_json['questions']
        elif isinstance(result_json, dict) and 'question_id' in result_json and 'topic' in result_json:
            print("Result is a single question object")
            # Handle case where API returns a single question object
            result_list = [result_json]
        else:
            # Handle unexpected response format
            print(f"Unexpected response format: {result_json}")
            raise ValueError(f"Unexpected response format from OpenAI API: {type(result_json)}")
            
        # Validate the result has at least one question
        if not result_list or len(result_list) == 0:
            raise ValueError("No questions were generated. Please try again with more detailed syllabus content.")
        
        # Convert to SyllabusQuestion objects
        questions = []
        for item in result_list:
            # Ensure marking scheme values are integers
            marking_scheme = {}
            for criterion, mark in item["marking_scheme"].items():
                # Convert any float values to integers
                marking_scheme[criterion] = int(mark)
            
            questions.append(
                SyllabusQuestion(
                    question_id=item["question_id"],
                    topic=item["topic"],
                    question=item["question"],
                    max_marks=item["max_marks"],
                    marking_scheme=marking_scheme,
                    model_answer=item["model_answer"]
                )
            )
        
        return questions
        
    except ValueError as e:
        print(f"Validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except json.JSONDecodeError as e:
        print(f"JSON parsing error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to parse LLM response: {str(e)}")
    except Exception as e:
        print(f"Error generating questions: {e}")
        raise HTTPException(status_code=500, detail=f"Error generating questions: {str(e)}")
