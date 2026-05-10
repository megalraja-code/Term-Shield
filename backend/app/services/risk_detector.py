import re

RISK_PATTERNS = {

    "auto renew": {
        "score": 15,
        "message": "Subscription may renew automatically"
    },

    "automatically renew": {
        "score": 15,
        "message": "Subscription may renew automatically"
    },

    "third-party": {
        "score": 20,
        "message": "Your data may be shared with third parties"
    },

    "share your data": {
        "score": 20,
        "message": "Company may share your personal data"
    },

    "we may terminate": {
        "score": 20,
        "message": "Company can terminate your account"
    },

    "terminate your account": {
        "score": 20,
        "message": "Account may be removed without warning"
    },

    "no refund": {
        "score": 15,
        "message": "Refunds may not be available"
    },

    "non-refundable": {
        "score": 15,
        "message": "Payments may be non-refundable"
    },

    "binding arbitration": {
        "score": 25,
        "message": "You may lose the right to sue in court"
    },

    "change these terms at any time": {
        "score": 15,
        "message": "Terms can change anytime without approval"
    },

    "location data": {
        "score": 20,
        "message": "App may track your location"
    },

    "collect biometric": {
        "score": 25,
        "message": "Biometric data may be collected"
    },

    "sell your data": {
        "score": 30,
        "message": "Your personal data may be sold"
    },

    "track your activity": {
        "score": 20,
        "message": "User activity may be tracked"
    },

    "cookies": {
        "score": 5,
        "message": "Website uses tracking cookies"
    }
}


def detect_risks(content: str):

    text = content.lower()

    total_score = 0

    found_risks = []

    for keyword, risk in RISK_PATTERNS.items():

        if re.search(re.escape(keyword), text):

            total_score += risk["score"] * 0.7

            if risk["message"] not in found_risks:
                found_risks.append(risk["message"])

    total_score = round(total_score)

    if total_score <= 25:
        level = "Safe"

    elif total_score <= 55:
        level = "Medium Risk"

    elif total_score <= 80:
        level = "High Risk"

    else:
        level = "Critical Risk"

    total_score = min(total_score, 100)

    return {
        "risk_score": total_score,
        "risk_level": level,
        "risks": found_risks
    }