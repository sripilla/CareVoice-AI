"""
Batch evaluation for Telugu only.

Usage:
    python scripts/batch_evaluate_telugu.py
"""

from batch_common import RESULTS_DIR, run

if __name__ == "__main__":
    run(["telugu"], RESULTS_DIR / "telugu")
