import logging
import pickle
import os
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import joblib

logger = logging.getLogger(__name__)

_models = {}
_vectorizers = {}

SAMPLE_SCAM_TEXTS = [
    "URGENT: Your account has been compromised. Click here immediately to verify: http://fake-bank.xyz",
    "Congratulations! You won $10,000. Send your bank details to claim your prize now!",
    "IRS FINAL NOTICE: You owe back taxes. Call immediately or face arrest: 1-800-FAKE-IRS",
    "Your package is on hold. Pay $2.99 customs fee at: http://phish-site.com/pay",
    "WINNER! You have been selected for FREE iPhone 15. Claim now: bit.ly/scam123",
    "Dear customer, your Netflix subscription expired. Update payment: netflix-secure-update.tk",
    "Hello, I am a Nigerian prince and I need your help transferring $50 million dollars",
    "Job offer: Work from home earn $5000/week no experience needed! Apply now!",
    "Your social security number has been suspended. Press 1 to speak with officer",
    "FREE gift card! You've been selected. Verify your identity to claim: survey-scam.com",
    "ALERT: Unusual activity detected on your bank account. Verify now to avoid suspension",
    "You have a pending lawsuit. Settle immediately or face legal action. Call us now!",
    "Crypto investment opportunity! 500% returns guaranteed in 30 days. Limited time!",
    "Your computer has virus! Call Microsoft support immediately: 1-888-FAKE-MS",
    "Romantic connection: I saw your profile and fell in love. Please send money for ticket",
    "Loan approved! Get $50,000 today. No credit check. Just pay $200 processing fee",
    "GOVERNMENT GRANT: You qualify for $9,000. Call to claim before it expires today!",
    "Your electric will be shut off in 2 hours unless you pay with gift cards immediately",
    "Amazon security alert: unauthorized purchase detected. Click to cancel: amaz0n-secure.net",
    "You owe customs tax on your package. Pay via Western Union to release it",
]

SAMPLE_SAFE_TEXTS = [
    "Hi! Just checking in to see how you're doing. Hope everything is well!",
    "Meeting tomorrow at 3pm in conference room B. Please bring the quarterly report.",
    "Your order has been shipped! Track it at amazon.com/orders with your order ID",
    "Reminder: Your dentist appointment is scheduled for Friday at 2:30 PM",
    "The weather looks great this weekend. Want to go hiking on Saturday?",
    "Your monthly bank statement is now available. Log in at your bank's official website",
    "Happy Birthday! Wishing you all the best on your special day!",
    "Please review the attached document and provide feedback by end of week",
    "Dinner reservation confirmed for 7pm at The Italian Place on Main Street",
    "Your prescription is ready for pickup at CVS pharmacy on Oak Avenue",
    "Team lunch tomorrow at noon. We'll be going to the new Thai restaurant",
    "Reminder: Please submit your timesheet by 5pm Friday for payroll processing",
    "Your flight AA1234 departs at 9:45am from Terminal B. Gate opens 1 hour before",
    "Library books due: 'Python Programming' and 'Data Science Handbook' - return by Friday",
    "Hi Mom, just wanted to let you know I arrived safely. Will call tonight!",
    "Quarterly taxes due next month. Remember to gather your documents",
    "New software update available for your device. Update when convenient",
    "Can you pick up milk and eggs on your way home? Thanks!",
    "Your gym membership renewal is coming up. Renew at the front desk or online",
    "School play is this Friday at 6pm. Parking available behind the auditorium",
]

SAMPLE_SCAM_URLS = [
    "http://paypa1-secure.com/verify",
    "https://amaz0n-login.xyz/account",
    "http://bank-secure-verify.tk/login",
    "https://netflix-payment-update.ml/billing",
    "http://irs-tax-refund.club/claim",
    "https://microsoft-support-helpdesk.com/virus-removal",
    "http://bit.ly/freegift2024win",
    "https://gov-grant-9000.top/apply",
    "http://crypto-500percent-returns.xyz/invest",
    "https://loginverification-secure.ru/bank",
]

