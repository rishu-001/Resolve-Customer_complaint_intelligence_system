"""
nlp_engine.py — Complaint Intelligence NLP Engine
Uses: NLTK, TextBlob, scikit-learn, keyword rules
No paid APIs required — fully offline NLP.
"""

import re
import random
from textblob import TextBlob

# ── Category Rules ─────────────────────────────────────────────────────────
CATEGORY_RULES = {
    "Payment Issue": [
        "charged", "charge", "payment", "refund", "billing", "bill", "invoice",
        "double charge", "overcharged", "debit", "credit card", "transaction",
        "money", "price", "fee", "subscription", "cost", "pay", "paid"
    ],
    "Delivery Problem": [
        "delivery", "deliver", "shipped", "shipping", "package", "parcel",
        "order", "arrived", "arrive", "late", "missing", "lost", "tracking",
        "courier", "dispatch", "not received", "never came", "delay", "delayed"
    ],
    "Technical Issue": [
        "app", "website", "crash", "bug", "error", "not working", "broken",
        "slow", "loading", "login", "password", "account", "glitch", "freeze",
        "technical", "issue", "problem", "failure", "down", "outage", "fix"
    ],
    "Customer Service": [
        "rude", "unprofessional", "agent", "representative", "support",
        "hung up", "ignored", "no response", "waiting", "hold", "helpline",
        "staff", "service", "attitude", "behavior", "disrespectful", "unhelpful"
    ],
    "Product Quality": [
        "quality", "broken", "damaged", "defective", "not working", "poor",
        "bad", "fake", "wrong", "different", "description", "product", "item",
        "size", "color", "material", "smell", "expired", "manufacturer"
    ],
    "Return & Refund": [
        "return", "exchange", "refund", "replacement", "warranty", "guarantee",
        "policy", "send back", "returned", "rejected", "refused", "accept"
    ],
    "Account Issue": [
        "account", "login", "logout", "locked", "banned", "suspended",
        "access", "password", "email", "username", "profile", "settings",
        "verification", "otp", "2fa", "security", "hack", "unauthorized"
    ],
    "General Feedback": []  # fallback
}

# ── Urgency Rules ──────────────────────────────────────────────────────────
URGENCY_KEYWORDS = {
    "Critical": [
        "immediately", "urgent", "emergency", "asap", "right now", "today",
        "lawsuit", "legal", "fraud", "scam", "stolen", "hack", "threat",
        "critical", "life", "dangerous", "severe", "unacceptable"
    ],
    "High": [
        "angry", "furious", "never again", "cancel", "frustrated", "outraged",
        "worst", "terrible", "disgusted", "demand", "escalate", "complain",
        "disappointed", "ridiculous", "absurd", "unbelievable"
    ],
    "Medium": [
        "problem", "issue", "concern", "unhappy", "not happy", "bad",
        "wrong", "mistake", "error", "help", "please", "resolve", "fix"
    ],
}

# ── Departments ────────────────────────────────────────────────────────────
DEPT_MAP = {
    "Payment Issue": "Finance & Billing",
    "Delivery Problem": "Logistics & Fulfillment",
    "Technical Issue": "Engineering Support",
    "Customer Service": "Quality & HR",
    "Product Quality": "Product & QA",
    "Return & Refund": "Returns Management",
    "Account Issue": "Trust & Safety",
    "General Feedback": "Customer Success"
}

