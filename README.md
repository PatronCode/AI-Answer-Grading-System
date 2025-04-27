# AI Exam Marking System

An automated system for marking exam answers using AI, with support for both text input and handwritten answers through OCR.

## Features

- **AI-Powered Grading**: Uses OpenAI's GPT models to grade student answers against model answers
- **Handwriting Recognition**: Extracts text from images of handwritten answers using Google Vision API
- **Detailed Feedback**: Provides comprehensive feedback with specific marking points
- **User-Friendly Interface**: Clean, responsive web interface for submitting answers and viewing feedback
- **Question Management**: Loads questions from a JSON file for easy management

## Setup

### Prerequisites

- Python 3.8+
- Google Cloud account with Vision API enabled
- OpenAI API key

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

## API Endpoints

- `GET /questions`: Get all available questions
- `GET /questions/{question_id}`: Get a specific question by ID
- `POST /submit-answer`: Submit a text answer for grading
- `POST /submit-image`: Submit an image for OCR and optional grading

## Technologies Used

- **Backend**: FastAPI, Python
- **Frontend**: HTML, CSS (Tailwind CSS), JavaScript
- **AI Services**: OpenAI API, Google Cloud Vision API
- **Other**: Pydantic, JSON

## License

[MIT License](LICENSE)