SAMPLE_SAFE_URLS = [
    "https://www.google.com/search?q=weather",
    "https://amazon.com/orders/track",
    "https://github.com/user/repository",
    "https://docs.python.org/3/library",
    "https://stackoverflow.com/questions/12345",
    "https://www.wikipedia.org/wiki/Machine_learning",
    "https://mail.google.com/mail/inbox",
    "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    "https://linkedin.com/in/profile",
    "https://www.bbc.com/news/technology",
]


def create_text_classifier():
    """Create and train a text scam classifier."""
    texts = SAMPLE_SCAM_TEXTS + SAMPLE_SAFE_TEXTS
    labels = [1] * len(SAMPLE_SCAM_TEXTS) + [0] * len(SAMPLE_SAFE_TEXTS)

    pipeline = Pipeline([
        ('tfidf', TfidfVectorizer(
            ngram_range=(1, 3),
            max_features=5000,
            stop_words='english',
            lowercase=True,
            analyzer='word'
        )),
        ('classifier', GradientBoostingClassifier(
            n_estimators=100,
            learning_rate=0.1,
            max_depth=5,
            random_state=42
        ))
    ])

    X_train, X_test, y_train, y_test = train_test_split(
        texts, labels, test_size=0.2, random_state=42, stratify=labels
    )

    pipeline.fit(X_train, y_train)
    y_pred = pipeline.predict(X_test)
    logger.info(f"Text Classifier Report:\n{classification_report(y_test, y_pred)}")

    return pipeline


def create_url_classifier():
    """Create and train a URL scam classifier."""
    from app.ml.url_analyzer import extract_url_features

    urls = SAMPLE_SCAM_URLS + SAMPLE_SAFE_URLS
    labels = [1] * len(SAMPLE_SCAM_URLS) + [0] * len(SAMPLE_SAFE_URLS)

    features = [extract_url_features(url) for url in urls]
    X = np.array(features)

    classifier = RandomForestClassifier(
        n_estimators=100,
        max_depth=10,
        random_state=42
    )
    classifier.fit(X, labels)
    return classifier


def create_keyword_extractor():
    """Create TF-IDF vectorizer for keyword extraction."""
    all_texts = SAMPLE_SCAM_TEXTS + SAMPLE_SAFE_TEXTS
    vectorizer = TfidfVectorizer(ngram_range=(1, 2), max_features=1000, stop_words='english')
    vectorizer.fit(all_texts)
    return vectorizer


def load_all_models():
    """Load or create all ML models."""
    global _models, _vectorizers

    models_dir = "saved_models"
    os.makedirs(models_dir, exist_ok=True)

    text_model_path = os.path.join(models_dir, "text_classifier.pkl")
    url_model_path = os.path.join(models_dir, "url_classifier.pkl")
    keyword_model_path = os.path.join(models_dir, "keyword_extractor.pkl")

    # Text classifier
    if os.path.exists(text_model_path):
        logger.info("Loading saved text classifier...")
        _models['text'] = joblib.load(text_model_path)
    else:
        logger.info("Training new text classifier...")
        _models['text'] = create_text_classifier()
        joblib.dump(_models['text'], text_model_path)
        logger.info("Text classifier saved.")

    # URL classifier
    if os.path.exists(url_model_path):
        logger.info("Loading saved URL classifier...")
        _models['url'] = joblib.load(url_model_path)
    else:
        logger.info("Training new URL classifier...")
        _models['url'] = create_url_classifier()
        joblib.dump(_models['url'], url_model_path)
        logger.info("URL classifier saved.")

    # Keyword extractor
    if os.path.exists(keyword_model_path):
        logger.info("Loading saved keyword extractor...")
        _vectorizers['keyword'] = joblib.load(keyword_model_path)
    else:
        logger.info("Creating keyword extractor...")
        _vectorizers['keyword'] = create_keyword_extractor()
        joblib.dump(_vectorizers['keyword'], keyword_model_path)
        logger.info("Keyword extractor saved.")

    logger.info("✅ All ML models loaded successfully!")


def get_model(name: str):
    return _models.get(name)


def get_vectorizer(name: str):
    return _vectorizers.get(name)
