"""
Device and precision selection.

Kept out of config.py so that importing configuration never drags in
torch -- the API schemas and the Streamlit client both import config
and neither should pay for a torch import.
"""

from utils.logger import get_logger

logger = get_logger(__name__)

_RESOLVED_DEVICE = None


def resolve_device(preference: str = "auto") -> str:
    """
    Return the best available torch device name.

    Order of preference: CUDA (NVIDIA, including Jetson Orin), then
    MPS (Apple Silicon), then CPU.

    Parameters
    ----------
    preference : str
        "auto", "cuda", "mps" or "cpu". An explicit choice is honoured
        if the backend is actually available, and warned about and
        downgraded if it is not.
    """

    global _RESOLVED_DEVICE

    if _RESOLVED_DEVICE and preference == "auto":
        return _RESOLVED_DEVICE

    import torch

    available = {"cpu"}

    if torch.cuda.is_available():
        available.add("cuda")

    if (
        hasattr(torch.backends, "mps")
        and torch.backends.mps.is_available()
    ):
        available.add("mps")

    if preference != "auto":

        if preference in available:
            device = preference

        else:
            logger.warning(
                "Requested device '%s' is not available "
                "(available: %s). Falling back to CPU.",
                preference,
                ", ".join(sorted(available)),
            )
            device = "cpu"

    elif "cuda" in available:
        device = "cuda"

    elif "mps" in available:
        device = "mps"

    else:
        device = "cpu"

    if preference == "auto":
        _RESOLVED_DEVICE = device

    logger.info(
        "Using device: %s (available: %s)",
        device,
        ", ".join(sorted(available)),
    )

    return device


def resolve_dtype(device: str, preference: str = "auto"):
    """
    Return the torch dtype to load models with.

    Defaults are deliberately conservative:

    - CUDA  -> float16. Well-trodden, halves memory, and on a Jetson
      Orin it is what makes the larger models fit at all.
    - MPS   -> float32. Apple Silicon has the unified memory to spare,
      and float16 on MPS still produces NaNs in some seq2seq stacks.
      Set CAREVOICE_DTYPE=float16 to trade that safety for speed.
    - CPU   -> float32. float16 on CPU is slower, not faster.
    """

    import torch

    named = {
        "float16": torch.float16,
        "float32": torch.float32,
        "bfloat16": torch.bfloat16,
    }

    if preference != "auto":

        if preference not in named:
            raise ValueError(
                f"Unknown dtype '{preference}'. "
                f"Expected one of: {', '.join(named)}."
            )

        return named[preference]

    if device == "cuda":
        return torch.float16

    return torch.float32


def describe(device: str, dtype) -> str:
    """
    Short human-readable label for logs and the dashboard.
    """

    return f"{device}/{str(dtype).replace('torch.', '')}"
