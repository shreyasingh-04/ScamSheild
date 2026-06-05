import re
import socket
import ssl
import urllib.parse
from typing import Dict, List, Any
import numpy as np
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

SUSPICIOUS_TLDS = ['.tk', '.ml', '.ga', '.cf', '.gq', '.xyz', '.top', '.club', '.ru', '.cn', '.pw', '.cc']
PHISHING_KEYWORDS = [
    'login', 'signin', 'verify', 'secure', 'account', 'update', 'confirm',
    'banking', 'paypal', 'netflix', 'amazon', 'apple', 'microsoft', 'google',
    'irs', 'tax', 'refund', 'prize', 'winner', 'free', 'gift', 'claim',
    'password', 'credential', 'support', 'helpdesk', 'recovery'
]

BRAND_SPOOFING = {
    'paypal': ['paypa1', 'paypall', 'pay-pal', 'paypal-secure'],
    'amazon': ['amaz0n', 'amazzon', 'amazon-secure', 'amazon-login'],
    'microsoft': ['m1crosoft', 'micros0ft', 'microsoft-support'],
    'apple': ['app1e', 'apple-id', 'apple-secure'],
    'google': ['g00gle', 'googgle', 'google-verify'],
    'netflix': ['netf1ix', 'netflix-update', 'netflix-billing'],
    'irs': ['irs-gov', 'tax-refund', 'irs-tax'],
    'bank': ['bank-secure', 'online-bank', 'banking-verify'],
}

KNOWN_SAFE_DOMAINS = [
    'google.com', 'youtube.com', 'facebook.com', 'amazon.com', 'apple.com',
    'microsoft.com', 'twitter.com', 'instagram.com', 'linkedin.com', 'github.com',
    'stackoverflow.com', 'wikipedia.org', 'reddit.com', 'netflix.com', 'paypal.com',
    'bbc.com', 'cnn.com', 'nytimes.com', 'medium.com', 'spotify.com'
]


