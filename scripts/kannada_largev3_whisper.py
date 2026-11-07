"""
Standalone transcriber for BuzzASR/kannada, a Kannada-only fine-tune
of openai/whisper-large-v3 - kept fully separate from
finetuned_whisper.py (which uses vasista22/whisper-kannada-medium) so
that script stays untouched. This is an alternative, less-verified
Kannada model to compare against both the large-v3 baseline and the
vasista22 medium fine-tune.

Not used by the production pipeline.
"""

import soundfile as sf
import torch
from transformers import (
    GenerationConfig,
    WhisperForConditionalGeneration,
    WhisperProcessor,
)

MODEL_NAME = "BuzzASR/kannada"

# BuzzASR models are reported to be large-v3-based, so use large-v3's
# generation_config as the fallback if this checkpoint's own is
# incomplete (same issue hit with the vasista22 fine-tunes).
BASE_GENERATION_CONFIG = "openai/whisper-large-v3"

TARGET_SAMPLE_RATE = 16000


class KannadaLargeV3Transcriber:
    """
    Wraps BuzzASR/kannada, loaded via plain transformers (CPU/float32,
    no CUDA-specific code - the model card's example assumes a GPU,
    but that's not required for inference).
    """

    def __init__(self):
        self.processor = WhisperProcessor.from_pretrained(MODEL_NAME)

        # This checkpoint's weights are stored in float16 (its model
        # card's example runs on GPU). Force float32 on load so the
        # weights match our float32 audio input - float16 also isn't
        # a useful/always-supported optimization on CPU anyway.
        self.model = WhisperForConditionalGeneration.from_pretrained(
            MODEL_NAME,
            torch_dtype=torch.float32,
        )

        self.model.eval()

        try:
            # Prefer the checkpoint's own generation_config if it's
            # complete.
            self.model.generate(
                torch.zeros(1, 80, 3000),
                language="kn",
                task="transcribe",
                max_new_tokens=1,
            )
        except ValueError:
            # Incomplete generation_config (missing lang_to_id/
            # task_to_id/is_multilingual) - same issue as the
            # vasista22 fine-tunes. Fall back to large-v3's config.
            self.model.generation_config = (
                GenerationConfig.from_pretrained(BASE_GENERATION_CONFIG)
            )

    def transcribe(self, audio_path: str) -> str:
        """
        Transcribe an audio file, resampling to 16kHz mono as needed.
        """

        audio_np, sample_rate = sf.read(
            audio_path,
            dtype="float32",
            always_2d=True,
        )

        waveform = torch.from_numpy(audio_np.T)

        if waveform.shape[0] > 1:
            waveform = waveform.mean(dim=0, keepdim=True)

        if sample_rate != TARGET_SAMPLE_RATE:
            import torchaudio

            resampler = torchaudio.transforms.Resample(
                orig_freq=sample_rate,
                new_freq=TARGET_SAMPLE_RATE,
            )
            waveform = resampler(waveform)

        audio = waveform.squeeze(0).numpy()

        inputs = self.processor(
            audio,
            sampling_rate=TARGET_SAMPLE_RATE,
            return_tensors="pt",
        )

        with torch.no_grad():
            predicted_ids = self.model.generate(
                inputs.input_features,
                language="kn",
                task="transcribe",
            )

        transcript = self.processor.batch_decode(
            predicted_ids,
            skip_special_tokens=True,
        )[0]

        return transcript.strip()
