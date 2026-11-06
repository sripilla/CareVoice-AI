"""
Batch evaluation for English only.

Usage:
    python scripts/batch_evaluate_english.py
"""

from batch_common import RESULTS_DIR, run

if __name__ == "__main__":
    run(["english"], RESULTS_DIR / "english")
