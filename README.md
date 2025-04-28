# AI Exam Marking System

An automated system for marking exam answers using AI, with support for both text input and handwritten answers through OCR.

## Features

- **AI-Powered Grading**: Uses OpenAI's GPT models to grade student answers against model answers
- **Handwriting Recognition**: Extracts text from images of handwritten answers using Google Vision API
- **Detailed Feedback**: Provides comprehensive feedback with specific marking points
- **User-Friendly Interface**: Clean, responsive web interface for submitting answers and viewing feedback
- **Question Management**: Loads questions from a JSON file for easy management
- **Syllabus Question Generation**: Generate custom questions from syllabus content

## Approach and Tools Used

- **Microservices Architecture**: Modular services for authentication, database, LLM, OCR, and syllabus processing
- **FastAPI Backend**: High-performance asynchronous API framework
- **MongoDB Database**: Flexible document storage for users, feedback, and questions
- **JWT Authentication**: Secure token-based authentication system
- **OpenAI GPT-4o**: Advanced language model for generating feedback and questions
- **Google Vision API**: Cloud-based OCR for handwritten text recognition
- **Responsive Frontend**: Pure HTML/CSS/JS implementation with Tailwind CSS

## Prompt Design Strategy

- **Structured JSON Outputs**: All LLM prompts are designed to return structured JSON for consistent parsing
- **Detailed Instructions**: Prompts include specific criteria for evaluation and formatting
- **System Role Definition**: Each prompt begins with a clear system role (e.g., "expert educator", "exam marker")
- **Temperature Control**: Lower temperature (0.3) for feedback generation to ensure consistency, higher (0.7) for creative question generation
- **Marking Scheme Integration**: Prompts include the marking scheme to ensure fair and consistent grading
- **Model Answer Comparison**: Student answers are evaluated against comprehensive model answers

## Assumptions and Limitations

- **OCR Limitations**: While we use Google Vision API, OCR technology still faces challenges with handwritten text:
  - **Noise Detection**: Extra lines, paper background, or wrinkles can be incorrectly detected as text
  - **Character Confusion**: Handwritten letters with unusual shapes may be misinterpreted
  - **Tesseract Alternative**: We initially tested with Tesseract OCR but found its accuracy insufficient for handwritten text
  - **Handwriting Variability**: Different handwriting styles significantly impact recognition accuracy
  - **Image Quality Dependency**: Results heavily depend on image resolution, lighting, and contrast

- **LLM Limitations**:
  - **Token Limits**: Long answers may be truncated due to model context limits
  - **Subject Expertise**: Model may have varying levels of expertise across different academic subjects
  - **Marking Consistency**: May not always match human marker consistency across similar answers

- **System Assumptions**:
  - Questions and model answers are pre-defined and well-structured
  - Users have stable internet connections for API calls
  - Syllabus content is provided in a clear, structured format

## Setup

### Prerequisites

- Python 3.8+
- Google Cloud account with Vision API enabled
- OpenAI API key
- MongoDB database (local or Atlas)

### Installation

1. Clone the repository:
   ```
   git clone <repository-url>
   cd <repository-directory>
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   Create a `.env` file in the root directory with the following:
   ```
   OPENAI_API_KEY=your_openai_api_key
   MONGODB_URI=your_mongodb_connection_string
   SECRET_KEY=your_jwt_secret_key
   ```

4. Set up Google Cloud credentials:
   - Place your Google Cloud service account JSON file in a secure location
   - Update the path in `app/services/ocr_service.py` to point to your credentials file:
     ```python
     os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "path/to/your/credentials.json"
     ```

5. Prepare your questions:
   - Edit the `questions.json` file to include your own questions, model answers, and marking schemes

### Running the Application

1. Start the server:
   ```
   uvicorn app.main:app --reload
   ```

2. Open your browser and navigate to:
   ```
   http://127.0.0.1:8000
   ```

## Usage

### Text Submission

1. Select the "Text Answer" tab
2. Choose a question from the dropdown
3. Type your answer in the text area
4. Click "Submit for Marking"
5. View your feedback and marks

### Image Submission (Handwritten Answers)

1. Select the "Image Upload" tab
2. Choose a question from the dropdown
3. Upload an image of your handwritten answer
4. Optionally check "Grade extracted text" to receive feedback
5. Click "Upload and Process"
6. View the extracted text and optional feedback

### Syllabus Question Generation

1. Navigate to the Syllabus Upload page
2. Enter your subject name and desired number of questions
3. Upload a syllabus file or paste syllabus text
4. Submit to generate questions
5. Review and save the generated questions

## API Endpoints

- `GET /questions`: Get all available questions
- `GET /questions/{question_id}`: Get a specific question by ID
- `POST /submit-answer`: Submit a text answer for grading
- `POST /submit-image`: Submit an image for OCR and optional grading
- `POST /api/syllabus/generate-questions`: Generate questions from syllabus content

## Technologies Used

- **Backend**: FastAPI, Python
- **Frontend**: HTML, CSS (Tailwind CSS), JavaScript
- **AI Services**: OpenAI API, Google Cloud Vision API
- **Database**: MongoDB with Motor async driver
- **Authentication**: JWT, Passlib
- **Other**: Pydantic, JSON

## License

[MIT License](LICENSE)
