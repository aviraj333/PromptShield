
import re
import unicodedata
from urllib.parse import unquote

DEMO_SECRET = "PSH-DEMO-SECRET-4821"

PATTERNS = [
    re.compile(
        r"ignore\s+(all\s+)?previous\s+instructions",
        re.IGNORECASE,
    ),
    re.compile(
        r"reveal\s+(the\s+)?(system\s+prompt|protected prompt|secret)",
        re.IGNORECASE,
    ),
    re.compile(
        r"disregard\s+(all\s+)?(prior|previous)\s+instructions",
        re.IGNORECASE,
    ),
]

def normalize(text: str) -> str:
    text = unicodedata.normalize("NFKC", text)
    text = re.sub(r"[\u200B-\u200F\uFEFF]", "", text)
    text = unquote(text)
    return re.sub(r"\s+", " ", text).strip()

def inspect_prompt(content: str, source: str) -> dict:
    normalized = normalize(content)
    signals = []
    reasons = []

    if DEMO_SECRET.lower() in normalized.lower():
        signals.append("protected_value_exposure")
        reasons.append("Demo protected value detected.")

    matched = [
        pattern for pattern in PATTERNS
        if pattern.search(normalized)
    ]

    if matched:
        signals.append("instruction_override")
        reasons.append("Potential malicious instruction detected.")

    if "protected_value_exposure" in signals:
        decision = "BLOCK"
        sanitized_content = None

    elif matched and source == "user":
        decision = "BLOCK"
        sanitized_content = None

    elif matched and source in ("retrieved_document", "tool_output"):
        sentences = re.split(r"(?<=[.!?])\s+", content.strip())
        safe_sentences = []
        removed = False

        for sentence in sentences:
            if any(pattern.search(normalize(sentence)) for pattern in matched):
                removed = True
            else:
                safe_sentences.append(sentence)

        if removed and safe_sentences:
            decision = "SANITIZE"
            sanitized_content = " ".join(safe_sentences).strip()
            reasons.append("Recognized suspicious sentence removed.")
        else:
            decision = "ESCALATE"
            sanitized_content = None
            reasons.append("Could not safely isolate suspicious content.")

    elif matched:
        decision = "ESCALATE"
        sanitized_content = None

    else:
        decision = "ALLOW"
        sanitized_content = None
        reasons.append("No configured attack pattern matched.")

    return {
        "decision": decision,
        "reasons": reasons,
        "signals": signals or ["normal_content"],
        "sanitized_content": sanitized_content,
    }