# ── Actions ────────────────────────────────────────────────────────────────
ACTION_MAP = {
    ("Payment Issue", "Critical"):    ("Immediate refund + escalate to finance manager", "2 hours"),
    ("Payment Issue", "High"):        ("Process refund, send apology voucher", "4 hours"),
    ("Payment Issue", "Medium"):      ("Investigate billing, respond with findings", "24 hours"),
    ("Payment Issue", "Low"):         ("Send billing statement, await response", "48 hours"),
    ("Delivery Problem", "Critical"): ("Emergency re-dispatch + courier escalation", "2 hours"),
    ("Delivery Problem", "High"):     ("Locate package, offer expedited re-send", "4 hours"),
    ("Delivery Problem", "Medium"):   ("Initiate trace request, update customer", "24 hours"),
    ("Delivery Problem", "Low"):      ("Check tracking, share update", "48 hours"),
    ("Technical Issue", "Critical"):  ("Escalate to senior engineer immediately", "1 hour"),
    ("Technical Issue", "High"):      ("Assign developer, send workaround", "4 hours"),
    ("Technical Issue", "Medium"):    ("Log bug report, send ETA", "24 hours"),
    ("Technical Issue", "Low"):       ("Add to bug tracker, acknowledge", "72 hours"),
    ("Customer Service", "Critical"): ("Manager callback + formal apology", "1 hour"),
    ("Customer Service", "High"):     ("Manager review + apology voucher", "4 hours"),
    ("Customer Service", "Medium"):   ("Internal review, follow-up call", "24 hours"),
    ("Customer Service", "Low"):      ("Feedback logged, send survey", "72 hours"),
    ("Product Quality", "Critical"):  ("Replacement + quality team alert", "4 hours"),
    ("Product Quality", "High"):      ("Replacement dispatched, escalate QA", "8 hours"),
    ("Product Quality", "Medium"):    ("Replacement processed", "24 hours"),
    ("Product Quality", "Low"):       ("Feedback logged with QA team", "72 hours"),
    ("Return & Refund", "Critical"):  ("Immediate return label + refund initiated", "2 hours"),
    ("Return & Refund", "High"):      ("Return approved, refund in 3–5 days", "8 hours"),
    ("Return & Refund", "Medium"):    ("Return process explained, label sent", "24 hours"),
    ("Return & Refund", "Low"):       ("Policy information sent", "72 hours"),
    ("Account Issue", "Critical"):    ("Security team alert + account recovery", "30 mins"),
    ("Account Issue", "High"):        ("Account unlocked, security review", "2 hours"),
    ("Account Issue", "Medium"):      ("Verification resent, guide shared", "24 hours"),
    ("Account Issue", "Low"):         ("Self-service guide shared", "72 hours"),
    ("General Feedback", "Critical"): ("Senior management review", "4 hours"),
    ("General Feedback", "High"):     ("Team lead follow-up", "24 hours"),
    ("General Feedback", "Medium"):   ("Feedback acknowledged", "48 hours"),
    ("General Feedback", "Low"):      ("Feedback logged", "1 week"),
}

# ── Suggested Replies ─────────────────────────────────────────────────────
def generate_reply(category, urgency, sentiment):
    openings = {
        "Critical": "We sincerely apologize for this critical issue and are treating it with the highest priority.",
        "High":     "We're truly sorry to hear about your experience and understand your frustration.",
        "Medium":   "Thank you for reaching out. We're sorry to hear you're having trouble.",
        "Low":      "Thank you for your feedback. We appreciate you taking the time to contact us.",
    }
    closings = {
        "Payment Issue":    "Our billing team will review your account and ensure any incorrect charges are reversed promptly.",
        "Delivery Problem": "Our logistics team will investigate your shipment status and provide a resolution immediately.",
        "Technical Issue":  "Our engineering team has been notified and will work to resolve this issue as quickly as possible.",
        "Customer Service": "We have flagged this interaction for an internal review and will ensure this does not happen again.",
        "Product Quality":  "A replacement will be arranged and we've notified our quality assurance team about this issue.",
        "Return & Refund":  "We will process your return/refund as a priority and keep you updated throughout.",
        "Account Issue":    "Our security team will immediately investigate and help you regain full access to your account.",
        "General Feedback": "Your feedback has been forwarded to the relevant team and we will take appropriate action.",
    }
    opening = openings.get(urgency, openings["Medium"])
    closing = closings.get(category, closings["General Feedback"])
    return f"Dear Valued Customer,\n\n{opening} {closing}\n\nWe appreciate your patience and will be in touch shortly.\n\nWarm regards,\nCustomer Support Team"


