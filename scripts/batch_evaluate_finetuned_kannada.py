"""
Fine-tuned Whisper comparison for Kannada only
(vasista22/whisper-kannada-medium).

Usage:
    python scripts/batch_evaluate_finetuned_kannada.py
"""

from finetuned_common import run_finetuned

if __name__ == "__main__":
    run_finetuned(["kannada"])
