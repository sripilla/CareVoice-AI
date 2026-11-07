"""
Language-specific fine-tuned Whisper models, used only for the batch
evaluation comparison against the baseline large-v3 model used by the
main app (speech/transcriber.py). Not used by the production pipeline.

Models (community fine-tunes by vasista22, Apache-2.0):
    Telugu:  vasista22/whisper-telugu-large-v2
    Kannada: vasista22/whisper-kannada-medium (no "large" variant
             exists for Kannada from this author, so this is the
             best available size)
"""

import soundfile as sf
import torch
import torchaudio
from transformers import WhisperForConditionalGeneration, WhisperProcessor

FINETUNED_MODELS = {
    "te": "vasista22/whisper-telugu-large-v2",
    "kn": "vasista22/whisper-kannada-medium",
}

TARGET_SAMPLE_RATE = 16000


class FineTunedTranscriber:
    """
    Wraps a language-specific fine-tuned Whisper model loaded via
    plain transformers (these checkpoints aren't available in
    CTranslate2/faster-whisper format).
    """

    def __init__(self, language_code: str):
        if language_code not in FINETUNED_MODELS:
            raise ValueError(
                f"No fine-tuned model configured for language "
                f"'{language_code}'."
            )

        model_name = FINETUNED_MODELS[language_code]

        self.processor = WhisperProcessor.from_pretrained(model_name)

        self.model = WhisperForConditionalGeneration.from_pretrained(
            model_name
        )

        self.model.eval()

        # Force decoding in the fine-tuned language/task, matching how
        # these models are intended to be used (no auto language
        # detection needed since the checkpoint is single-language).
        self.forced_decoder_ids = (
            self.processor.get_decoder_prompt_ids(
                language=language_code,
                task="transcribe",
            )
        )

    def transcribe(self, audio_path: str) -> str:
        """
        Transcribe an audio file, resampling to 16kHz mono as needed.
        """

        # Read with soundfile (libsndfile) instead of torchaudio.load(),
        # which now requires the separate torchcodec package for
        # decoding. soundfile handles plain WAV files directly.
        audio_np, sample_rate = sf.read(
            audio_path,
            dtype="float32",
            always_2d=True,
        )

        waveform = torch.from_numpy(audio_np.T)

        if waveform.shape[0] > 1:
            waveform = waveform.mean(dim=0, keepdim=True)

        if sample_rate != TARGET_SAMPLE_RATE:
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
                forced_decoder_ids=self.forced_decoder_ids,
            )

        transcript = self.processor.batch_decode(
            predicted_ids,
            skip_special_tokens=True,
        )[0]

        return transcript.strip()
