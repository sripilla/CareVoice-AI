"""
Language sanity checks.

Whisper occasionally misdetects Indian-language audio as English and
emits a romanized transliteration ("No Peru Lakshmi" for "Naa peru
Lakshmi"). Text like that contains almost no common English words,
so the ratio of recognised tokens separates real English from a
transliterated transcript without loading any model.
"""

import re

from config import ENGLISH_WORD_RATIO_THRESHOLD
from utils.logger import get_logger

logger = get_logger(__name__)

COMMON_ENGLISH_WORDS = {
    "the", "a", "an", "and", "or", "but", "if", "then", "so",
    "in", "on", "at", "for", "to", "of", "with", "from", "by",
    "as", "is", "are", "was", "were", "be", "been", "being",
    "have", "has", "had", "do", "does", "did", "will", "would",
    "can", "could", "should", "shall", "may", "might", "must",
    "i", "you", "he", "she", "it", "we", "they", "me", "him",
    "her", "us", "them", "my", "your", "his", "its", "our",
    "their", "this", "that", "these", "those", "not", "no",
    "yes", "am", "what", "when", "where", "who", "how", "why",
    "there", "here", "also", "very", "only", "all", "some",
    "any", "every", "each", "more", "most", "much", "many",
    "name", "age", "years", "year", "old", "day", "days",
    "week", "weeks", "month", "months", "night", "morning",
    "time", "since", "past", "last", "now", "today", "get",
    "gets", "getting", "take", "taking", "feel", "feeling",
    "pain", "fever", "cough", "cold", "sleep", "unable",
    "medicine", "doctor", "patient", "problem", "worse",
    "better", "severe", "mild",
}


def looks_like_english(text: str) -> bool:
    """
    Heuristically decide whether text is English.

    Returns True when a sufficient fraction of alphabetic tokens
    are common English words. Non-Latin text and romanized
    transliterations both score near zero.
    """

    tokens = re.findall(r"[a-zA-Z]+", text.lower())

    if not tokens:
        return False

    matches = sum(
        1
        for token in tokens
        if token in COMMON_ENGLISH_WORDS
    )

    ratio = matches / len(tokens)

    logger.debug(
        "English word ratio: %.2f (%d/%d tokens)",
        ratio,
        matches,
        len(tokens),
    )

    return ratio >= ENGLISH_WORD_RATIO_THRESHOLD
