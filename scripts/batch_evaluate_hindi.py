"""
Batch evaluation for Hindi only.

Usage:
    python scripts/batch_evaluate_hindi.py
"""

from batch_common import RESULTS_DIR, run

if __name__ == "__main__":
    run(["hindi"], RESULTS_DIR / "hindi")
