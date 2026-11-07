"""
Fine-tuned Whisper comparison for Tamil only
(vasista22/whisper-tamil-large-v2).

Usage:
    python scripts/batch_evaluate_finetuned_tamil.py
"""

from finetuned_common import run_finetuned

if __name__ == "__main__":
    run_finetuned(["tamil"])
