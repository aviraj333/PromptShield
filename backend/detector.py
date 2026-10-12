
import re
import unicodedata
from urllib.parse import unquote

DEMO_SECRET = "PSH-DEMO-SECRET-4821"

ATTACK_PATTERNS = [
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

# These phrases trigger a review instead of automatic approval.
AMBIGUOUS_PATTERNS = [
    re.compile(
        r"may\s+conflict\s+with\s+(the\s+)?system\s+policy",
        re.IGNORECASE,
    ),
    re.compile(
        r"intended\s+action\s+is\s+unclear",
        re.IGNORECASE,
    ),
    re.compile(
        r"unclear\s+whether\s+to\s+(follow|execute)",
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
        pattern for pattern in ATTACK_PATTERNS
        if pattern.search(normalized)
    ]

    ambiguous = any(
        pattern.search(normalized)
        for pattern in AMBIGUOUS_PATTERNS
    )

    if matched:
        signals.append("instruction_override")
        reasons.append("Potential malicious instruction detected.")

    if ambiguous:
        signals.append("ambiguous_security_content")
        reasons.append(
            "Ambiguous policy-related content requires review."
        )

    # Mandatory block takes priority.
    if "protected_value_exposure" in signals:
        decision = "BLOCK"
        sanitized_content = None

    # Known direct injection from a user is blocked.
    elif matched and source == "user":
        decision = "BLOCK"
        sanitized_content = None

    # For untrusted sources, sanitize only if the suspicious
    # sentence can be isolated safely.
    elif matched and source in ("retrieved_document", "tool_output"):
        sentences = re.split(r"(?<=[.!?])\s+", content.strip())
        safe_sentences = []
        removed = False

        for sentence in sentences:
            normalized_sentence = normalize(sentence)

            if any(
                pattern.search(normalized_sentence)
                for pattern in ATTACK_PATTERNS
            ):
                removed = True
            else:
                safe_sentences.append(sentence)

        if removed and safe_sentences:
            decision = "SANITIZE"
            sanitized_content = " ".join(safe_sentences).strip()
            reasons.append(
                "Recognized suspicious sentence removed."
            )
        else:
            decision = "ESCALATE"
            sanitized_content = None
            reasons.append(
                "Suspicious content could not be isolated safely."
            )

    # Uncertain security-related content requires review.
    elif ambiguous:
        decision = "ESCALATE"
        sanitized_content = None

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
