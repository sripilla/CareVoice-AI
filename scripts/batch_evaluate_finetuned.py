"""
Fine-tuned Whisper comparison for all languages with a fine-tune
available (Telugu, Kannada, Tamil).

For single-language runs, use the per-language scripts instead:
    scripts/batch_evaluate_finetuned_telugu.py
    scripts/batch_evaluate_finetuned_kannada.py
    scripts/batch_evaluate_finetuned_tamil.py

For comparison against the baseline large-v3 results, see
batch_evaluate_telugu.py / batch_evaluate_kannada.py / batch_evaluate_tamil.py.

See finetuned_common.py for the shared evaluation logic, and
finetuned_whisper.py for which model is used per language.

Usage:
    python scripts/batch_evaluate_finetuned.py
"""

from finetuned_common import run_finetuned

ENABLED_LANGUAGES = ["telugu", "kannada", "tamil"]

if __name__ == "__main__":
    run_finetuned(ENABLED_LANGUAGES)
