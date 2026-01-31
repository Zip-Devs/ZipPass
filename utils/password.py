"""
Password utilities for ZipPass

Improved strength estimation:
- Hard caps for low variety
- Penalties for repetition
- Entropy-driven levels
"""

from __future__ import annotations

import math
import re
import secrets
import string
from dataclasses import dataclass
from collections import Counter
from typing import List


# =========================
# Result model
# =========================

@dataclass(slots=True)
class PasswordStrength:
    score: int                 # 0..100
    entropy: float             # bits
    length: int
    has_lower: bool
    has_upper: bool
    has_digit: bool
    has_symbol: bool
    warnings: List[str]

    @property
    def level(self) -> str:
        if self.score >= 80:
            return "strong"
        if self.score >= 50:
            return "medium"
        return "weak"


# =========================
# Regex
# =========================

_LOWER_RE = re.compile(r"[a-z]")
_UPPER_RE = re.compile(r"[A-Z]")
_DIGIT_RE = re.compile(r"\d")
_SYMBOL_RE = re.compile(rf"[{re.escape(string.punctuation)}]")


# =========================
# Strength estimation
# =========================

def estimate_strength(password: str) -> PasswordStrength:
    warnings: List[str] = []
    length = len(password)

    if not password:
        return PasswordStrength(
            score=0,
            entropy=0.0,
            length=0,
            has_lower=False,
            has_upper=False,
            has_digit=False,
            has_symbol=False,
            warnings=["Empty password"],
        )

    has_lower = bool(_LOWER_RE.search(password))
    has_upper = bool(_UPPER_RE.search(password))
    has_digit = bool(_DIGIT_RE.search(password))
    has_symbol = bool(_SYMBOL_RE.search(password))

    # -------------------------
    # Charset size
    # -------------------------

    charset = 0
    if has_lower:
        charset += 26
    if has_upper:
        charset += 26
    if has_digit:
        charset += 10
    if has_symbol:
        charset += len(string.punctuation)

    entropy = length * math.log2(charset) if charset > 0 else 0.0

    # -------------------------
    # Base score
    # -------------------------

    score = 0

    # Length
    if length >= 16:
        score += 35
    elif length >= 12:
        score += 25
    elif length >= 8:
        score += 15
    else:
        warnings.append("Password is too short")

    # Variety
    variety = sum([has_lower, has_upper, has_digit, has_symbol])
    score += variety * 8

    if variety <= 1:
        warnings.append("Very low character variety")

    # Entropy
    if entropy >= 80:
        score += 25
    elif entropy >= 60:
        score += 15
    elif entropy >= 40:
        score += 5
    else:
        warnings.append("Low entropy")

    # -------------------------
    # Repetition penalty
    # -------------------------

    counter = Counter(password)
    most_common = counter.most_common(1)[0][1]
    repeat_ratio = most_common / length

    if repeat_ratio > 0.5:
        score -= 25
        warnings.append("Too many repeated characters")
    elif repeat_ratio > 0.3:
        score -= 10
        warnings.append("Repeated characters")

    # -------------------------
    # Pattern checks
    # -------------------------

    lower = password.lower()

    if re.search(r"(1234|abcd|qwer|password|admin|login)", lower):
        score -= 15
        warnings.append("Common pattern detected")

    if lower == password or password.upper() == password:
        score -= 10
        warnings.append("Single letter case")

    # -------------------------
    # HARD CAPS (IMPORTANT)
    # -------------------------

    # One charset can never be strong
    if variety == 1:
        score = min(score, 40)

    # Low entropy cannot be medium+
    if entropy < 40:
        score = min(score, 45)

    # Very short passwords are always weak
    if length < 8:
        score = min(score, 30)

    score = max(0, min(100, score))

    return PasswordStrength(
        score=score,
        entropy=round(entropy, 2),
        length=length,
        has_lower=has_lower,
        has_upper=has_upper,
        has_digit=has_digit,
        has_symbol=has_symbol,
        warnings=warnings,
    )


# =========================
# Password generation
# =========================

def generate_password(
    length: int = 16,
    *,
    use_lower: bool = True,
    use_upper: bool = True,
    use_digits: bool = True,
    use_symbols: bool = True,
) -> str:
    if length < 4:
        raise ValueError("Password length must be >= 4")

    pools = []
    if use_lower:
        pools.append(string.ascii_lowercase)
    if use_upper:
        pools.append(string.ascii_uppercase)
    if use_digits:
        pools.append(string.digits)
    if use_symbols:
        pools.append(string.punctuation)

    if not pools:
        raise ValueError("No character sets selected")

    password_chars = [secrets.choice(pool) for pool in pools]
    all_chars = "".join(pools)

    while len(password_chars) < length:
        password_chars.append(secrets.choice(all_chars))

    secrets.SystemRandom().shuffle(password_chars)
    return "".join(password_chars)


# =========================
# Helper
# =========================

def is_strong_enough(password: str, *, min_score: int = 60) -> bool:
    return estimate_strength(password).score >= min_score
