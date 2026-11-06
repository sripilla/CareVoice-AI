"""
Batch evaluation for Tamil only.

Usage:
    python scripts/batch_evaluate_tamil.py
"""

from batch_common import RESULTS_DIR, run

if __name__ == "__main__":
    run(["tamil"], RESULTS_DIR / "tamil")
