"""
Batch evaluation for all languages (Telugu, Kannada, Hindi, English).

For single-language runs, use the per-language scripts instead:
    scripts/batch_evaluate_telugu.py
    scripts/batch_evaluate_kannada.py
    scripts/batch_evaluate_hindi.py
    scripts/batch_evaluate_english.py

See batch_common.py for the shared evaluation logic and what metrics
are currently computed.

Usage:
    python scripts/batch_evaluate.py
"""

from batch_common import RESULTS_DIR, run

ENABLED_LANGUAGES = ["telugu", "kannada", "hindi", "english"]

if __name__ == "__main__":
    run(ENABLED_LANGUAGES, RESULTS_DIR)
