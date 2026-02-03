# FACTLY - AI-Powered News Credibility Verification Platform

## 📋 Project Overview

FACTLY is a comprehensive AI-powered platform designed to verify the credibility of news headlines and articles through advanced fact-checking algorithms and multiple external verification sources. The platform combines machine learning, natural language processing, and cross-referenced fact-checking APIs to provide users with a reliable "Factly Score™" that quantifies the trustworthiness of news content.

### 🎯 Key Features

- **Factly Score™ Algorithm**: Proprietary weighted scoring system combining NLP analysis, fact-check databases, and source credibility assessment
- **Multi-Source Verification**: Integrates with Google Fact Check API and NewsLdr for comprehensive claim verification
- **Real-time Analysis**: Instant credibility assessment with detailed evidence breakdown
- **Interactive Web Interface**: User-friendly React-based frontend for easy content verification
- **Advanced NLP Processing**: Text preprocessing, language detection, and bias analysis
- **Caching System**: Optimized performance with intelligent response caching
- **Modular Architecture**: Microservices-based design for scalability and maintainability

### 🏗️ Architecture Components

- **Frontend**: React.js web application with responsive UI components
- **Backend Services**:
  - Fact Checking Service: Orchestrates multiple verification APIs
  - Scoring Service: Implements the Factly Score™ algorithm
  - NLP Service: Text processing and analysis
- **External APIs**: Google Fact Check API, NewsLdr API
- **Caching**: Redis-compatible caching for API responses

## 🔧 System Requirements

### Minimum Requirements
- **Operating System**: Windows 10/11, macOS 10.15+, or Linux (Ubuntu 18.04+)
- **RAM**: 4GB minimum, 8GB recommended
- **Storage**: 2GB free space
- **Network**: Stable internet connection for API calls

### Backend Requirements
- **Python**: 3.8 or higher
- **Dependencies**: See `backend/requirements.txt`
- **API Keys**: Google Fact Check API key, NewsLdr API key (optional for basic functionality)

### Frontend Requirements
- **Node.js**: 16.x or higher
- **npm**: 7.x or higher

## 📦 Installation

### Backend Setup

1. **Navigate to backend directory**:
   ```bash
   cd backend
   ```

2. **Create virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Download NLTK data** (required for NLP processing):
   ```python
   import nltk
   nltk.download('punkt')
   nltk.download('stopwords')
   ```

### Frontend Setup

1. **Navigate to frontend directory**:
   ```bash
   cd frontend
   ```

2. **Install dependencies**:
   ```bash
   npm install
   ```

## ⚙️ Environment Setup

### API Keys Configuration

Create a `.env` file in the backend directory:

```env
# Google Fact Check API
GOOGLE_FACT_CHECK_API_KEY=your_google_api_key_here

# NewsLdr API (optional)
NEWSLDR_API_KEY=your_newsldr_api_key_here

# Application Settings
DEBUG=True
CACHE_TTL=3600
MAX_API_REQUESTS_PER_MINUTE=60
```

### Obtaining API Keys

