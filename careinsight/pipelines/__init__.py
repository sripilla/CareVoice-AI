"""
Speech-to-English backend registry.

Backends are imported lazily: `seamless` pulls in a multi-GB model
stack and `indic` needs a gated download, so selecting one must not
cost anything for the others.
"""

from config import PIPELINE
from careinsight.pipelines.base import SpeechPipeline, SpeechResult
from utils.logger import get_logger

logger = get_logger(__name__)

PIPELINES = {
    "cascade": (
        "careinsight.pipelines.cascade",
        "CascadePipeline",
    ),
    "seamless": (
        "careinsight.pipelines.seamless",
        "SeamlessPipeline",
    ),
    "indic": (
        "careinsight.pipelines.indic",
        "IndicPipeline",
    ),
}


def get_pipeline_class(name: str = None):
    """
    Return the pipeline class for a backend name.
    """

    name = (name or PIPELINE).strip().lower()

    if name not in PIPELINES:

        raise ValueError(
            f"Unknown pipeline '{name}'. "
            f"Expected one of: {', '.join(sorted(PIPELINES))}."
        )

    import importlib

    module_path, class_name = PIPELINES[name]

    module = importlib.import_module(module_path)

    return getattr(module, class_name)


def build_pipeline(name: str = None) -> SpeechPipeline:
    """
    Instantiate the configured speech-to-English backend.
    """

    name = (name or PIPELINE).strip().lower()

    pipeline_class = get_pipeline_class(name)

    logger.info("Using '%s' pipeline: %s", name, pipeline_class.label)

    return pipeline_class()


__all__ = [
    "PIPELINES",
    "SpeechPipeline",
    "SpeechResult",
    "build_pipeline",
    "get_pipeline_class",
]
