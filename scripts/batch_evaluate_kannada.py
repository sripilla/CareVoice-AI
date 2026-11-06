"""
Batch evaluation for Kannada only (KA01-KA15).

Usage:
    python scripts/batch_evaluate_kannada.py
"""

from batch_common import RESULTS_DIR, run

if __name__ == "__main__":
    run(["kannada"], RESULTS_DIR / "kannada")
