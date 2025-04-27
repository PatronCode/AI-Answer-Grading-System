import json
import os
from openai import AsyncOpenAI
from dotenv import load_dotenv
from app.models.schemas import FeedbackResponse, MarkingPoint

# Load environment variables from .env file
load_dotenv()

# Initialize OpenAI async client
client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

async def generate_feedback(
    question_text: str,
    student_answer: str,
    model_answer: str,
    marking_scheme: dict,
    max_marks: int,
    topic: str
) -> FeedbackResponse:
    """Generate feedback on a student answer using OpenAI."""
    
    try:
        # Call OpenAI API with JSON mode
        response = await client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are an expert exam marker. Always provide responses in valid JSON format."},
                {"role": "user", "content": f"""You are an expert exam marker for {topic}.

QUESTION:
{question_text}

STUDENT ANSWER:
{student_answer}

MODEL ANSWER:
{model_answer}

MARKING SCHEME (Total: {max_marks} marks):
{json.dumps(marking_scheme, indent=2)}

Your task is to mark the student answer according to the marking scheme.
For each marking criterion:
1. Determine how many marks to award
2. Provide specific feedback
3. If marks were deducted, explain exactly why

Respond with a JSON object with this structure:
{{
  "total_marks_awarded": <int: total marks awarded>,
  "overall_feedback": <string: overall assessment>,
  "detailed_marking": [
    {{
      "criterion": <string: marking criterion>,
      "max_mark": <int: maximum mark>,
      "awarded_mark": <int: awarded mark>,
      "feedback": <string: specific feedback>,
      "explanation": <string: explanation for any deductions>
    }},
    ...
  ]
}}
"""}
            ],
            temperature=0.3,
            max_tokens=1500,
            response_format={"type": "json_object"}  # Enable JSON mode
        )
        
        # Parse the JSON response directly from the new API structure
        result_dict = json.loads(response.choices[0].message.content)
        
        # Create marking points
        detailed_marking = []
        for item in result_dict["detailed_marking"]:
            detailed_marking.append(
                MarkingPoint(
                    criterion=item["criterion"],
                    max_mark=item["max_mark"],
                    awarded_mark=item["awarded_mark"],
                    feedback=item["feedback"],
                    explanation=item["explanation"]
                )
            )
        
        # Return feedback response
        return FeedbackResponse(
            question_id=question_text.split()[0] if ' ' in question_text else "Q",
            total_marks_available=max_marks,
            total_marks_awarded=result_dict["total_marks_awarded"],
            overall_feedback=result_dict["overall_feedback"],
            detailed_marking=detailed_marking
        )
        
    except Exception as e:
        print(f"Error generating feedback: {e}")
        return FeedbackResponse(
            question_id="error",
            total_marks_available=max_marks,
            total_marks_awarded=0,
            overall_feedback=f"Error generating feedback: {str(e)}",
            detailed_marking=[]
        )
