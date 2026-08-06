"""
The English heuristic that guards against Whisper language
misdetection.

The romanized sample below is the real failure this project hit:
Telugu audio detected as English, transcribed as a transliteration,
and passed through the pipeline as if it were English.
"""

from utils.language import looks_like_english

ROMANIZED_TELUGU = (
    "No Peru Lakshmi. No 70 Samchral. Gatamudu Rozruluga Naku "
    "Daggu Peryu Telekpati Jhuram Wunnai. Raptri time Lo Daggu "
    "Ekku Ga Vastundi. Sarigga Niddra Pattadam Leedu."
)


def test_accepts_real_english():

    assert looks_like_english(
        "My name is Lakshmi. I am 70 years old. I have had a "
        "cough and a mild fever for three days."
    )


def test_accepts_short_english():

    assert looks_like_english(
        "I have a headache since yesterday."
    )


def test_accepts_translated_phrasing():

    assert looks_like_english(
        "My name is Lakshmi. My age is 70 years. I have had a "
        "cough and mild fever for the last three days."
    )


def test_rejects_romanized_telugu():

    assert not looks_like_english(ROMANIZED_TELUGU)


def test_rejects_native_script():

    assert not looks_like_english(
        "నా పేరు లక్ష్మి. నా వయసు 70 సంవత్సరాలు."
    )


def test_rejects_empty_text():

    assert not looks_like_english("")
    assert not looks_like_english("   ")
    assert not looks_like_english("123 456")
