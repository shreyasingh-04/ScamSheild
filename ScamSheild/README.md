# 🛡️ ScamShield AI — Intelligent Scam Detection System

> Production-grade, real-time scam detection across SMS, Email, Voice Calls & URLs  
> Powered by Machine Learning, Explainable AI, and Crowd-Sourced Intelligence

---

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Quick Start (VS Code)](#quick-start-vscode)
- [Backend Setup](#backend-setup)
- [Android App Setup](#android-app-setup)
- [ML Model Training](#ml-model-training)
- [API Documentation](#api-documentation)
- [Running Tests](#running-tests)
- [Environment Variables](#environment-variables)
- [Architecture](#architecture)
- [Contributing](#contributing)

---

## 🎯 Overview

ScamShield AI is a full-stack intelligent scam detection system that analyzes:
- 📱 **SMS / Text Messages** — Detects phishing, fraud, and social engineering
- 📧 **Emails** — Identifies sender spoofing, malicious links, and suspicious content
- 🔊 **Voice Calls** — Analyzes transcripts for IRS scams, robocalls, and threats
- 🌐 **URLs** — Detects phishing sites, brand spoofing, and malicious domains

The system uses an ensemble of ML models combined with rule-based analysis to achieve high accuracy with full explainability.

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🤖 ML Text Classification | TF-IDF + Gradient Boosting + Random Forest ensemble |
| 🌐 URL Phishing Detection | 15-feature URL analysis with RandomForest |
| 🎙️ Voice Scam Detection | Pattern matching on call transcripts |
| 📊 Risk Scoring | Composite 0-100 risk score with breakdown |
| 💬 AI Chatbot | GPT-4o-mini powered assistant (rule-based fallback) |
| 🧠 Explainable AI | Plain-English explanations for every verdict |
| 👥 Crowd Database | Community-reported scam numbers/URLs |
| 📡 Real-Time Alerts | WebSocket push notifications |
| 📈 Analytics Dashboard | Charts, trends, and statistics |
| 🔔 Push Notifications | Firebase Cloud Messaging alerts |

---

## 🛠️ Tech Stack

### Backend
- **FastAPI** (0.115+) — High-performance async REST API
- **Scikit-learn** (1.5+) — ML models (TF-IDF, Random Forest, Gradient Boosting)
- **Firebase Admin SDK** (6.6+) — Firestore database (optional)
- **WebSockets** — Real-time alerts
- **OpenAI API** — Enhanced chatbot (optional)

### Android App
- **Kotlin** + **Jetpack Compose** — Modern declarative UI
- **Hilt** — Dependency injection
- **Retrofit** + **OkHttp** — HTTP client
- **Firebase** — Authentication, Firestore, FCM
- **Navigation Compose** — In-app navigation

### ML Pipeline
- TF-IDF Vectorizer (ngram 1-3, 8000 features)
- Voting Ensemble: Logistic Regression + Random Forest + Gradient Boosting
- URL Feature Extractor (15 numerical features)
- Pattern-based Voice Analyzer

---

## 📁 Project Structure

```
scam-detection-system/
├── backend/                    # FastAPI Python backend
│   ├── app/
│   │   ├── main.py            # Application entry point
│   │   ├── api/               # API route handlers
│   │   │   ├── analyze.py     # Text/URL/Email/Voice endpoints
│   │   │   ├── chatbot.py     # AI chatbot endpoint
│   │   │   ├── dashboard.py   # Analytics endpoints
│   │   │   ├── report.py      # Crowd-report endpoints
│   │   │   └── websocket_manager.py
│   │   ├── ml/                # Machine learning modules
│   │   │   ├── model_loader.py   # Model training & loading
│   │   │   ├── text_analyzer.py  # Text scam detection
│   │   │   ├── url_analyzer.py   # URL safety analysis
│   │   │   └── voice_analyzer.py # Voice transcript analysis
│   │   ├── services/
│   │   │   └── risk_scorer.py    # Composite risk scoring
│   │   └── utils/
│   │       └── firebase.py       # Firebase/in-memory DB
│   ├── tests/
│   │   └── test_scam_detection.py  # Full test suite
│   ├── requirements.txt
│   └── .env.example
│
├── android/                    # Kotlin Android app
│   ├── app/src/main/java/com/scamdetector/
│   │   ├── MainActivity.kt
│   │   ├── ScamShieldApplication.kt
│   │   ├── ui/
│   │   │   ├── screens/       # All app screens
│   │   │   ├── components/    # Reusable UI components
│   │   │   ├── navigation/    # Nav graph
│   │   │   ├── theme/         # Colors, typography
│   │   │   └── viewmodel/     # ViewModels
│   │   ├── data/
│   │   │   ├── remote/        # API service & models
│   │   │   └── repository/    # Data repository
│   │   ├── di/                # Hilt DI modules
│   │   └── utils/             # FCM service
│   └── app/build.gradle
│
├── ml_models/
│   ├── datasets/
│   │   └── scam_dataset.csv   # Training data
│   └── train_models.py        # Model training script
│
└── docs/
    └── ARCHITECTURE.md        # System architecture
```

---

## 🚀 Quick Start (VS Code)

### Prerequisites

| Tool | Version | Download |
|------|---------|----------|
| Python | 3.11 or 3.12 | [python.org](https://python.org) |
| uv | latest | [github.com/astral-sh/uv](https://github.com/astral-sh/uv) |
| Git | any | [git-scm.com](https://git-scm.com) |
| Android Studio | Hedgehog+ | [developer.android.com](https://developer.android.com/studio) |
| VS Code | latest | [code.visualstudio.com](https://code.visualstudio.com) |

### Step 1 — Clone / Extract the Project

```bash
# If from zip:
unzip scam-detection-system.zip
cd scam-detection-system

# Open in VS Code:
code .
```

## 🚀 Quick Start (Future Runs)

Once set up, here's how to run ScamShield AI:

### Backend Only
```bash
cd scam-detection-system/backend
venv\Scripts\activate
python -m app.main
```
Server starts at: **http://localhost:8000**

### With Android App
1. **Start Backend** (as above)
2. **Open Android Studio** → Open `android/` folder
3. **Run Emulator** → Click ▶️ Run button

### Run Tests
```bash
cd scam-detection-system/backend
venv\Scripts\activate
pytest tests/ -v
```

### Retrain ML Models
```bash
cd scam-detection-system/ml_models
python train_models.py
```

### API Testing
```bash
# Health check
curl http://localhost:8000/health

# Test scam analysis
curl "http://localhost:8000/api/v1/analyze/text?text=URGENT:+Your+account+is+suspended&message_type=sms"
```

---

## 🔄 Full Setup (First Time Only)

## 🐍 Backend Setup

### 1. Create & Activate Virtual Environment

```bash
cd backend

# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 1.5 Install uv (Optional but Recommended)

uv is a fast, reliable Python package installer that handles dependencies better than pip.

```bash
# Windows PowerShell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. Install Dependencies

```bash
# Using uv (recommended - fast and reliable)
uv pip install -r requirements.txt

# OR using pip
pip install -r requirements.txt
```

### 3. Configure Environment

```bash
# Copy the example env file
cp .env.example .env

# Edit .env with your values (optional — system works without API keys)
# The system uses in-memory storage if Firebase is not configured
# The chatbot uses rule-based logic if OpenAI key is not set
```

### 4. Start the Backend Server

```bash
# From the backend/ directory
python -m app.main

# OR with uvicorn directly:
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

✅ Server starts at: **http://localhost:8000**  
📚 API Docs at: **http://localhost:8000/docs**  
📖 ReDoc at: **http://localhost:8000/redoc**

> **Note:** On first startup, ML models will be trained automatically (~30 seconds). Subsequent starts load cached models instantly.

### 5. Verify Backend is Running

```bash
curl http://localhost:8000/health
# Expected: {"status":"healthy","message":"ScamShield AI is running"}
```

---

## 📱 Android App Setup

### Prerequisites
- Android Studio installed
- Android SDK 26+ (API level 26)
- Java 17

### 1. Open in Android Studio

```
File → Open → select scam-detection-system/android/
```

Wait for Gradle sync to complete (~2-3 minutes first time).

### 2. Configure Backend URL

The app connects to `http://10.0.2.2:8000` by default (Android Emulator's localhost).

If using a physical device, update `BuildConfig.BASE_URL` in `build.gradle`:
```groovy
buildConfigField "String", "BASE_URL", '"http://YOUR_COMPUTER_IP:8000"'
```

Find your computer IP: `ipconfig` (Windows) / `ifconfig` (Mac/Linux)

### 3. Firebase Setup (Optional)

1. Go to [console.firebase.google.com](https://console.firebase.google.com)
2. Create project "ScamShield"
3. Add Android app with package name `com.scamdetector`
4. Download `google-services.json`
5. Place in `android/app/google-services.json`

> Without Firebase, the app still works — data is stored in-memory on the backend.

### 4. Run the App

1. Create/start an Android Virtual Device (AVD) in Android Studio
2. Click ▶️ Run button
3. Select your emulator/device

---

## 🧠 ML Model Training

Train models on your own dataset:

```bash
cd ml_models

# Install dependencies
uv pip install scikit-learn pandas numpy joblib

# Run training script
python train_models.py
```

The trained models are saved to `ml_models/saved_models/` and automatically used by the backend.

**Dataset format** (`datasets/scam_dataset.csv`):
```csv
text,label,scam_type
"Your account is suspended click here",1,Phishing
"Meeting tomorrow at 3pm",0,
```

---

## 🔌 API Documentation

### Analyze Text/SMS
```http
POST /api/v1/analyze/text
Content-Type: application/json

{
  "text": "URGENT: Your account is suspended...",
  "message_type": "sms",
  "is_unknown_sender": true
}
```

**Response:**
```json
{
  "is_scam": true,
  "confidence": 89.5,
  "risk_score": 78.2,
  "risk_level": "HIGH",
  "scam_type": "Phishing Attack",
  "explanation": ["Urgency language detected", "Suspicious keywords found"],
  "recommendation": "Do NOT engage. Block this sender immediately."
}
```

### Analyze URL
```http
POST /api/v1/analyze/url
Content-Type: application/json

{ "url": "http://paypa1-secure.tk/verify" }
```

### Analyze Email
```http
POST /api/v1/analyze/email
Content-Type: application/json

{
  "subject": "URGENT: Verify your PayPal account",
  "body": "Click here to verify...",
  "sender_email": "support@paypa1.com"
}
```

### Analyze Voice Transcript
```http
POST /api/v1/analyze/voice
Content-Type: application/json

{
  "transcript": "This is the IRS, you owe taxes...",
  "caller_id": "+1-800-555-0000"
}
```

### AI Chatbot
```http
POST /api/v1/chatbot/ask
Content-Type: application/json

{ "message": "Is this message safe? You won a million dollars!" }
```

### Report a Scam
```http
POST /api/v1/report/scam
Content-Type: application/json

{
  "report_type": "phone",
  "phone_number": "1-800-SCAM",
  "description": "IRS scam demanding gift cards",
  "scam_type": "Government Impersonation"
}
```

### WebSocket Alerts
```
ws://localhost:8000/ws/alerts
```

---

## 🧪 Running Tests

```bash
cd backend

# Activate virtual environment first
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ -v --tb=short

# Run specific test class
pytest tests/test_scam_detection.py::TestApiEndpoints -v
pytest tests/test_scam_detection.py::TestTextAnalysis -v
pytest tests/test_scam_detection.py::TestUrlAnalysis -v
```

Expected output: **35+ tests passing** ✅

---

## 🔐 Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `OPENAI_API_KEY` | Optional | GPT-4o-mini for enhanced chatbot |
| `FIREBASE_CREDENTIALS_PATH` | Optional | Path to Firebase service account JSON |
| `FIREBASE_PROJECT_ID` | Optional | Firebase project ID |
| `GOOGLE_APPLICATION_CREDENTIALS` | Optional | Google STT credentials |
| `HOST` | No | Server host (default: 0.0.0.0) |
| `PORT` | No | Server port (default: 8000) |
| `SECRET_KEY` | No | JWT secret for auth (if enabled) |

> **The system works fully without any API keys** using in-memory storage and rule-based chatbot.

---

## 🏗️ Architecture

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for full system diagrams.

**Key design decisions:**
- **Hybrid ML + Rules**: ML models handle learned patterns; rules catch known scam keywords
- **Composite scoring**: Multiple analysis sources weighted by reliability
- **Graceful degradation**: Firebase/OpenAI optional; system works without them
- **XAI first**: Every verdict includes human-readable explanations

## 🚀 Deployment Guide

### Backend Deployment

#### Option 1: Railway (Recommended - Free tier available)
1. **Create Railway account**: https://railway.app
2. **Connect GitHub repo**
3. **Deploy**:
   ```bash
   # Railway auto-detects Python apps
   # Set environment variables in Railway dashboard
   ```
4. **Database**: Use Railway's PostgreSQL or keep in-memory

#### Option 2: Render
1. **Create Render account**: https://render.com
2. **New Web Service** from GitHub
3. **Build Command**: `pip install -r requirements.txt`
4. **Start Command**: `python -m app.main`

#### Option 3: Docker Deployment
```dockerfile
# Dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["python", "-m", "app.main"]
```

```bash
# Build and run
docker build -t scamshield .
docker run -p 8000:8000 scamshield
```

#### Option 4: Heroku
```yaml
# Procfile
web: python -m app.main
```

### Android App Deployment

#### Google Play Store
1. **Build Release APK**:
   - In Android Studio: Build → Generate Signed Bundle/APK
   - Create signing key
   - Build release APK

2. **Create Play Console Account**: https://play.google.com/console
3. **Upload APK**:
   - Create app listing
   - Upload APK
   - Add screenshots, descriptions
   - Set pricing (free)
   - Publish

#### Alternative: Direct APK Distribution
- Host APK on website/GitHub Releases
- Users download and install manually

### Environment Variables for Production

```bash
# Required
HOST=0.0.0.0
PORT=8000

# Optional
OPENAI_API_KEY=your_key_here
FIREBASE_PROJECT_ID=your_project
FIREBASE_CREDENTIALS_PATH=/path/to/credentials.json
```

### Production Checklist

- [ ] Update `BASE_URL` in Android app to production backend URL
- [ ] Enable HTTPS
- [ ] Set up monitoring/logging
- [ ] Configure database (Firebase/Supabase)
- [ ] Set up CI/CD pipeline
- [ ] Add rate limiting
- [ ] Security audit

---

## 🔮 Future Enhancements

- [ ] Deepfake voice detection (ElevenLabs / Resemble AI)
- [ ] Browser extension for URL checking
- [ ] WhatsApp Business API integration
- [ ] BERT/transformer-based text classification
- [ ] Multi-language support
- [ ] Federated learning for privacy-preserving model updates

---

## 📄 License

MIT License — free to use for educational and commercial projects.

---

## 🙏 Acknowledgments

Built with FastAPI, Scikit-learn, Jetpack Compose, and Firebase.

**Stay safe. When in doubt, don't.** 🛡️
