"""
ScamShield AI - Comprehensive Test Suite
Run: pytest tests/ -v
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.ml.text_analyzer import analyze_text, extract_text_features, determine_scam_type
from app.ml.url_analyzer import analyze_url, extract_url_features
from app.ml.voice_analyzer import analyze_voice_transcript
from app.ml.model_loader import load_all_models, get_model
from app.services.risk_scorer import calculate_risk_score, get_risk_level_info

client = TestClient(app)


# ─── Model Loading ────────────────────────────────────────────────────────────

class TestModelLoading:
    def test_models_load_successfully(self):
        load_all_models()
        assert get_model('text') is not None
        assert get_model('url') is not None

    def test_text_model_predicts(self):
        load_all_models()
        model = get_model('text')
        result = model.predict(["test message"])
        assert result is not None
        assert len(result) == 1

    def test_text_model_probability(self):
        load_all_models()
        model = get_model('text')
        proba = model.predict_proba(["test message"])
        assert proba.shape == (1, 2)
        assert abs(sum(proba[0]) - 1.0) < 0.001


# ─── Text Analysis ────────────────────────────────────────────────────────────

class TestTextAnalysis:
    @pytest.fixture(autouse=True)
    def load_models(self):
        load_all_models()

    SCAM_TEXTS = [
        "URGENT: Your bank account has been suspended. Click http://fake-bank.xyz to verify NOW!",
        "Congratulations! You won $50,000! Send your bank details to claim the prize immediately!",
        "IRS FINAL NOTICE: You owe back taxes. Pay now or face arrest. Call 1-800-FAKE-IRS",
        "Your social security number has been suspended. Press 1 to speak with a federal officer.",
        "FREE iPhone! Click now to claim: bit.ly/freeiphone123 Limited time offer expires today!",
    ]

    SAFE_TEXTS = [
        "Hi, can we reschedule our meeting to 3pm? Something came up.",
        "Your dentist appointment is confirmed for Thursday at 2:30 PM.",
        "Team lunch tomorrow at noon. Please let me know if you can join.",
        "The quarterly report is attached. Please review before Friday.",
        "Happy birthday! Hope you have a wonderful day with your family!",
    ]

    def test_scam_texts_detected(self):
        model = get_model('text')
        for text in self.SCAM_TEXTS:
            result = analyze_text(text, model)
            assert result['risk_score'] > 0, f"Risk should be >0 for: {text[:50]}"

    def test_safe_texts_not_flagged(self):
        model = get_model('text')
        for text in self.SAFE_TEXTS:
            result = analyze_text(text, model)
            assert result['is_scam'] == False or result['risk_score'] < 70, \
                f"Safe text incorrectly flagged: {text[:50]}"

    def test_analysis_returns_required_fields(self):
        model = get_model('text')
        result = analyze_text("Test message for field validation", model)
        required_fields = ['is_scam', 'confidence', 'risk_score', 'explanation', 'keyword_analysis']
        for field in required_fields:
            assert field in result, f"Missing field: {field}"

    def test_confidence_in_valid_range(self):
        model = get_model('text')
        result = analyze_text("URGENT: Click here now to win prizes!", model)
        assert 0 <= result['confidence'] <= 100

    def test_risk_score_in_valid_range(self):
        model = get_model('text')
        result = analyze_text("Normal everyday message content", model)
        assert 0 <= result['risk_score'] <= 100

    def test_empty_text_handled(self):
        model = get_model('text')
        result = analyze_text("", model)
        assert result['is_scam'] == False
        assert result['risk_score'] == 0

    def test_short_text_handled(self):
        model = get_model('text')
        result = analyze_text("Hi", model)
        assert result is not None

    def test_keyword_extraction(self):
        model = get_model('text')
        result = analyze_text("URGENT prize winner claim money NOW", model)
        assert len(result.get('explanation', [])) > 0


# ─── URL Analysis ─────────────────────────────────────────────────────────────

class TestUrlAnalysis:
    @pytest.fixture(autouse=True)
    def load_models(self):
        load_all_models()

    SCAM_URLS = [
        "http://paypa1-secure.com/verify",
        "https://amaz0n-login.xyz/account",
        "http://bank-secure-verify.tk/login",
        "http://192.168.1.1/admin/login",
        "http://bit.ly/freegift2024",
    ]

    SAFE_URLS = [
        "https://www.google.com",
        "https://amazon.com/orders",
        "https://github.com/user/repo",
        "https://docs.python.org",
        "https://stackoverflow.com",
    ]

    def test_scam_urls_detected(self):
        model = get_model('url')
        for url in self.SCAM_URLS:
            result = analyze_url(url, model)
            assert result['risk_score'] > 10, f"Should have some risk: {url}"

    def test_safe_urls_allowed(self):
        model = get_model('url')
        for url in self.SAFE_URLS:
            result = analyze_url(url, model)
            assert result['is_safe'] == True, f"Safe URL flagged: {url}"

    def test_url_result_fields(self):
        model = get_model('url')
        result = analyze_url("https://www.google.com", model)
        required = ['is_safe', 'safety_score', 'risk_score', 'flags', 'explanation', 'domain_info']
        for field in required:
            assert field in result

    def test_https_vs_http(self):
        model = get_model('url')
        https = analyze_url("https://example-site.com", model)
        http = analyze_url("http://example-site.com", model)
        assert https['risk_score'] <= http['risk_score']

    def test_suspicious_tld_flagged(self):
        model = get_model('url')
        result = analyze_url("https://free-money.tk/claim", model)
        assert "SUSPICIOUS_TLD" in result['flags']

    def test_feature_extraction(self):
        features = extract_url_features("https://www.google.com")
        assert len(features) == 15
        assert all(0.0 <= f <= 1.0 for f in features)

    def test_invalid_url_handled(self):
        model = get_model('url')
        result = analyze_url("not-a-url", model)
        assert result is not None


# ─── Voice Analysis ───────────────────────────────────────────────────────────

class TestVoiceAnalysis:
    SCAM_TRANSCRIPT = """
    This is a final notice from the IRS. We have been trying to reach you regarding 
    a serious matter. Your social security number has been suspended due to suspicious 
    activity. You must call us back immediately at 1-800-555-0123 or we will issue 
    an arrest warrant. Do not hang up. This is urgent.
    """

    SAFE_TRANSCRIPT = """
    Hi, this is Dr. Smith's office calling to remind you about your appointment 
    tomorrow at 2:30 PM. Please call us if you need to reschedule. Our number is 
    555-1234. Have a great day!
    """

    def test_scam_voice_detected(self):
        result = analyze_voice_transcript(self.SCAM_TRANSCRIPT)
        assert result['is_scam'] == True
        assert result['risk_score'] > 30

    def test_safe_voice_not_flagged(self):
        result = analyze_voice_transcript(self.SAFE_TRANSCRIPT)
        assert result['risk_score'] < 50

    def test_voice_result_fields(self):
        result = analyze_voice_transcript(self.SCAM_TRANSCRIPT)
        required = ['is_scam', 'confidence', 'risk_score', 'flagged_phrases', 'tone_analysis', 'explanation']
        for field in required:
            assert field in result

    def test_empty_transcript(self):
        result = analyze_voice_transcript("")
        assert result['is_scam'] == False

    def test_scam_type_identified(self):
        result = analyze_voice_transcript(self.SCAM_TRANSCRIPT)
        assert result['scam_type'] is not None


# ─── Risk Scorer ──────────────────────────────────────────────────────────────

class TestRiskScorer:
    def test_composite_score_calculation(self):
        text_analysis = {'risk_score': 80, 'is_scam': True}
        url_analysis = {'risk_score': 70}
        result = calculate_risk_score(text_analysis=text_analysis, url_analysis=url_analysis)
        assert 0 <= result['overall_risk_score'] <= 100
        assert result['risk_level'] in ['SAFE', 'LOW', 'MEDIUM', 'HIGH', 'CRITICAL']

    def test_safe_score(self):
        text_analysis = {'risk_score': 5, 'is_scam': False}
        result = calculate_risk_score(text_analysis=text_analysis)
        assert result['risk_level'] in ['SAFE', 'LOW']

    def test_high_risk_score(self):
        text_analysis = {'risk_score': 90, 'is_scam': True}
        url_analysis = {'risk_score': 85}
        result = calculate_risk_score(text_analysis=text_analysis, url_analysis=url_analysis)
        assert result['risk_level'] in ['HIGH', 'CRITICAL']

    def test_risk_level_info(self):
        assert get_risk_level_info(80)['level'] == 'CRITICAL'
        assert get_risk_level_info(60)['level'] == 'HIGH'
        assert get_risk_level_info(35)['level'] == 'MEDIUM'
        assert get_risk_level_info(15)['level'] == 'LOW'
        assert get_risk_level_info(5)['level'] == 'SAFE'


# ─── API Endpoints ────────────────────────────────────────────────────────────

class TestApiEndpoints:
    def test_root_endpoint(self):
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "service" in data
        assert data["service"] == "ScamShield AI"

    def test_health_endpoint(self):
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"

    def test_analyze_text_endpoint(self):
        response = client.post("/api/v1/analyze/text", json={
            "text": "URGENT: Your account has been suspended. Click here to verify immediately!",
            "message_type": "sms"
        })
        assert response.status_code == 200
        data = response.json()
        assert "is_scam" in data
        assert "risk_score" in data
        assert "confidence" in data
        assert "explanation" in data

    def test_analyze_safe_text(self):
        response = client.post("/api/v1/analyze/text", json={
            "text": "Hi, just checking in. Are you free for lunch tomorrow?",
            "message_type": "sms"
        })
        assert response.status_code == 200
        data = response.json()
        assert data['risk_score'] < 70

    def test_analyze_url_endpoint(self):
        response = client.post("/api/v1/analyze/url", json={
            "url": "http://paypa1-secure-verify.tk/login"
        })
        assert response.status_code == 200
        data = response.json()
        assert "is_safe" in data
        assert "safety_score" in data
        assert "flags" in data
        assert data['is_safe'] == False

    def test_analyze_safe_url(self):
        response = client.post("/api/v1/analyze/url", json={"url": "https://www.google.com"})
        assert response.status_code == 200
        data = response.json()
        assert data['is_safe'] == True

    def test_analyze_email_endpoint(self):
        response = client.post("/api/v1/analyze/email", json={
            "subject": "URGENT: Verify your PayPal account immediately",
            "body": "Your account has been limited. Click here to verify: paypa1-secure.com",
            "sender_email": "noreply@paypal-secure-update.xyz"
        })
        assert response.status_code == 200
        data = response.json()
        assert "is_scam" in data
        assert "risk_score" in data

    def test_analyze_voice_endpoint(self):
        response = client.post("/api/v1/analyze/voice", json={
            "transcript": "This is the IRS. Your social security number is suspended. Call immediately or face arrest."
        })
        assert response.status_code == 200
        data = response.json()
        assert "is_scam" in data
        assert data['is_scam'] == True

    def test_chatbot_endpoint(self):
        response = client.post("/api/v1/chatbot/ask", json={
            "message": "Is this message safe? You won a million dollars click here now!"
        })
        assert response.status_code == 200
        data = response.json()
        assert "response" in data
        assert len(data['response']) > 0

    def test_dashboard_stats_endpoint(self):
        response = client.get("/api/v1/dashboard/stats")
        assert response.status_code == 200
        data = response.json()
        required = ['total_analyzed', 'scams_detected', 'safe_messages']
        for field in required:
            assert field in data

    def test_report_scam_endpoint(self):
        response = client.post("/api/v1/report/scam", json={
            "report_type": "phone",
            "phone_number": "1-800-SCAM-NOW",
            "description": "Caller claimed to be IRS and demanded gift card payment",
            "scam_type": "Government Impersonation"
        })
        assert response.status_code == 200
        data = response.json()
        assert data['success'] == True
        assert 'report_id' in data

    def test_empty_text_rejected(self):
        response = client.post("/api/v1/analyze/text", json={"text": ""})
        assert response.status_code == 422

    def test_missing_text_rejected(self):
        response = client.post("/api/v1/analyze/text", json={})
        assert response.status_code == 422


# ─── Integration Tests ────────────────────────────────────────────────────────

class TestIntegration:
    """End-to-end integration tests simulating real scam scenarios."""

    def test_phishing_sms_scenario(self):
        """Simulate receiving a phishing SMS."""
        response = client.post("/api/v1/analyze/text", json={
            "text": "URGENT ALERT: Your Chase Bank account is SUSPENDED. Verify NOW at: chase-bank-alert.tk/verify or face permanent closure!",
            "message_type": "sms",
            "is_unknown_sender": True
        })
        assert response.status_code == 200
        data = response.json()
        # Should have non-trivial risk or be flagged as scam
        assert data['risk_score'] > 20 or data['is_scam'] == True

    def test_safe_email_scenario(self):
        """Simulate a legitimate business email."""
        response = client.post("/api/v1/analyze/email", json={
            "subject": "Q3 Performance Review - Action Required",
            "body": "Please complete your self-review by Friday. The link to the review portal has been sent separately.",
            "sender_email": "hr@company.com"
        })
        assert response.status_code == 200
        data = response.json()
        assert data['risk_score'] < 60

    def test_voice_scam_scenario(self):
        """Simulate an IRS phone scam."""
        response = client.post("/api/v1/analyze/voice", json={
            "transcript": "This is officer John from the IRS. We have a warrant for your arrest for unpaid taxes. You must pay $2000 in gift cards immediately or you will be arrested today.",
            "caller_id": "+1-800-555-0000"
        })
        assert response.status_code == 200
        data = response.json()
        # IRS keywords + arrest + gift card should produce risk
        assert data['risk_score'] > 0 or data['is_scam'] == True
        assert "is_scam" in data
        assert "risk_score" in data

    def test_report_and_check_workflow(self):
        """Simulate reporting a scam number and checking the database."""
        # Report
        report_response = client.post("/api/v1/report/scam", json={
            "report_type": "phone",
            "phone_number": "1-555-SCAM-999",
            "description": "IRS scam call demanding gift cards",
            "scam_type": "Government Impersonation"
        })
        assert report_response.status_code == 200
        assert report_response.json()['success'] == True

    def test_url_phishing_scenario(self):
        """Simulate clicking a phishing link."""
        response = client.post("/api/v1/analyze/url", json={
            "url": "http://amaz0n-secure-login.xyz/signin"
        })
        assert response.status_code == 200
        data = response.json()
        assert data['is_safe'] == False
        assert data['risk_score'] > 50


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
