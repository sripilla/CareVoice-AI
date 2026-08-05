"""
Side-by-side comparison of speech and translation models.

The current pipeline is a *cascade*: Telugu speech -> Telugu text ->
English text. Errors compound, so a small ASR slip becomes a large
translation error ("రెండు రోజుల" -> "రెండ్ రోల్" -> "Red Roll").
This script measures each stage separately and also tries models that
collapse both stages into one.

Usage
-----
    python -m scripts.benchmark_models --list
    python -m scripts.benchmark_models --audio data/raw_audio/telugu/TE001.wav \
        --candidates baseline,indictrans2

Each candidate downloads its own weights on first run. Sizes are shown
by --list; on CPU expect minutes per candidate.
"""

import argparse
import json
import time
from pathlib import Path

from utils.logger import get_logger

logger = get_logger(__name__)

RESULTS_PATH = Path("benchmark_results.json")


# ==========================================================
# Speech recognition candidates
# ==========================================================

def asr_whisper(audio_path: str, model_name: str) -> dict:
    """
    Faster-Whisper transcription (the current approach).
    """

    from faster_whisper import WhisperModel

    model = WhisperModel(
        model_name,
        device="cpu",
        compute_type="int8",
    )

    segments, info = model.transcribe(audio_path, beam_size=5)

    text = " ".join(
        segment.text for segment in segments
    ).strip()

    return {
        "text": text,
        "language": info.language,
        "confidence": round(info.language_probability, 3),
    }


def asr_whisper_telugu(audio_path: str) -> dict:
    """
    A Whisper checkpoint fine-tuned specifically on Telugu.

    Generic Whisper has to infer the script from the audio, which is
    where it fails -- it has written Telugu speech in Devanagari.
    A Telugu-only model cannot make that mistake.
    """

    import torch
    from transformers import (
        AutoModelForSpeechSeq2Seq,
        AutoProcessor,
    )

    name = "vasista22/whisper-telugu-large-v2"

    processor = AutoProcessor.from_pretrained(name)
    model = AutoModelForSpeechSeq2Seq.from_pretrained(name)
    model.eval()

    audio = _load_audio(audio_path)

    inputs = processor(
        audio,
        sampling_rate=16000,
        return_tensors="pt",
    )

    forced = processor.get_decoder_prompt_ids(
        language="te",
        task="transcribe",
    )

    with torch.no_grad():
        generated = model.generate(
            inputs.input_features,
            forced_decoder_ids=forced,
            max_new_tokens=440,
        )

    text = processor.batch_decode(
        generated,
        skip_special_tokens=True,
    )[0]

    return {
        "text": text.strip(),
        "language": "te",
        "confidence": None,
    }


# ==========================================================
# Translation candidates
# ==========================================================

def mt_nllb(text: str) -> str:
    """
    NLLB-200 distilled 600M -- the current translator.
    """

    from transformers import (
        AutoModelForSeq2SeqLM,
        AutoTokenizer,
    )

    name = "facebook/nllb-200-distilled-600M"

    tokenizer = AutoTokenizer.from_pretrained(name)
    model = AutoModelForSeq2SeqLM.from_pretrained(name)

    tokenizer.src_lang = "tel_Telu"

    inputs = tokenizer(
        text,
        return_tensors="pt",
        truncation=True,
        max_length=512,
    )

    generated = model.generate(
        **inputs,
        forced_bos_token_id=tokenizer.convert_tokens_to_ids(
            "eng_Latn"
        ),
        max_length=512,
    )

    return tokenizer.batch_decode(
        generated,
        skip_special_tokens=True,
    )[0]


def mt_indictrans2(text: str) -> str:
    """
    AI4Bharat IndicTrans2, purpose-built for the 22 scheduled
    Indian languages. Reported to beat NLLB-54B, Google and GPT-3.5
    on Indic pairs despite being far smaller.
    """

    import torch
    from transformers import (
        AutoModelForSeq2SeqLM,
        AutoTokenizer,
    )

    name = "ai4bharat/indictrans2-indic-en-dist-200M"

    tokenizer = AutoTokenizer.from_pretrained(
        name,
        trust_remote_code=True,
    )

    model = AutoModelForSeq2SeqLM.from_pretrained(
        name,
        trust_remote_code=True,
    )

    model.eval()

    # IndicTrans2 expects explicit source/target language tags.
    tagged = f"tel_Telu eng_Latn {text}"

    inputs = tokenizer(
        tagged,
        return_tensors="pt",
        truncation=True,
        max_length=256,
    )

    with torch.no_grad():
        generated = model.generate(
            **inputs,
            max_length=256,
            num_beams=5,
        )

    return tokenizer.batch_decode(
        generated,
        skip_special_tokens=True,
    )[0]


