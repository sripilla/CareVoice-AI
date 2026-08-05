"""
Device and precision selection.

Backends are faked so the logic is verified on any host, including
CI machines with no GPU.
"""

import pytest

from conftest import skip_without

skip_without("torch", "torch unavailable on this host")

import torch  # noqa: E402

import utils.device as device_module  # noqa: E402
from utils.device import (  # noqa: E402
    describe,
    resolve_device,
    resolve_dtype,
)


@pytest.fixture(autouse=True)
def clear_cache():
    """
    resolve_device memoises the auto result; reset between tests.
    """

    device_module._RESOLVED_DEVICE = None
    yield
    device_module._RESOLVED_DEVICE = None


def _fake_backends(monkeypatch, cuda=False, mps=False):

    monkeypatch.setattr(
        torch.cuda,
        "is_available",
        lambda: cuda,
    )

    monkeypatch.setattr(
        torch.backends.mps,
        "is_available",
        lambda: mps,
    )


# ==========================================================
# Automatic selection
# ==========================================================

def test_prefers_cuda(monkeypatch):

    _fake_backends(monkeypatch, cuda=True, mps=True)

    assert resolve_device("auto") == "cuda"


def test_falls_back_to_mps(monkeypatch):
    """
    Apple Silicon: no CUDA, but Metal is available.
    """

    _fake_backends(monkeypatch, cuda=False, mps=True)

    assert resolve_device("auto") == "mps"


def test_falls_back_to_cpu(monkeypatch):

    _fake_backends(monkeypatch, cuda=False, mps=False)

    assert resolve_device("auto") == "cpu"


# ==========================================================
# Explicit selection
# ==========================================================

def test_explicit_choice_is_honoured(monkeypatch):

    _fake_backends(monkeypatch, cuda=True, mps=True)

    assert resolve_device("mps") == "mps"
    assert resolve_device("cpu") == "cpu"


def test_unavailable_choice_downgrades(monkeypatch):
    """
    Asking for CUDA on a Mac must not crash the pipeline.
    """

    _fake_backends(monkeypatch, cuda=False, mps=True)

    assert resolve_device("cuda") == "cpu"


def test_explicit_choice_is_not_cached(monkeypatch):

    _fake_backends(monkeypatch, cuda=False, mps=True)

    resolve_device("cpu")

    assert resolve_device("auto") == "mps"


# ==========================================================
# Precision
# ==========================================================

def test_cuda_defaults_to_float16():
    """
    Halving memory is what makes the larger models fit on a Jetson.
    """

    assert resolve_dtype("cuda") is torch.float16


def test_mps_defaults_to_float32():
    """
    Apple Silicon has unified memory to spare, and float16 on MPS
    still produces NaNs in some seq2seq stacks. Correctness first.
    """

    assert resolve_dtype("mps") is torch.float32


def test_cpu_defaults_to_float32():

    assert resolve_dtype("cpu") is torch.float32


@pytest.mark.parametrize(
    "name, expected",
    [
        ("float16", torch.float16),
        ("float32", torch.float32),
        ("bfloat16", torch.bfloat16),
    ],
)
def test_explicit_dtype(name, expected):

    assert resolve_dtype("mps", name) is expected


def test_unknown_dtype_is_rejected():

    with pytest.raises(ValueError) as error:
        resolve_dtype("cpu", "float8")

    assert "float8" in str(error.value)


def test_describe_is_readable():

    assert describe("mps", torch.float32) == "mps/float32"


# ==========================================================
# CTranslate2 constraint
# ==========================================================

def test_whisper_downgrades_mps_to_cpu():
    """
    CTranslate2 has no Metal backend. Whisper must quietly run on
    CPU rather than failing on an Apple Silicon machine.
    """

    from speech.transcriber import _resolve_whisper_device

    device, compute = _resolve_whisper_device("mps", "float16")

    assert device == "cpu"

    # float16 is a GPU format; CPU wants int8.
    assert compute == "int8"


def test_whisper_keeps_supported_devices():

    from speech.transcriber import _resolve_whisper_device

    assert _resolve_whisper_device("cuda", "float16") == (
        "cuda",
        "float16",
    )
    assert _resolve_whisper_device("cpu", "int8") == (
        "cpu",
        "int8",
    )


def test_whisper_auto_follows_shared_device(monkeypatch):

    from speech import transcriber

    _fake_backends(monkeypatch, cuda=False, mps=True)

    device, _ = transcriber._resolve_whisper_device(
        "auto",
        "int8",
    )

    # auto -> mps -> downgraded to cpu for CTranslate2.
    assert device == "cpu"
