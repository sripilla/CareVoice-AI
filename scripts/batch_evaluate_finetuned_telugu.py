"""
Fine-tuned Whisper comparison for Telugu only
(vasista22/whisper-telugu-large-v2).

Usage:
    python scripts/batch_evaluate_finetuned_telugu.py
"""

from finetuned_common import run_finetuned

if __name__ == "__main__":
    run_finetuned(["telugu"])
