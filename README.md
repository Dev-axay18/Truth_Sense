# TruthSense - AI-Powered News Verification Platform

TruthSense is a futuristic web application that helps users verify the authenticity of news articles using AI technology. The platform provides comprehensive analysis of news content, including classification, confidence scores, and verification status.

## Features

- News analysis through headlines, full articles, or URLs
- AI-powered classification (True/Fake/Unverified)
- Confidence scoring
- Country of origin detection
- Verification status
- History tracking
- Modern, responsive UI with futuristic design

## Tech Stack

### Frontend
- React
- Tailwind CSS
- Axios for API calls
- React Toastify for notifications

### Backend
- FastAPI (Python)
- OpenAI API for analysis
- SQLite for data storage

## Setup Instructions

### Prerequisites
- Node.js (v14 or higher)
- Python 3.8 or higher
- OpenAI API key

### Backend Setup
1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file in the backend directory:
   ```
   OPENAI_API_KEY=your_api_key_here
   ```

5. Start the backend server:
   ```bash
   uvicorn main:app --reload
   ```

### Frontend Setup
1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the development server:
   ```bash
   npm start
   ```

The application will be available at `http://localhost:3000`

## Usage

1. Open the application in your web browser
2. Choose your input method (Headline, Article, or URL)
3. Enter your news content
4. Click "Analyze News" to get results
5. View the detailed analysis including classification, confidence score, and verification status

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details. 