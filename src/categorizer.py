import os
import re
from dataclasses import dataclass
from typing import Dict, List, Tuple


CATEGORIES = [
    "Order status",
    "Delivery delay",
    "Refund request",
    "Product issue",
    "Subscription issue",
    "Payment failure",
    "General product question",
    "Other",
]


KEYWORDS: Dict[str, List[str]] = {
    "Order status": [
        "order status",
        "where is my order",
        "tracking",
        "shipment status",
        "check status",
        "latest status",
        "any update",
        "status for order",
        "has shipped",
        "dispatched",
        "in transit",
        "live tracking",
        "status update",
        "still says processing",
        "order pending",
        "is pending",
    ],
    "Delivery delay": [
        "delivery delayed",
        "delivery delay",
        "late delivery",
        "delivery is late",
        "late by",
        "parcel due",
        "not delivered",
        "stuck at hub",
        "shipment delayed",
        "delayed again",
        "no eta",
        "expected delivery date passed",
        "courier has not moved",
        "waiting on delayed",
    ],
    "Refund request": [
        "refund",
        "money back",
        "refund status",
        "refund not credited",
        "initiate refund",
    ],
    "Product issue": [
        "damaged",
        "broken",
        "wrong item",
        "wrong flavor",
        "quality",
        "tastes odd",
        "seal was broken",
        "replace",
        "clumps",
    ],
    "Subscription issue": [
        "subscription",
        "auto renewal",
        "pause my monthly",
        "cancel my",
    ],
    "Payment failure": [
        "payment failed",
        "checkout failed",
        "card declined",
        "unable to pay",
        "retry payment",
    ],
    "General product question": [
        "which product",
        "best for beginners",
        "how to use",
        "ingredients",
        "what is the difference",
    ],
}


@dataclass
class ClassificationResult:
    category: str
    confidence: float
    method: str


def _normalize(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    return re.sub(r"\s+", " ", text)


def classify_rule_based(message: str) -> ClassificationResult:
    normalized = _normalize(message)
    score_by_category: Dict[str, float] = {category: 0.0 for category in CATEGORIES}

    for category, words in KEYWORDS.items():
        score = 0.0
        for word in words:
            if word in normalized:
                score += 1.0
        score_by_category[category] = score

    best_category, best_score = max(score_by_category.items(), key=lambda x: x[1])

    if best_score == 0:
        return ClassificationResult(category="Other", confidence=0.35, method="rule")

    total_score = sum(score_by_category.values())
    confidence = min(0.99, 0.45 + (best_score / max(total_score, 1.0)))
    return ClassificationResult(category=best_category, confidence=round(confidence, 2), method="rule")


def classify_with_optional_llm(message: str) -> ClassificationResult:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return classify_rule_based(message)

    try:
        from openai import OpenAI
    except Exception:
        return classify_rule_based(message)

    client = OpenAI(api_key=api_key)
    prompt = (
        "Classify this customer support message into one category only: "
        f"{', '.join(CATEGORIES)}. "
        "Return JSON with keys category and confidence (0 to 1). "
        f"Message: {message}"
    )

    try:
        response = client.responses.create(
            model="gpt-4.1-mini",
            input=prompt,
            temperature=0,
        )
        raw = response.output_text.strip()
        match = re.search(r"\{.*\}", raw, re.DOTALL)
        if not match:
            return classify_rule_based(message)
        payload = match.group(0)
        import json

        data = json.loads(payload)
        category = data.get("category", "Other")
        confidence = float(data.get("confidence", 0.5))
        if category not in CATEGORIES:
            category = "Other"
        return ClassificationResult(
            category=category,
            confidence=round(max(0.0, min(confidence, 1.0)), 2),
            method="llm",
        )
    except Exception:
        return classify_rule_based(message)


def classify_message(message: str, use_llm: bool = False) -> ClassificationResult:
    if use_llm:
        return classify_with_optional_llm(message)
    return classify_rule_based(message)