1. **Google Fact Check API**:
   - Visit [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select existing one
   - Enable "Fact Check Tools API"
   - Create credentials (API Key)
   - Restrict the key to Fact Check API only

2. **NewsLdr API** (Optional):
   - Visit [NewsLdr](https://newsldr.com/) website
   - Sign up for an API account
   - Obtain your API key from the dashboard

## 🚀 Running the Application

### Development Mode

1. **Start Backend**:
   ```bash
   cd backend
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   python -m services.main  # Assuming main.py exists, adjust as needed
   ```

2. **Start Frontend** (in a new terminal):
   ```bash
   cd frontend
   npm start
   ```

3. **Access the application**:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:5000 (adjust port as configured)

### Production Deployment

1. **Backend Production Setup**:
   ```bash
   cd backend
   pip install gunicorn
   gunicorn --bind 0.0.0.0:8000 services.main:app
   ```

2. **Frontend Production Build**:
   ```bash
   cd frontend
   npm run build
   # Serve the build directory with a web server (nginx, Apache, etc.)
   ```

## 📚 API Documentation

### Base URL
```
http://localhost:5000/api/v1
```

### Endpoints

#### POST /verify
Verify the credibility of a news claim.

**Request Body**:
```json
{
  "claim": "The Earth is flat according to recent scientific studies.",
  "language": "en",
  "include_evidence": true
}
```

**Response**:
```json
{
  "factly_score": 15,
  "classification": "Likely Fake",
  "confidence_level": "High",
  "components": [
    {
      "name": "NLP Model Confidence",
      "score": 0.2,
      "weight": 0.4,
      "weighted_score": 0.08,
      "justification": "NLP model confidence: 0.20",
      "evidence": ["Direct NLP confidence score: 0.20"]
    }
  ],
  "justifications": [
    "Factly Score™ of 15/100 indicates likely fake credibility.",
    "NLP Model Confidence: NLP model confidence: 0.20"
  ],
  "evidence_summary": {
    "claim_reviews_count": 0,
    "related_news_count": 0,
    "source_reliability_available": false,
    "component_breakdown": {
      "NLP Model Confidence": {
        "score": 0.2,
        "weight": 0.4,
        "weighted_score": 0.08
      }
    },
    "api_sources_used": [],
    "overall_confidence": 0.0
  },
  "timestamp": "2024-01-29T10:00:00.000Z",
  "metadata": {
    "original_claim": "The Earth is flat according to recent scientific studies.",
    "api_sources": [],
    "processing_timestamp": "2024-01-29T10:00:00.000Z"
  }
}
```

**Sample cURL Request**:
```bash
curl -X POST http://localhost:5000/api/v1/verify \
  -H "Content-Type: application/json" \
  -d '{
    "claim": "COVID-19 vaccines contain microchips for tracking.",
    "language": "en",
    "include_evidence": true
  }'
```

#### GET /health
Check API health status.

**Response**:
```json
{
  "status": "healthy",
  "timestamp": "2024-01-29T10:00:00.000Z",
  "services": {
    "fact_checking": "operational",
    "nlp": "operational",
    "scoring": "operational"
  }
}
```

### Error Responses

**400 Bad Request**:
```json
{
  "error": "ValidationError",
  "message": "Claim text is required and cannot be empty",
  "timestamp": "2024-01-29T10:00:00.000Z"
}
```

**429 Too Many Requests**:
```json
{
  "error": "RateLimitExceeded",
  "message": "API rate limit exceeded. Please try again later.",
  "retry_after": 60
}
```

## 🏛️ Architecture Overview

### Service Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   React Frontend│    │  Backend API     │    │  External APIs  │
│                 │    │                  │    │                 │
│ • User Interface│◄──►│ • Fact Checking  │◄──►│ • Google Fact   │
│ • Score Display │    │ • Scoring        │    │   Check API     │
│ • Evidence Panel│    │ • NLP Processing │    │ • NewsLdr API   │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │   Caching Layer │
                       │   (Redis)       │
                       └─────────────────┘
```

### Component Descriptions

#### Fact Checking Service
- **Purpose**: Orchestrates fact-checking across multiple APIs
- **APIs Used**: Google Fact Check, NewsLdr
- **Output**: Unified verification results with confidence scores

#### Scoring Service
- **Purpose**: Implements Factly Score™ algorithm
- **Components**:
  - NLP Model Confidence (40% weight)
  - Google Fact Check Results (35% weight)
  - NewsLdr Source Credibility (15% weight)
  - Language Bias & Tone Analysis (10% weight)
- **Output**: 0-100 credibility score with classification

#### NLP Service
- **Purpose**: Text preprocessing and analysis
- **Features**: Language detection, tokenization, bias analysis
- **Libraries**: NLTK, langdetect, scikit-learn

#### Caching Manager
- **Purpose**: Performance optimization and rate limiting
- **Features**: TTL-based caching, API response storage
- **Backend**: Compatible with Redis or in-memory cache

## 🔧 Troubleshooting

### Common Issues

#### Backend Installation Issues

**Problem**: `ModuleNotFoundError` for transformers or torch
**Solution**:
```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
pip install transformers
```

**Problem**: NLTK data download fails
**Solution**:
```python
import nltk
nltk.download('punkt')
nltk.download('stopwords')
```

#### API Key Issues

**Problem**: Google Fact Check API returns 403 Forbidden
**Solution**:
- Verify API key is correct
- Ensure Fact Check Tools API is enabled in Google Cloud Console
- Check API key restrictions

**Problem**: Rate limiting errors
**Solution**:
- Implement exponential backoff
- Check API usage limits
- Consider upgrading API plans

#### Frontend Issues

**Problem**: npm install fails
**Solution**:
```bash
rm -rf node_modules package-lock.json
npm cache clean --force
npm install
```

**Problem**: CORS errors in development
**Solution**: Configure CORS in backend:
```python
from flask_cors import CORS
CORS(app)
```

### Performance Optimization

- **Enable Caching**: Ensure Redis is running for production caching
- **API Rate Limiting**: Implement request throttling
- **Database Indexing**: Add indexes for frequently queried fields
- **CDN**: Use CDN for static frontend assets

### Logging and Monitoring

- **Log Levels**: Set to DEBUG for development, INFO/WARN for production
- **Monitoring**: Implement health checks and metrics collection
- **Error Tracking**: Use services like Sentry for error monitoring

## 🤝 Contributing

We welcome contributions to FACTLY! Please follow these guidelines:

### Development Setup

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature-name`
3. Set up development environment following installation instructions
4. Make your changes
5. Run tests: `npm test` (frontend) and `python -m pytest` (backend)
6. Commit changes: `git commit -am 'Add new feature'`
7. Push to branch: `git push origin feature/your-feature-name`
8. Submit a Pull Request

### Code Standards

- **Python**: Follow PEP 8 style guidelines
- **JavaScript/React**: Use ESLint configuration
- **Documentation**: Update README and docstrings for new features
- **Testing**: Write unit tests for new functionality

### Commit Message Format

```
type(scope): description

[optional body]

[optional footer]
```

Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

### Reporting Issues

- Use GitHub Issues for bug reports and feature requests
- Include detailed steps to reproduce
- Provide system information and error logs
- Suggest potential solutions if possible

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

### MIT License Summary

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

---

**FACTLY** - Empowering users with AI-driven news credibility verification. Built with ❤️ for a more informed world.