class ComplaintAnalyzer:
    def __init__(self):
        self.categories = list(CATEGORY_RULES.keys())

    def _classify_category(self, text: str) -> tuple[str, float]:
        text_lower = text.lower()
        scores = {}
        for cat, keywords in CATEGORY_RULES.items():
            if not keywords:
                scores[cat] = 0
                continue
            hits = sum(1 for kw in keywords if kw in text_lower)
            scores[cat] = hits / len(keywords)

        best_cat = max(scores, key=scores.get)
        best_score = scores[best_cat]

        if best_score == 0:
            return "General Feedback", 55.0

        # Normalize confidence
        confidence = min(95, 55 + best_score * 500)

        # Tie-breaking: if score is low, lower confidence
        if best_score < 0.05:
            confidence = max(55, confidence - 10)

        return best_cat, round(confidence, 1)

    def _classify_urgency(self, text: str, sentiment_score: float) -> str:
        text_lower = text.lower()
        for urgency, keywords in URGENCY_KEYWORDS.items():
            if any(kw in text_lower for kw in keywords):
                return urgency

        # Fallback on sentiment polarity
        if sentiment_score < -0.5:
            return "High"
        elif sentiment_score < -0.2:
            return "Medium"
        else:
            return "Low"

    def _get_sentiment(self, text: str) -> tuple[str, float]:
        blob = TextBlob(text)
        polarity = blob.sentiment.polarity
        if polarity < -0.3:
            return "Negative", polarity
        elif polarity > 0.2:
            return "Positive", polarity
        else:
            return "Neutral", polarity

    def _extract_key_issues(self, text: str) -> list[str]:
        issues = []
        text_lower = text.lower()

        patterns = {
            r'\border\s*#?\w+\b': "Order number mentioned",
            r'\bcharged\s+twice\b|\bdouble\s+charge\b': "Double charge detected",
            r'\bno\s+response\b|\bnot\s+respond\b': "Lack of response",
            r'\b\d+\s+day[s]?\b': "Specific timeframe mentioned",
            r'\bcancel\b': "Cancellation intent",
            r'\brefund\b': "Refund requested",
            r'\blegal\b|\blawsuit\b': "Legal threat",
            r'\bthird\s+time\b|\bagain\b|\brepeat\b': "Recurring issue",
        }

        for pattern, label in patterns.items():
            if re.search(pattern, text_lower):
                issues.append(label)

        # Check exclamation marks / caps as emotion indicator
        if text.count("!") > 1:
            issues.append("High emotional intensity")
        if sum(1 for c in text if c.isupper()) > len(text) * 0.2:
            issues.append("All caps used — very frustrated")

        if not issues:
            issues = ["Standard complaint", "Awaiting classification"]

        return issues[:5]

    def _generate_labels(self, text: str, category: str) -> list[str]:
        labels = [category.lower().replace(" ", "-")]
        text_lower = text.lower()
        if any(w in text_lower for w in ["refund", "money", "charge", "bill"]):
            labels.append("financial-impact")
        if any(w in text_lower for w in ["first time", "third time", "again", "repeat"]):
            labels.append("recurring")
        if any(w in text_lower for w in ["loyal", "years", "long time"]):
            labels.append("loyal-customer")
        if any(w in text_lower for w in ["cancel", "leave", "switch"]):
            labels.append("churn-risk")
        if any(w in text_lower for w in ["legal", "lawsuit", "fraud"]):
            labels.append("legal-risk")
        return labels

    def analyze(self, text: str) -> dict:
        category, confidence = self._classify_category(text)
        sentiment_label, sentiment_score = self._get_sentiment(text)
        urgency = self._classify_urgency(text, sentiment_score)
        action, sla = ACTION_MAP.get((category, urgency), ("Assign to support team", "24 hours"))
        department = DEPT_MAP.get(category, "Customer Success")
        key_issues = self._extract_key_issues(text)
        labels = self._generate_labels(text, category)
        suggested_reply = generate_reply(category, urgency, sentiment_label)

        return {
            "category": category,
            "urgency": urgency,
            "sentiment": sentiment_label,
            "confidence": confidence,
            "action": action,
            "sla": sla,
            "department": department,
            "key_issues": key_issues,
            "labels": labels,
            "suggested_reply": suggested_reply,
        }