def extract_url_features(url: str) -> List[float]:
    """Extract numerical features from URL for ML classification."""
    features = []

    try:
        parsed = urllib.parse.urlparse(url if '://' in url else 'http://' + url)
        domain = parsed.netloc.lower()
        path = parsed.path.lower()
        full_url = url.lower()

        # Feature 1: Uses HTTPS
        features.append(1.0 if parsed.scheme == 'https' else 0.0)

        # Feature 2: URL length (normalized)
        features.append(min(len(url) / 200, 1.0))

        # Feature 3: Domain length (normalized)
        features.append(min(len(domain) / 50, 1.0))

        # Feature 4: Number of subdomains
        subdomain_count = len(domain.split('.')) - 2
        features.append(min(subdomain_count / 5, 1.0))

        # Feature 5: Contains IP address
        features.append(1.0 if re.search(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', domain) else 0.0)

        # Feature 6: Suspicious TLD
        has_suspicious_tld = any(domain.endswith(tld) for tld in SUSPICIOUS_TLDS)
        features.append(1.0 if has_suspicious_tld else 0.0)

        # Feature 7: Phishing keywords in URL
        keyword_count = sum(1 for kw in PHISHING_KEYWORDS if kw in full_url)
        features.append(min(keyword_count / 10, 1.0))

        # Feature 8: Brand spoofing
        spoofing_detected = False
        for brand, variants in BRAND_SPOOFING.items():
            if any(variant in domain for variant in variants):
                spoofing_detected = True
                break
        features.append(1.0 if spoofing_detected else 0.0)

        # Feature 9: Hyphen count in domain
        features.append(min(domain.count('-') / 5, 1.0))

        # Feature 10: URL shortener
        shorteners = ['bit.ly', 'tinyurl', 't.co', 'goo.gl', 'ow.ly', 'short.io']
        features.append(1.0 if any(s in domain for s in shorteners) else 0.0)

        # Feature 11: Is known safe domain
        is_safe = any(domain.endswith(safe) or domain == safe for safe in KNOWN_SAFE_DOMAINS)
        features.append(1.0 if is_safe else 0.0)

        # Feature 12: Special char count
        special_chars = re.findall(r'[~`!@#$%^&*()+={}|<>?]', url)
        features.append(min(len(special_chars) / 10, 1.0))

        # Feature 13: Number count in domain
        number_count = len(re.findall(r'\d', domain))
        features.append(min(number_count / 10, 1.0))

        # Feature 14: Port specified
        features.append(1.0 if parsed.port and parsed.port not in [80, 443] else 0.0)

        # Feature 15: Path depth
        path_depth = len([p for p in path.split('/') if p])
        features.append(min(path_depth / 10, 1.0))

    except Exception as e:
        logger.warning(f"URL feature extraction error: {e}")
        features = [0.0] * 15

    # Pad to ensure consistent length
    while len(features) < 15:
        features.append(0.0)

    return features[:15]


def analyze_url(url: str, model) -> Dict[str, Any]:
    """Comprehensive URL analysis for phishing/scam detection."""
    if not url or len(url.strip()) < 5:
        return {
            "is_safe": True,
            "safety_score": 100,
            "risk_score": 0,
            "confidence": 0,
            "flags": [],
            "explanation": ["URL too short to analyze"],
            "domain_info": {}
        }

    try:
        parsed = urllib.parse.urlparse(url if '://' in url else 'http://' + url)
        domain = parsed.netloc.lower()
    except Exception:
        return {"is_safe": False, "safety_score": 0, "risk_score": 100, "flags": ["Invalid URL"], "explanation": ["Could not parse URL"]}

    flags = []
    risk_factors = []
    risk_score = 0

    # HTTPS check
    uses_https = parsed.scheme == 'https'
    if not uses_https:
        flags.append("NO_HTTPS")
        risk_factors.append("Uses insecure HTTP connection (no encryption)")
        risk_score += 20

    # Known safe domain
    is_known_safe = any(domain.endswith(safe) or domain == safe for safe in KNOWN_SAFE_DOMAINS)
    if is_known_safe:
        risk_score = max(0, risk_score - 30)

    # Suspicious TLD
    for tld in SUSPICIOUS_TLDS:
        if domain.endswith(tld):
            flags.append("SUSPICIOUS_TLD")
            risk_factors.append(f"Uses suspicious/free TLD: {tld}")
            risk_score += 30
            break

    # URL shortener
    shorteners = ['bit.ly', 'tinyurl', 't.co', 'goo.gl', 'ow.ly', 'short.io', 'rb.gy']
    if any(s in domain for s in shorteners):
        flags.append("URL_SHORTENER")
        risk_factors.append("URL shortener detected — destination hidden")
        risk_score += 15

    # IP address as domain
    if re.search(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', domain):
        flags.append("IP_AS_DOMAIN")
        risk_factors.append("IP address used instead of domain name")
        risk_score += 35

    # Brand spoofing
    spoofed_brand = None
    for brand, variants in BRAND_SPOOFING.items():
        if any(variant in domain for variant in variants):
            flags.append("BRAND_SPOOFING")
            risk_factors.append(f"Possible brand spoofing: mimics '{brand}'")
            risk_score += 40
            spoofed_brand = brand
            break

    # Phishing keywords
    url_lower = url.lower()
    found_phishing_kws = [kw for kw in PHISHING_KEYWORDS if kw in url_lower]
    if len(found_phishing_kws) > 2:
        flags.append("PHISHING_KEYWORDS")
        risk_factors.append(f"Multiple phishing keywords: {', '.join(found_phishing_kws[:5])}")
        risk_score += 20

    # Excessive subdomains
    subdomain_count = len(domain.split('.')) - 2
    if subdomain_count > 3:
        flags.append("EXCESSIVE_SUBDOMAINS")
        risk_factors.append(f"Unusual number of subdomains ({subdomain_count})")
        risk_score += 15

    # Hyphens in domain
    hyphen_count = domain.split('.')[0].count('-')
    if hyphen_count > 2:
        flags.append("EXCESSIVE_HYPHENS")
        risk_factors.append(f"Multiple hyphens in domain ({hyphen_count})")
        risk_score += 10

    # URL length
    if len(url) > 100:
        flags.append("LONG_URL")
        risk_factors.append(f"Unusually long URL ({len(url)} characters)")
        risk_score += 10

    # ML prediction
    try:
        features = extract_url_features(url)
        ml_proba = model.predict_proba([features])[0]
        ml_risk = float(ml_proba[1]) * 40  # ML contributes up to 40 points
        risk_score += ml_risk
    except Exception as e:
        logger.warning(f"URL ML prediction failed: {e}")

    risk_score = min(100, max(0, risk_score))
    safety_score = 100 - risk_score
    is_safe = risk_score < 40

    explanation = risk_factors if risk_factors else ["URL appears safe based on analysis"]

    return {
        "is_safe": is_safe,
        "safety_score": round(safety_score, 1),
        "risk_score": round(risk_score, 1),
        "confidence": min(95, 50 + len(flags) * 10),
        "flags": flags,
        "explanation": explanation,
        "domain_info": {
            "domain": domain,
            "uses_https": uses_https,
            "is_known_safe": is_known_safe,
            "subdomain_count": subdomain_count,
            "spoofed_brand": spoofed_brand,
            "phishing_keywords_found": found_phishing_kws[:5],
            "url_length": len(url)
        },
        "verdict": "SAFE" if is_safe else ("SUSPICIOUS" if risk_score < 70 else "DANGEROUS")
    }