# ==========================================================
# Direct speech-to-English (no cascade)
# ==========================================================

def s2tt_seamless(audio_path: str) -> dict:
    """
    SeamlessM4T v2 translates speech straight to English text.

    This removes the intermediate Telugu transcript entirely, so an
    ASR spelling slip can no longer be re-interpreted as a different
    English word.
    """

    import torch
    from transformers import (
        AutoProcessor,
        SeamlessM4Tv2ForSpeechToText,
    )

    name = "facebook/seamless-m4t-v2-large"

    processor = AutoProcessor.from_pretrained(name)
    model = SeamlessM4Tv2ForSpeechToText.from_pretrained(name)
    model.eval()

    audio = _load_audio(audio_path)

    inputs = processor(
        audios=audio,
        sampling_rate=16000,
        return_tensors="pt",
    )

    with torch.no_grad():
        generated = model.generate(
            **inputs,
            tgt_lang="eng",
        )

    english = processor.batch_decode(
        generated,
        skip_special_tokens=True,
    )[0]

    return {
        "text": english.strip(),
        "language": "direct",
        "confidence": None,
    }


# ==========================================================
# Helpers
# ==========================================================

def _load_audio(audio_path: str):
    """
    Decode any supported container to 16 kHz mono float32.

    Reuses faster-whisper's PyAV-backed decoder so no extra
    dependency or ffmpeg binary is needed.
    """

    from faster_whisper.audio import decode_audio

    return decode_audio(audio_path, sampling_rate=16000)


# ==========================================================
# Candidates
# ==========================================================

def _pipeline(name: str):
    """
    Run one of the engine's real pipeline backends.

    Benchmarking the actual production code path -- rather than a
    parallel reimplementation -- is what makes the winner directly
    adoptable: set CAREVOICE_PIPELINE to it and you are done.
    """

    from careinsight.pipelines import build_pipeline

    result = build_pipeline(name).to_english

    def run(audio: str) -> dict:

        outcome = result(audio)

        return {
            "transcript": (
                outcome.original_transcript
                or "(no intermediate transcript)"
            ),
            "english": outcome.english_transcript,
            "language": outcome.detected_language,
            "confidence": outcome.language_probability,
            "warnings": outcome.warnings,
        }

    return run


CANDIDATES = {
    "cascade": {
        "label": "PIPELINE=cascade (Whisper -> NLLB, current)",
        "size": "~4 GB",
        "run": lambda audio: _pipeline("cascade")(audio),
    },
    "seamless-pipeline": {
        "label": "PIPELINE=seamless (direct speech -> English)",
        "size": "~9 GB",
        "run": lambda audio: _pipeline("seamless")(audio),
    },
    "indic-pipeline": {
        "label": "PIPELINE=indic (Whisper -> IndicTrans2, gated)",
        "size": "~6 GB",
        "run": lambda audio: _pipeline("indic")(audio),
    },
    "baseline": {
        "label": "Whisper large-v3 -> NLLB-600M (raw, no pipeline)",
        "size": "~4 GB",
        "run": lambda audio: _cascade(
            asr_whisper(audio, "large-v3"),
            mt_nllb,
        ),
    },
    "indictrans2": {
        "label": "Whisper large-v3 -> IndicTrans2-200M",
        "size": "~2 GB (+baseline ASR)",
        "run": lambda audio: _cascade(
            asr_whisper(audio, "large-v3"),
            mt_indictrans2,
        ),
    },
    "telugu-asr": {
        "label": "Whisper-Telugu-large-v2 -> IndicTrans2-200M",
        "size": "~7 GB",
        "run": lambda audio: _cascade(
            asr_whisper_telugu(audio),
            mt_indictrans2,
        ),
    },
    "seamless": {
        "label": "SeamlessM4T v2 direct speech -> English",
        "size": "~9 GB",
        "run": lambda audio: _direct(s2tt_seamless(audio)),
    },
}


