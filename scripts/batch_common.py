"""
Shared logic for the per-language batch evaluation scripts
(batch_evaluate_telugu.py, batch_evaluate_kannada.py,
batch_evaluate_hindi.py, batch_evaluate_english.py) and the
all-languages batch_evaluate.py.

Walks data/raw_audio/<language>/*.wav, runs each file through the
speech recognition + language detection stage, and compares the
output against the reference data in
data/metadata/<language>_ground_truth.json.

Currently computes:
    - Word Error Rate (WER)
    - Character Error Rate (CER)
    - Language Detection Accuracy
    - Average Processing Time

Other metrics (BLEU, ROUGE-L, Entity Extraction F1, Risk Assessment
Accuracy/F1) need additional ground-truth fields (reference
translation, reference summary, reference entities, reference risk
level) that aren't collected yet. Once those are added to the
ground-truth JSON files, this module can be extended to run the full
pipeline (translation, summarization, extraction, risk assessment)
and score those stages too.
"""

import csv
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from careinsight.engine import CareVoiceEngine
from config import BASE_DIR

try:
    import jiwer
except ImportError:
    jiwer = None

if jiwer is not None:
    # Normalize case/punctuation/whitespace before comparing, so
    # formatting differences between the reference text and Whisper's
    # raw output (e.g. "Doctor," vs "doctor") aren't counted as word
    # errors.
    WER_TRANSFORM = jiwer.Compose(
        [
            jiwer.ToLowerCase(),
            jiwer.RemovePunctuation(),
            jiwer.RemoveMultipleSpaces(),
            jiwer.Strip(),
            jiwer.ReduceToListOfListOfWords(),
        ]
    )

    # Same normalization, but reduced to characters instead of words,
    # for Character Error Rate.
    CER_TRANSFORM = jiwer.Compose(
        [
            jiwer.ToLowerCase(),
            jiwer.RemovePunctuation(),
            jiwer.RemoveMultipleSpaces(),
            jiwer.Strip(),
            jiwer.ReduceToListOfListOfChars(),
        ]
    )
else:
    WER_TRANSFORM = None
    CER_TRANSFORM = None

RAW_AUDIO_DIR = BASE_DIR / "data" / "raw_audio"
METADATA_DIR = BASE_DIR / "data" / "metadata"
RESULTS_DIR = BASE_DIR / "reports" / "batch_evaluation"

LANGUAGE_CODES = {
    "telugu": "te",
    "kannada": "kn",
    "hindi": "hi",
    "english": "en",
    "tamil": "ta",
}

# Per-language cap on file number (e.g. only KA01-KA15, skipping any
# higher-numbered files that don't have audio yet).
MAX_FILE_NUMBER = {
    "kannada": 15,
}


def file_number(audio_path: Path) -> int | None:
    """
    Extract the trailing number from a filename like 'KA07.wav' -> 7.
    Returns None if the filename doesn't end in digits.
    """

    digits = "".join(
        ch for ch in audio_path.stem if ch.isdigit()
    )

    return int(digits) if digits else None


def load_ground_truth(language: str) -> dict:
    """
    Load the reference data for a language, if it exists.
    """

    gt_file = METADATA_DIR / f"{language}_ground_truth.json"

    if not gt_file.exists():
        return {}

    with open(gt_file, encoding="utf-8") as f:
        return json.load(f)


def word_error_rate(reference: str, hypothesis: str):
    """
    Compute WER between a reference and hypothesis transcript.
    Returns None if jiwer isn't installed or either string is empty.
    """

    if jiwer is None:
        return None

    if not reference.strip() or not hypothesis.strip():
        return None

    return jiwer.wer(
        reference,
        hypothesis,
        reference_transform=WER_TRANSFORM,
        hypothesis_transform=WER_TRANSFORM,
    )


def character_error_rate(reference: str, hypothesis: str):
    """
    Compute CER between a reference and hypothesis transcript.
    Returns None if jiwer isn't installed or either string is empty.
    """

    if jiwer is None:
        return None

    if not reference.strip() or not hypothesis.strip():
        return None

    return jiwer.cer(
        reference,
        hypothesis,
        reference_transform=CER_TRANSFORM,
        hypothesis_transform=CER_TRANSFORM,
    )


