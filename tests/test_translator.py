"""
Chunking and the graceful-degradation paths.

These branches never touch the model, so the tests build the
Translator without running __init__ (which would download NLLB).
"""

import pytest

from conftest import skip_without
from config import TRANSLATION_CHUNK_CHARS

# Guard on torch rather than transformers: transformers imports its
# submodules lazily, so `import transformers` succeeds even when the
# torch native libraries (Microsoft Visual C++ runtime on Windows)
# are missing.
skip_without(
    "torch",
    "Translation stack unavailable on this host",
)

from translation.translator import Translator  # noqa: E402


@pytest.fixture
def translator():
    """
    A Translator with no model loaded.
    """

    return object.__new__(Translator)


# ==========================================================
# Chunking
# ==========================================================

def test_short_text_is_a_single_chunk(translator):

    assert translator._chunk("I have a fever.") == [
        "I have a fever."
    ]


def test_long_text_is_split_on_sentence_boundaries(translator):

    sentence = "The patient reports a persistent cough. "

    text = sentence * 40

    chunks = translator._chunk(text)

    assert len(chunks) > 1

    # Every chunk stays inside the model's window...
    assert all(
        len(chunk) <= TRANSLATION_CHUNK_CHARS
        for chunk in chunks
    )

    # ...and nothing is dropped.
    assert "".join(chunks).count("persistent cough") == 40


def test_devanagari_danda_ends_a_sentence(translator):

    text = ("मुझे बुखार है। " * 60).strip()

    chunks = translator._chunk(text)

    assert len(chunks) > 1
    assert all(chunk.strip() for chunk in chunks)


def test_single_oversized_sentence_is_not_dropped(translator):

    # No sentence boundary to split on anywhere.
    text = "word " * (TRANSLATION_CHUNK_CHARS)

    chunks = translator._chunk(text)

    assert len(chunks) == 1
    assert chunks[0].startswith("word")


def test_chunking_preserves_all_sentences(translator):

    sentences = [
        f"Sentence number {index}."
        for index in range(60)
    ]

    chunks = translator._chunk(" ".join(sentences))

    rejoined = " ".join(chunks)

    for sentence in sentences:
        assert sentence in rejoined


# ==========================================================
# Degradation
# ==========================================================

def test_empty_transcript_warns_instead_of_failing(translator):

    result = translator.translate_with_meta("   ", "te")

    assert result["text"] == ""
    assert result["translated"] is False
    assert result["warnings"]


def test_english_passes_through_untranslated(translator):

    result = translator.translate_with_meta(
        "I have a fever.",
        "en",
    )

    assert result["text"] == "I have a fever."
    assert result["translated"] is False
    assert result["warnings"] == []


def test_unsupported_language_degrades_with_a_warning(translator):

    # French is not in LANGUAGE_MAP. The old behaviour raised
    # ValueError, which surfaced as an opaque HTTP 500.
    result = translator.translate_with_meta(
        "J'ai de la fievre.",
        "fr",
    )

    assert result["text"] == "J'ai de la fievre."
    assert result["translated"] is False
    assert len(result["warnings"]) == 1
    assert "fr" in result["warnings"][0]
