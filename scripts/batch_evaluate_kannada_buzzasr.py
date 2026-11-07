"""
Batch evaluation for Kannada using BuzzASR/kannada (large-v3-based),
as an alternative to the vasista22/whisper-kannada-medium fine-tune
already compared in batch_evaluate_finetuned_kannada.py.

Kept fully separate from finetuned_whisper.py / finetuned_common.py /
batch_evaluate_finetuned_kannada.py, which are left untouched.

Writes results to reports/batch_evaluation_kannada_buzzasr/, separate
from both the large-v3 baseline (reports/batch_evaluation/kannada/)
and the vasista22 fine-tune (reports/batch_evaluation_finetuned/kannada/),
so all three can be compared side by side.

Usage:
    python scripts/batch_evaluate_kannada_buzzasr.py
"""

import time

from batch_common import (
    MAX_FILE_NUMBER,
    RAW_AUDIO_DIR,
    RESULTS_DIR,
    character_error_rate,
    file_number,
    load_ground_truth,
    save_results,
    summarize,
    word_error_rate,
)
from kannada_largev3_whisper import MODEL_NAME, KannadaLargeV3Transcriber

OUTPUT_DIR = RESULTS_DIR.parent / "batch_evaluation_kannada_buzzasr"


def evaluate() -> list[dict]:
    """
    Run BuzzASR/kannada against the Kannada audio files, scoring
    against the same ground truth used for the other Kannada runs.
    """

    audio_dir = RAW_AUDIO_DIR / "kannada"

    if not audio_dir.exists():
        print(f"'{audio_dir}' not found.")
        return []

    print(f"Loading {MODEL_NAME}...")

    transcriber = KannadaLargeV3Transcriber()

    ground_truth = load_ground_truth("kannada")

    max_number = MAX_FILE_NUMBER.get("kannada")

    rows = []

    for audio_path in sorted(audio_dir.glob("*.wav")):

        if max_number is not None:
            number = file_number(audio_path)
            if number is not None and number > max_number:
                continue

        entry = ground_truth.get(audio_path.name)

        start = time.perf_counter()

        try:
            transcript = transcriber.transcribe(str(audio_path))
        except Exception as exc:
            print(f"{audio_path.name}: FAILED ({exc})")
            rows.append(
                {
                    "file": audio_path.name,
                    "model": MODEL_NAME,
                    "error": str(exc),
                }
            )
            continue

        elapsed = time.perf_counter() - start

        row = {
            "file": audio_path.name,
            "model": MODEL_NAME,
            "transcript": transcript,
            "processing_time_sec": round(elapsed, 2),
            "reference_transcript": None,
            "wer": None,
            "cer": None,
        }

        if entry and entry.get("reference_transcript"):
            wer = word_error_rate(entry["reference_transcript"], transcript)
            cer = character_error_rate(
                entry["reference_transcript"],
                transcript,
            )
            row["reference_transcript"] = entry["reference_transcript"]
            row["wer"] = round(wer, 4) if wer is not None else None
            row["cer"] = round(cer, 4) if cer is not None else None

        rows.append(row)

        print(
            f"{audio_path.name}: "
            f"wer={row['wer']}, "
            f"cer={row['cer']}, "
            f"time={elapsed:.2f}s"
        )

    return rows


if __name__ == "__main__":
    results = evaluate()

    if results:
        summary = summarize(results)
        save_results(results, summary, OUTPUT_DIR)