def _cascade(asr_result: dict, translate) -> dict:
    """
    Run a two-stage candidate and keep both intermediate texts.
    """

    english = (
        translate(asr_result["text"])
        if asr_result["text"]
        else ""
    )

    return {
        "transcript": asr_result["text"],
        "english": english,
        "language": asr_result["language"],
        "confidence": asr_result["confidence"],
    }


def _direct(result: dict) -> dict:
    """
    Run a single-stage candidate.
    """

    return {
        "transcript": "(no intermediate transcript)",
        "english": result["text"],
        "language": result["language"],
        "confidence": result["confidence"],
    }


# ==========================================================
# Entry point
# ==========================================================

def main():

    parser = argparse.ArgumentParser(
        description="Compare ASR/translation stacks."
    )

    parser.add_argument(
        "--audio",
        default="data/raw_audio/telugu/TE001.wav",
    )

    parser.add_argument(
        "--candidates",
        default="baseline",
        help="Comma-separated: " + ", ".join(CANDIDATES),
    )

    parser.add_argument(
        "--list",
        action="store_true",
        help="Show available candidates and exit.",
    )

    # Translation-only mode. Skips ASR entirely so only one model is
    # resident at a time -- essential on a memory-constrained host,
    # where loading ASR and MT together exhausts RAM.
    parser.add_argument(
        "--text",
        help="Translate this text instead of transcribing audio.",
    )

    parser.add_argument(
        "--text-file",
        help=(
            "Read the text to translate from this UTF-8 file. "
            "Safer than --text for Indic scripts, which shells "
            "mangle."
        ),
    )

    parser.add_argument(
        "--mt",
        choices=["nllb", "indictrans2"],
        help="Translator to use with --text/--text-file.",
    )

    args = parser.parse_args()

    if args.text_file:
        args.text = Path(args.text_file).read_text(
            encoding="utf-8"
        ).strip()

    if args.text:

        if not args.mt:
            raise SystemExit("--text requires --mt")

        translate = {
            "nllb": mt_nllb,
            "indictrans2": mt_indictrans2,
        }[args.mt]

        started = time.time()

        english = translate(args.text)

        print(f"\n[{args.mt}] {round(time.time() - started, 1)}s")
        print(f"  input  : {args.text}")
        print(f"  english: {english}\n")

        return

    if args.list:

        print("\nAvailable candidates:\n")

        for key, candidate in CANDIDATES.items():
            print(
                f"  {key:<14} {candidate['label']}"
                f"\n  {'':<14} download {candidate['size']}\n"
            )

        return

    audio = Path(args.audio)

    if not audio.exists():
        raise SystemExit(f"Audio not found: {audio}")

    selected = [
        name.strip()
        for name in args.candidates.split(",")
        if name.strip()
    ]

    unknown = set(selected) - set(CANDIDATES)

    if unknown:
        raise SystemExit(
            f"Unknown candidate(s): {', '.join(sorted(unknown))}"
        )

    results = {}

    for name in selected:

        candidate = CANDIDATES[name]

        print(f"\n{'=' * 70}")
        print(f"Running: {candidate['label']}")
        print(f"{'=' * 70}\n")

        started = time.time()

        try:

            outcome = candidate["run"](str(audio))
            outcome["error"] = None

        except Exception as error:

            logger.exception("Candidate '%s' failed.", name)

            outcome = {
                "transcript": "",
                "english": "",
                "language": None,
                "confidence": None,
                "error": f"{type(error).__name__}: {error}",
            }

        outcome["seconds"] = round(time.time() - started, 1)
        outcome["label"] = candidate["label"]

        results[name] = outcome

        _print_result(name, outcome)

    RESULTS_PATH.write_text(
        json.dumps(results, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    print(f"\nSaved to {RESULTS_PATH}\n")


def _print_result(name: str, outcome: dict):

    print(f"[{name}] {outcome['seconds']}s")

    if outcome["error"]:
        print(f"  FAILED: {outcome['error']}")
        return

    print(f"  transcript : {outcome['transcript']}")
    print(f"  english    : {outcome['english']}")


if __name__ == "__main__":
    main()
