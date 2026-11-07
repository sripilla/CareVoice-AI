"""
Shared logic for the per-language fine-tuned Whisper comparison
scripts (batch_evaluate_finetuned_telugu.py,
batch_evaluate_finetuned_kannada.py, batch_evaluate_finetuned_tamil.py)
and the all-languages batch_evaluate_finetuned.py.

Writes results to reports/batch_evaluation_finetuned/<language>/,
separate from the baseline large-v3 results directory
(reports/batch_evaluation/<language>/), so both can be compared side
by side.
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
from finetuned_whisper import FINETUNED_MODELS, FineTunedTranscriber

FINETUNED_RESULTS_DIR = RESULTS_DIR.parent / "batch_evaluation_finetuned"

LANGUAGE_CODES = {
    "telugu": "te",
    "kannada": "kn",
    "tamil": "ta",
}


def evaluate_finetuned(languages: list[str]) -> list[dict]:
    """
    Run the fine-tuned model for each language against its audio
    files, scoring against the same ground truth used for the
    baseline comparison.
    """

    rows = []

    for language in languages:

        expected_code = LANGUAGE_CODES.get(language)

        if expected_code not in FINETUNED_MODELS:
            print(
                f"Skipping '{language}': no fine-tuned model configured."
            )
            continue

        audio_dir = RAW_AUDIO_DIR / language

        if not audio_dir.exists():
            print(f"Skipping '{language}': {audio_dir} not found.")
            continue

        print(
            f"Loading fine-tuned model for '{language}' "
            f"({FINETUNED_MODELS[expected_code]})..."
        )

        transcriber = FineTunedTranscriber(expected_code)

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
                transcript = transcriber.transcribe(str(audio_path))
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
                "model": FINETUNED_MODELS[expected_code],
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
                f"wer={row['wer']}, "
                f"cer={row['cer']}, "
                f"time={elapsed:.2f}s"
            )

    return rows


def run_finetuned(languages: list[str]):
    """
    Convenience entry point: evaluate, summarize, and save fine-tuned
    results for the given languages, one output directory per
    language.
    """

    results = evaluate_finetuned(languages)

    for language in languages:
        language_rows = [
            r for r in results if r.get("language_folder") == language
        ]

        if not language_rows:
            continue

        print(f"\n--- {language} (fine-tuned) ---")
        summary = summarize(language_rows)
        save_results(
            language_rows,
            summary,
            FINETUNED_RESULTS_DIR / language,
        )
