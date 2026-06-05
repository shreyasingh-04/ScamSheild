# ScamShield AI - System Architecture

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         SCAMSHIELD AI SYSTEM                                │
└─────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────┐    HTTP/REST     ┌──────────────────────────────────┐
│                      │◄────────────────►│                                  │
│   ANDROID APP        │                  │   FASTAPI BACKEND                │
│   (Kotlin/Compose)   │    WebSocket     │   (Python 3.11+)                 │
│                      │◄────────────────►│                                  │
│  ┌─────────────────┐ │                  │  ┌────────────────────────────┐  │
│  │ HomeScreen      │ │                  │  │ API Routers                │  │
│  │ AnalyzeScreen   │ │                  │  │  /api/v1/analyze/text      │  │
│  │ ChatbotScreen   │ │                  │  │  /api/v1/analyze/url       │  │
│  │ DashboardScreen │ │                  │  │  /api/v1/analyze/email     │  │
│  │ ReportScreen    │ │                  │  │  /api/v1/analyze/voice     │  │
│  │ HistoryScreen   │ │                  │  │  /api/v1/chatbot/ask       │  │
│  └─────────────────┘ │                  │  │  /api/v1/report/scam       │  │
│                      │                  │  │  /api/v1/dashboard/stats   │  │
│  ┌─────────────────┐ │                  │  │  /ws/alerts (WebSocket)    │  │
│  │ ViewModels      │ │                  │  └────────────────────────────┘  │
│  │ Repository      │ │                  │                                  │
│  │ Retrofit API    │ │                  │  ┌────────────────────────────┐  │
│  └─────────────────┘ │                  │  │ ML Pipeline                │  │
│                      │                  │  │  TextAnalyzer              │  │
│  ┌─────────────────┐ │                  │  │   └─ TF-IDF + Ensemble     │  │
│  │ Firebase FCM    │ │                  │  │  UrlAnalyzer               │  │
│  │ Push Alerts     │ │                  │  │   └─ RandomForest          │  │
│  └─────────────────┘ │                  │  │  VoiceAnalyzer             │  │
│                      │                  │  │   └─ Pattern Matching      │  │
└──────────────────────┘                  │  │  RiskScorer                │  │
                                          │  │   └─ Weighted Composite    │  │
                                          │  └────────────────────────────┘  │
                                          │                                  │
                                          │  ┌────────────────────────────┐  │
                                          │  │ External Services          │  │
                                          │  │  OpenAI GPT-4o-mini        │  │
                                          │  │  Google Speech-to-Text     │  │
                                          │  │  Firebase Firestore        │  │
                                          │  └────────────────────────────┘  │
                                          └──────────────────────────────────┘
                                                          │
                                          ┌───────────────▼─────────────────┐
                                          │       FIREBASE FIRESTORE         │
                                          │                                  │
                                          │  Collections:                    │
                                          │  • analysis_history              │
                                          │  • crowd_reports                 │
                                          │  • scam_alerts                   │
                                          │  • user_stats                    │
                                          └──────────────────────────────────┘
```

## ML Pipeline Architecture

```
User Input (Text/URL/Voice/Email)
         │
         ▼
┌─────────────────────────────────────┐
│         PREPROCESSING               │
│  • Text cleaning & normalization    │
│  • Feature extraction               │
│  • Pattern matching                 │
└─────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────┐
│      ML MODEL ENSEMBLE              │
│                                     │
│  Text:  ┌─────────────────────┐     │
│         │ TF-IDF Vectorizer   │     │
│         │ (ngram 1-3)         │     │
│         └──────────┬──────────┘     │
│                    ▼                │
│         ┌──────────────────────┐    │
│         │ Voting Ensemble      │    │
│         │ LR + RF + GBoost    │    │
│         └──────────────────────┘    │
│                                     │
│  URL:   ┌─────────────────────┐     │
│         │ 15 Numerical        │     │
│         │ Features            │     │
│         └──────────┬──────────┘     │
│                    ▼                │
│         ┌──────────────────────┐    │
│         │ Random Forest        │    │
│         │ (200 estimators)     │    │
│         └──────────────────────┘    │
│                                     │
│  Voice: Pattern + Keyword Matching  │
└─────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────┐
│       RULE-BASED BOOSTING           │
│  • Keyword category scoring         │
│  • Urgency indicator detection      │
│  • Behavioral anomaly analysis      │
│  • Crowd database lookup            │
└─────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────┐
│       COMPOSITE RISK SCORE          │
│  Text Analysis    × 35%            │
│  URL Analysis     × 30%            │
│  Voice Analysis   × 20%            │
│  Behavioral       × 15%            │
│  Sender History   + modifier       │
└─────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────┐
│   EXPLAINABLE AI OUTPUT             │
│  • Risk Score (0-100)               │
│  • Risk Level (SAFE/LOW/MEDIUM/     │
│                HIGH/CRITICAL)       │
│  • Scam Type Classification         │
│  • Keyword Highlights               │
│  • Detailed Explanation             │
│  • Recommendations                  │
└─────────────────────────────────────┘
```

## Data Flow

```
1. User pastes suspicious content in Android app
2. App sends POST request to FastAPI backend
3. Backend preprocesses input
4. ML models analyze content in parallel
5. Rule-based engine boosts/adjusts ML scores  
6. Crowd database checked for known threats
7. Composite risk score calculated
8. XAI explanation generated
9. Result returned to app in <500ms
10. Real-time alert sent via WebSocket if critical
11. Analysis saved to Firebase Firestore
12. Dashboard statistics updated
```

## Security Architecture

```
┌─────────────────────────────────────┐
│           SECURITY LAYERS           │
│                                     │
│  1. Input Validation (Pydantic)     │
│  2. Rate Limiting (per endpoint)    │
│  3. CORS Configuration              │
│  4. HTTPS in Production             │
│  5. Firebase Auth (optional)        │
│  6. API Key Management              │
└─────────────────────────────────────┘
```