def evaluate(languages: list[str]) -> list[dict]:
    """
    Run speech recognition + language detection on every audio file
    under the given languages, scoring against ground truth where
    available.
    """

    engine = CareVoiceEngine()

    rows = []

    for language in languages:

        expected_code = LANGUAGE_CODES.get(language)

        if expected_code is None:
            print(f"Skipping '{language}': unknown language.")
            continue

        audio_dir = RAW_AUDIO_DIR / language

        if not audio_dir.exists():
            print(f"Skipping '{language}': {audio_dir} not found.")
            continue

        ground_truth = load_ground_truth(language)

        max_number = MAX_FILE_NUMBER.get(language)

        for audio_path in sorted(audio_dir.glob("*.wav")):

            if max_number is not None:
                number = file_number(audio_path)
                if number is not None and number > max_number:
                    continue

            entry = ground_truth.get(audio_path.name)

            start = time.perf_counter()

            try:
                transcript, detected_language = engine._transcribe_audio(
                    str(audio_path)
                )
            except Exception as exc:
                print(f"[{language}] {audio_path.name}: FAILED ({exc})")
                rows.append(
                    {
                        "file": audio_path.name,
                        "language_folder": language,
                        "error": str(exc),
                    }
                )
                continue

            elapsed = time.perf_counter() - start

            row = {
                "file": audio_path.name,
                "language_folder": language,
                "expected_language": expected_code,
                "detected_language": detected_language,
                "language_correct": detected_language == expected_code,
                "transcript": transcript,
                "processing_time_sec": round(elapsed, 2),
                "reference_transcript": None,
                "wer": None,
                "cer": None,
            }

            if entry and entry.get("reference_transcript"):
                wer = word_error_rate(
                    entry["reference_transcript"],
                    transcript,
                )
                cer = character_error_rate(
                    entry["reference_transcript"],
                    transcript,
                )
                row["reference_transcript"] = entry["reference_transcript"]
                row["wer"] = round(wer, 4) if wer is not None else None
                row["cer"] = round(cer, 4) if cer is not None else None

            rows.append(row)

            print(
                f"[{language}] {audio_path.name}: "
                f"lang={detected_language} "
                f"({'OK' if row['language_correct'] else 'MISMATCH'}), "
                f"wer={row['wer']}, "
                f"cer={row['cer']}, "
                f"time={elapsed:.2f}s"
            )

    return rows


def summarize(rows: list[dict]) -> dict:
    """
    Aggregate per-file results into overall metrics.
    """

    valid_lang = [r for r in rows if "language_correct" in r]
    valid_wer = [r for r in rows if r.get("wer") is not None]
    valid_cer = [r for r in rows if r.get("cer") is not None]
    valid_time = [r for r in rows if "processing_time_sec" in r]

    lang_accuracy = (
        sum(r["language_correct"] for r in valid_lang) / len(valid_lang)
        if valid_lang
        else None
    )

    avg_wer = (
        sum(r["wer"] for r in valid_wer) / len(valid_wer)
        if valid_wer
        else None
    )

    avg_cer = (
        sum(r["cer"] for r in valid_cer) / len(valid_cer)
        if valid_cer
        else None
    )

    avg_time = (
        sum(r["processing_time_sec"] for r in valid_time) / len(valid_time)
        if valid_time
        else None
    )

    print("\n=== Summary ===")
    print(f"Files evaluated: {len(rows)}")

    print(
        f"Language Detection Accuracy: {lang_accuracy:.2%}"
        if lang_accuracy is not None
        else "Language Detection Accuracy: N/A"
    )

    print(
        f"Average WER: {avg_wer:.4f}"
        if avg_wer is not None
        else "Average WER: N/A (no matching reference transcripts)"
    )

    print(
        f"Average CER: {avg_cer:.4f}"
        if avg_cer is not None
        else "Average CER: N/A (no matching reference transcripts)"
    )

    print(
        f"Average Processing Time: {avg_time:.2f}s"
        if avg_time is not None
        else "Average Processing Time: N/A"
    )

    return {
        "files_evaluated": len(rows),
        "language_detection_accuracy": lang_accuracy,
        "average_wer": avg_wer,
        "average_cer": avg_cer,
        "average_processing_time_sec": avg_time,
    }


def save_results(rows: list[dict], summary: dict, output_dir: Path = RESULTS_DIR):
    """
    Save per-file results as CSV and the aggregate summary as JSON
    into output_dir.
    """

    output_dir.mkdir(parents=True, exist_ok=True)

    csv_path = output_dir / "per_file_results.csv"

    fieldnames = sorted({key for row in rows for key in row.keys()})

    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    summary_path = output_dir / "summary.json"

    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    print(f"\nPer-file results saved to: {csv_path}")
    print(f"Summary saved to: {summary_path}")


def run(languages: list[str], output_dir: Path = RESULTS_DIR):
    """
    Convenience entry point: evaluate, summarize, and save results
    for the given languages.
    """

    rows = evaluate(languages)
    summary = summarize(rows)
    save_results(rows, summary, output_dir)
